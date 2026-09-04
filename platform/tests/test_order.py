from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.order import (OrderIncompleteError, OrderNotFound, OrderService,
                                OrderStatusError)


class FakeOrderStore:
    def __init__(self, *, current="created", exists=True, product_id="classic-rose-dozen"):
        self.created = None
        self.advanced = None
        self.current = current
        self.exists = exists
        self.product_id = product_id

    def create_or_get(self, **kwargs):
        self.created = kwargs
        return {"order_id": kwargs["order_id"], "status": "created",
                "context_version": kwargs["context_version"]}

    def advance_status(self, **kwargs):
        self.advanced = kwargs
        if not self.exists:
            return None
        if self.current not in kwargs["allowed_priors"]:
            return {"order_id": "order-1", "status": self.current, "changed": False}
        return {"order_id": "order-1", "status": kwargs["target_status"], "changed": True}

    def set_delay(self, **kwargs):
        self.delayed = kwargs
        if not self.exists:
            return None
        delayed = kwargs["delayed"]
        return {"order_id": "order-1", "status": self.current, "delayed": delayed,
                "authoritative_status": "delayed" if delayed else self.current}

    def checkout_view(self, session_id):
        if not self.exists:
            return None
        return {
            "order_id": "order-1",
            "status": self.current,
            "product": {"product_id": self.product_id} if self.product_id else {},
            "delivery": {},
            "context_version": 1,
        }

    def list_recent(self, *, limit=50, after_cursor=None):
        self.listed_limit = limit
        self.listed_cursor = after_cursor
        if not self.exists:
            return []
        return [{
            "order_id": "order-1",
            "session_id": "sess-1",
            "status": self.current,
            "delayed": False,
            "product": {
                "product_id": self.product_id,
                "options": {"card_message": "Happy birthday Mum", "size": "large"},
                "email": "private@example.invalid",
            },
            "delivery": {
                "destination_reference": "dest-1",
                "timing": {"date": "2026-09-01", "window": "morning"},
                "street": "12 Private Lane",
            },
            "updated_at": "2026-09-02T12:00:00+00:00",
            "aea_client": "web",
            "decline_code": None,
            "email": "private@example.invalid",
        }]


class OrderServiceTests(unittest.TestCase):
    def _service(self, store=None):
        return OrderService(store or FakeOrderStore(), new_id=lambda: "order-1")

    def test_requires_both_product_and_delivery(self):
        service = self._service()
        with self.assertRaises(OrderIncompleteError):
            service.create(session_id="s", decisions={}, context_version=1)
        with self.assertRaises(OrderIncompleteError) as missing_delivery:
            service.create(session_id="s", decisions={"product": {"product_id": "p"}},
                           context_version=1)
        self.assertEqual("delivery", missing_delivery.exception.missing)
        with self.assertRaises(OrderIncompleteError) as missing_product:
            service.create(session_id="s", decisions={"delivery": {"destination_reference": "r"}},
                           context_version=1)
        self.assertEqual("product", missing_product.exception.missing)

    def test_creates_from_assembled_decisions(self):
        store = FakeOrderStore()
        result = self._service(store).create(
            session_id="s",
            decisions={"product": {"product_id": "p", "options": {"size": "large"}},
                       "delivery": {"destination_reference": "r",
                                    "timing": {"date": "2026-09-01", "window": "morning"}}},
            context_version=3)
        self.assertEqual("order-1", result["order_id"])
        self.assertEqual("created", result["status"])
        self.assertEqual({"product_id": "p", "options": {"size": "large"}}, store.created["product"])
        self.assertEqual(3, store.created["context_version"])

    def test_advance_status_forward_only(self):
        store = FakeOrderStore(current="created")
        service = OrderService(store, new_id=lambda: "m-1")
        result = service.advance_status(session_id="s", target_status="preparing",
                                        correlation_id="c", subject_reference="subj")
        self.assertEqual("preparing", result["status"])
        self.assertIn("created", store.advanced["allowed_priors"])
        self.assertNotIn("preparing", store.advanced["allowed_priors"])

    def test_advance_status_rejects_unknown_and_backward(self):
        service = OrderService(FakeOrderStore(current="dispatched"))
        with self.assertRaises(OrderStatusError):
            service.advance_status(session_id="s", target_status="teleported",
                                   correlation_id="c", subject_reference="subj")
        with self.assertRaises(OrderStatusError):
            service.advance_status(session_id="s", target_status="preparing",
                                   correlation_id="c", subject_reference="subj")

    def test_advance_status_missing_order(self):
        service = OrderService(FakeOrderStore(exists=False))
        with self.assertRaises(OrderNotFound):
            service.advance_status(session_id="s", target_status="preparing",
                                   correlation_id="c", subject_reference="subj")

    def test_advance_status_allows_completion(self):
        store = FakeOrderStore(current="delivered")
        result = OrderService(store).advance_status(
            session_id="s", target_status="completed", correlation_id="c",
            subject_reference="subj")
        self.assertEqual("completed", result["status"])

    def test_set_delay_publishes_authoritative_state(self):
        service = OrderService(FakeOrderStore(current="preparing"))
        delayed = service.set_delay(session_id="s", delayed=True, correlation_id="c",
                                    subject_reference="subj")
        self.assertTrue(delayed["delayed"])
        self.assertEqual("delayed", delayed["authoritative_status"])
        cleared = service.set_delay(session_id="s", delayed=False, correlation_id="c",
                                    subject_reference="subj")
        self.assertFalse(cleared["delayed"])
        self.assertEqual("preparing", cleared["authoritative_status"])
        with self.assertRaises(OrderNotFound):
            OrderService(FakeOrderStore(exists=False)).set_delay(
                session_id="s", delayed=True, correlation_id="c", subject_reference="subj")

    def test_session_prior_product_id_only_after_confirmed_order(self):
        self.assertIsNone(OrderService(FakeOrderStore(current="created"))
                          .session_prior_product_id("s"))
        self.assertIsNone(
            OrderService(FakeOrderStore(current="submitted", product_id="lilac-bouquet"))
            .session_prior_product_id("s"))
        self.assertEqual(
            "classic-rose-dozen",
            OrderService(FakeOrderStore(current="confirmed"))
            .session_prior_product_id("s"))
        self.assertIsNone(OrderService(FakeOrderStore(exists=False))
                          .session_prior_product_id("s"))
        self.assertIsNone(OrderService(FakeOrderStore(current="submitted", product_id=""))
                          .session_prior_product_id("s"))
        self.assertIsNone(OrderService(FakeOrderStore(current="submitted"))
                          .session_prior_product_id("  "))

    def test_prior_product_id_falls_back_to_browser_recall(self):
        class RecallingStore(FakeOrderStore):
            def recalled_product_id(self, session_id):
                self.looked_up = session_id
                return "lilac-bouquet"

        store = RecallingStore(current="created")
        self.assertEqual("lilac-bouquet", self._service(store).prior_product_id("s2"))
        self.assertEqual("s2", store.looked_up)
        self.assertIsNone(
            OrderService(FakeOrderStore(current="submitted")).prior_product_id("s"))
        self.assertIsNone(OrderService(FakeOrderStore(current="created")).prior_product_id("s"))
        self.assertIsNone(self._service().prior_product_id("  "))

        class BrokenStore(FakeOrderStore):
            def recalled_product_id(self, session_id):
                raise RuntimeError("lookup")

        self.assertIsNone(OrderService(BrokenStore(current="created")).prior_product_id("s"))

    def test_list_recent_is_least_data_without_email_or_product_dump(self):
        store = FakeOrderStore(current="confirmed")
        items = self._service(store).list_recent(limit=50)
        self.assertEqual(50, store.listed_limit)
        self.assertEqual(1, len(items))
        item = items[0]
        self.assertEqual("order-1", item["order_id"])
        self.assertEqual("sess-1", item["session_id"])
        self.assertEqual("confirmed", item["status"])
        self.assertFalse(item["delayed"])
        self.assertEqual("confirmed", item["authoritative_status"])
        self.assertEqual("classic-rose-dozen", item["product_id"])
        self.assertEqual("dest-1", item["destination_reference"])
        self.assertEqual({"date": "2026-09-01", "window": "morning"}, item["timing"])
        self.assertEqual("Happy birthday Mum", item["card_message"])
        self.assertEqual("Classic Rose Dozen", item["catalog_title"])
        self.assertEqual("web", item["channel"])
        self.assertEqual("paid", item["payment_state"])
        self.assertEqual("2026-09-02T12:00:00+00:00", item["updated_at"])
        self.assertNotIn("email", item)
        self.assertNotIn("product", item)
        self.assertNotIn("delivery", item)
        self.assertNotIn("street", item)
        self.assertNotIn("options", item)
        self.assertNotIn("decline_code", item)
        self.assertNotIn("aea_client", item)
        blob = str(item)
        self.assertNotIn("private@example.invalid", blob)
        self.assertNotIn("12 Private Lane", blob)

    def test_list_recent_truncates_card_message_and_marks_delayed(self):
        store = FakeOrderStore(current="preparing")
        def delayed_rows(*, limit=50, after_cursor=None):
            store.listed_limit = limit
            return [{
                "order_id": "order-2",
                "session_id": "sess-2",
                "status": "preparing",
                "delayed": True,
                "product": {"product_id": "lilac-bouquet",
                            "options": {"card_message": "x" * 400}},
                "delivery": {"destination_reference": "dest-2",
                             "timing": {"date": "2026-09-03", "window": "afternoon"}},
                "updated_at": "2026-09-02T13:00:00+00:00",
            }]
        store.list_recent = delayed_rows
        item = self._service(store).list_recent()[0]
        self.assertTrue(item["delayed"])
        self.assertEqual("delayed", item["authoritative_status"])
        self.assertEqual(280, len(item["card_message"]))
        self.assertEqual("Lilac Bouquet", item["catalog_title"])
        self.assertIsNone(item["channel"])
        self.assertEqual("paid", item["payment_state"])

    def test_list_recent_marks_declined_and_unknown_channel(self):
        store = FakeOrderStore(current="submitted")
        def declined_rows(*, limit=50, after_cursor=None):
            store.listed_limit = limit
            return [{
                "order_id": "order-3",
                "session_id": "sess-3",
                "status": "submitted",
                "delayed": False,
                "product": {"product_id": "not-a-catalog-sku"},
                "delivery": {"destination_reference": "dest-3"},
                "updated_at": "2026-09-02T14:00:00+00:00",
                "aea_client": "rog-phone",
                "decline_code": "card_declined",
            }]
        store.list_recent = declined_rows
        item = self._service(store).list_recent()[0]
        self.assertEqual("declined", item["payment_state"])
        self.assertEqual("unknown", item["channel"])
        self.assertIsNone(item["catalog_title"])


    def test_list_recent_accepts_cursor_and_raised_limit(self):
        """Pagination: limit can go up to 200 and cursor is forwarded."""
        store = FakeOrderStore(current="confirmed")
        items = self._service(store).list_recent(limit=100, after_cursor="2026-09-01T00:00:00+00:00")
        self.assertEqual(100, store.listed_limit)
        self.assertEqual("2026-09-01T00:00:00+00:00", store.listed_cursor)
        # Cap at 200
        self._service(store).list_recent(limit=999)
        self.assertEqual(200, store.listed_limit)

    def test_list_recent_includes_observed_total_when_priced(self):
        """#385: staff list exposes observed basket total without PII."""
        store = FakeOrderStore(current="confirmed")
        item = self._service(store).list_recent()[0]
        self.assertIn("total", item)
        self.assertIsInstance(item["total"], float)
        self.assertNotIn("email", item)


if __name__ == "__main__":
    unittest.main()
