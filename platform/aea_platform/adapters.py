from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from .kafka_config import kafka_producer_config
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

        Groups `experience_invalidation` rows (written by `apply_experience_patch`
        or `invalidate_projection`) into one event per context version, in
        monotonic order, so a resuming client receives only the deltas it missed.
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

    def invalidate_projection(self, session_id: str, *, projection_key: str,
                              reason: str) -> int | None:
        """Bump context version and record a workspace projection invalidation.

        Used when authoritative domain state changes outside experience-state
        patches (e.g. order status for NFR-011 reactive tracking). Does not
        mutate the experience-state JSON document.
        """
        row = self.connection.execute(
            "UPDATE orchestration.experience_session "
            "SET context_version = context_version + 1, updated_at = clock_timestamp() "
            "WHERE session_id=%s AND lifecycle_status='active' "
            "RETURNING context_version",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        context_version = row[0]
        self.connection.execute(
            "INSERT INTO orchestration.experience_invalidation "
            "(session_id, context_version, projection_key, reason) "
            "VALUES (%s,%s,%s,%s) "
            "ON CONFLICT (session_id, context_version, projection_key) DO NOTHING",
            (session_id, context_version, projection_key, reason),
        )
        return context_version


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
            self.connection.execute(
                "INSERT INTO inventory.availability_observation "
                "(product_id,available_quantity,source_version,observed_at) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (product_id, source_version) DO NOTHING",
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

    def list_observations(self, product_ids: tuple[str, ...] | None = None) -> list[dict]:
        """Validated snapshot history for FR-012 trend analysis."""
        if product_ids:
            rows = self.connection.execute(
                "SELECT product_id,available_quantity,source_version,observed_at "
                "FROM inventory.availability_observation WHERE product_id=ANY(%s) "
                "ORDER BY product_id, observed_at, source_version",
                (list(product_ids),),
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT product_id,available_quantity,source_version,observed_at "
                "FROM inventory.availability_observation "
                "ORDER BY product_id, observed_at, source_version",
            ).fetchall()
        return [{
            "product_id": row[0],
            "available_quantity": int(row[1]),
            "source_version": int(row[2]),
            "observed_at": row[3],
        } for row in rows]

    def record_forecast(self, *, session_id: str, context_version: int,
                        message_id: str, correlation_id: str,
                        subject_reference: str, published_at: datetime,
                        items) -> None:
        payload = {
            "product_ids": [item.product_id for item in items],
            "recommendations": [{
                "product_id": item.product_id,
                "trend": item.trend,
                "recommendation": item.recommendation,
                "fact_references": list(item.fact_references),
            } for item in items],
        }
        envelope = {
            "message_id": message_id, "topic": "inventory.forecast.ready",
            "message_type": "event", "schema_version": "1.0.0",
            "session_id": session_id, "correlation_id": correlation_id,
            "source": "inventory", "context_version": context_version,
            "publication_time": published_at.isoformat(),
            "security_context": {"classification": "confidential",
                                 "subject_reference": subject_reference},
            "payload": payload, "outcome": {},
        }
        self.connection.execute(
            "INSERT INTO orchestration.outbox_message "
            "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
            "VALUES (%s,%s,%s,'inventory.forecast.ready',%s,%s::jsonb)",
            (message_id, session_id, context_version, session_id, json.dumps(envelope)),
        )


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
            "SELECT order_id::text,status,delayed FROM orchestration.customer_order "
            "WHERE session_id=%s", (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {"order_id": row[0], "status": row[1], "delayed": row[2]}

    def checkout_view(self, session_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT order_id::text,status,product,delivery,context_version "
            "FROM orchestration.customer_order WHERE session_id=%s", (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {"order_id": row[0], "status": row[1], "product": row[2],
                "delivery": row[3], "context_version": row[4]}

    def _checkout_envelope(self, *, message_id, topic, source, session_id, order_id,
                           context_version, correlation_id, subject_reference,
                           published_at, payload) -> dict:
        return {
            "message_id": message_id, "topic": topic, "message_type": "event",
            "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": correlation_id, "source": source,
            "context_version": context_version, "publication_time": published_at.isoformat(),
            "security_context": {"classification": "confidential",
                                 "subject_reference": subject_reference},
            "payload": payload, "outcome": {},
        }

    def request_checkout(self, *, session_id, order_id, total, payment_reference, message_id,
                         correlation_id, subject_reference, published_at, context_version,
                         product=None, delivery=None) -> bool:
        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT status FROM orchestration.customer_order WHERE session_id=%s FOR UPDATE",
                (session_id,)).fetchone()
            if row is None or row[0] not in ("created", "submitted"):
                return False
            if isinstance(product, dict) and isinstance(delivery, dict):
                self.connection.execute(
                    "UPDATE orchestration.customer_order SET status='submitted', "
                    "product=%s::jsonb, delivery=%s::jsonb, context_version=%s, "
                    "updated_at=clock_timestamp() WHERE session_id=%s",
                    (json.dumps(product), json.dumps(delivery), context_version, session_id))
            else:
                self.connection.execute(
                    "UPDATE orchestration.customer_order SET status='submitted', "
                    "updated_at=clock_timestamp() WHERE session_id=%s", (session_id,))
            self.connection.execute(
                "INSERT INTO orchestration.checkout_intent "
                "(order_id,session_id,payment_reference,total,correlation_id,"
                "subject_reference,context_version) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (order_id) DO UPDATE SET "
                "payment_reference=EXCLUDED.payment_reference, total=EXCLUDED.total, "
                "correlation_id=EXCLUDED.correlation_id, "
                "subject_reference=EXCLUDED.subject_reference, "
                "context_version=EXCLUDED.context_version, decline_code=NULL, "
                "updated_at=clock_timestamp()",
                (order_id, session_id, payment_reference, total, correlation_id,
                 subject_reference, context_version))
            envelope = self._checkout_envelope(
                message_id=message_id, topic="order.checkout.requested", source="orchestration",
                session_id=session_id, order_id=order_id, context_version=context_version,
                correlation_id=correlation_id, subject_reference=subject_reference,
                published_at=published_at, payload={"draft_order_id": order_id, "total": total})
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'order.checkout.requested',%s,%s::jsonb)",
                (message_id, session_id, context_version, order_id, json.dumps(envelope)))
            return True

    def remember_browser_product(self, session_id: str) -> None:
        """Persist the least-data accepted-order projection for FR-008 reorder."""
        self.connection.execute(
            "INSERT INTO orchestration.browser_order_recall "
            "(recall_id, product_id, order_id, expires_at) "
            "SELECT s.recall_id, btrim(o.product->>'product_id'), o.order_id, "
            "clock_timestamp() + interval '30 days' "
            "FROM orchestration.experience_session s "
            "JOIN orchestration.customer_order o ON o.session_id = s.session_id "
            "WHERE s.session_id=%s AND s.recall_id IS NOT NULL "
            "AND o.status IN ('confirmed','preparing','dispatched',"
            "'delivered','completed') "
            "AND COALESCE(btrim(o.product->>'product_id'), '') <> '' "
            "ON CONFLICT (recall_id) DO UPDATE SET "
            "product_id=EXCLUDED.product_id, order_id=EXCLUDED.order_id, "
            "expires_at=EXCLUDED.expires_at, updated_at=clock_timestamp()",
            (session_id,),
        )

    def recalled_product_id(self, session_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT r.product_id FROM orchestration.experience_session s "
            "JOIN orchestration.browser_order_recall r ON r.recall_id = s.recall_id "
            "JOIN orchestration.customer_order o ON o.order_id = r.order_id "
            "WHERE s.session_id=%s AND s.lifecycle_status='active' "
            "AND r.expires_at > clock_timestamp() "
            "AND o.status IN ('confirmed','preparing','dispatched',"
            "'delivered','completed')",
            (session_id,),
        ).fetchone()
        if row is None or not isinstance(row[0], str) or not row[0].strip():
            return None
        return row[0].strip()

    def load_checkout_intent(self, order_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT order_id::text,session_id::text,payment_reference,total,correlation_id,"
            "subject_reference,context_version,decline_code "
            "FROM orchestration.checkout_intent WHERE order_id=%s", (order_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "order_id": row[0], "session_id": row[1], "payment_reference": row[2],
            "total": float(row[3]), "correlation_id": row[4], "subject_reference": row[5],
            "context_version": row[6], "decline_code": row[7],
        }

    def clear_checkout_intent(self, order_id: str) -> None:
        self.connection.execute(
            "DELETE FROM orchestration.checkout_intent WHERE order_id=%s", (order_id,))

    def record_authorization_succeeded(self, *, session_id, order_id, message_id,
                                       correlation_id, subject_reference, published_at,
                                       context_version) -> None:
        envelope = self._checkout_envelope(
            message_id=message_id, topic="payment.authorization.succeeded", source="payment",
            session_id=session_id, order_id=order_id, context_version=context_version,
            correlation_id=correlation_id, subject_reference=subject_reference,
            published_at=published_at,
            payload={"authorization_id": message_id, "draft_order_id": order_id})
        self.connection.execute(
            "INSERT INTO orchestration.outbox_message "
            "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
            "VALUES (%s,%s,%s,'payment.authorization.succeeded',%s,%s::jsonb)",
            (message_id, session_id, context_version, order_id, json.dumps(envelope)))

    def record_authorization_failed(self, *, session_id, order_id, decline_code, message_id,
                                    correlation_id, subject_reference, published_at,
                                    context_version) -> None:
        self.connection.execute(
            "UPDATE orchestration.checkout_intent SET decline_code=%s, "
            "updated_at=clock_timestamp() WHERE order_id=%s",
            (decline_code, order_id))
        envelope = self._checkout_envelope(
            message_id=message_id, topic="payment.authorization.failed", source="payment",
            session_id=session_id, order_id=order_id, context_version=context_version,
            correlation_id=correlation_id, subject_reference=subject_reference,
            published_at=published_at,
            payload={"draft_order_id": order_id,
                     "recoverable_error": {"code": decline_code}})
        self.connection.execute(
            "INSERT INTO orchestration.outbox_message "
            "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
            "VALUES (%s,%s,%s,'payment.authorization.failed',%s,%s::jsonb)",
            (message_id, session_id, context_version, order_id, json.dumps(envelope)))

    def confirm(self, *, session_id, order_id, message_id, correlation_id,
                subject_reference, published_at, context_version) -> bool:
        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT status FROM orchestration.customer_order WHERE session_id=%s FOR UPDATE",
                (session_id,)).fetchone()
            if row is None or row[0] != "submitted":
                return False
            self.connection.execute(
                "UPDATE orchestration.customer_order SET status='confirmed', "
                "updated_at=clock_timestamp() WHERE session_id=%s", (session_id,))
            # FR-008 history becomes eligible only after payment authorization and
            # the authoritative order transition succeed in this transaction.
            self.remember_browser_product(session_id)
            envelope = self._checkout_envelope(
                message_id=message_id, topic="order.confirmed", source="order",
                session_id=session_id, order_id=order_id, context_version=context_version,
                correlation_id=correlation_id, subject_reference=subject_reference,
                published_at=published_at,
                payload={"order_id": order_id, "confirmation_state": "confirmed"})
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'order.confirmed',%s,%s::jsonb)",
                (message_id, session_id, context_version, order_id, json.dumps(envelope)))
            PsycopgExperienceStateStore(self.connection).invalidate_projection(
                session_id, projection_key="order", reason="order_confirmed")
            return True

    def advance_status(self, *, session_id: str, target_status: str,
                       allowed_priors: tuple[str, ...], message_id: str,
                       correlation_id: str, subject_reference: str,
                       published_at: datetime) -> dict | None:
        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT order_id::text,status,context_version FROM orchestration.customer_order "
                "WHERE session_id=%s FOR UPDATE", (session_id,),
            ).fetchone()
            if row is None:
                return None
            order_id, current, context_version = row
            if current not in allowed_priors:
                return {"order_id": order_id, "status": current, "changed": False}
            # A forward move also resolves any active delay (FR-023).
            self.connection.execute(
                "UPDATE orchestration.customer_order SET status=%s, delayed=false, "
                "updated_at=clock_timestamp() WHERE session_id=%s", (target_status, session_id))
            envelope = {
                "message_id": message_id, "topic": "order.status.updated",
                "message_type": "event", "schema_version": "1.0.0", "session_id": session_id,
                "correlation_id": correlation_id, "source": "order",
                "context_version": context_version,
                "publication_time": published_at.isoformat(),
                "security_context": {"classification": "confidential",
                                     "subject_reference": subject_reference},
                "payload": {"order_id": order_id, "authoritative_status": target_status},
                "outcome": {},
            }
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'order.status.updated',%s,%s::jsonb)",
                (message_id, session_id, context_version, order_id, json.dumps(envelope)))
            PsycopgExperienceStateStore(self.connection).invalidate_projection(
                session_id, projection_key="order", reason="order_status_updated")
            return {"order_id": order_id, "status": target_status, "changed": True}

    def set_delay(self, *, session_id: str, delayed: bool, message_id: str,
                  correlation_id: str, subject_reference: str,
                  published_at: datetime) -> dict | None:
        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT order_id::text,status,context_version FROM orchestration.customer_order "
                "WHERE session_id=%s FOR UPDATE", (session_id,)).fetchone()
            if row is None:
                return None
            order_id, status, context_version = row
            authoritative_status = "delayed" if delayed else status
            self.connection.execute(
                "UPDATE orchestration.customer_order SET delayed=%s, updated_at=clock_timestamp() "
                "WHERE session_id=%s", (delayed, session_id))
            envelope = {
                "message_id": message_id, "topic": "order.status.updated",
                "message_type": "event", "schema_version": "1.0.0", "session_id": session_id,
                "correlation_id": correlation_id, "source": "order",
                "context_version": context_version,
                "publication_time": published_at.isoformat(),
                "security_context": {"classification": "confidential",
                                     "subject_reference": subject_reference},
                "payload": {"order_id": order_id, "authoritative_status": authoritative_status},
                "outcome": {},
            }
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'order.status.updated',%s,%s::jsonb)",
                (message_id, session_id, context_version, order_id, json.dumps(envelope)))
            PsycopgExperienceStateStore(self.connection).invalidate_projection(
                session_id, projection_key="order", reason="order_status_updated")
            return {"order_id": order_id, "status": status, "delayed": delayed,
                    "authoritative_status": authoritative_status}


class PsycopgSupportStore:
    """Publish FAQ, situational, and escalation support events."""

    def __init__(self, connection):
        self.connection = connection

    def record_answer(self, *, session_id: str, answer: str,
                      approved_source_references: list, message_id: str,
                      correlation_id: str, subject_reference: str,
                      published_at: datetime, context_version: int) -> None:
        envelope = {
            "message_id": message_id, "topic": "support.faq.answered",
            "message_type": "event", "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": correlation_id, "source": "ai-concierge",
            "context_version": context_version, "publication_time": published_at.isoformat(),
            "security_context": {"classification": "confidential",
                                 "subject_reference": subject_reference},
            "payload": {"answer": answer,
                        "approved_source_references": list(approved_source_references)},
            "outcome": {},
        }
        with self.connection.transaction():
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'support.faq.answered',%s,%s::jsonb)",
                (message_id, session_id, context_version, session_id, json.dumps(envelope)))

    def record_situation(self, *, session_id: str, answer: str, situation_kind: str,
                         fact_references: list, message_id: str, correlation_id: str,
                         subject_reference: str, published_at: datetime,
                         context_version: int) -> None:
        envelope = {
            "message_id": message_id, "topic": "support.situation.answered",
            "message_type": "event", "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": correlation_id, "source": "support-service",
            "context_version": context_version, "publication_time": published_at.isoformat(),
            "security_context": {"classification": "confidential",
                                 "subject_reference": subject_reference},
            "payload": {"answer": answer, "situation_kind": situation_kind,
                        "fact_references": list(fact_references)},
            "outcome": {},
        }
        with self.connection.transaction():
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'support.situation.answered',%s,%s::jsonb)",
                (message_id, session_id, context_version, session_id, json.dumps(envelope)))

    def record_escalation(self, *, session_id: str, escalation_reason: str,
                          context_reference: str, message_id: str,
                          correlation_id: str, subject_reference: str,
                          published_at: datetime, context_version: int) -> None:
        envelope = {
            "message_id": message_id, "topic": "support.escalation.requested",
            "message_type": "command", "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": correlation_id, "source": "support-service",
            "context_version": context_version, "publication_time": published_at.isoformat(),
            "security_context": {"classification": "confidential",
                                 "subject_reference": subject_reference},
            "payload": {"escalation_reason": escalation_reason,
                        "context_reference": context_reference},
            "outcome": {},
        }
        with self.connection.transaction():
            self.connection.execute(
                "INSERT INTO orchestration.outbox_message "
                "(message_id,session_id,context_version,topic,aggregate_key,envelope) "
                "VALUES (%s,%s,%s,'support.escalation.requested',%s,%s::jsonb)",
                (message_id, session_id, context_version, session_id, json.dumps(envelope)))

    def list_escalations(self, *, limit: int = 50) -> list[dict]:
        """Recent `support.escalation.requested` rows for a florist inbox.

        Returns opaque session/context references and the allowlisted reason.
        Envelope security_context (subject_reference) is not exposed.
        """
        capped = min(max(int(limit), 1), 50)
        rows = self.connection.execute(
            "SELECT message_id, session_id, created_at, envelope "
            "FROM orchestration.outbox_message "
            "WHERE topic = 'support.escalation.requested' "
            "ORDER BY created_at DESC LIMIT %s",
            (capped,)).fetchall()
        items = []
        for message_id, session_id, created_at, envelope in rows:
            payload = (envelope or {}).get("payload") or {}
            requested_at = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)
            items.append({
                "message_id": str(message_id),
                "session_id": str(session_id),
                "escalation_reason": payload.get("escalation_reason"),
                "context_reference": payload.get("context_reference"),
                "requested_at": requested_at,
            })
        return items

    def list_session_answers(self, *, session_id: str, limit: int = 20) -> list[dict]:
        """Prior ASO answers for florist follow-up. Least-data; no subject_reference."""
        capped = min(max(int(limit), 1), 20)
        rows = self.connection.execute(
            "SELECT message_id, created_at, topic, envelope "
            "FROM orchestration.outbox_message "
            "WHERE session_id = %s AND topic IN "
            "('support.faq.answered', 'support.situation.answered') "
            "ORDER BY created_at ASC LIMIT %s",
            (session_id, capped)).fetchall()
        items = []
        for message_id, created_at, topic, envelope in rows:
            payload = (envelope or {}).get("payload") or {}
            answered_at = (
                created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at))
            kind = "situation" if topic == "support.situation.answered" else "faq"
            item = {
                "message_id": str(message_id),
                "kind": kind,
                "answer": payload.get("answer"),
                "answered_at": answered_at,
            }
            if kind == "faq":
                refs = payload.get("approved_source_references") or []
                if isinstance(refs, list):
                    item["approved_source_references"] = [
                        str(ref) for ref in refs if isinstance(ref, str)][:8]
            else:
                if isinstance(payload.get("situation_kind"), str):
                    item["situation_kind"] = payload["situation_kind"]
                refs = payload.get("fact_references") or []
                if isinstance(refs, list):
                    item["fact_references"] = [
                        str(ref) for ref in refs if isinstance(ref, str)][:8]
            if isinstance(item.get("answer"), str) and item["answer"]:
                items.append(item)
        return items


class PsycopgRetrievalStore:
    """pgvector + FTS hybrid store for retrieval.knowledge_chunk (ADR-014/015)."""

    def __init__(self, connection):
        self.connection = connection

    def upsert(self, rows: list[dict]) -> None:
        from .retrieval import vector_literal
        with self.connection.transaction():
            for row in rows:
                self.connection.execute(
                    "INSERT INTO retrieval.knowledge_chunk "
                    "(chunk_id,source_reference,body,terms,embedding) "
                    "VALUES (%s,%s,%s,%s,%s::vector) "
                    "ON CONFLICT (chunk_id) DO UPDATE SET "
                    "source_reference=EXCLUDED.source_reference, body=EXCLUDED.body, "
                    "terms=EXCLUDED.terms, embedding=EXCLUDED.embedding, "
                    "updated_at=clock_timestamp()",
                    (row["chunk_id"], row["source_reference"], row["body"], row["terms"],
                     vector_literal(row["embedding"])))

    def vector_search(self, embedding, *, allowed, limit) -> list[dict]:
        from .retrieval import vector_literal
        literal = vector_literal(embedding)
        if allowed is None:
            rows = self.connection.execute(
                "SELECT chunk_id,source_reference,body FROM retrieval.knowledge_chunk "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (literal, limit)).fetchall()
        elif not allowed:
            return []
        else:
            rows = self.connection.execute(
                "SELECT chunk_id,source_reference,body FROM retrieval.knowledge_chunk "
                "WHERE source_reference = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s",
                (list(allowed), literal, limit)).fetchall()
        return [{"chunk_id": row[0], "source_reference": row[1], "body": row[2],
                 "vector_rank": index, "keyword_rank": None}
                for index, row in enumerate(rows, start=1)]

    def keyword_search(self, query: str, *, allowed, limit) -> list[dict]:
        from .retrieval import fts_or_query
        tsquery = fts_or_query(query)
        if not tsquery:
            return []
        if allowed is None:
            rows = self.connection.execute(
                "SELECT chunk_id,source_reference,body FROM retrieval.knowledge_chunk, "
                "to_tsquery('english', %s) AS query "
                "WHERE search_tsv @@ query "
                "ORDER BY ts_rank(search_tsv, query) DESC LIMIT %s",
                (tsquery, limit)).fetchall()
        elif not allowed:
            return []
        else:
            rows = self.connection.execute(
                "SELECT chunk_id,source_reference,body FROM retrieval.knowledge_chunk, "
                "to_tsquery('english', %s) AS query "
                "WHERE source_reference = ANY(%s) AND search_tsv @@ query "
                "ORDER BY ts_rank(search_tsv, query) DESC LIMIT %s",
                (tsquery, list(allowed), limit)).fetchall()
        return [{"chunk_id": row[0], "source_reference": row[1], "body": row[2],
                 "vector_rank": None, "keyword_rank": index}
                for index, row in enumerate(rows, start=1)]


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


class PsycopgQualityStore:
    """Persist payload-free NFR-008 quality/error events for intent and FAQ."""

    def __init__(self, connection):
        self.connection = connection

    def record(self, event: dict) -> None:
        recorded_at = event["recorded_at"]
        self.connection.execute(
            "INSERT INTO orchestration.ai_quality_event "
            "(event_id,path,outcome,error_code,quality_flags,assistant_mode,matched,recorded_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (event["event_id"], event["path"], event["outcome"], event.get("error_code"),
             list(event.get("quality_flags") or ()), event.get("assistant_mode"),
             event.get("matched"), recorded_at),
        )

    def summary(self) -> dict:
        counts = {
            path: {outcome: 0 for outcome in ("ok", "fallback", "unmatched", "error")}
            for path in ("intent", "faq")
        }
        for path, outcome, total in self.connection.execute(
            "SELECT path, outcome, count(*) FROM orchestration.ai_quality_event "
            "GROUP BY path, outcome"
        ).fetchall():
            counts[path][outcome] = int(total)
        recent = []
        for path, outcome, error_code, assistant_mode, quality_flags, recorded_at in (
                self.connection.execute(
                    "SELECT path, outcome, error_code, assistant_mode, quality_flags, recorded_at "
                    "FROM orchestration.ai_quality_event "
                    "WHERE outcome IN ('error', 'fallback') "
                    "ORDER BY recorded_at DESC LIMIT 20"
                ).fetchall()):
            recent.append({
                "path": path, "outcome": outcome, "error_code": error_code,
                "assistant_mode": assistant_mode,
                "quality_flags": list(quality_flags or ()),
                "recorded_at": recorded_at.isoformat() if hasattr(recorded_at, "isoformat")
                else recorded_at,
            })
        return {"paths": ["intent", "faq"], "counts": counts, "recent_errors": recent}


class KafkaAcknowledgedPublisher:
    def __init__(self, bootstrap_servers: str, client_id: str, environ=None):
        from confluent_kafka import Producer
        self.producer = Producer(
            kafka_producer_config(bootstrap_servers, client_id, environ))

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
