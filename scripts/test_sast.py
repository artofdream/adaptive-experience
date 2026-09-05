#!/usr/bin/env python3
"""Unit tests for the #328 Bandit Python SAST gate (pin, scope, High bar)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_sast.py"
CI = ROOT / ".gitlab-ci.yml"
CONFIG = ROOT / "bandit.yaml"
PINNED_VERSION = "1.9.4"

sys.path.insert(0, str(ROOT / "scripts"))
from check_sast import (  # noqa: E402
    EXCLUDE_REASONS,
    KNOWN_BAD_TEST_ID,
    SCOPED_TREES,
    SKIP_REASONS,
    load_config,
)


def sast_job_block() -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(r"^bandit:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError("bandit job missing from .gitlab-ci.yml")
    return match.group(0)


class SastGateTests(unittest.TestCase):
    def test_ci_pins_bandit(self) -> None:
        block = sast_job_block()
        self.assertIn(f"bandit=={PINNED_VERSION}", block)
        self.assertIn("python:3.12-alpine", block)
        self.assertNotIn("pip install bandit\n", block)
        self.assertNotIn("pip install --no-cache-dir bandit\n", block)

    def test_ci_job_is_required(self) -> None:
        block = sast_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_sast.py", block)
        self.assertIn("scripts/test_sast.py", block)

    def test_ci_retains_report(self) -> None:
        block = sast_job_block()
        self.assertIn("artifacts:", block)
        self.assertIn("when: always", block)
        self.assertIn("bandit-report.json", block)

    def test_config_scopes_compile_trees(self) -> None:
        self.assertEqual(SCOPED_TREES, ("scripts", "platform", "edge"))
        config = load_config()
        excludes = list(config["exclude_dirs"])
        skips = list(config["skips"])
        self.assertEqual(set(excludes), set(EXCLUDE_REASONS))
        self.assertEqual(set(skips), set(SKIP_REASONS))
        self.assertEqual(skips, [])
        self.assertIn("scripts/fixtures/sast", excludes)
        self.assertNotIn("platform", excludes)
        self.assertNotIn("edge", excludes)
        self.assertNotIn("scripts", excludes)

    def test_header_comment_calls_bandit_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:10])
        self.assertIn("bandit (blocking, #328)", header)
        self.assertNotIn("bandit (advisory)", header)
        self.assertIn("ruff (blocking, #327)", header)

    def test_known_bad_fixture_fails(self) -> None:
        if not shutil.which("bandit"):
            self.skipTest("bandit is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, combined)
        self.assertIn(KNOWN_BAD_TEST_ID, combined)

    def test_clean_baseline_fixture_passes(self) -> None:
        if not shutil.which("bandit"):
            self.skipTest("bandit is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean SAST baseline passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
