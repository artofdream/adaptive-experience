#!/usr/bin/env python3
"""Outbox relay worker: publish governed outbox messages to Kafka, guarded.

Wires the transactional outbox to Kafka through the privacy guard so publication
is fail-closed. Run once by default, or `--loop` for a continuous worker.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.adapters import KafkaAcknowledgedPublisher, PsycopgOutboxStore  # noqa: E402
from aea_platform.outbox import OutboxRelay  # noqa: E402
from aea_platform.policy import KafkaPolicy  # noqa: E402
from aea_platform.privacy import PayloadPrivacyGuard, SourceGuardedPublisher  # noqa: E402

DSN = os.environ.get(
    "AEA_POSTGRES_DSN",
    "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
)
BOOTSTRAP = os.environ.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092")
SCHEMAS = ROOT.parent / "docs" / "04-technical-architecture" / "schemas"


def build_relay(connection, *, worker: str = "outbox-relay",
                publisher=None) -> OutboxRelay:
    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    guard = PayloadPrivacyGuard(policy, SCHEMAS)
    target = publisher or KafkaAcknowledgedPublisher(BOOTSTRAP, worker)
    return OutboxRelay(PsycopgOutboxStore(connection), SourceGuardedPublisher(guard, target), worker)


def main() -> None:
    loop = "--loop" in sys.argv
    with psycopg.connect(DSN, autocommit=True) as connection:
        relay = build_relay(connection)
        while True:
            published, failed = relay.run_once()
            print(f"relay published={published} failed={failed}")
            if not loop:
                return
            time.sleep(1)


if __name__ == "__main__":
    main()
