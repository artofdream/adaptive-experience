#!/usr/bin/env python3
"""Unit tests for check_ui_visual_sync.py."""

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "edge" / "scripts"))

from check_ui_visual_sync import check_wireframe_assets, check_ui_tile_components, REQUIRED_TILES


class TestUIVisualSync(unittest.TestCase):
    def test_wireframe_assets_exist(self):
        ok, errors = check_wireframe_assets()
        self.assertTrue(ok, f"Wireframe asset check failed: {errors}")

    def test_ui_tiles_count(self):
        self.assertEqual(len(REQUIRED_TILES), 8)
        self.assertIn("T-01", REQUIRED_TILES)
        self.assertIn("T-08", REQUIRED_TILES)

    def test_ui_tile_components(self):
        ok, errors = check_ui_tile_components()
        self.assertTrue(ok, f"UI tile check failed: {errors}")


if __name__ == "__main__":
    unittest.main()
