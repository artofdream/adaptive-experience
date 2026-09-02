from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.internal_api import InternalOrchestrationApp


class _FakeOrderService:
    def __init__(self, view):
        self.store = SimpleNamespace(checkout_view=lambda session_id: view)


class OperatorSummaryFactsTests(unittest.TestCase):
    def _app(self, view):
        # Minimal stub: only helpers under test need order.store.checkout_view.
        app = InternalOrchestrationApp.__new__(InternalOrchestrationApp)
        app.order = _FakeOrderService(view)
        return app

    def test_selection_flattens_card_from_options_and_adds_title(self):
        """#383/#385: florist facts get card + catalog title."""
        app = self._app(None)
        shaped = app._operator_selection_facts(
            "s1",
            {"product_id": "classic-rose-dozen",
             "options": {"card_message": "Happy Birthday Mom! Love always."}},
            {},
        )
        self.assertEqual("classic-rose-dozen", shaped["product_id"])
        self.assertEqual("Happy Birthday Mom! Love always.", shaped["card_message"])
        self.assertEqual("Classic Rose Dozen", shaped["catalog_title"])

    def test_selection_card_falls_back_to_order_product_options(self):
        """#383: live summaries often omit selection.card_message."""
        view = {
            "product": {
                "product_id": "lilac-bouquet",
                "options": {"card_message": "Thinking of you"},
            },
            "status": "confirmed",
            "aea_client": "companion-android",
        }
        app = self._app(view)
        shaped = app._operator_selection_facts(
            "s1", {"product_id": "lilac-bouquet"}, {})
        self.assertEqual("Thinking of you", shaped["card_message"])
        self.assertEqual("Lilac Bouquet", shaped["catalog_title"])

    def test_order_facts_include_channel_total_payment(self):
        """#384/#385: channel badge + paid total on session order facet."""
        view = {
            "status": "confirmed",
            "aea_client": "web",
            "decline_code": None,
            "product": {"product_id": "classic-rose-dozen"},
        }
        app = self._app(view)
        shaped = app._operator_order_facts(
            "s1",
            {"order_id": "o1", "status": "confirmed", "delayed": False,
             "authoritative_status": "confirmed"},
            {"total": 82.0, "currency": "EUR"},
        )
        self.assertEqual("web", shaped["channel"])
        self.assertEqual(82.0, shaped["total"])
        self.assertEqual("EUR", shaped["currency"])
        self.assertEqual("paid", shaped["payment_state"])


if __name__ == "__main__":
    unittest.main()
