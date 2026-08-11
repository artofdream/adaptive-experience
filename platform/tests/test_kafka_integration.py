from __future__ import annotations

import os
import sys
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@unittest.skipUnless(os.environ.get("AEA_INTEGRATION") == "1", "container integration test")
class KafkaIntegrationTests(unittest.TestCase):
    def test_acknowledged_publish_and_manual_offset_commit(self):
        from confluent_kafka import Consumer, TopicPartition
        from aea_platform.adapters import KafkaAcknowledgedPublisher, KafkaManualOffsets
        from aea_platform.consumer import ConsumedRecord

        bootstrap = os.environ["AEA_KAFKA_BOOTSTRAP"]
        group = f"workspace-ci-{uuid.uuid4()}"
        consumer = Consumer({
            "bootstrap.servers": bootstrap,
            "group.id": group,
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
        })
        consumer.subscribe(["customer.message.submitted"])
        session_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        envelope = {
            "message_id": message_id,
            "topic": "customer.message.submitted",
            "message_type": "event",
            "schema_version": "1.0.0",
            "session_id": session_id,
            "correlation_id": str(uuid.uuid4()),
            "source": "orchestration",
            "context_version": 1,
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {},
            "payload": {"message_text": "integration-test"},
            "outcome": {},
        }
        publisher = KafkaAcknowledgedPublisher(bootstrap, "outbox-relay-ci")
        publisher.publish(envelope["topic"], session_id, envelope)

        deadline = time.monotonic() + 30
        received = None
        while time.monotonic() < deadline:
            candidate = consumer.poll(1)
            if candidate is not None and candidate.error() is None:
                import json
                decoded = json.loads(candidate.value())
                if decoded["message_id"] == message_id:
                    received = candidate
                    break
        self.assertIsNotNone(received)
        record = ConsumedRecord(received.topic(), received.partition(), received.offset(), envelope)
        KafkaManualOffsets(consumer).commit(record)
        committed = consumer.committed(
            [TopicPartition(received.topic(), received.partition())], timeout=10
        )[0]
        self.assertEqual(received.offset() + 1, committed.offset)
        consumer.close()
