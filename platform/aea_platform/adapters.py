from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from .outbox import OutboxRecord
from .policy import KafkaPolicy


class PsycopgOutboxStore:
    def __init__(self, connection):
        self.connection = connection

    def claim(self, worker: str, limit: int) -> list[OutboxRecord]:
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orchestration.claim_outbox(%s, %s)", (worker, limit))
            columns = [item.name for item in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return [OutboxRecord(str(r["message_id"]), r["topic"], r["aggregate_key"],
                             r["envelope"], r["attempt_count"]) for r in rows]

    def mark_published(self, message_id: str, published_at: datetime) -> None:
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orchestration.outbox_message SET published_at=%s, claimed_by=NULL, "
                "claimed_until=NULL, last_error_code=NULL WHERE message_id=%s AND published_at IS NULL",
                (published_at, message_id),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("outbox publication claim was lost")

    def release_for_retry(self, message_id: str, error_code: str, delay_seconds: int) -> None:
        retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orchestration.outbox_message SET next_attempt_at=%s, claimed_by=NULL, "
                "claimed_until=NULL, last_error_code=%s WHERE message_id=%s AND published_at IS NULL",
                (retry_at, error_code[:128], message_id),
            )


class PsycopgConsumerTransaction:
    """Run the handler and idempotency outcome in one local transaction."""

    def __init__(self, connection):
        self.connection = connection

    def outcome(self, consumer_group: str, message_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT outcome FROM orchestration.consumed_message "
            "WHERE consumer_group=%s AND message_id=%s",
            (consumer_group, message_id),
        ).fetchone()
        return row[0] if row else None

    def active_context_version(self, session_id: str) -> int | None:
        row = self.connection.execute(
            "SELECT context_version FROM orchestration.experience_session WHERE session_id=%s",
            (session_id,),
        ).fetchone()
        return row[0] if row else None

    def apply(self, consumer_group: str, message: dict, handler) -> str:
        message_id = message["message_id"]
        with self.connection.transaction():
            # Serialize concurrent deliveries of one logical message without
            # holding a session-wide lock.
            self.connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"{consumer_group}:{message_id}",),
            )
            prior = self.outcome(consumer_group, message_id)
            if prior is not None:
                return "duplicate"
            active = self.active_context_version(message["session_id"])
            outcome = "stale" if active is not None and message["context_version"] < active else "applied"
            if outcome == "applied":
                handler(message)
            self.connection.execute(
                "INSERT INTO orchestration.consumed_message "
                "(consumer_group,message_id,topic,session_id,context_version,outcome,correlation_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (consumer_group, message_id, message["topic"], message["session_id"],
                 message["context_version"], outcome, message.get("correlation_id")),
            )
            return outcome


class KafkaAcknowledgedPublisher:
    def __init__(self, bootstrap_servers: str, client_id: str):
        from confluent_kafka import Producer
        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id,
            "acks": "all",
            "enable.idempotence": True,
            "max.in.flight.requests.per.connection": 5,
        })

    def publish(self, topic: str, key: str, message: dict) -> None:
        result: dict = {}

        def delivered(error, broker_message):
            result["error"] = error
            result["message"] = broker_message

        self.producer.produce(topic, key=key.encode(), value=json.dumps(message).encode(), callback=delivered)
        remaining = self.producer.flush(30)
        if remaining or result.get("error") is not None or "message" not in result:
            raise RuntimeError("KafkaAcknowledgementFailed")


class KafkaManualOffsets:
    def __init__(self, consumer):
        self.consumer = consumer

    def commit(self, record) -> None:
        from confluent_kafka import TopicPartition
        committed = self.consumer.commit(
            offsets=[TopicPartition(record.topic, record.partition, record.offset + 1)],
            asynchronous=False,
        )
        if not committed or committed[0].error is not None:
            raise RuntimeError("KafkaOffsetCommitFailed")


class KafkaFailureRouter:
    """Durably transfer a failure before the caller advances its source offset."""

    def __init__(self, policy: KafkaPolicy, publisher: KafkaAcknowledgedPublisher,
                 max_attempts: int = 3):
        self.policy = policy
        self.publisher = publisher
        self.max_attempts = max_attempts

    def route(self, consumer_group: str, record, error: Exception) -> str:
        envelope = deepcopy(record.message)
        topic = self.policy.require_consume(consumer_group, envelope["topic"])
        outcome = dict(envelope.get("outcome") or {})
        attempt = int(outcome.get("delivery_attempt", 0)) + 1
        outcome.update({
            "delivery_attempt": attempt,
            "failure_code": type(error).__name__[:128],
        })
        envelope["outcome"] = outcome
        recoverable = not isinstance(error, (PermissionError, ValueError))
        if recoverable and attempt <= self.max_attempts:
            tiers = self.policy.defaults["retry_tiers"]
            tier = tiers[min(attempt - 1, len(tiers) - 1)]["name"]
            destination = topic.retry_topic(consumer_group, tier)
            result = "retry"
        else:
            destination = topic.dlq_topic(consumer_group)
            result = "dead_letter"
        # The governed envelope retains its canonical topic. The retry/DLQ name
        # is transport routing metadata only.
        self.publisher.publish(destination, envelope[topic.key], envelope)
        return result
