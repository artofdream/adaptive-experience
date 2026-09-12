"""Unit tests for ReorderService in platform/aea_platform/reorder.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.reorder import (
    PRIOR_ORDERS_CAP,
    PriorOrderItem,
    PriorOrderSummary,
    ReorderService,
    least_data_prior_order,
    least_data_reorder_options,
)


class TestReorderService(unittest.TestCase):
    def setUp(self):
        self.item = PriorOrderItem(
            product_id="classic-rose-dozen",
            size="large",
            card_message="Happy Birthday Mom!",
            customizations={"colour": "red", "ribbon": "gold"},
            quantity=1,
            price_cents=8990
        )
        self.order = PriorOrderSummary(
            order_id="ord-1001",
            browser_token="token-browser-abc",
            items=[self.item],
            total_cents=8990,
            created_at_iso="2026-08-15T10:00:00Z",
            delivery_postcode="2000"
        )
        self.service = ReorderService(order_store={"token-browser-abc": [self.order]})

    def test_get_prior_orders(self):
        orders = self.service.get_prior_orders("token-browser-abc")
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].order_id, "ord-1001")

    def test_prepare_reorder_unmodified(self):
        payload = self.service.prepare_reorder("token-browser-abc", "ord-1001")
        self.assertEqual(payload["source_order_id"], "ord-1001")
        self.assertFalse(payload["modified"])
        self.assertEqual(len(payload["reorder_items"]), 1)
        self.assertEqual(payload["reorder_items"][0]["card_message"], "Happy Birthday Mom!")

    def test_prepare_reorder_modified(self):
        mod = {
            "classic-rose-dozen": {
                "card_message": "With Lots of Love, Sarah",
                "size": "deluxe"
            }
        }
        payload = self.service.prepare_reorder("token-browser-abc", "ord-1001", modify_items=mod)
        self.assertTrue(payload["modified"])
        self.assertEqual(payload["reorder_items"][0]["card_message"], "With Lots of Love, Sarah")
        self.assertEqual(payload["reorder_items"][0]["size"], "deluxe")

    def test_least_data_reorder_options_from_real_order_product(self):
        """FR-008 #424: live Path B extracts options from a real order product."""
        projected = least_data_reorder_options({
            "product_id": "classic-rose-dozen",
            "options": {"size": "Standard", "quantity": 2,
                        "card_message": "Happy Birthday Mum"},
            "recipient": "Mum",
            "payment_reference": "tok_secret",
        })
        self.assertEqual({
            "size": "Standard",
            "quantity": 2,
            "card_message": "Happy Birthday Mum",
        }, projected)
        self.assertNotIn("recipient", projected)
        self.assertNotIn("payment_reference", projected)

    def test_least_data_reorder_options_omits_invalid_tokens(self):
        self.assertEqual({}, least_data_reorder_options({
            "product_id": "classic-rose-dozen",
            "options": {"size": "", "quantity": 99, "card_message": "\x01"},
        }))
        self.assertEqual({}, least_data_reorder_options(None))

    def test_least_data_prior_order_drops_pii(self):
        """FR-008 #426: Path B allowlist is SKU plus size / qty / card only."""
        projected = least_data_prior_order({
            "product_id": "lilac-bouquet",
            "options": {
                "size": "Deluxe",
                "quantity": 2,
                "card_message": "Love you Mum",
                "recipient": "Mum",
            },
            "order_id": "secret",
            "email": "private@example.invalid",
        })
        self.assertEqual({
            "product_id": "lilac-bouquet",
            "size": "Deluxe",
            "quantity": 2,
            "card_message": "Love you Mum",
        }, projected)
        self.assertEqual(5, PRIOR_ORDERS_CAP)
        self.assertEqual({"size": "Deluxe"}, least_data_reorder_options({
            "options": {"size": "Deluxe", "card_message": ""},
        }))
        self.assertIsNone(least_data_prior_order({"product_id": "  "}))


if __name__ == "__main__":
    unittest.main()
