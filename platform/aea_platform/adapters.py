from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from .outbox import OutboxRecord
from .policy import KafkaPolicy
from .state import StatePatch


class PsycopgExperienceStateStore:
    """Authoritative selective-mutation boundary for experience state."""

    def __init__(self, connection):
        self.connection = connection

    def apply_patch(self, session_id: str, expected_context_version: int,
                    state_schema_version: int, patch: StatePatch,
                    messages: list[dict] | None = None) -> int:
        row = self.connection.execute(
            "SELECT orchestration.apply_experience_patch(%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)",
            (session_id, expected_context_version, state_schema_version,
             json.dumps(patch.values), json.dumps(patch.changed_facets),
             json.dumps(messages or [])),
        ).fetchone()
        return row[0]

    def load(self, session_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT state_schema_version,context_version,state FROM orchestration.experience_session "
            "WHERE session_id=%s AND lifecycle_status='active'",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {"state_schema_version": row[0], "context_version": row[1], "state": row[2]}


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
            cursor.execute(
                "UPDATE orchestration.message_audit SET outcome=outcome || %s::jsonb, recorded_at=%s "
                "WHERE message_id=%s AND stage='publication'",
                (json.dumps({"status": "published", "published_at": published_at.isoformat()}),
                 published_at, message_id),
            )

    def release_for_retry(self, message_id: str, error_code: str, delay_seconds: int) -> None:
        retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orchestration.outbox_message SET next_attempt_at=%s, claimed_by=NULL, "
                "claimed_until=NULL, last_error_code=%s WHERE message_id=%s AND published_at IS NULL",
                (retry_at, error_code[:128], message_id),
            )
            cursor.execute(
                "UPDATE orchestration.message_audit SET outcome=outcome || %s::jsonb, recorded_at=clock_timestamp() "
                "WHERE message_id=%s AND stage='publication'",
                (json.dumps({"status": "retry", "failure_code": error_code[:128]}), message_id),
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

    def active_context_version(self, session_id: str, *, lock: bool = False) -> int | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            "SELECT context_version FROM orchestration.experience_session "
            "WHERE session_id=%s AND lifecycle_status='active'" + suffix,
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
            # Serialize result application with intent mutations. Exact equality
            # is required: neither an older result nor a result from an unknown
            # future context may mutate the active workspace projection.
            active = self.active_context_version(message["session_id"], lock=True)
            outcome = "applied" if message["context_version"] == active else "stale"
            if outcome == "applied":
                handler(message)
            self.connection.execute(
                "INSERT INTO orchestration.consumed_message "
                "(consumer_group,message_id,topic,session_id,context_version,outcome,correlation_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (consumer_group, message_id, message["topic"], message["session_id"],
                 message["context_version"], outcome, message.get("correlation_id")),
            )
            self._write_audit(consumer_group, message, outcome)
            return outcome

    def record_outcome(self, consumer_group: str, message: dict,
                       outcome: str, failure_code: str | None = None) -> None:
        with self.connection.transaction():
            self.connection.execute(
                "INSERT INTO orchestration.consumed_message "
                "(consumer_group,message_id,topic,session_id,context_version,outcome,failure_code,correlation_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (consumer_group,message_id) DO NOTHING",
                (consumer_group, message["message_id"], message["topic"], message.get("session_id"),
                 message["context_version"], outcome, failure_code, message["correlation_id"]),
            )
            self._write_audit(consumer_group, message, outcome, failure_code)

    def _write_audit(self, consumer_group: str, message: dict, outcome: str,
                     failure_code: str | None = None) -> None:
        details = {"status": outcome}
        if failure_code:
            details["failure_code"] = failure_code
        self.connection.execute(
            "INSERT INTO orchestration.message_audit "
            "(message_id,stage,actor,topic,source,correlation_id,context_version,publication_time,outcome,security_context) "
            "VALUES (%s,'consumption',%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb) "
            "ON CONFLICT (message_id,stage,actor) DO UPDATE SET outcome=EXCLUDED.outcome, recorded_at=clock_timestamp()",
            (message["message_id"], consumer_group, message["topic"], message["source"],
             message["correlation_id"], message["context_version"], message["publication_time"],
             json.dumps(details), json.dumps(message["security_context"])),
        )


class PsycopgAuditReader:
    """Return payload-free workflow trace metadata for authorized operator paths."""

    def __init__(self, connection):
        self.connection = connection

    def trace(self, correlation_id: str) -> list[dict]:
        rows = self.connection.execute(
            "SELECT message_id::text,stage,actor,topic,source,correlation_id,context_version,"
            "publication_time,outcome,security_context,recorded_at "
            "FROM orchestration.message_audit WHERE correlation_id=%s ORDER BY recorded_at",
            (correlation_id,),
        ).fetchall()
        keys = ("message_id", "stage", "actor", "topic", "source", "correlation_id",
                "context_version", "publication_time", "outcome", "security_context", "recorded_at")
        return [dict(zip(keys, row)) for row in rows]


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
