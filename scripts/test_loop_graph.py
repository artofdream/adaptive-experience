#!/usr/bin/env python3
"""Unit tests for check_loop_graph.py."""

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_loop_graph import load_loop_graph_scripts, check_loop_graph_integrity


class TestLoopGraphGuard(unittest.TestCase):
    def test_load_loop_graph_scripts(self):
        scripts = load_loop_graph_scripts()
        self.assertTrue(len(scripts) > 0)
        self.assertIn("scripts/check_coherence.py", scripts)

    def test_check_loop_graph_integrity(self):
        missing_files, uncovered_in_ci = check_loop_graph_integrity()
        self.assertEqual(missing_files, [], f"Missing files: {missing_files}")
        self.assertEqual(uncovered_in_ci, [], f"Uncovered in CI: {uncovered_in_ci}")


if __name__ == "__main__":
    unittest.main()
