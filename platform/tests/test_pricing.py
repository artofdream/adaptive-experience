from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.pricing import REFERENCE_DELIVERY_FEE, PricingService


class PricingServiceTests(unittest.TestCase):
    def setUp(self):
        self.pricing = PricingService()
        # classic-rose-dozen is 70.0 in the reference catalog.
        self.price = self.pricing.prices["classic-rose-dozen"]

    def test_no_summary_until_a_known_product_is_selected(self):
        self.assertIsNone(self.pricing.summarize({}))
        self.assertIsNone(self.pricing.summarize({"delivery": {"destination_reference": "r"}}))
        self.assertIsNone(self.pricing.summarize({"product": {"product_id": "not-in-catalog"}}))
        self.assertIsNone(self.pricing.summarize("not-a-dict"))

    def test_product_only_summary(self):
        summary = self.pricing.summarize({"product": {"product_id": "classic-rose-dozen"}})
        self.assertEqual([{"label": "product", "product_id": "classic-rose-dozen",
                           "amount": round(self.price, 2)}], summary["itemized_charges"])
        self.assertEqual(round(self.price, 2), summary["total"])
        self.assertEqual("USD", summary["currency"])

    def test_card_message_is_included_and_delivery_adds_a_line(self):
        summary = self.pricing.summarize({
            "product": {"product_id": "classic-rose-dozen", "options": {"card_message": "hi"}},
            "delivery": {"destination_reference": "addr-1"}})
        labels = [(c["label"], c["amount"]) for c in summary["itemized_charges"]]
        self.assertIn(("card_message", 0.0), labels)
        self.assertIn(("delivery", round(REFERENCE_DELIVERY_FEE, 2)), labels)
        self.assertEqual(round(self.price + REFERENCE_DELIVERY_FEE, 2), summary["total"])


if __name__ == "__main__":
    unittest.main()
