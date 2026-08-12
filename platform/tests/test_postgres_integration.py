from __future__ import annotations

import json
import os
import sys
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@unittest.skipUnless(os.environ.get("AEA_INTEGRATION") == "1", "container integration test")
class PostgreSQLIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        cls.psycopg = psycopg
        cls.connection = psycopg.connect(os.environ["AEA_POSTGRES_DSN"], autocommit=True)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        with self.connection.transaction():
            self.connection.execute("TRUNCATE inventory.product_availability, orchestration.message_audit, orchestration.outbox_message, "
                                    "orchestration.experience_invalidation, orchestration.consumed_message, "
                                    "orchestration.experience_session CASCADE")

    def create_session(self):
        session_id = uuid.uuid4()
        self.connection.execute(
            "INSERT INTO orchestration.experience_session "
            "(session_id, state_schema_version, expires_at) VALUES (%s, 1, clock_timestamp() + interval '1 day')",
            (session_id,),
        )
        self.connection.commit()
        return session_id

    def mutation(self, session_id, expected, message_id=None):
        message_id = message_id or uuid.uuid4()
        envelope = {
            "message_id": str(message_id), "topic": "experience.intent.updated",
            "message_type": "event", "schema_version": "1.0.0",
            "session_id": str(session_id), "correlation_id": "correlation-test",
            "source": "orchestration", "context_version": expected + 1,
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {"classification": "confidential"},
            "payload": {"structured_intent": {"occasion": "birthday"}}, "outcome": {}
        }
        messages = [{"message_id": str(message_id), "topic": "experience.intent.updated",
                     "aggregate_key": str(session_id), "envelope": envelope}]
        return self.connection.execute(
            "SELECT orchestration.apply_experience_mutation(%s,%s,1,%s::jsonb,%s::jsonb,%s::jsonb)",
            (session_id, expected, json.dumps({"intent": "birthday"}),
             json.dumps([{"projection_key": "recommendations", "reason": "intent_changed"}]),
             json.dumps(messages)),
        ).fetchone()[0]

    def test_state_version_invalidation_and_outbox_commit_together(self):
        session_id = self.create_session()
        with self.connection.transaction():
            self.assertEqual(1, self.mutation(session_id, 0))
        row = self.connection.execute(
            "SELECT s.context_version, count(DISTINCT i.projection_key), count(DISTINCT o.message_id) "
            "FROM orchestration.experience_session s "
            "LEFT JOIN orchestration.experience_invalidation i USING (session_id) "
            "LEFT JOIN orchestration.outbox_message o USING (session_id) "
            "WHERE s.session_id=%s GROUP BY s.context_version", (session_id,)
        ).fetchone()
        self.assertEqual((1, 1, 1), row)

    def test_failure_rolls_back_state_and_outbox(self):
        session_id = self.create_session()
        with self.assertRaises(RuntimeError):
            with self.connection.transaction():
                self.mutation(session_id, 0)
                raise RuntimeError("injected after mutation")
        self.connection.rollback()
        self.assertEqual(0, self.connection.execute(
            "SELECT context_version FROM orchestration.experience_session WHERE session_id=%s", (session_id,)
        ).fetchone()[0])
        self.assertEqual(0, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message WHERE session_id=%s", (session_id,)
        ).fetchone()[0])

    def test_stale_compare_and_set_rejects_second_writer(self):
        session_id = self.create_session()
        with self.connection.transaction():
            self.mutation(session_id, 0)
        with self.assertRaises(self.psycopg.errors.SerializationFailure):
            with self.connection.transaction():
                self.mutation(session_id, 0)
        self.connection.rollback()
        self.assertEqual(1, self.connection.execute(
            "SELECT context_version FROM orchestration.experience_session WHERE session_id=%s", (session_id,)
        ).fetchone()[0])

    def test_migrations_are_at_latest_version(self):
        versions = [row[0] for row in self.connection.execute(
            "SELECT version FROM orchestration.schema_migration ORDER BY version"
        ).fetchall()]
        self.assertEqual([1, 2, 3, 4, 5, 6, 7], versions)

    def test_inventory_snapshots_are_monotonic_fresh_and_governed(self):
        from aea_platform.adapters import PsycopgInventoryAvailabilityStore
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService

        session_id = self.create_session()
        now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        store = PsycopgInventoryAvailabilityStore(self.connection)
        service = InventoryAvailabilityService(store, now=lambda: now,
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000030"))
        self.assertEqual("applied", service.record(AvailabilitySnapshot("rose-1", 3, 2, now)))
        self.assertEqual("duplicate", service.record(AvailabilitySnapshot("rose-1", 3, 2, now)))
        self.assertEqual("conflict", service.record(AvailabilitySnapshot("rose-1", 4, 2, now)))
        self.assertEqual("stale", service.record(AvailabilitySnapshot("rose-1", 0, 1, now)))
        self.assertEqual("applied", service.record(AvailabilitySnapshot(
            "old-1", 2, 1, datetime(2026, 8, 12, 11, 58, tzinfo=timezone.utc))))
        result = service.validate(session_id=str(session_id),
            product_ids=["rose-1", "old-1", "missing"],
            observed_context_version=0, correlation_id="inventory-test", subject_reference="subject")
        self.assertEqual("available", result.availability["rose-1"]["status"])
        self.assertEqual({"status": "unknown", "freshness": "stale", "source_version": 1},
                         result.availability["old-1"])
        self.assertEqual("unknown", result.availability["missing"]["status"])
        event = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message WHERE message_id=%s", (result.message_id,)
        ).fetchone()[0]
        self.assertEqual("inventory.availability.validated", event["topic"])
        self.assertEqual(result.availability, event["payload"]["availability"])

    def test_intent_analysis_updates_shared_understanding_and_suggestions_atomically(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.intent import IntentAnalysisService, ReferenceIntentInterpreter

        session_id = self.create_session()
        self.connection.execute(
            "UPDATE orchestration.experience_session SET state=%s::jsonb WHERE session_id=%s",
            (json.dumps({"decisions": {"product": {"id": "kept", "completed": True}}}),
             session_id),
        )
        service = IntentAnalysisService(
            PsycopgExperienceStateStore(self.connection), ReferenceIntentInterpreter(),
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000021"),
        )
        result = service.analyze(
            session_id=str(session_id),
            message_text="Bright roses for Mum's birthday tomorrow, budget €75",
            observed_context_version=0, correlation_id="intent-correlation",
            subject_reference="subject-reference",
        )
        self.assertEqual(1, result.context_version)
        restored = PsycopgExperienceStateStore(self.connection).load(str(session_id))
        self.assertEqual("kept", restored["state"]["decisions"]["product"]["id"])
        self.assertEqual("birthday", restored["state"]["shared_understanding"]["occasion"])
        self.assertEqual(75.0, restored["state"]["shared_understanding"]["budget"])
        self.assertEqual([], restored["state"]["thought_completion"]["suggestions"])
        invalidated = {row[0] for row in self.connection.execute(
            "SELECT projection_key FROM orchestration.experience_invalidation "
            "WHERE session_id=%s AND context_version=1", (session_id,),
        ).fetchall()}
        self.assertEqual({"recommendations", "order_summary", "delivery", "conversation"},
                         invalidated)
        outbox = self.connection.execute(
            "SELECT topic,context_version,envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s", (session_id,),
        ).fetchone()
        self.assertEqual("experience.intent.updated", outbox[0])
        self.assertEqual(result.structured_intent, outbox[2]["payload"]["structured_intent"])

    def test_intent_analysis_stale_writer_rolls_back_state_and_event(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.intent import IntentAnalysisService, ReferenceIntentInterpreter

        session_id = self.create_session()
        service = IntentAnalysisService(
            PsycopgExperienceStateStore(self.connection), ReferenceIntentInterpreter()
        )
        service.analyze(session_id=str(session_id), message_text="birthday",
                        observed_context_version=0, correlation_id="first",
                        subject_reference="subject")
        with self.assertRaises(self.psycopg.errors.SerializationFailure):
            service.analyze(session_id=str(session_id), message_text="budget €50",
                            observed_context_version=0, correlation_id="stale",
                            subject_reference="subject")
        self.connection.rollback()
        restored = PsycopgExperienceStateStore(self.connection).load(str(session_id))
        self.assertEqual("birthday", restored["state"]["shared_understanding"]["occasion"])
        self.assertNotIn("budget", restored["state"]["shared_understanding"])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message WHERE session_id=%s",
            (session_id,),
        ).fetchone()[0])

    def test_shared_understanding_correction_is_selective_atomic_and_versioned(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.intent import SharedUnderstandingService

        session_id = self.create_session()
        self.connection.execute(
            "UPDATE orchestration.experience_session SET state=%s::jsonb WHERE session_id=%s",
            (json.dumps({
                "shared_understanding": {"occasion": "birthday", "budget": 50},
                "decisions": {"product": {"id": "kept", "completed": True}},
            }), session_id),
        )
        service = SharedUnderstandingService(
            PsycopgExperienceStateStore(self.connection),
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000040"),
        )
        result = service.correct(
            session_id=str(session_id), corrections={"budget": 80},
            observed_context_version=0, correlation_id="correction-correlation",
            subject_reference="subject-reference",
        )
        self.assertEqual(1, result.context_version)
        restored = PsycopgExperienceStateStore(self.connection).load(str(session_id))
        self.assertEqual(80, restored["state"]["shared_understanding"]["budget"])
        self.assertEqual("birthday", restored["state"]["shared_understanding"]["occasion"])
        self.assertEqual("kept", restored["state"]["decisions"]["product"]["id"])
        invalidated = {row[0] for row in self.connection.execute(
            "SELECT projection_key FROM orchestration.experience_invalidation "
            "WHERE session_id=%s AND context_version=1", (session_id,),
        ).fetchall()}
        self.assertEqual({"recommendations", "order_summary", "conversation"}, invalidated)
        outbox = self.connection.execute(
            "SELECT topic,context_version,envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s", (session_id,),
        ).fetchone()
        self.assertEqual(("experience.intent.updated", 1), outbox[:2])
        self.assertEqual(result.structured_intent,
                         outbox[2]["payload"]["structured_intent"])

        with self.assertRaises(self.psycopg.errors.SerializationFailure):
            service.correct(
                session_id=str(session_id), corrections={"budget": 90},
                observed_context_version=0, correlation_id="stale-correction",
                subject_reference="subject-reference",
            )
        self.connection.rollback()
        restored = PsycopgExperienceStateStore(self.connection).load(str(session_id))
        self.assertEqual(80, restored["state"]["shared_understanding"]["budget"])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message WHERE session_id=%s",
            (session_id,),
        ).fetchone()[0])

    def test_conversation_submission_commits_transcript_invalidation_and_outbox(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.conversation import ConversationService

        session_id = self.create_session()
        service = ConversationService(
            PsycopgExperienceStateStore(self.connection),
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000020"),
        )
        result = service.submit(
            session_id=str(session_id), subject_reference="subject-reference",
            message_text="flowers for Mum", observed_context_version=0,
            correlation_id="conversation-correlation",
        )
        self.assertEqual(1, result.context_version)
        projection = service.projection(session_id=str(session_id))
        self.assertEqual("flowers for Mum", projection["messages"][0]["text"])
        invalidations = self.connection.execute(
            "SELECT projection_key,reason FROM orchestration.experience_invalidation "
            "WHERE session_id=%s", (session_id,),
        ).fetchall()
        self.assertEqual([("conversation", "customer_message_submitted")], invalidations)
        outbox = self.connection.execute(
            "SELECT topic,context_version,envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s", (session_id,),
        ).fetchone()
        self.assertEqual("customer.message.submitted", outbox[0])
        self.assertEqual(1, outbox[1])
        self.assertEqual({"message_text": "flowers for Mum"}, outbox[2]["payload"])
        self.assertEqual("subject-reference", outbox[2]["security_context"]["subject_reference"])

    def test_conversation_submission_rejects_stale_writer_without_partial_state(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.conversation import ConversationService

        session_id = self.create_session()
        service = ConversationService(PsycopgExperienceStateStore(self.connection))
        service.submit(session_id=str(session_id), subject_reference="subject",
                       message_text="first", observed_context_version=0,
                       correlation_id="first")
        with self.assertRaises(self.psycopg.errors.SerializationFailure):
            service.submit(session_id=str(session_id), subject_reference="subject",
                           message_text="stale", observed_context_version=0,
                           correlation_id="stale")
        self.connection.rollback()
        projection = service.projection(session_id=str(session_id))
        self.assertEqual(["first"], [item["text"] for item in projection["messages"]])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message WHERE session_id=%s",
            (session_id,),
        ).fetchone()[0])

    def test_selective_patch_preserves_decisions_and_invalidates_only_dependents(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        initial = {
            "shared_understanding": {"occasion": "birthday", "budget": 60},
            "decisions": {"product": {"id": "rose-1", "completed": True}},
            "tiles": {"delivery": {"status": "complete"}},
        }
        self.connection.execute(
            "UPDATE orchestration.experience_session SET state=%s::jsonb WHERE session_id=%s",
            (json.dumps(initial), session_id),
        )
        store = PsycopgExperienceStateStore(self.connection)
        version = store.apply_patch(
            str(session_id), 0, 1,
            StatePatch.create(
                {"shared_understanding": {"budget": 75}},
                ["shared_understanding.budget"],
            ),
        )
        restored = store.load(str(session_id))
        self.assertEqual(1, version)
        self.assertEqual("birthday", restored["state"]["shared_understanding"]["occasion"])
        self.assertEqual(75, restored["state"]["shared_understanding"]["budget"])
        self.assertEqual(initial["decisions"], restored["state"]["decisions"])
        self.assertEqual(initial["tiles"], restored["state"]["tiles"])
        invalidated = {row[0] for row in self.connection.execute(
            "SELECT projection_key FROM orchestration.experience_invalidation "
            "WHERE session_id=%s AND context_version=1", (session_id,)
        ).fetchall()}
        self.assertEqual({"recommendations", "order_summary"}, invalidated)

    def test_selective_patch_rejects_unknown_dependency_facet(self):
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        store = PsycopgExperienceStateStore(self.connection)
        with self.assertRaises(self.psycopg.errors.InvalidParameterValue):
            store.apply_patch(
                str(session_id), 0, 1,
                StatePatch.create({"unknown": {"facet": True}}, ["unknown.facet"]),
            )
        self.connection.rollback()
        self.assertEqual(0, store.load(str(session_id))["context_version"])

    def test_consumer_idempotency_and_stale_outcome_are_transactional(self):
        from aea_platform.adapters import PsycopgConsumerTransaction

        session_id = self.create_session()
        transaction = PsycopgConsumerTransaction(self.connection)
        applied = []
        message = {
            "message_id": str(uuid.uuid4()), "topic": "experience.intent.updated",
            "session_id": str(session_id), "context_version": 0, "correlation_id": "test",
            "source": "orchestration", "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {"classification": "confidential"},
        }
        self.assertEqual("applied", transaction.apply("workspace", message, lambda item: applied.append(item)))
        self.assertEqual("duplicate", transaction.apply("workspace", message, lambda item: applied.append(item)))
        self.assertEqual(1, len(applied))

        with self.connection.transaction():
            self.mutation(session_id, 0)
        stale = dict(message, message_id=str(uuid.uuid4()), context_version=0)
        self.assertEqual("stale", transaction.apply("workspace", stale, lambda item: applied.append(item)))
        self.assertEqual(1, len(applied))

        future = dict(message, message_id=str(uuid.uuid4()), context_version=2)
        self.assertEqual("stale", transaction.apply("workspace", future, lambda item: applied.append(item)))
        self.assertEqual(1, len(applied))

        outcomes = self.connection.execute(
            "SELECT context_version,outcome,count(*) FROM orchestration.consumed_message "
            "WHERE consumer_group='workspace' GROUP BY context_version,outcome"
        ).fetchall()
        self.assertEqual({(0, "applied", 1), (0, "stale", 1), (2, "stale", 1)}, set(outcomes))

    def test_missing_session_result_is_recorded_stale_without_handler(self):
        from aea_platform.adapters import PsycopgConsumerTransaction

        missing_session_id = uuid.uuid4()
        message = {
            "message_id": str(uuid.uuid4()), "topic": "experience.intent.updated",
            "session_id": str(missing_session_id), "context_version": 0,
            "correlation_id": "missing-session", "source": "orchestration",
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {"classification": "confidential"},
        }
        applied = []
        transaction = PsycopgConsumerTransaction(self.connection)
        self.assertEqual("stale", transaction.apply("workspace", message, applied.append))
        self.assertEqual([], applied)
        self.assertEqual("stale", self.connection.execute(
            "SELECT outcome FROM orchestration.consumed_message "
            "WHERE consumer_group='workspace' AND message_id=%s",
            (message["message_id"],),
        ).fetchone()[0])

    def test_payload_free_audit_trace_records_publication_and_consumption(self):
        from aea_platform.adapters import PsycopgAuditReader, PsycopgConsumerTransaction, PsycopgOutboxStore

        session_id = self.create_session()
        message_id = uuid.uuid4()
        with self.connection.transaction():
            self.mutation(session_id, 0, message_id)
        store = PsycopgOutboxStore(self.connection)
        published_at = datetime.now(timezone.utc)
        claimed = store.claim("audit-test", 1)
        self.assertEqual(str(message_id), claimed[0].message_id)
        store.mark_published(str(message_id), published_at)

        envelope = claimed[0].envelope
        transaction = PsycopgConsumerTransaction(self.connection)
        self.assertEqual("applied", transaction.apply("workspace", envelope, lambda _: None))
        trace = PsycopgAuditReader(self.connection).trace("correlation-test")
        self.assertEqual(["publication", "consumption"], [item["stage"] for item in trace])
        self.assertEqual("published", trace[0]["outcome"]["status"])
        self.assertEqual("applied", trace[1]["outcome"]["status"])
        for item in trace:
            self.assertEqual(str(message_id), item["message_id"])
            self.assertEqual("experience.intent.updated", item["topic"])
            self.assertEqual("orchestration", item["source"])
            self.assertEqual(1, item["context_version"])
            self.assertEqual({"classification": "confidential"}, item["security_context"])
            self.assertNotIn("payload", item)

        columns = {row[0] for row in self.connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='orchestration' AND table_name='message_audit'"
        ).fetchall()}
        self.assertNotIn("payload", columns)

    def test_retry_outcome_is_audited_with_sanitized_failure_code(self):
        from aea_platform.adapters import PsycopgAuditReader, PsycopgConsumerTransaction

        session_id = self.create_session()
        message = {
            "message_id": str(uuid.uuid4()), "topic": "experience.intent.updated",
            "session_id": str(session_id), "context_version": 0,
            "correlation_id": "retry-correlation", "source": "orchestration",
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {},
        }
        PsycopgConsumerTransaction(self.connection).record_outcome(
            "workspace", message, "retry", "TimeoutError"
        )
        trace = PsycopgAuditReader(self.connection).trace("retry-correlation")
        self.assertEqual("retry", trace[0]["outcome"]["status"])
        self.assertEqual("TimeoutError", trace[0]["outcome"]["failure_code"])
