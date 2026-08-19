#!/usr/bin/env python3
"""Unit tests for check_stakeholder_cadence.py."""

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_stakeholder_cadence import evaluate_cadence, ROLES


class TestStakeholderCadence(unittest.TestCase):
    def test_role_roster_count(self):
        self.assertGreaterEqual(len(ROLES), 10, "Expected at least 10 AEA stakeholder roles")
        self.assertIn("aea-project-manager", ROLES)
        self.assertIn("aea-appsec-auditor", ROLES)
        self.assertIn("aea-coherence-guardian", ROLES)

    def test_evaluate_cadence(self):
        report = evaluate_cadence()
        self.assertIn("total_roles", report)
        self.assertIn("daily_brief_fresh", report)
        self.assertEqual(report["total_roles"], len(ROLES))


if __name__ == "__main__":
    unittest.main()
