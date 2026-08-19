"""Unit tests for payment simulation engine in platform/aea_platform/payment.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.payment import (
    normalize_payment_reference,
    PaymentValidationError,
    ReferencePaymentAuthority,
    PaymentSimulationEngine,
)


class TestPaymentSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PaymentSimulationEngine()

    def test_normalize_payment_reference_valid_tokens(self):
        self.assertEqual(normalize_payment_reference("tok_visa"), "tok_visa")
        self.assertEqual(normalize_payment_reference("pay_token_12345"), "pay_token_12345")

    def test_normalize_payment_reference_raw_card_rejected(self):
        with self.assertRaises(PaymentValidationError):
            normalize_payment_reference("4111111111111111")

    def test_successful_simulation_tok_visa(self):
        result = self.engine.process_checkout_payment(
            order_id="ord-9001",
            payment_reference="tok_visa",
            amount_cents=8990
        )
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["event_type"], "payment.processed.v1")
        self.assertTrue(result["transaction_id"].startswith("txn_sim_"))

    def test_declined_simulation_tok_chargeDeclined(self):
        result = self.engine.process_checkout_payment(
            order_id="ord-9002",
            payment_reference="tok_chargeDeclined",
            amount_cents=8990
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["event_type"], "payment.failed.v1")
        self.assertEqual(result["error"], "card_declined")


if __name__ == "__main__":
    unittest.main()
