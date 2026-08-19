#!/usr/bin/env python3
"""Unit tests for run_all_guards.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_all_guards import GUARDS, run_guards


class TestRunAllGuards(unittest.TestCase):
    def test_guards_inventory_count(self):
        self.assertGreaterEqual(len(GUARDS), 10)

    def test_run_guards_execution(self):
        success = run_guards()
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
