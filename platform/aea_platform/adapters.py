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

    def invalidations_after(self, session_id: str, after_context_version: int) -> list[dict]:
        """Per-context-version change trail for the workspace stream.

        Groups `experience_invalidation` rows (written by `apply_experience_patch`)
        into one event per context version, in monotonic order, so a resuming
        client receives only the deltas it missed.
        """
        rows = self.connection.execute(
            "SELECT context_version,projection_key,reason FROM orchestration.experience_invalidation "
            "WHERE session_id=%s AND context_version > %s ORDER BY context_version,projection_key",
            (session_id, after_context_version),
        ).fetchall()
        grouped: dict[int, list] = {}
        for context_version, projection_key, reason in rows:
            grouped.setdefault(int(context_version), []).append(
                {"projection_key": projection_key, "reason": reason})
        return [{"context_version": version, "invalidated_projections": grouped[version]}
                for version in sorted(grouped)]


class PsycopgInventoryAvailabilityStore:
    """Monotonic inventory authority with atomic validation publication."""

    def __init__(self, connection):
        self.connection = connection

    def record_snapshot(self, product_id: str, available_quantity: int,
                        source_version: int, observed_at: datetime) -> str:
        with self.connection.transaction():
            current = self.connection.execute(
                "SELECT available_quantity,source_version,observed_at FROM inventory.product_availability "
                "WHERE product_id=%s FOR UPDATE", (product_id,),
            ).fetchone()
            if current is not None and source_version < current[1]:
                return "stale"
            if current is not None and source_version == current[1]:
                return "duplicate" if (available_quantity, observed_at) == (current[0], current[2]) else "conflict"
            self.connection.execute(
                "INSERT INTO inventory.product_availability "
                "(product_id,available_quantity,source_version,observed_at) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (product_id) DO UPDATE SET available_quantity=EXCLUDED.available_quantity, "
                "source_version=EXCLUDED.source_version,observed_at=EXCLUDED.observed_at,updated_at=clock_timestamp()",
                (product_id, available_quantity, source_version, observed_at),
            )
            return "applied"

    def validate_and_enqueue(self, *, session_id: str, expected_context_version: int,
                             product_ids: tuple[str, ...], freshness_cutoff: datetime,
                             message_id: str, correlation_id: str, subject_reference: str,
                             published_at: datetime) -> dict[str, dict]:
        with self.connection.transaction():
            session = self.connection.execute(
                "SELECT context_version FROM orchestration.experience_session "
                "WHERE session_id=%s AND lifecycle_status='active' FOR UPDATE", (session_id,),
            ).fetchone()
            if session is None or session[0] != expected_context_version:
                raise RuntimeError("stale experience context")
            rows = self.connection.execute(
                "SELECT product_id,available_quantity,source_version,observed_at "
                "FROM inventory.product_availability WHERE product_id=ANY(%s)",
                (list(product_ids),),
            ).fetchall()
            indexed = {row[0]: row for row in rows}
            availability = {}
            for product_id in product_ids:
                row = indexed.get(product_id)
                if row is None:
                    availability[product_id] = {"status": "unknown", "freshness": "missing"}
                elif row[3] < freshness_cutoff:
                    availability[product_id] = {"status": "unknown", "freshness": "stale",
                                                "source_version": row[2]}
                else:
                    availability[product_id] = {
                        "status": "available" if row[1] > 0 else "unavailable",
                        "freshness": "current", "available_quantity": row[1],
                        "source_version": row[2], "observed_at": row[3].isoformat(),
                    }
            payload = {"product_ids": list(product_ids), "availability": availability}
            envelope = {
                "message_id": message_id, "topic": "inventory.availability.validated",
                "message_type": "event", "schema_version": "1.0.0",
                "session_id": session_id, "correlation_id": correlation_id,
                "source": "inventory", "context_version": expected_context_version,
                "publication_time": published_at.isoformat(),
                "security_context": {"classification": "confidential",
                                     "subject_reference": subject_reference},
                "payload": payload, "outcome": {},
            }
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'inventory.availability.validated',%s,%s::jsonb)",
                (message_id, session_id, expected_context_version, session_id, json.dumps(envelope)),
            )
            return availability

    def read_availability(self, product_ids: tuple[str, ...],
                          freshness_cutoff: datetime) -> dict[str, dict]:
        """Non-authoritative availability read for the recommendations badge.

        Reads current snapshots without an experience-context lock and without
        enqueuing a governed event. Authoritative revalidation with publication
        and audit stays in `validate_and_enqueue` at selection time.
        """
        rows = self.connection.execute(
            "SELECT product_id,available_quantity,source_version,observed_at "
            "FROM inventory.product_availability WHERE product_id=ANY(%s)",
            (list(product_ids),),
        ).fetchall()
        indexed = {row[0]: row for row in rows}
        availability = {}
        for product_id in product_ids:
            row = indexed.get(product_id)
            if row is None:
                availability[product_id] = {"status": "unknown", "freshness": "missing"}
            elif row[3] < freshness_cutoff:
                availability[product_id] = {"status": "unknown", "freshness": "stale",
                                            "source_version": row[2]}
            else:
                availability[product_id] = {
                    "status": "available" if row[1] > 0 else "unavailable",
                    "freshness": "current", "available_quantity": row[1],
                    "source_version": row[2], "observed_at": row[3].isoformat(),
                }
        return availability


class PsycopgRecommendationStore:
    """Recommendation authority publication for product.recommendations.ready."""

    def __init__(self, connection):
        self.connection = connection

    def enqueue_ready(
        self,
        *,
        session_id: str,
        expected_context_version: int,
        message_id: str,
        correlation_id: str,
        subject_reference: str,
        published_at: datetime,
        eligible_product_ids: list[str],
        ranking: list[dict],
    ) -> None:
        with self.connection.transaction():
            session = self.connection.execute(
                "SELECT context_version FROM orchestration.experience_session "
                "WHERE session_id=%s AND lifecycle_status='active' FOR UPDATE",
                (session_id,),
            ).fetchone()
            if session is None or session[0] != expected_context_version:
                raise RuntimeError("stale experience context")
            payload = {
                "eligible_product_ids": list(eligible_product_ids),
                "ranking": list(ranking),
            }
            envelope = {
                "message_id": message_id,
                "topic": "product.recommendations.ready",
                "message_type": "event",
                "schema_version": "1.0.0",
                "session_id": session_id,
                "correlation_id": correlation_id,
                "source": "recommendation",
                "context_version": expected_context_version,
                "publication_time": published_at.isoformat(),
                "security_context": {
                    "classification": "confidential",
                    "subject_reference": subject_reference,
                },
                "payload": payload,
                "outcome": {},
            }
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'product.recommendations.ready',%s,%s::jsonb)",
                (
                    message_id,
                    session_id,
                    expected_context_version,
                    session_id,
                    json.dumps(envelope),
                ),
            )


class PsycopgOrderStore:
    """Customer order aggregate (FR-013). One order per experience session."""

    def __init__(self, connection):
        self.connection = connection

    def create_or_get(self, *, session_id: str, order_id: str, context_version: int,
                      product: dict, delivery: dict) -> dict:
        with self.connection.transaction():
            self.connection.execute(
                "INSERT INTO orchestration.customer_order "
                "(order_id,session_id,context_version,product,delivery) "
                "VALUES (%s,%s,%s,%s::jsonb,%s::jsonb) ON CONFLICT (session_id) DO NOTHING",
                (order_id, session_id, context_version, json.dumps(product), json.dumps(delivery)),
            )
            row = self.connection.execute(
                "SELECT order_id::text,status,context_version FROM orchestration.customer_order "
                "WHERE session_id=%s", (session_id,),
            ).fetchone()
        return {"order_id": row[0], "status": row[1], "context_version": row[2]}

    def by_session(self, session_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT order_id::text,status FROM orchestration.customer_order WHERE session_id=%s",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {"order_id": row[0], "status": row[1]}


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
