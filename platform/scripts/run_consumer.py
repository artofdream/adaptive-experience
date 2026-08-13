#!/usr/bin/env python3
"""Reference governed consumer worker for a subscriber group.

Subscribes to the topics a group consumes (per the Kafka policy) and processes
each record through the governed path: delivery guard, idempotency,
version-checked apply, retry/DLQ, and manual offset commit. The reference handler
records consumption; real subscribers supply domain handlers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.adapters import (KafkaAcknowledgedPublisher, KafkaFailureRouter,  # noqa: E402
                                   KafkaManualOffsets, PsycopgConsumerTransaction)
from aea_platform.consumer import GovernedConsumer, KafkaGovernedConsumerRunner  # noqa: E402
from aea_platform.policy import KafkaPolicy  # noqa: E402
from aea_platform.privacy import PayloadPrivacyGuard  # noqa: E402

DSN = os.environ.get(
    "AEA_POSTGRES_DSN",
    "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
)
BOOTSTRAP = os.environ.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092")
SCHEMAS = ROOT.parent / "docs" / "04-technical-architecture" / "schemas"


def subscribed_topics(policy: KafkaPolicy, group: str) -> list[str]:
    return [name for name, topic in policy.topics.items() if group in topic.subscribers]


def build_consumer_runner(connection, kafka_consumer, *, group: str,
                          publisher=None) -> KafkaGovernedConsumerRunner:
    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    guard = PayloadPrivacyGuard(policy, SCHEMAS)
    dlq_publisher = publisher or KafkaAcknowledgedPublisher(BOOTSTRAP, f"{group}-failure-router")
    governed = GovernedConsumer(
        group, PsycopgConsumerTransaction(connection), KafkaManualOffsets(kafka_consumer),
        KafkaFailureRouter(policy, dlq_publisher), guard)
    return KafkaGovernedConsumerRunner(kafka_consumer, governed)


def main() -> None:
    from confluent_kafka import Consumer
    group = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "workspace"
    loop = "--loop" in sys.argv
    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    topics = subscribed_topics(policy, group)
    consumer = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": group,
                         "enable.auto.commit": False, "auto.offset.reset": "earliest"})
    consumer.subscribe(topics)
    with psycopg.connect(DSN, autocommit=True) as connection:
        runner = build_consumer_runner(connection, consumer, group=group)
        try:
            while True:
                outcomes = runner.run_once(lambda envelope: None)
                if outcomes:
                    print(f"consumer {group} outcomes={outcomes}")
                if not loop:
                    return
        finally:
            consumer.close()


if __name__ == "__main__":
    main()
