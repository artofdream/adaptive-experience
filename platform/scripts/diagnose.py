from __future__ import annotations

import os

import psycopg
from confluent_kafka.admin import AdminClient


def main() -> None:
    dsn = os.environ.get("AEA_POSTGRES_DSN", "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience")
    with psycopg.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT count(*), count(*) FILTER (WHERE claimed_until < clock_timestamp()) "
                       "FROM orchestration.outbox_message WHERE published_at IS NULL")
        pending, expired_claims = cursor.fetchone()
        cursor.execute("SELECT max(version) FROM orchestration.schema_migration")
        version = cursor.fetchone()[0]
    metadata = AdminClient({"bootstrap.servers": os.environ.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092")}).list_topics(timeout=10)
    print({"migration_version": version, "pending_outbox": pending,
           "expired_outbox_claims": expired_claims, "kafka_topics": len(metadata.topics)})


if __name__ == "__main__":
    main()

