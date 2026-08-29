"""Unit tests for the DSO+SSE dependency pin cadence ledger."""

from __future__ import annotations

import unittest

from check_dependency_pin_cadence import HEADERS, LEDGER, ledger_ok


class DependencyPinCadenceTests(unittest.TestCase):
    def test_ledger_present_and_valid(self) -> None:
        ok, msg = ledger_ok()
        self.assertTrue(ok, msg)
        self.assertTrue(LEDGER.is_file())
        self.assertEqual(len(HEADERS), 6)


if __name__ == "__main__":
    unittest.main()
