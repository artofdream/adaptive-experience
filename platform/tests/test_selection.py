from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.selection import (SelectionValidationError, normalize_card_message,
                                    normalize_selection_options, normalize_size)


class CardMessageContractTests(unittest.TestCase):
    def test_card_message_is_optional_and_empty_is_none(self):
        self.assertIsNone(normalize_card_message(None))
        self.assertIsNone(normalize_card_message(""))
        self.assertIsNone(normalize_card_message("   \n  "))
        self.assertEqual("Happy birthday", normalize_card_message("  Happy birthday  "))

    def test_card_message_length_and_characters(self):
        self.assertEqual("a" * 280, normalize_card_message("a" * 280))
        self.assertEqual("line1\nline2", normalize_card_message("line1\nline2"))
        with self.assertRaises(SelectionValidationError):
            normalize_card_message("a" * 281)
        with self.assertRaises(SelectionValidationError):
            normalize_card_message("bad\x07bell")
        with self.assertRaises(SelectionValidationError):
            normalize_card_message(123)

    def test_size_shape(self):
        self.assertIsNone(normalize_size(None))
        self.assertIsNone(normalize_size("   "))
        self.assertEqual("large", normalize_size(" large "))
        with self.assertRaises(SelectionValidationError):
            normalize_size("x" * 41)

    def test_options_keep_size_card_message_and_thin_fr003(self):
        self.assertEqual({}, normalize_selection_options(None))
        self.assertEqual({}, normalize_selection_options({}))
        self.assertEqual({"size": "large", "card_message": "hi"},
                         normalize_selection_options({"size": "large", "card_message": "hi"}))
        # Blank fields are dropped, not stored empty.
        self.assertEqual({}, normalize_selection_options({"card_message": "  ", "size": ""}))
        self.assertEqual(
            {"flower_type": "roses", "colour": "red", "ribbon": "satin"},
            normalize_selection_options(
                {"flower_type": "Roses", "colour": "Red", "ribbon": "Satin"},
                product_id="classic-rose-dozen",
            ),
        )

    def test_options_accept_thin_fr003_and_reject_gift_card(self):
        self.assertEqual(
            {"colour": "red"},
            normalize_selection_options({"colour": "red"}, product_id="classic-rose-dozen"),
        )
        self.assertEqual(
            {"ribbon": "kraft"},
            normalize_selection_options({"ribbon": "kraft"}, product_id="classic-rose-dozen"),
        )
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options({"ribbon": "gold"})
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options({"gift_card_value": "50"})
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options(
                {"flower_type": "tulips"}, product_id="classic-rose-dozen")
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options({"flower_type": "roses"})
    def test_m10_compositional_selection_palette_and_safety_exclusions(self):
        opts = {
            "palette": "pastel_romance",
            "safety_exclusions": ["pet_safe_cat", "lily_free"]
        }
        res = normalize_selection_options(opts)
        self.assertEqual(res["palette"], "pastel_romance")
        self.assertEqual(res["safety_exclusions"], ["pet_safe_cat", "lily_free"])

    def test_m10_compositional_selection_invalid_palette(self):
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options({"palette": "neon_glow"})

    def test_m10_compositional_selection_invalid_safety_exclusion(self):
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options({"safety_exclusions": ["invalid_allergen"]})


if __name__ == "__main__":
    unittest.main()
