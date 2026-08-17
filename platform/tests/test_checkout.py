from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.order import (CheckoutService, CheckoutStateError, CheckoutTotalMismatch,
                                OrderNotFound, _amounts_equal)
from aea_platform.payment import (PaymentOutcome, PaymentValidationError,
                                  ReferencePaymentAuthority, normalize_payment_reference)
from aea_platform.payment_checkout import PaymentCheckoutHandler
from aea_platform.pricing import PricingService, REFERENCE_DELIVERY_FEE


class PaymentAuthorityTests(unittest.TestCase):
    def test_reference_rejects_raw_card_and_blank(self):
        self.assertEqual("tok_abc", normalize_payment_reference("  tok_abc  "))
        for pan in ("4111111111111111", "4111 1111 1111 1111", "4111-1111-1111-1111"):
            with self.assertRaises(PaymentValidationError):
                normalize_payment_reference(pan)
        for bad in ("", None, 123):
            with self.assertRaises(PaymentValidationError):
                normalize_payment_reference(bad)

    def test_authorization_outcomes(self):
        authority = ReferencePaymentAuthority()
        self.assertTrue(authority.authorize(payment_reference="tok_ok", total=70.0).authorized)
        declined = authority.authorize(payment_reference="decline-1", total=70.0)
        self.assertFalse(declined.authorized)
        self.assertEqual("declined", declined.decline_code)
        self.assertFalse(authority.authorize(payment_reference="tok_ok", total=0).authorized)
        with self.assertRaises(PaymentValidationError):
            authority.authorize(payment_reference="4111111111111111", total=70.0)


class FakeCheckoutStore:
    def __init__(self, view, *, intent=None):
        self.view = view
        self.intent = intent
        self.requested = False
        self.confirmed = False
        self.failed = False
        self.succeeded = False
        self.cleared = False
        self.last_request = None

    def checkout_view(self, session_id):
        return self.view

    def request_checkout(self, **kwargs):
        self.requested = True
        self.last_request = kwargs
        self.intent = {
            "order_id": kwargs["order_id"], "session_id": kwargs["session_id"],
            "payment_reference": kwargs["payment_reference"], "total": kwargs["total"],
            "correlation_id": kwargs["correlation_id"],
            "subject_reference": kwargs["subject_reference"],
            "context_version": kwargs["context_version"], "decline_code": None,
        }
        return self.view["status"] in ("created", "submitted")

    def load_checkout_intent(self, order_id):
        if self.intent and self.intent["order_id"] == order_id:
            return self.intent
        return None

    def clear_checkout_intent(self, order_id):
        self.cleared = True
        self.intent = None

    def confirm(self, **kwargs):
        self.confirmed = True
        if self.view:
            self.view = {**self.view, "status": "confirmed"}
        return True

    def record_authorization_succeeded(self, **kwargs):
        self.succeeded = True

    def record_authorization_failed(self, **kwargs):
        self.failed = True
        if self.intent:
            self.intent["decline_code"] = kwargs["decline_code"]


class FakePricing:
    def __init__(self, total=70.0):
        self.total = total

    def summarize(self, decisions):
        if self.total is None:
            return None
        return {"currency": "USD", "itemized_charges": [], "total": self.total}


class CheckoutServiceTests(unittest.TestCase):
    def _view(self, status="created"):
        return {"order_id": "o1", "status": status, "product": {"product_id": "p"},
                "delivery": {"destination_reference": "r"}, "context_version": 2}

    def _service(self, store, *, total=70.0):
        return CheckoutService(store, FakePricing(total), new_id=lambda: "m")

    def test_submit_stores_intent_without_confirming(self):
        store = FakeCheckoutStore(self._view())
        result = self._service(store).submit(
            session_id="s", payment_reference="tok_ok", observed_total=70.0,
            correlation_id="c", subject_reference="subj")
        self.assertTrue(result["accepted"] and result["pending"])
        self.assertEqual("submitted", result["status"])
        self.assertTrue(store.requested)
        self.assertFalse(store.confirmed)
        self.assertEqual("tok_ok", store.last_request["payment_reference"])

    def test_total_mismatch_missing_and_confirmed_order(self):
        with self.assertRaises(CheckoutTotalMismatch):
            self._service(FakeCheckoutStore(self._view())).submit(
                session_id="s", payment_reference="tok", observed_total=999.0,
                correlation_id="c", subject_reference="subj")
        with self.assertRaises(OrderNotFound):
            self._service(FakeCheckoutStore(None)).submit(
                session_id="s", payment_reference="tok", observed_total=70.0,
                correlation_id="c", subject_reference="subj")
        with self.assertRaises(CheckoutStateError):
            self._service(FakeCheckoutStore(self._view("confirmed"))).submit(
                session_id="s", payment_reference="tok", observed_total=70.0,
                correlation_id="c", subject_reference="subj")
        with self.assertRaises(CheckoutStateError):
            self._service(FakeCheckoutStore(self._view()), total=None).submit(
                session_id="s", payment_reference="tok", observed_total=70.0,
                correlation_id="c", subject_reference="subj")

    def test_amounts_equal_accepts_json_int_and_rejects_bool(self):
        self.assertTrue(_amounts_equal(47, 47.0))
        self.assertTrue(_amounts_equal(47.0, 47))
        self.assertFalse(_amounts_equal(True, 1.0))
        self.assertFalse(_amounts_equal(82.0, 47.0))

    def test_submit_prices_current_decisions_not_stale_order_snapshot(self):
        store = FakeCheckoutStore({
            "order_id": "o1", "status": "submitted",
            "product": {"product_id": "classic-rose-dozen"},
            "delivery": {"destination_reference": "old-home"},
            "context_version": 2,
        })
        service = CheckoutService(store, PricingService(), new_id=lambda: "m")
        live = {
            "product": {"product_id": "budget-mixed-bunch"},
            "delivery": {"destination_reference": "home"},
        }
        live_total = round(35.0 + REFERENCE_DELIVERY_FEE, 2)
        stale_total = round(70.0 + REFERENCE_DELIVERY_FEE, 2)
        self.assertEqual(47.0, live_total)
        with self.assertRaises(CheckoutTotalMismatch):
            service.submit(
                session_id="s", payment_reference="tok", observed_total=live_total,
                correlation_id="c", subject_reference="subj")
        # Browser JSON often sends 47 rather than 47.0 for order_summary.total.
        result = service.submit(
            session_id="s", payment_reference="tok_ok", observed_total=47,
            correlation_id="c", subject_reference="subj", decisions=live,
            context_version=4)
        self.assertTrue(result["accepted"] and result["pending"])
        self.assertEqual(live_total, result["total"])
        self.assertEqual(4, result["context_version"])
        self.assertEqual("budget-mixed-bunch", store.last_request["product"]["product_id"])
        self.assertEqual("home", store.last_request["delivery"]["destination_reference"])
        self.assertNotEqual(stale_total, result["total"])


class PaymentCheckoutHandlerTests(unittest.TestCase):
    def test_authorize_confirms_on_success(self):
        store = FakeCheckoutStore(
            {"order_id": "o1", "status": "submitted", "product": {}, "delivery": {},
             "context_version": 2},
            intent={"order_id": "o1", "session_id": "s", "payment_reference": "tok_ok",
                    "total": 70.0, "correlation_id": "c", "subject_reference": "subj",
                    "context_version": 2, "decline_code": None})
        outcome = PaymentCheckoutHandler(
            store, ReferencePaymentAuthority(), new_id=lambda: "m").handle_checkout_requested({
                "payload": {"draft_order_id": "o1", "total": 70.0}})
        self.assertTrue(outcome.authorized)
        self.assertTrue(store.succeeded and store.confirmed and store.cleared)

    def test_authorize_records_decline_without_confirm(self):
        store = FakeCheckoutStore(
            {"order_id": "o1", "status": "submitted", "product": {}, "delivery": {},
             "context_version": 2},
            intent={"order_id": "o1", "session_id": "s", "payment_reference": "decline-1",
                    "total": 70.0, "correlation_id": "c", "subject_reference": "subj",
                    "context_version": 2, "decline_code": None})
        outcome = PaymentCheckoutHandler(
            store, ReferencePaymentAuthority(), new_id=lambda: "m").handle_checkout_requested({
                "payload": {"draft_order_id": "o1", "total": 70.0}})
        self.assertFalse(outcome.authorized)
        self.assertTrue(store.failed)
        self.assertFalse(store.confirmed)


if __name__ == "__main__":
    unittest.main()
