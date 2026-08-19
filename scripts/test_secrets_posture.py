#!/usr/bin/env python3
"""Unit tests for check_secrets_posture.py."""

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_secrets_posture import check_gitignore_patterns, check_secret_templates


class TestSecretsPosture(unittest.TestCase):
    def test_gitignore_patterns(self):
        ok, errors = check_gitignore_patterns()
        self.assertTrue(ok, f"Gitignore pattern check failed: {errors}")

    def test_secret_templates(self):
        ok, errors = check_secret_templates()
        self.assertTrue(ok, f"Secret template check failed: {errors}")


if __name__ == "__main__":
    unittest.main()
