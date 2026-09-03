from __future__ import annotations

import json
import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta, timezone
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
            self.connection.execute("TRUNCATE retrieval.knowledge_chunk, inventory.availability_observation, inventory.product_availability, orchestration.ai_quality_event, orchestration.message_audit, orchestration.outbox_message, "
                                    "orchestration.experience_invalidation, orchestration.consumed_message, "
                                    "orchestration.browser_order_recall, orchestration.experience_session CASCADE")

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
            "SELECT orchestration.apply_experience_patch(%s,%s,1,%s::jsonb,%s::jsonb,%s::jsonb)",
            (session_id, expected,
             json.dumps({"shared_understanding": {"occasion": "birthday"}}),
             json.dumps(["shared_understanding.occasion"]),
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
        expected = [
            int(path.name[:3])
            for path in sorted((ROOT / "migrations").glob("[0-9][0-9][0-9]_*.sql"))
        ]
        self.assertEqual(len(expected), 24)
        self.assertTrue({19, 20, 21, 22, 23, 24}.issubset(set(expected)))
        self.assertEqual(expected, versions)

    def test_superseded_mutation_function_is_dropped(self):
        signature = "(uuid,bigint,integer,jsonb,jsonb,jsonb)"
        self.assertIsNone(self.connection.execute(
            f"SELECT to_regprocedure('orchestration.apply_experience_mutation{signature}')"
        ).fetchone()[0])
        self.assertIsNotNone(self.connection.execute(
            f"SELECT to_regprocedure('orchestration.apply_experience_patch{signature}')"
        ).fetchone()[0])

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

    def test_inventory_forecast_uses_validated_snapshot_history(self):
        import asyncio
        from aea_platform.adapters import PsycopgInventoryAvailabilityStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService

        session_id = self.create_session()
        now = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        inventory.record(AvailabilitySnapshot(
            "classic-rose-dozen", 10, 1, now - timedelta(days=2)))
        inventory.record(AvailabilitySnapshot("classic-rose-dozen", 4, 2, now))
        inventory.record(AvailabilitySnapshot("pink-flower-vase", 5, 1, now))
        app = InternalOrchestrationApp(self.connection, "internal-token")
        app.forecast.now = lambda: now
        status, body = asyncio.run(self._invoke_internal(
            app, "GET", "/internal/v1/operator/forecasts", b"",
            f"session_id={session_id}".encode()))
        self.assertEqual(200, status)
        items = {item["product_id"]: item for item in body["items"]}
        self.assertEqual("declining", items["classic-rose-dozen"]["trend"])
        self.assertIn("Plan a replenishment", items["classic-rose-dozen"]["recommendation"])
        self.assertEqual("insufficient", items["pink-flower-vase"]["trend"])
        event = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message WHERE topic=%s",
            ("inventory.forecast.ready",),
        ).fetchone()[0]
        self.assertEqual(["classic-rose-dozen", "pink-flower-vase"], event["payload"]["product_ids"])

    def test_workspace_projection_and_stream_expose_facets_and_invalidations(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        store = PsycopgExperienceStateStore(self.connection)
        # A shared-understanding change bumps the context version and derives a
        # recommendations invalidation through the projection_dependency registry.
        with self.connection.transaction():
            new_version = store.apply_patch(
                str(session_id), 0, 1,
                StatePatch.create({"shared_understanding": {"occasion": "birthday"}},
                                  ["shared_understanding.occasion"]), [])
        self.assertEqual(1, new_version)

        trail = store.invalidations_after(str(session_id), 0)
        self.assertEqual(1, trail[0]["context_version"])
        self.assertIn("recommendations",
                      [p["projection_key"] for p in trail[0]["invalidated_projections"]])

        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(path, query=b""):
            return asyncio.run(self._invoke_internal(app, "GET", path, b"", query))

        status, workspace = drive(f"/internal/v1/sessions/{session_id}/workspace")
        self.assertEqual(200, status)
        self.assertEqual(1, workspace["context_version"])
        self.assertEqual("birthday",
                         workspace["facets"]["shared_understanding"]["structured_intent"]["occasion"])
        self.assertIn("conversation", workspace["facets"])

        _, snapshot = drive(f"/internal/v1/sessions/{session_id}/stream")
        self.assertEqual("snapshot", snapshot["events"][0]["kind"])
        self.assertEqual(1, snapshot["events"][0]["context_version"])

        _, delta = drive(f"/internal/v1/sessions/{session_id}/stream", b"after=0")
        self.assertEqual("invalidation", delta["events"][0]["kind"])
        self.assertIn("recommendations",
                      [p["projection_key"] for p in delta["events"][0]["invalidated_projections"]])

    def test_order_creation_assembles_decisions_and_is_idempotent(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")
        order_body = json.dumps({"correlation_id": "ord"}).encode()

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        # No assembled decisions yet -> order is incomplete.
        status, result = drive("POST", f"/internal/v1/sessions/{session_id}/order", order_body)
        self.assertEqual(422, status)
        self.assertEqual("order_incomplete", result["code"])

        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "classic-rose-dozen",
                                           "options": {"size": "large",
                                                       "card_message": "Happy birthday Mum"}}}},
                ["decisions.product"]), [])
        with self.connection.transaction():
            store.apply_patch(str(session_id), 1, 1, StatePatch.create(
                {"decisions": {"delivery": {"destination_reference": "addr-9",
                                            "timing": {"date": "2026-09-01", "window": "morning"}}}},
                ["decisions.delivery"]), [])

        status2, created = drive("POST", f"/internal/v1/sessions/{session_id}/order", order_body)
        self.assertEqual(202, status2)
        self.assertEqual("created", created["order_status"])
        order_id = created["order_id"]
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.customer_order WHERE session_id=%s",
            (session_id,)).fetchone()[0])

        _, workspace = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
        self.assertEqual({"order_id": order_id, "status": "created", "delayed": False,
                          "authoritative_status": "created"}, workspace["facets"]["order"])

        # Idempotent per session: a second create returns the same order.
        _, again = drive("POST", f"/internal/v1/sessions/{session_id}/order", order_body)
        self.assertEqual(order_id, again["order_id"])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.customer_order WHERE session_id=%s",
            (session_id,)).fetchone()[0])

        list_status, listed = drive("GET", "/internal/v1/operator/orders")
        self.assertEqual(200, list_status)
        matching = [item for item in listed["items"] if item["order_id"] == order_id]
        self.assertEqual(1, len(matching))
        item = matching[0]
        self.assertEqual(str(session_id), item["session_id"])
        self.assertEqual("created", item["status"])
        self.assertEqual("classic-rose-dozen", item["product_id"])
        self.assertEqual("addr-9", item["destination_reference"])
        self.assertEqual({"date": "2026-09-01", "window": "morning"}, item["timing"])
        self.assertEqual("Happy birthday Mum", item["card_message"])
        self.assertEqual("Classic Rose Dozen", item["catalog_title"])
        self.assertEqual("unpaid", item["payment_state"])
        self.assertIsNone(item["channel"])
        self.assertNotIn("email", item)
        self.assertNotIn("product", item)
        self.assertNotIn("delivery", item)
        self.assertNotIn("payment_reference", item)
        self.assertNotIn("street", item)
        self.assertNotIn("decline_code", item)
        blob = json.dumps(listed)
        self.assertNotIn("email", blob)
        self.assertNotIn("@", blob)

    def test_workspace_projection_latency_under_repeated_load(self):
        import asyncio
        import time
        from aea_platform.adapters import (PsycopgExperienceStateStore,
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        now = datetime.now(timezone.utc)
        InventoryAvailabilityService(PsycopgInventoryAvailabilityStore(self.connection),
            now=lambda: now).record(AvailabilitySnapshot("classic-rose-dozen", 5, 1, now))
        store = PsycopgExperienceStateStore(self.connection)
        for expected, patch, facet in (
                (0, {"shared_understanding": {"occasion": "birthday"}}, "shared_understanding.occasion"),
                (1, {"decisions": {"product": {"product_id": "classic-rose-dozen"}}}, "decisions.product"),
                (2, {"decisions": {"delivery": {"destination_reference": "addr-1",
                     "timing": {"date": "2026-09-01", "window": "morning"}}}}, "decisions.delivery")):
            with self.connection.transaction():
                store.apply_patch(str(session_id), expected, 1,
                                  StatePatch.create(patch, [facet]), [])

        app = InternalOrchestrationApp(self.connection, "internal-token")
        asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/order",
            json.dumps({"correlation_id": "ord"}).encode()))

        # The heaviest read path: aggregate every facet (conversation, intent,
        # recommendations, order summary, order, delivery, selection) repeatedly.
        latencies, facets, status = [], None, None
        for _ in range(50):
            start = time.monotonic()
            status, workspace = asyncio.run(self._invoke_internal(
                app, "GET", f"/internal/v1/sessions/{session_id}/workspace"))
            latencies.append(time.monotonic() - start)
            facets = workspace["facets"]
        self.assertEqual(200, status)
        for key in ("recommendations", "order_summary", "order", "delivery", "selection"):
            self.assertIn(key, facets)
        latencies.sort()
        p95 = latencies[int(0.95 * len(latencies))]
        self.assertLess(p95, 1.0, f"workspace projection p95 too slow: {p95:.3f}s")

    def test_order_summary_facet_reflects_and_recomputes_from_decisions(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        store = PsycopgExperienceStateStore(self.connection)
        app = InternalOrchestrationApp(self.connection, "internal-token")

        def workspace():
            _, ws = asyncio.run(self._invoke_internal(
                app, "GET", f"/internal/v1/sessions/{session_id}/workspace"))
            return ws

        # No product decision yet -> no order summary.
        self.assertNotIn("order_summary", workspace()["facets"])

        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "classic-rose-dozen"}}},
                ["decisions.product"]), [])
        summary = workspace()["facets"]["order_summary"]
        self.assertEqual(70.0, summary["total"])
        labels = [c["label"] for c in summary["itemized_charges"]]
        self.assertEqual("product", labels[0])
        for required in ("product", "customization", "tax", "discount"):
            self.assertIn(required, labels)

        # Adding the delivery decision recomputes the summary (derived projection).
        with self.connection.transaction():
            store.apply_patch(str(session_id), 1, 1, StatePatch.create(
                {"decisions": {"delivery": {"destination_reference": "addr-1",
                                            "timing": {"date": "2026-09-01", "window": "morning"}}}},
                ["decisions.delivery"]), [])
        summary2 = workspace()["facets"]["order_summary"]
        self.assertEqual(round(70.0 + REFERENCE_DELIVERY_FEE, 2), summary2["total"])
        labels2 = [c["label"] for c in summary2["itemized_charges"]]
        for required in ("product", "customization", "delivery", "tax", "discount"):
            self.assertIn(required, labels2)

    def test_quantity_update_after_cart_select_reflects_in_order_summary(self):
        """Regression: updating quantity through the single-product customize path
        (T-04) must not be shadowed by the stale `items` cart entry written by the
        initial card select. apply_experience_patch deep-merges objects, so the
        earlier `items:[qty 1]` survived and the FR-018 summary (which prefers
        `items` over top-level options) kept pricing a quantity of 2 as 1."""
        import asyncio
        from aea_platform.adapters import (PsycopgExperienceStateStore,  # noqa: F401
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService

        app = InternalOrchestrationApp(self.connection, "internal-token")
        session_id = self.create_session()
        now = datetime.now(timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        inventory.record(AvailabilitySnapshot("budget-mixed-bunch", 9, 1, now))

        def workspace():
            return asyncio.run(self._invoke_internal(
                app, "GET", f"/internal/v1/sessions/{session_id}/workspace"))[1]

        # 1) Browser "Select" on a recommendation card: a cart `items` entry with
        #    quantity 1 (the selectProduct path). Summary prices a single unit.
        status, first = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/selection",
            json.dumps({"product_id": "budget-mixed-bunch",
                        "items": [{"product_id": "budget-mixed-bunch", "quantity": 1,
                                   "options": {"quantity": 1}}],
                        "options": {"quantity": 1},
                        "observed_context_version": 0,
                        "correlation_id": "card-select"}).encode()))
        self.assertEqual(202, status)
        self.assertEqual(35.0, workspace()["facets"]["order_summary"]["total"])

        # 2) T-04 customize confirm: single-product options with quantity 2, no items.
        status, _second = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/selection",
            json.dumps({"product_id": "budget-mixed-bunch",
                        "options": {"quantity": 2},
                        "observed_context_version": first["context_version"],
                        "correlation_id": "customize-qty"}).encode()))
        self.assertEqual(202, status)

        summary = workspace()["facets"]["order_summary"]
        self.assertEqual(70.0, summary["total"])
        product_charge = [c for c in summary["itemized_charges"] if c["label"] == "product"][0]
        self.assertEqual(2, product_charge["quantity"])
        self.assertEqual(70.0, product_charge["amount"])

    def _order_ready_for_checkout(self, app):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.state import StatePatch
        session_id = self.create_session()
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "classic-rose-dozen"}}},
                ["decisions.product"]), [])
        with self.connection.transaction():
            store.apply_patch(str(session_id), 1, 1, StatePatch.create(
                {"decisions": {"delivery": {"destination_reference": "addr-1",
                                            "timing": {"date": "2026-09-01", "window": "morning"}}}},
                ["decisions.delivery"]), [])
        asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/order",
            json.dumps({"correlation_id": "ord"}).encode()))
        return session_id

    def test_checkout_confirms_order_and_publishes_events(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE

        app = InternalOrchestrationApp(self.connection, "internal-token")
        session_id = self._order_ready_for_checkout(app)
        total = round(70.0 + REFERENCE_DELIVERY_FEE, 2)
        path = f"/internal/v1/sessions/{session_id}/checkout"

        def post(payload):
            return asyncio.run(self._invoke_internal(app, "POST", path, json.dumps(payload).encode()))

        # Wrong total is rejected; a raw card reference is rejected.
        self.assertEqual(409, post({"payment_reference": "tok", "observed_total": 1.0,
                                    "correlation_id": "c"})[0])
        self.assertEqual(422, post({"payment_reference": "4111111111111111",
                                    "observed_total": total, "correlation_id": "c"})[0])

        status, result = post({"payment_reference": "tok_1", "observed_total": total,
                               "correlation_id": "c"})
        self.assertEqual(202, status)
        self.assertEqual("accepted", result["code"])
        self.assertTrue(result["pending"])
        self.assertEqual("confirmed", result["order_status"])

        topics = [row[0] for row in self.connection.execute(
            "SELECT topic FROM orchestration.outbox_message WHERE session_id=%s", (session_id,)).fetchall()]
        self.assertIn("order.checkout.requested", topics)
        self.assertIn("payment.authorization.succeeded", topics)
        self.assertIn("order.confirmed", topics)
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.consumed_message "
            "WHERE consumer_group='payment' AND outcome='applied'",).fetchone()[0])

        # NFR-013: the actual emitted checkout events are broker-clean (payment-free,
        # exact governed shape). The guard raises if any card/token/PII leaks.
        from aea_platform.policy import KafkaPolicy
        from aea_platform.privacy import PayloadPrivacyGuard
        guard = PayloadPrivacyGuard(KafkaPolicy.load(ROOT / "config" / "kafka-policy.json"),
                                    ROOT.parent / "docs" / "04-technical-architecture" / "schemas")
        for topic, principal in (("order.checkout.requested", "orchestration"),
                                 ("payment.authorization.succeeded", "payment"),
                                 ("order.confirmed", "order")):
            emitted = self.connection.execute(
                "SELECT envelope FROM orchestration.outbox_message "
                "WHERE session_id=%s AND topic=%s", (session_id, topic)).fetchone()[0]
            guard.validate_publication(principal, topic, emitted)

        _, workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{session_id}/workspace"))
        self.assertEqual("confirmed", workspace["facets"]["order"]["status"])

        # Re-checkout on a confirmed order conflicts.
        self.assertEqual(409, post({"payment_reference": "tok_1", "observed_total": total,
                                    "correlation_id": "c2"})[0])

    def test_workspace_hints_same_session_accepted_order_on_recommendations(self):
        import asyncio
        from aea_platform.adapters import (PsycopgExperienceStateStore,
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE
        from aea_platform.state import StatePatch

        app = InternalOrchestrationApp(self.connection, "internal-token")
        session_id = self._order_ready_for_checkout(app)
        now = datetime.now(timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        for product_id, qty in (("classic-rose-dozen", 5), ("lilac-bouquet", 2),
                                ("budget-mixed-bunch", 4)):
            inventory.record(AvailabilitySnapshot(product_id, qty, 1, now))

        def workspace():
            return asyncio.run(self._invoke_internal(
                app, "GET", f"/internal/v1/sessions/{session_id}/workspace"))[1]

        loaded = workspace()
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(
                str(session_id), loaded["context_version"], 1,
                StatePatch.create(
                    {"shared_understanding": {"occasion": "birthday", "budget": 100}},
                    ["shared_understanding.occasion", "shared_understanding.budget"]),
                [])

        draft_items = workspace()["facets"]["recommendations"]["items"]
        self.assertEqual("budget-mixed-bunch", draft_items[0]["product_id"])
        self.assertFalse(any(item.get("prior_order_hint") for item in draft_items))

        total = round(70.0 + REFERENCE_DELIVERY_FEE, 2)
        status, _result = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/checkout",
            json.dumps({"payment_reference": "tok_hint", "observed_total": total,
                        "correlation_id": "hint"}).encode()))
        self.assertEqual(202, status)

        hinted = workspace()["facets"]["recommendations"]["items"]
        self.assertEqual("classic-rose-dozen", hinted[0]["product_id"])
        self.assertTrue(hinted[0]["prior_order_hint"])

    def test_workspace_hints_durable_browser_recall_on_new_session(self):
        """FR-008 recall is isolated, least-data, and starts normal selection."""
        import asyncio
        from aea_platform.adapters import (PsycopgExperienceStateStore,
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE
        from aea_platform.state import StatePatch

        app = InternalOrchestrationApp(self.connection, "internal-token")
        first = self._order_ready_for_checkout(app)
        recall_id = str(uuid.uuid4())
        self.assertEqual(204, asyncio.run(self._invoke_internal(
            app, "PUT", f"/internal/v1/sessions/{first}",
            json.dumps({"recall_id": recall_id}).encode()))[0])

        now = datetime.now(timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        for product_id, qty in (("classic-rose-dozen", 5), ("lilac-bouquet", 2),
                                ("budget-mixed-bunch", 4)):
            inventory.record(AvailabilitySnapshot(product_id, qty, 1, now))

        total = round(70.0 + REFERENCE_DELIVERY_FEE, 2)
        status, _result = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{first}/checkout",
            json.dumps({"payment_reference": "tok_recall", "observed_total": total,
                        "correlation_id": "recall"}).encode()))
        self.assertEqual(202, status)

        second = uuid.uuid4()
        self.assertEqual(204, asyncio.run(self._invoke_internal(
            app, "PUT", f"/internal/v1/sessions/{second}",
            json.dumps({"recall_id": recall_id}).encode()))[0])
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(
                str(second), 0, 1,
                StatePatch.create(
                    {"shared_understanding": {"occasion": "birthday", "budget": 100}},
                    ["shared_understanding.occasion", "shared_understanding.budget"]),
                [])

        _, workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{second}/workspace"))
        items = workspace["facets"]["recommendations"]["items"]
        self.assertEqual("classic-rose-dozen", items[0]["product_id"])
        self.assertTrue(items[0]["prior_order_hint"])
        self.assertEqual(70.0, items[0]["price"])  # current catalog price, not history
        self.assertIsNone(app.order.session_prior_product_id(str(second)))
        self.assertEqual("classic-rose-dozen", app.order.prior_product_id(str(second)))

        recall_row = self.connection.execute(
            "SELECT product_id,order_id IS NOT NULL,expires_at > clock_timestamp() "
            "FROM orchestration.browser_order_recall WHERE recall_id=%s",
            (recall_id,)).fetchone()
        self.assertEqual(("classic-rose-dozen", True, True), tuple(recall_row))
        columns = {row[0] for row in self.connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='orchestration' AND table_name='browser_order_recall'")}
        self.assertEqual(
            {"recall_id", "product_id", "order_id", "expires_at", "updated_at"}, columns)

        # Reorder initiation is the normal selection command: inventory is
        # revalidated and no historical options, delivery, card, or payment return.
        status, selected = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{second}/selection",
            json.dumps({"product_id": "classic-rose-dozen", "options": {},
                        "observed_context_version": 1,
                        "correlation_id": "reorder-select"}).encode()))
        self.assertEqual(202, status)
        self.assertEqual(2, selected["context_version"])
        _, selected_workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{second}/workspace"))
        self.assertEqual(
            {"product_id": "classic-rose-dozen", "options": {}},
            selected_workspace["facets"]["selection"])
        self.assertNotIn("delivery", selected_workspace["facets"])
        self.assertNotIn("order", selected_workspace["facets"])

        # Another opaque recall ID cannot see this browser's history.
        isolated = uuid.uuid4()
        self.assertEqual(204, asyncio.run(self._invoke_internal(
            app, "PUT", f"/internal/v1/sessions/{isolated}",
            json.dumps({"recall_id": str(uuid.uuid4())}).encode()))[0])
        with self.connection.transaction():
            store.apply_patch(
                str(isolated), 0, 1,
                StatePatch.create(
                    {"shared_understanding": {"occasion": "birthday", "budget": 100}},
                    ["shared_understanding.occasion", "shared_understanding.budget"]), [])
        _, isolated_workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{isolated}/workspace"))
        self.assertFalse(any(item.get("prior_order_hint") for item in
                             isolated_workspace["facets"]["recommendations"]["items"]))

        # Expired server-side history fails closed even if a stale cookie is replayed.
        self.connection.execute(
            "UPDATE orchestration.browser_order_recall "
            "SET expires_at=clock_timestamp() - interval '1 second' WHERE recall_id=%s",
            (recall_id,))
        _, expired_workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{second}/workspace"))
        self.assertFalse(any(item.get("prior_order_hint") for item in
                             expired_workspace["facets"]["recommendations"]["items"]))

    def test_browser_session_get_binds_to_experience_session(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp

        app = InternalOrchestrationApp(self.connection, "internal-token")
        missing = uuid.uuid4()
        self.assertEqual(404, asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{missing}"))[0])
        session_id = self.create_session()
        status, body = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{session_id}"))
        self.assertEqual(200, status)
        self.assertEqual(str(session_id), body["session_id"])
        self.assertNotIn("state", body)
        recall_id = str(uuid.uuid4())
        self.assertEqual(204, asyncio.run(self._invoke_internal(
            app, "PUT", f"/internal/v1/sessions/{session_id}",
            json.dumps({"recall_id": recall_id}).encode()))[0])
        status, body = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{session_id}"))
        self.assertEqual(200, status)
        self.assertEqual(recall_id, body["recall_id"])

    def test_checkout_decline_leaves_order_submitted(self):
        import asyncio
        from aea_platform.adapters import (PsycopgExperienceStateStore,
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE
        from aea_platform.state import StatePatch

        app = InternalOrchestrationApp(self.connection, "internal-token")
        session_id = self._order_ready_for_checkout(app)
        recall_id = str(uuid.uuid4())
        self.assertEqual(204, asyncio.run(self._invoke_internal(
            app, "PUT", f"/internal/v1/sessions/{session_id}",
            json.dumps({"recall_id": recall_id}).encode()))[0])
        total = round(70.0 + REFERENCE_DELIVERY_FEE, 2)

        status, result = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/checkout",
            json.dumps({"payment_reference": "decline-1", "observed_total": total,
                        "correlation_id": "c"}).encode()))
        self.assertEqual(202, status)
        self.assertEqual("accepted", result["code"])
        self.assertTrue(result["pending"])
        self.assertEqual("submitted", result["order_status"])
        self.assertEqual("declined", result["decline_code"])

        counts = self.connection.execute(
            "SELECT "
            "count(*) FILTER (WHERE topic='order.checkout.requested'), "
            "count(*) FILTER (WHERE topic='payment.authorization.failed'), "
            "count(*) FILTER (WHERE topic='order.confirmed') "
            "FROM orchestration.outbox_message WHERE session_id=%s", (session_id,)).fetchone()
        self.assertEqual((1, 1, 0), counts)
        self.assertEqual("submitted", self.connection.execute(
            "SELECT status FROM orchestration.customer_order WHERE session_id=%s",
            (session_id,)).fetchone()[0])
        self.assertEqual(0, self.connection.execute(
            "SELECT count(*) FROM orchestration.browser_order_recall WHERE recall_id=%s",
            (recall_id,)).fetchone()[0])

        # FR-008: a declined checkout is not purchase history in a later session.
        now = datetime.now(timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        inventory.record(AvailabilitySnapshot("classic-rose-dozen", 5, 1, now))
        later = uuid.uuid4()
        self.assertEqual(204, asyncio.run(self._invoke_internal(
            app, "PUT", f"/internal/v1/sessions/{later}",
            json.dumps({"recall_id": recall_id}).encode()))[0])
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(
                str(later), 0, 1,
                StatePatch.create(
                    {"shared_understanding": {"occasion": "birthday", "budget": 100}},
                    ["shared_understanding.occasion", "shared_understanding.budget"]), [])
        _, workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{later}/workspace"))
        self.assertFalse(any(item.get("prior_order_hint") for item in
                             workspace["facets"]["recommendations"]["items"]))

    def test_checkout_creates_order_from_assembled_decisions(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE
        from aea_platform.state import StatePatch

        app = InternalOrchestrationApp(self.connection, "internal-token")
        session_id = self.create_session()
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "classic-rose-dozen"}}},
                ["decisions.product"]), [])
        with self.connection.transaction():
            store.apply_patch(str(session_id), 1, 1, StatePatch.create(
                {"decisions": {"delivery": {"destination_reference": "addr-1",
                                            "timing": {"date": "2026-09-01", "window": "morning"}}}},
                ["decisions.delivery"]), [])
        total = round(70.0 + REFERENCE_DELIVERY_FEE, 2)
        status, result = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/checkout",
            json.dumps({"payment_reference": "tok_1", "observed_total": total,
                        "correlation_id": "c"}).encode()))
        self.assertEqual(202, status)
        self.assertEqual("accepted", result["code"])
        self.assertEqual("confirmed", result["order_status"])
        self.assertTrue(result.get("order_id"))

        empty = self.create_session()
        status, result = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{empty}/checkout",
            json.dumps({"payment_reference": "tok_1", "observed_total": total,
                        "correlation_id": "c"}).encode()))
        self.assertEqual(422, status)
        self.assertEqual("order_incomplete", result["code"])

    def test_checkout_uses_live_order_summary_not_stale_submitted_snapshot(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.pricing import REFERENCE_DELIVERY_FEE
        from aea_platform.state import StatePatch

        app = InternalOrchestrationApp(self.connection, "internal-token")
        session_id = self._order_ready_for_checkout(app)
        self.connection.execute(
            "UPDATE orchestration.customer_order SET status='submitted' WHERE session_id=%s",
            (session_id,))
        store = PsycopgExperienceStateStore(self.connection)
        version = self.connection.execute(
            "SELECT context_version FROM orchestration.experience_session WHERE session_id=%s",
            (session_id,)).fetchone()[0]
        with self.connection.transaction():
            store.apply_patch(str(session_id), version, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "budget-mixed-bunch"}}},
                ["decisions.product"]), [])
        _, workspace = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{session_id}/workspace"))
        live_total = workspace["facets"]["order_summary"]["total"]
        self.assertEqual(round(35.0 + REFERENCE_DELIVERY_FEE, 2), live_total)
        self.assertEqual("submitted", workspace["facets"]["order"]["status"])
        stale = self.connection.execute(
            "SELECT product->>'product_id' FROM orchestration.customer_order WHERE session_id=%s",
            (session_id,)).fetchone()[0]
        self.assertEqual("classic-rose-dozen", stale)

        status, result = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/checkout",
            json.dumps({"payment_reference": "tok_1", "observed_total": 47,
                        "correlation_id": "c-live"}).encode()))
        self.assertEqual(202, status)
        self.assertEqual("accepted", result["code"])
        product_id = self.connection.execute(
            "SELECT product->>'product_id' FROM orchestration.customer_order WHERE session_id=%s",
            (session_id,)).fetchone()[0]
        self.assertEqual("budget-mixed-bunch", product_id)

    def test_order_status_advances_forward_and_publishes(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        status_path = f"/internal/v1/sessions/{session_id}/order/status"

        # No order yet -> 404.
        body = json.dumps({"target_status": "preparing", "correlation_id": "st"}).encode()
        self.assertEqual(404, drive("POST", status_path, body)[0])

        # Assemble decisions and create the order.
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "classic-rose-dozen"}}},
                ["decisions.product"]), [])
        with self.connection.transaction():
            store.apply_patch(str(session_id), 1, 1, StatePatch.create(
                {"decisions": {"delivery": {"destination_reference": "addr-9",
                                            "timing": {"date": "2026-09-01", "window": "morning"}}}},
                ["decisions.delivery"]), [])
        drive("POST", f"/internal/v1/sessions/{session_id}/order",
              json.dumps({"correlation_id": "ord"}).encode())

        # Forward transitions each publish order.status.updated and update the facet.
        for target in ("preparing", "dispatched", "delivered"):
            status, result = drive("POST", status_path,
                json.dumps({"target_status": target, "correlation_id": "st"}).encode())
            self.assertEqual(202, status)
            self.assertEqual(target, result["status"])
            _, workspace = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
            self.assertEqual(target, workspace["facets"]["order"]["status"])

        self.assertEqual(3, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='order.status.updated'", (session_id,)).fetchone()[0])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='order.status.updated' "
            "AND envelope->'payload'->>'authoritative_status'='delivered'",
            (session_id,)).fetchone()[0])
        # NFR-011: status writes also invalidate the workspace `order` facet so
        # SSE clients can refresh without a user-triggered pull.
        self.assertEqual(3, self.connection.execute(
            "SELECT count(*) FROM orchestration.experience_invalidation "
            "WHERE session_id=%s AND projection_key='order' "
            "AND reason='order_status_updated'", (session_id,)).fetchone()[0])
        _, stream = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/sessions/{session_id}/stream", b"", b"after=2"))
        order_events = [
            event for event in stream["events"]
            if event["kind"] == "invalidation"
            and any(p["projection_key"] == "order"
                    for p in event["invalidated_projections"])
        ]
        self.assertEqual(3, len(order_events))

        # Backward and unknown transitions are rejected.
        self.assertEqual(409, drive("POST", status_path,
            json.dumps({"target_status": "preparing", "correlation_id": "st"}).encode())[0])
        self.assertEqual(422, drive("POST", status_path,
            json.dumps({"target_status": "teleported", "correlation_id": "st"}).encode())[0])

    def test_order_delay_flag_and_completion_tracking(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        store = PsycopgExperienceStateStore(self.connection)
        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        def order_facet():
            _, ws = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
            return ws["facets"]["order"]

        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1, StatePatch.create(
                {"decisions": {"product": {"product_id": "classic-rose-dozen"}}},
                ["decisions.product"]), [])
        with self.connection.transaction():
            store.apply_patch(str(session_id), 1, 1, StatePatch.create(
                {"decisions": {"delivery": {"destination_reference": "addr-1",
                                            "timing": {"date": "2026-09-01", "window": "morning"}}}},
                ["decisions.delivery"]), [])
        drive("POST", f"/internal/v1/sessions/{session_id}/order",
              json.dumps({"correlation_id": "ord"}).encode())
        drive("POST", f"/internal/v1/sessions/{session_id}/order/status",
              json.dumps({"target_status": "preparing", "correlation_id": "st"}).encode())

        # Delay is displayed as the authoritative state and published.
        status, delayed = drive("POST", f"/internal/v1/sessions/{session_id}/order/delay",
            json.dumps({"delayed": True, "correlation_id": "dl"}).encode())
        self.assertEqual(202, status)
        self.assertEqual("delayed", delayed["authoritative_status"])
        facet = order_facet()
        self.assertTrue(facet["delayed"])
        self.assertEqual("delayed", facet["authoritative_status"])
        self.assertEqual("preparing", facet["status"])

        # A forward move resolves the delay; completion is terminal.
        drive("POST", f"/internal/v1/sessions/{session_id}/order/status",
              json.dumps({"target_status": "dispatched", "correlation_id": "st"}).encode())
        self.assertFalse(order_facet()["delayed"])
        for target in ("delivered", "completed"):
            drive("POST", f"/internal/v1/sessions/{session_id}/order/status",
                  json.dumps({"target_status": target, "correlation_id": "st"}).encode())
        final = order_facet()
        self.assertEqual("completed", final["status"])
        self.assertEqual("completed", final["authoritative_status"])

        # Every emitted order-status event is a clean, governed payload.
        from aea_platform.policy import KafkaPolicy
        from aea_platform.privacy import PayloadPrivacyGuard
        guard = PayloadPrivacyGuard(KafkaPolicy.load(ROOT / "config" / "kafka-policy.json"),
                                    ROOT.parent / "docs" / "04-technical-architecture" / "schemas")
        for row in self.connection.execute(
                "SELECT envelope FROM orchestration.outbox_message "
                "WHERE session_id=%s AND topic='order.status.updated'", (session_id,)).fetchall():
            guard.validate_publication("order", "order.status.updated", row[0])

    def test_support_answers_from_approved_knowledge_and_publishes(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.policy import KafkaPolicy
        from aea_platform.privacy import PayloadPrivacyGuard

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")
        path = f"/internal/v1/sessions/{session_id}/support"

        def ask(question):
            return asyncio.run(self._invoke_internal(
                app, "POST", path, json.dumps({"question": question, "correlation_id": "c"}).encode()))

        status, answer = ask("When do you deliver?")
        self.assertEqual(200, status)
        self.assertTrue(answer["matched"])
        self.assertIn("policy:delivery", answer["approved_source_references"])

        _, miss = ask("random unrelated gibberish token")
        self.assertFalse(miss["matched"])
        self.assertEqual([], miss["approved_source_references"])

        rows = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='support.faq.answered'", (session_id,)).fetchall()
        self.assertEqual(2, len(rows))
        guard = PayloadPrivacyGuard(KafkaPolicy.load(ROOT / "config" / "kafka-policy.json"),
                                    ROOT.parent / "docs" / "04-technical-architecture" / "schemas")
        for row in rows:
            guard.validate_publication("ai-concierge", "support.faq.answered", row[0])

        quality = self.connection.execute(
            "SELECT path, outcome, matched FROM orchestration.ai_quality_event "
            "WHERE path='faq' ORDER BY recorded_at"
        ).fetchall()
        self.assertEqual([("faq", "ok", True), ("faq", "unmatched", False)], quality)

    def test_support_situation_answers_from_session_facts(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.policy import KafkaPolicy
        from aea_platform.privacy import PayloadPrivacyGuard

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")
        status, body = asyncio.run(self._invoke_internal(
            app, "POST", f"/internal/v1/sessions/{session_id}/support",
            json.dumps({"question": "What is my order status?",
                        "correlation_id": "sit"}).encode()))
        self.assertEqual(200, status)
        self.assertEqual("situation", body["kind"])
        self.assertIn("does not have an order", body["answer"])
        envelope = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='support.situation.answered'",
            (session_id,)).fetchone()[0]
        guard = PayloadPrivacyGuard(KafkaPolicy.load(ROOT / "config" / "kafka-policy.json"),
                                    ROOT.parent / "docs" / "04-technical-architecture" / "schemas")
        guard.validate_publication("support-service", "support.situation.answered", envelope)
        self.assertEqual("order_status", envelope["payload"]["situation_kind"])

    def test_support_escalation_publishes_least_data_command(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.policy import KafkaPolicy
        from aea_platform.privacy import PayloadPrivacyGuard

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")
        path = f"/internal/v1/sessions/{session_id}/support/escalation"
        status, body = asyncio.run(self._invoke_internal(
            app, "POST", path, json.dumps({
                "reason": "unresolved_request", "correlation_id": "c",
            }).encode()))
        self.assertEqual(202, status)
        self.assertTrue(body["accepted"])
        self.assertEqual("escalation_recorded", body["code"])
        self.assertEqual("unresolved_request", body["escalation_reason"])
        self.assertIn("florist", body["acknowledgement"].lower())

        rejected = asyncio.run(self._invoke_internal(
            app, "POST", path, json.dumps({
                "reason": "call_me", "correlation_id": "c",
            }).encode()))
        self.assertEqual(422, rejected[0])
        pii = asyncio.run(self._invoke_internal(
            app, "POST", path, json.dumps({
                "reason": "unresolved_request", "correlation_id": "c",
                "email": "private@example.invalid",
            }).encode()))
        self.assertEqual(422, pii[0])

        rows = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='support.escalation.requested'",
            (session_id,)).fetchall()
        self.assertEqual(1, len(rows))
        envelope = rows[0][0]
        self.assertEqual("support-service", envelope["source"])
        self.assertEqual({"escalation_reason": "unresolved_request",
                          "context_reference": str(session_id)}, envelope["payload"])
        guard = PayloadPrivacyGuard(KafkaPolicy.load(ROOT / "config" / "kafka-policy.json"),
                                    ROOT.parent / "docs" / "04-technical-architecture" / "schemas")
        guard.validate_publication("support-service", "support.escalation.requested", envelope)

        inbox_status, inbox = asyncio.run(self._invoke_internal(
            app, "GET", "/internal/v1/operator/escalations"))
        self.assertEqual(200, inbox_status)
        self.assertEqual(1, len(inbox["items"]))
        item = inbox["items"][0]
        self.assertEqual(str(session_id), item["session_id"])
        self.assertEqual("unresolved_request", item["escalation_reason"])
        self.assertEqual(str(session_id), item["context_reference"])
        self.assertNotIn("subject_reference", item)
        self.assertNotIn("email", item)
        self.assertNotIn("security_context", item)

        summary_status, summary = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/operator/sessions/{session_id}"))
        self.assertEqual(200, summary_status)
        self.assertEqual(str(session_id), summary["session_id"])
        self.assertIn("messages", summary["conversation"])
        self.assertNotIn("email", summary)
        self.assertNotIn("payment_reference", summary)
        missing = asyncio.run(self._invoke_internal(
            app, "GET", "/internal/v1/operator/sessions/00000000-0000-0000-0000-000000000000"))
        self.assertEqual(404, missing[0])

    def test_operator_session_includes_prior_aso_answers(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")
        path = f"/internal/v1/sessions/{session_id}/support"
        faq_status, faq = asyncio.run(self._invoke_internal(
            app, "POST", path, json.dumps({
                "question": "When do you deliver?", "correlation_id": "faq",
            }).encode()))
        self.assertEqual(200, faq_status)
        self.assertTrue(faq["matched"])
        sit_status, sit = asyncio.run(self._invoke_internal(
            app, "POST", path, json.dumps({
                "question": "What is my order status?", "correlation_id": "sit",
            }).encode()))
        self.assertEqual(200, sit_status)
        self.assertEqual("situation", sit["kind"])

        status, summary = asyncio.run(self._invoke_internal(
            app, "GET", f"/internal/v1/operator/sessions/{session_id}"))
        self.assertEqual(200, status)
        answers = summary["support_answers"]
        kinds = {item["kind"] for item in answers}
        self.assertIn("faq", kinds)
        self.assertIn("situation", kinds)
        self.assertTrue(any("2 PM" in item["answer"] for item in answers if item["kind"] == "faq"))
        for item in answers:
            self.assertNotIn("subject_reference", item)
            self.assertNotIn("email", item)
            self.assertNotIn("security_context", item)

    def test_retrieval_indexes_approved_chunks_and_hybrid_query_filters_unapproved(self):
        from aea_platform.adapters import PsycopgRetrievalStore
        from aea_platform.retrieval import KnowledgeChunk, RetrievalService, chunks_from_approved

        extension = self.connection.execute(
            "SELECT 1 FROM pg_extension WHERE extname='vector'").fetchone()
        if extension is None:
            self.skipTest("pgvector extension is not available")

        service = RetrievalService(PsycopgRetrievalStore(self.connection))
        service.index(chunks_from_approved() + (
            KnowledgeChunk("evil:price", "evil:price",
                           "Same-day delivery is always free.", "deliver shipping"),))
        hits = service.retrieve(
            "shipping time for bouquets",
            allowed_source_references=("policy:delivery", "policy:returns", "product:care",
                                       "policy:substitution", "policy:card-message"))
        self.assertTrue(hits)
        self.assertEqual("policy:delivery", hits[0].source_reference)
        self.assertIsNotNone(hits[0].keyword_rank)
        self.assertNotIn("evil:price", [hit.source_reference for hit in hits])

        unrelated = service.retrieve("what is the meaning of life")
        self.assertTrue(all(hit.keyword_rank is None for hit in unrelated))

    def test_delivery_details_write_facet_and_event_without_raw_pii(self):
        import asyncio
        from aea_platform.adapters import PsycopgExperienceStateStore
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        body = json.dumps({"delivery": {"destination_reference": "addr-ref-9",
                                        "timing": {"date": "2026-09-01", "window": "morning"}},
                           "observed_context_version": 0, "correlation_id": "del"}).encode()
        status, result = drive("POST", f"/internal/v1/sessions/{session_id}/delivery", body)
        self.assertEqual(202, status)
        self.assertEqual(1, result["context_version"])

        envelope = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='delivery.details.updated'", (session_id,)).fetchone()[0]
        self.assertEqual({"destination_reference": "addr-ref-9",
                          "timing": {"date": "2026-09-01", "window": "morning"}},
                         envelope["payload"])

        _, workspace = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
        self.assertEqual("addr-ref-9", workspace["facets"]["delivery"]["destination_reference"])
        self.assertEqual({"date": "2026-09-01", "window": "morning"},
                         workspace["facets"]["delivery"]["timing"])

        # Raw recipient PII is rejected with no state mutation.
        bad = json.dumps({"delivery": {"recipient_name": "Jane", "destination_reference": "r",
                                       "timing": {"date": "2026-09-01", "window": "morning"}},
                          "observed_context_version": result["context_version"],
                          "correlation_id": "del2"}).encode()
        self.assertEqual(422, drive("POST", f"/internal/v1/sessions/{session_id}/delivery", bad)[0])

        # FR-020: an unrelated intent change preserves the delivery decision.
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), result["context_version"], 1,
                StatePatch.create({"shared_understanding": {"occasion": "anniversary"}},
                                  ["shared_understanding.occasion"]), [])
        _, workspace2 = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
        self.assertEqual("addr-ref-9", workspace2["facets"]["delivery"]["destination_reference"])

    @staticmethod
    async def _invoke_internal(app, method, path, body=b"", query=b""):
        sent = []
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}
        async def send(message):
            sent.append(message)
        scope = {"type": "http", "method": method, "path": path, "query_string": query,
                 "headers": [(b"authorization", b"Bearer internal-token"),
                             (b"x-subject-reference", b"subject-1")]}
        await app(scope, receive, send)
        return sent[0]["status"], json.loads(sent[1]["body"] or b"{}")

    def test_selection_emits_product_selected_and_recommendations_show_availability(self):
        import asyncio
        from aea_platform.adapters import (PsycopgExperienceStateStore,
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        now = datetime.now(timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        inventory.record(AvailabilitySnapshot("classic-rose-dozen", 5, 1, now))
        inventory.record(AvailabilitySnapshot("budget-mixed-bunch", 0, 1, now))  # unavailable

        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), 0, 1,
                StatePatch.create({"shared_understanding": {"occasion": "birthday"}},
                                  ["shared_understanding.occasion"]), [])

        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        # Recommendations facet is availability-aware (FR-011).
        _, workspace = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
        by_id = {item["product_id"]: item
                 for item in workspace["facets"]["recommendations"]["items"]}
        self.assertTrue(by_id["classic-rose-dozen"]["available"])

        # Selecting an available product emits product.selected exactly once at v2.
        body = json.dumps({"product_id": "classic-rose-dozen", "options": {"card_message": "hi"},
                           "observed_context_version": 1, "correlation_id": "sel-corr"}).encode()
        status, result = drive("POST", f"/internal/v1/sessions/{session_id}/selection", body)
        self.assertEqual(202, status)
        self.assertEqual(2, result["context_version"])
        selected = self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='product.selected'", (session_id,)).fetchone()[0]
        self.assertEqual(1, selected)

        _, workspace2 = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
        self.assertEqual("classic-rose-dozen", workspace2["facets"]["selection"]["product_id"])

        # An unavailable product is rejected with no product.selected and no version bump.
        bad = json.dumps({"product_id": "budget-mixed-bunch", "options": {},
                          "observed_context_version": 2, "correlation_id": "sel-corr2"}).encode()
        status_bad, result_bad = drive("POST", f"/internal/v1/sessions/{session_id}/selection", bad)
        self.assertEqual(409, status_bad)
        self.assertEqual("product_unavailable", result_bad["code"])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='product.selected'", (session_id,)).fetchone()[0])
        self.assertEqual(2, self.connection.execute(
            "SELECT context_version FROM orchestration.experience_session "
            "WHERE session_id=%s", (session_id,)).fetchone()[0])

    def test_local_inventory_seeder_writes_fresh_reference_catalog(self):
        from aea_platform.adapters import PsycopgInventoryAvailabilityStore
        from aea_platform.inventory import InventoryAvailabilityService
        from aea_platform.local_inventory_seed import (
            next_source_version, reference_product_ids, seed_once, snapshots_are_fresh,
        )

        now = datetime.now(timezone.utc)
        service = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        self.assertEqual(1, next_source_version(self.connection))
        results = seed_once(service, self.connection, observed_at=now)
        self.assertEqual(set(reference_product_ids()), set(results))
        self.assertTrue(all(status == "applied" for status in results.values()))
        self.assertTrue(snapshots_are_fresh(self.connection))
        availability = service.availability(product_ids=list(reference_product_ids()))
        for product_id in reference_product_ids():
            self.assertEqual("available", availability[product_id]["status"])
        second = seed_once(service, self.connection)
        self.assertTrue(all(status == "applied" for status in second.values()))
        self.assertEqual(3, next_source_version(self.connection))

    def test_lily_reference_live_test_writes_fresh_catalog_in_production(self):
        from unittest.mock import patch

        from aea_platform.adapters import PsycopgInventoryAvailabilityStore
        from aea_platform.inventory import InventoryAvailabilityService
        from aea_platform.lily_reference_live_test import (
            FEED_NAME, assert_live_test_feed_allowed, record_reference_catalog,
            reference_product_ids, snapshots_are_fresh,
        )
        from aea_platform.local_inventory_seed import assert_local_seed_allowed

        now = datetime.now(timezone.utc)
        with patch.dict(os.environ, {
            "AEA_ENVIRONMENT": "production",
            "AEA_INVENTORY_FEED": FEED_NAME,
        }, clear=False):
            assert_live_test_feed_allowed()
            with self.assertRaisesRegex(RuntimeError, "must not run"):
                assert_local_seed_allowed()
            service = InventoryAvailabilityService(
                PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
            results = record_reference_catalog(
                service, self.connection, observed_at=now)
        self.assertEqual(set(reference_product_ids()), set(results))
        self.assertTrue(all(status == "applied" for status in results.values()))
        self.assertTrue(snapshots_are_fresh(self.connection))
        availability = service.availability(product_ids=list(reference_product_ids()))
        for product_id in reference_product_ids():
            self.assertEqual("available", availability[product_id]["status"])

    def test_selection_options_contract_and_fr020_preservation(self):
        import asyncio
        from aea_platform.adapters import (PsycopgExperienceStateStore,
                                           PsycopgInventoryAvailabilityStore)
        from aea_platform.internal_api import InternalOrchestrationApp
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.state import StatePatch

        session_id = self.create_session()
        now = datetime.now(timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now)
        inventory.record(AvailabilitySnapshot("classic-rose-dozen", 5, 1, now))

        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        # Selection carries normalized T-04 options including thin FR-003 keys.
        body = json.dumps({"product_id": "classic-rose-dozen",
                           "options": {"size": "large", "card_message": "  Happy birthday  ",
                                       "flower_type": "roses", "colour": "red",
                                       "ribbon": "satin"},
                           "observed_context_version": 0, "correlation_id": "sel"}).encode()
        status, result = drive("POST", f"/internal/v1/sessions/{session_id}/selection", body)
        self.assertEqual(202, status)
        envelope = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='product.selected'", (session_id,)).fetchone()[0]
        self.assertEqual({"size": "large", "card_message": "Happy birthday",
                          "flower_type": "roses", "colour": "red", "ribbon": "satin"},
                         envelope["payload"]["options"])
        self.assertEqual("classic-rose-dozen", envelope["payload"]["product_id"])

        # Gift-card value is rejected before any state mutation.
        bad = json.dumps({"product_id": "classic-rose-dozen",
                          "options": {"gift_card_value": "50"},
                          "observed_context_version": result["context_version"],
                          "correlation_id": "sel2"}).encode()
        self.assertEqual(422, drive("POST", f"/internal/v1/sessions/{session_id}/selection", bad)[0])
        self.assertEqual(1, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message "
            "WHERE session_id=%s AND topic='product.selected'", (session_id,)).fetchone()[0])

        # FR-020: an unrelated intent change preserves the recorded product decision.
        store = PsycopgExperienceStateStore(self.connection)
        with self.connection.transaction():
            store.apply_patch(str(session_id), result["context_version"], 1,
                StatePatch.create({"shared_understanding": {"occasion": "anniversary"}},
                                  ["shared_understanding.occasion"]), [])
        _, workspace = drive("GET", f"/internal/v1/sessions/{session_id}/workspace")
        self.assertEqual("classic-rose-dozen", workspace["facets"]["selection"]["product_id"])
        self.assertEqual({"size": "large", "card_message": "Happy birthday",
                          "flower_type": "roses", "colour": "red", "ribbon": "satin"},
                         workspace["facets"]["selection"]["options"])

    def test_recommendations_publish_ready_for_available_ranked_catalog(self):
        from aea_platform.adapters import (
            PsycopgInventoryAvailabilityStore,
            PsycopgRecommendationStore,
        )
        from aea_platform.inventory import AvailabilitySnapshot, InventoryAvailabilityService
        from aea_platform.recommendation import RecommendationService

        session_id = self.create_session()
        now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        inventory = InventoryAvailabilityService(
            PsycopgInventoryAvailabilityStore(self.connection), now=lambda: now,
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000031"),
        )
        for product_id, qty in (("classic-rose-dozen", 5), ("lilac-bouquet", 2),
                                ("budget-mixed-bunch", 0)):
            inventory.record(AvailabilitySnapshot(product_id, qty, 1, now))
        service = RecommendationService(
            PsycopgRecommendationStore(self.connection), inventory, now=lambda: now,
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000026"),
        )
        result = service.generate(
            session_id=str(session_id), observed_context_version=0,
            correlation_id="rec-integration", subject_reference="subject",
            intent={"occasion": "birthday", "budget": 100, "flower_preference": "roses"},
        )
        self.assertEqual(["classic-rose-dozen", "lilac-bouquet"], result.eligible_product_ids)
        topics = [row[0] for row in self.connection.execute(
            "SELECT topic FROM orchestration.outbox_message WHERE session_id=%s "
            "ORDER BY topic", (session_id,),
        ).fetchall()]
        self.assertEqual(
            ["inventory.availability.validated", "product.recommendations.ready"], topics
        )
        ready = self.connection.execute(
            "SELECT envelope FROM orchestration.outbox_message WHERE message_id=%s",
            (result.message_id,),
        ).fetchone()[0]
        self.assertEqual(result.eligible_product_ids, ready["payload"]["eligible_product_ids"])
        self.assertEqual("recommendation", ready["source"])

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

        service = SharedUnderstandingService(
            PsycopgExperienceStateStore(self.connection),
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000041"),
        )
        result = service.correct(
            session_id=str(session_id), corrections={"budget": 90},
            observed_context_version=0, correlation_id="stale-correction",
            subject_reference="subject-reference",
        )
        self.assertEqual(2, result.context_version)
        restored = PsycopgExperienceStateStore(self.connection).load(str(session_id))
        self.assertEqual(90, restored["state"]["shared_understanding"]["budget"])
        self.assertEqual("birthday", restored["state"]["shared_understanding"]["occasion"])
        self.assertEqual(2, self.connection.execute(
            "SELECT count(*) FROM orchestration.outbox_message WHERE session_id=%s",
            (session_id,),
        ).fetchone()[0])

    def test_shared_understanding_patch_rebases_stale_observed_after_conversation(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        status, accepted = drive(
            "POST", f"/internal/v1/sessions/{session_id}/conversation",
            json.dumps({"message_text": "Birthday roses for Mum, under $75",
                        "observed_context_version": 0, "correlation_id": "conv"}).encode())
        self.assertEqual(202, status)
        self.assertGreaterEqual(accepted["context_version"], 1)

        status, result = drive(
            "PATCH", f"/internal/v1/sessions/{session_id}/shared-understanding",
            json.dumps({"corrections": {"recipient": "Mum"},
                        "observed_context_version": 0, "correlation_id": "corr"}).encode())
        self.assertEqual(202, status)
        self.assertEqual("accepted", result["code"])
        self.assertGreater(result["context_version"], accepted["context_version"])

        _, shared = drive("GET", f"/internal/v1/sessions/{session_id}/shared-understanding")
        self.assertEqual("Mum", shared["structured_intent"]["recipient"])

    def test_intent_and_faq_quality_endpoint_is_payload_free(self):
        import asyncio
        from aea_platform.generative_ai import AvailableIntentInterpreter, GenerativeAIUnavailable
        from aea_platform.internal_api import InternalOrchestrationApp

        session_id = self.create_session()

        class Down:
            def interpret(self, *_):
                raise GenerativeAIUnavailable("down")

        app = InternalOrchestrationApp(
            self.connection, "internal-token",
            AvailableIntentInterpreter(Down(), failure_threshold=3))

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        status, accepted = drive(
            "POST", f"/internal/v1/sessions/{session_id}/conversation",
            json.dumps({"message_text": "Birthday roses for Mum",
                        "observed_context_version": 0, "correlation_id": "q-intent"}).encode())
        self.assertEqual(202, status)
        self.assertGreaterEqual(accepted["context_version"], 1)

        faq_status, faq = drive(
            "POST", f"/internal/v1/sessions/{session_id}/support",
            json.dumps({"question": "When do you deliver?", "correlation_id": "q-faq"}).encode())
        self.assertEqual(200, faq_status)
        self.assertTrue(faq["matched"])

        quality_status, quality = drive("GET", "/internal/v1/ai/quality")
        self.assertEqual(200, quality_status)
        self.assertEqual(["intent", "faq"], quality["paths"])
        self.assertGreaterEqual(quality["counts"]["intent"]["fallback"], 1)
        self.assertGreaterEqual(quality["counts"]["faq"]["ok"], 1)
        self.assertEqual("provider_unavailable", quality["recent_errors"][0]["error_code"])
        serialized = json.dumps(quality)
        self.assertNotIn("Birthday roses", serialized)
        self.assertNotIn("When do you deliver", serialized)
        self.assertNotIn("2 PM", serialized)

        columns = {row[0] for row in self.connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='orchestration' AND table_name='ai_quality_event'"
        ).fetchall()}
        self.assertTrue({"path", "outcome", "error_code", "quality_flags"} <= columns)
        self.assertNotIn("payload", columns)
        self.assertNotIn("question", columns)
        self.assertNotIn("answer", columns)
        self.assertNotIn("message_text", columns)

    def test_conversation_accepts_message_when_interpretation_is_stale(self):
        import asyncio
        from aea_platform.internal_api import InternalOrchestrationApp

        session_id = self.create_session()
        app = InternalOrchestrationApp(self.connection, "internal-token")

        class StaleInterpretation:
            def analyze(self, **_kwargs):
                error = RuntimeError("stale experience context")
                error.sqlstate = "40001"
                raise error

        app.intent = StaleInterpretation()

        def drive(method, path, body=b""):
            return asyncio.run(self._invoke_internal(app, method, path, body))

        status, result = drive(
            "POST", f"/internal/v1/sessions/{session_id}/conversation",
            json.dumps({"message_text": "Birthday roses for Mum",
                        "observed_context_version": 0, "correlation_id": "conv"}).encode())
        self.assertEqual(202, status)
        self.assertEqual("accepted", result["code"])
        self.assertEqual(1, result["context_version"])
        _, conversation = drive("GET", f"/internal/v1/sessions/{session_id}/conversation")
        self.assertEqual("Birthday roses for Mum", conversation["messages"][0]["text"])

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
