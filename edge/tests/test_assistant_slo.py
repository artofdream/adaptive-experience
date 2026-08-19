#!/usr/bin/env python3
"""Unit tests for check_assistant_slo.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "edge" / "scripts"))

from check_assistant_slo import evaluate_slo_metrics, P95_BUDGET_SECONDS, MIN_AVAILABILITY_PERCENT


class TestAssistantSLOGuard(unittest.TestCase):
    def test_evaluate_slo_metrics_success(self):
        samples = [0.5, 1.0, 1.5, 2.0, 2.2]
        success, msg = evaluate_slo_metrics(samples, 99.9)
        self.assertTrue(success)
        self.assertIn("p95 latency", msg)

    def test_evaluate_slo_metrics_latency_failure(self):
        samples = [0.5, 1.0, 1.5, 3.5, 4.0]
        success, msg = evaluate_slo_metrics(samples, 99.9)
        self.assertFalse(success)
        self.assertIn("exceeds budget", msg)

    def test_evaluate_slo_metrics_availability_failure(self):
        samples = [0.5, 1.0, 1.5]
        success, msg = evaluate_slo_metrics(samples, 98.0)
        self.assertFalse(success)
        self.assertIn("below threshold", msg)


if __name__ == "__main__":
    unittest.main()
