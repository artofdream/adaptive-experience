from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.pricing import (
    FR018_LABELS,
    REFERENCE_DELIVERY_FEE,
    PricingService,
)


class PricingServiceTests(unittest.TestCase):
    def setUp(self):
        self.pricing = PricingService()
        # classic-rose-dozen is 70.0 in the reference catalog.
        self.price = self.pricing.prices["classic-rose-dozen"]

    def _labels(self, summary):
        return [c["label"] for c in summary["itemized_charges"]]

    def test_no_summary_until_a_known_product_is_selected(self):
        self.assertIsNone(self.pricing.summarize({}))
        self.assertIsNone(self.pricing.summarize({"delivery": {"destination_reference": "r"}}))
        self.assertIsNone(self.pricing.summarize({"product": {"product_id": "not-in-catalog"}}))
        self.assertIsNone(self.pricing.summarize("not-a-dict"))

    def test_product_summary_emits_fr018_categories(self):
        summary = self.pricing.summarize({"product": {"product_id": "classic-rose-dozen"}})
        labels = self._labels(summary)
        for required in ("product", "customization", "tax", "discount"):
            self.assertIn(required, labels)
        self.assertNotIn("delivery", labels)
        self.assertEqual(
            {"product", "customization", "tax", "discount"},
            set(labels),
        )
        by_label = {c["label"]: c["amount"] for c in summary["itemized_charges"]}
        self.assertEqual(round(self.price, 2), by_label["product"])
        self.assertEqual(0.0, by_label["customization"])
        self.assertEqual(0.0, by_label["tax"])
        self.assertEqual(0.0, by_label["discount"])
        self.assertEqual(round(self.price, 2), summary["total"])
        self.assertEqual("USD", summary["currency"])

    def test_delivery_and_options_keep_fr018_categories(self):
        summary = self.pricing.summarize({
            "product": {
                "product_id": "classic-rose-dozen",
                "options": {"card_message": "hi", "colour": "red"},
            },
            "delivery": {"destination_reference": "addr-1"},
        })
        labels = self._labels(summary)
        for required in FR018_LABELS:
            self.assertIn(required, labels)
        by_label = {c["label"]: c["amount"] for c in summary["itemized_charges"]}
        self.assertEqual(0.0, by_label["customization"])
        self.assertEqual(round(REFERENCE_DELIVERY_FEE, 2), by_label["delivery"])
        self.assertEqual(
            round(self.price + REFERENCE_DELIVERY_FEE, 2),
            summary["total"],
        )

    def test_reference_tax_and_discount_adjust_total(self):
        pricing = PricingService(tax_rate=0.10, discount_amount=5.0)
        summary = pricing.summarize({
            "product": {"product_id": "classic-rose-dozen"},
            "delivery": {"destination_reference": "addr-1"},
        })
        by_label = {c["label"]: c["amount"] for c in summary["itemized_charges"]}
        taxable = round(self.price + REFERENCE_DELIVERY_FEE, 2)
        self.assertEqual(round(taxable * 0.10, 2), by_label["tax"])
        self.assertEqual(5.0, by_label["discount"])
        self.assertEqual(round(taxable + by_label["tax"] - 5.0, 2), summary["total"])


if __name__ == "__main__":
    unittest.main()
