#!/usr/bin/env python3
"""Unit tests for returning-shopper walk skip/xfail rules (#195)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import walk_returning_shopper as walk


class ReturningShopperClassifyTests(unittest.TestCase):
    def test_path_a_enabled_select_passes(self) -> None:
        result, _reason = walk.classify_select(
            path_b=False,
            enabled_selects=1,
            card_texts=["Classic Rose Dozen | $70.00 | Available"],
        )
        self.assertEqual("pass", result)

    def test_path_a_disabled_select_fails(self) -> None:
        result, reason = walk.classify_select(
            path_b=False,
            enabled_selects=0,
            card_texts=["Budget Mixed Bunch | Unknown"],
        )
        self.assertEqual("fail", result)
        self.assertIn("Path A", reason)

    def test_path_b_unknown_select_xfails(self) -> None:
        result, reason = walk.classify_select(
            path_b=True,
            enabled_selects=0,
            card_texts=["Budget Mixed Bunch | $35.00 | Unknown"],
        )
        self.assertEqual("xfail", result)
        self.assertIn("seeder", reason)

    def test_same_session_hint_blocked_without_payment(self) -> None:
        result, _reason = walk.classify_same_session_hint(
            payment_included=False, hint_visible=False
        )
        self.assertEqual("blocked", result)

    def test_same_session_hint_fails_after_pay_if_missing(self) -> None:
        result, _reason = walk.classify_same_session_hint(
            payment_included=True, hint_visible=False
        )
        self.assertEqual("fail", result)

    def test_durable_recall_blocked_while_193_open(self) -> None:
        result, reason = walk.classify_durable_recall(recalled=False)
        self.assertEqual("blocked", result)
        self.assertIn("#193", reason)

    def test_reorder_blocked_when_recall_blocked(self) -> None:
        result, _reason = walk.classify_reorder(recall_result="blocked", reordered=False)
        self.assertEqual("blocked", result)

    def test_path_b_host_detection(self) -> None:
        self.assertTrue(walk.is_path_b("https://aea.artof.link/"))
        self.assertFalse(walk.is_path_b(walk.PATH_A_URL))


class ReturningShopperJourneyDocTests(unittest.TestCase):
    def test_journey_doc_names_paths_and_recall(self) -> None:
        text = (
            walk.REPO / "implementations" / "florist" / "journeys" / "returning-shopper-journey.md"
        ).read_text(encoding="utf-8")
        self.assertIn("https://localhost:8443/", text)
        self.assertIn("https://aea.artof.link/", text)
        self.assertIn("#193", text)
        self.assertIn("xfail", text)
        self.assertIn("NFR-007", text)
        self.assertIn("walk_returning_shopper.py", text)


if __name__ == "__main__":
    unittest.main()
