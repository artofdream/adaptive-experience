from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.order import (OrderIncompleteError, OrderNotFound, OrderService,
                                OrderStatusError)


class FakeOrderStore:
    def __init__(self, *, current="created", exists=True):
        self.created = None
        self.advanced = None
        self.current = current
        self.exists = exists

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


if __name__ == "__main__":
    unittest.main()
