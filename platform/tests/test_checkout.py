from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.order import (CheckoutService, CheckoutStateError, CheckoutTotalMismatch,
                                OrderNotFound)
from aea_platform.payment import (PaymentOutcome, PaymentValidationError,
                                  ReferencePaymentAuthority, normalize_payment_reference)


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
    def __init__(self, view):
        self.view = view
        self.requested = False
        self.confirmed = False

    def checkout_view(self, session_id):
        return self.view

    def request_checkout(self, **kwargs):
        self.requested = True
        return self.view["status"] in ("created", "submitted")

    def confirm(self, **kwargs):
        self.confirmed = True
        return True


class FakePricing:
    def __init__(self, total=70.0):
        self.total = total

    def summarize(self, decisions):
        if self.total is None:
            return None
        return {"currency": "USD", "itemized_charges": [], "total": self.total}


class FakePayment:
    def __init__(self, outcome):
        self.outcome = outcome

    def authorize(self, *, payment_reference, total):
        return self.outcome


class CheckoutServiceTests(unittest.TestCase):
    def _view(self, status="created"):
        return {"order_id": "o1", "status": status, "product": {"product_id": "p"},
                "delivery": {"destination_reference": "r"}, "context_version": 2}

    def _service(self, store, *, total=70.0, outcome=PaymentOutcome(True)):
        return CheckoutService(store, FakePricing(total), FakePayment(outcome),
                               new_id=lambda: "m")

    def test_confirms_when_authorized(self):
        store = FakeCheckoutStore(self._view())
        result = self._service(store).checkout(
            session_id="s", payment_reference="tok_ok", observed_total=70.0,
            correlation_id="c", subject_reference="subj")
        self.assertTrue(result["confirmed"])
        self.assertEqual("confirmed", result["status"])
        self.assertTrue(store.requested and store.confirmed)

    def test_decline_leaves_order_submitted_without_confirm(self):
        store = FakeCheckoutStore(self._view())
        result = self._service(store, outcome=PaymentOutcome(False, "declined")).checkout(
            session_id="s", payment_reference="tok_ok", observed_total=70.0,
            correlation_id="c", subject_reference="subj")
        self.assertFalse(result["confirmed"])
        self.assertEqual("submitted", result["status"])
        self.assertEqual("declined", result["decline_code"])
        self.assertTrue(store.requested)
        self.assertFalse(store.confirmed)

    def test_total_mismatch_missing_and_confirmed_order(self):
        with self.assertRaises(CheckoutTotalMismatch):
            self._service(FakeCheckoutStore(self._view())).checkout(
                session_id="s", payment_reference="tok", observed_total=999.0,
                correlation_id="c", subject_reference="subj")
        with self.assertRaises(OrderNotFound):
            self._service(FakeCheckoutStore(None)).checkout(
                session_id="s", payment_reference="tok", observed_total=70.0,
                correlation_id="c", subject_reference="subj")
        with self.assertRaises(CheckoutStateError):
            self._service(FakeCheckoutStore(self._view("confirmed"))).checkout(
                session_id="s", payment_reference="tok", observed_total=70.0,
                correlation_id="c", subject_reference="subj")
        with self.assertRaises(CheckoutStateError):
            self._service(FakeCheckoutStore(self._view()), total=None).checkout(
                session_id="s", payment_reference="tok", observed_total=70.0,
                correlation_id="c", subject_reference="subj")


if __name__ == "__main__":
    unittest.main()
