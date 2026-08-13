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


def _order_status_envelope(session_id, message_id, order_id, *, poisoned=False):
    payload = {"order_id": str(order_id), "authoritative_status": "preparing"}
    if poisoned:
        payload["card_number"] = "4111111111111111"
    return {
        "message_id": str(message_id), "topic": "order.status.updated",
        "message_type": "event", "schema_version": "1.0.0", "session_id": str(session_id),
        "correlation_id": str(uuid.uuid4()), "source": "order", "context_version": 0,
        "publication_time": datetime.now(timezone.utc).isoformat(),
        "security_context": {"classification": "confidential"},
        "payload": payload, "outcome": {},
    }


@unittest.skipUnless(os.environ.get("AEA_INTEGRATION") == "1", "container integration test")
class BackboneIntegrationTests(unittest.TestCase):
    def test_relay_and_governed_consumer_run_end_to_end(self):
        import json

        import psycopg
        from confluent_kafka import Consumer

        from aea_platform.adapters import KafkaAcknowledgedPublisher

        sys.path.insert(0, str(ROOT / "scripts"))
        from run_consumer import build_consumer_runner
        from run_relay import build_relay

        bootstrap = os.environ["AEA_KAFKA_BOOTSTRAP"]
        connection = psycopg.connect(os.environ["AEA_POSTGRES_DSN"], autocommit=True)
        try:
            session_id, message_id, order_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            connection.execute(
                "INSERT INTO orchestration.experience_session "
                "(session_id,state_schema_version,expires_at) "
                "VALUES (%s,1,clock_timestamp() + interval '1 day')", (session_id,))
            connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,0,'order.status.updated',%s,%s::jsonb)",
                (message_id, session_id, str(order_id),
                 json.dumps(_order_status_envelope(session_id, message_id, order_id))))

            group_id = f"workspace-e2e-{uuid.uuid4()}"
            consumer = Consumer({"bootstrap.servers": bootstrap, "group.id": group_id,
                                 "enable.auto.commit": False, "auto.offset.reset": "earliest"})
            consumer.subscribe(["order.status.updated"])
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and not consumer.assignment():
                consumer.poll(0.5)
            self.assertTrue(consumer.assignment(), "consumer never received an assignment")

            # The relay publishes the outbox message to Kafka through the guard.
            relay = build_relay(connection, worker="relay-e2e",
                                publisher=KafkaAcknowledgedPublisher(bootstrap, "relay-e2e"))
            self.assertEqual((1, 0), relay.run_once())

            # The governed consumer decodes, guards delivery, applies, and commits.
            runner = build_consumer_runner(connection, consumer, group="workspace")
            outcomes: list = []
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and "applied" not in outcomes:
                outcomes += runner.run_once(lambda envelope: None, timeout=1.0)
            self.assertIn("applied", outcomes)
            self.assertEqual("applied", connection.execute(
                "SELECT outcome FROM orchestration.consumed_message "
                "WHERE consumer_group='workspace' AND message_id=%s", (message_id,)).fetchone()[0])
            consumer.close()

            # Fail-closed: a poisoned outbox message is never published to the broker.
            poison_id = uuid.uuid4()
            connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,0,'order.status.updated',%s,%s::jsonb)",
                (poison_id, session_id, str(order_id),
                 json.dumps(_order_status_envelope(session_id, poison_id, order_id, poisoned=True))))
            self.assertEqual((0, 1), relay.run_once())
            self.assertIsNone(connection.execute(
                "SELECT published_at FROM orchestration.outbox_message WHERE message_id=%s",
                (poison_id,)).fetchone()[0])
        finally:
            connection.close()


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
        assignment_deadline = time.monotonic() + 60
        while time.monotonic() < assignment_deadline and not consumer.assignment():
            consumer.poll(0.5)
        self.assertTrue(consumer.assignment(), "consumer group did not receive a partition assignment")

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

        deadline = time.monotonic() + 60
        received = None
        while time.monotonic() < deadline:
            candidate = consumer.poll(1)
            if candidate is not None and candidate.error() is not None:
                self.fail(f"Kafka consume failed: {candidate.error()}")
            if candidate is not None:
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
