#!/usr/bin/env python3
"""Offline unit tests for companion BFF parity probe helpers (#369)."""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import probe_companion_bff_parity as probe  # noqa: E402


class ProbeHelpersTest(unittest.TestCase):
    def test_validate_base_url(self):
        self.assertEqual(
            probe.validate_base_url("https://aea.artof.link/"),
            "https://aea.artof.link",
        )
        with self.assertRaises(ValueError):
            probe.validate_base_url("http://aea.artof.link")

    def test_weekend_utc(self):
        sat = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
        wed = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
        self.assertTrue(probe.is_weekend_utc(sat))
        self.assertFalse(probe.is_weekend_utc(wed))

    def test_pick_available_product(self):
        ws = {
            "facets": {
                "recommendations": {
                    "items": [
                        {"product_id": "sold", "available": False, "price": 1},
                        {
                            "product_id": "classic-rose-dozen",
                            "available": True,
                            "price": 70,
                        },
                    ]
                }
            }
        }
        picked = probe.pick_available_product(ws)
        assert picked is not None
        self.assertEqual(picked["product_id"], "classic-rose-dozen")

    def test_order_summary_total(self):
        ws = {"facets": {"order_summary": {"total": 82.0, "currency": "USD"}}}
        self.assertEqual(probe.order_summary_total(ws), 82.0)
        self.assertIsNone(probe.order_summary_total({"facets": {}}))

    def test_extract_error_code(self):
        self.assertEqual(
            probe.extract_error_code({"code": "total_mismatch"}), "total_mismatch"
        )
        self.assertEqual(
            probe.extract_error_code({"error": "csrf_rejected"}), "csrf_rejected"
        )


if __name__ == "__main__":
    unittest.main()
