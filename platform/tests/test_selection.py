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

    def test_options_keep_only_size_and_card_message(self):
        self.assertEqual({}, normalize_selection_options(None))
        self.assertEqual({}, normalize_selection_options({}))
        self.assertEqual({"size": "large", "card_message": "hi"},
                         normalize_selection_options({"size": "large", "card_message": "hi"}))
        # Blank fields are dropped, not stored empty.
        self.assertEqual({}, normalize_selection_options({"card_message": "  ", "size": ""}))

    def test_options_reject_fr003_controls(self):
        for control in ({"colour": "red"}, {"ribbon": "gold"}, {"flower_type": "rose"},
                        {"gift_card_value": "50"}, {"size": "large", "colour": "red"}):
            with self.assertRaises(SelectionValidationError):
                normalize_selection_options(control)
        with self.assertRaises(SelectionValidationError):
            normalize_selection_options("not-a-dict")


if __name__ == "__main__":
    unittest.main()
