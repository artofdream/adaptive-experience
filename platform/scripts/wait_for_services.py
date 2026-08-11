from __future__ import annotations

import os
import time

import psycopg
from confluent_kafka.admin import AdminClient


def wait(label, check, timeout=120):
    deadline = time.monotonic() + timeout
    error = None
    while time.monotonic() < deadline:
        try:
            check()
            print(f"{label} ready")
            return
        except Exception as current:
            error = current
            time.sleep(2)
    raise RuntimeError(f"{label} did not become ready: {type(error).__name__}")


def main() -> None:
    dsn = os.environ.get("AEA_POSTGRES_DSN", "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience")
    bootstrap = os.environ.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092")

    def postgres_ready():
        with psycopg.connect(dsn, connect_timeout=3) as connection:
            connection.execute("SELECT 1")

    def kafka_ready():
        AdminClient({"bootstrap.servers": bootstrap}).list_topics(timeout=3)

    wait("PostgreSQL", postgres_ready)
    wait("Kafka", kafka_ready)


if __name__ == "__main__":
    main()

