#!/usr/bin/env python3
"""Unit tests for the #327 Ruff gate (pin, scope, exclusions)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_ruff.py"
CI = ROOT / ".gitlab-ci.yml"
CONFIG = ROOT / "ruff.toml"
PINNED_VERSION = "0.16.5"

sys.path.insert(0, str(ROOT / "scripts"))
from check_ruff import EXCLUDE_REASONS, FORMAT_EXCLUDE_REASONS, SCOPED_TREES  # noqa: E402


def ruff_job_block() -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(r"^ruff:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError("ruff job missing from .gitlab-ci.yml")
    return match.group(0)


class RuffGateTests(unittest.TestCase):
    def test_ci_pins_ruff(self) -> None:
        block = ruff_job_block()
        self.assertIn(f"ruff=={PINNED_VERSION}", block)
        self.assertIn("python:3.12-alpine", block)
        self.assertNotIn("pip install ruff\n", block)
        self.assertNotIn("pip install --no-cache-dir ruff\n", block)

    def test_ci_job_is_required(self) -> None:
        block = ruff_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_ruff.py", block)
        self.assertIn("scripts/test_ruff.py", block)

    def test_config_scopes_compile_trees(self) -> None:
        self.assertEqual(SCOPED_TREES, ("scripts", "platform", "edge"))
        config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config.get("required-version"), f"=={PINNED_VERSION}")
        self.assertGreaterEqual(int(config.get("line-length", 0)), 584)
        self.assertEqual(config.get("lint", {}).get("select"), ["E9", "F63", "F7", "F82"])
        excludes = list(config.get("extend-exclude", []))
        self.assertEqual(set(excludes), set(EXCLUDE_REASONS))
        self.assertIn("scripts/fixtures/ruff", excludes)
        self.assertNotIn("platform", excludes)
        self.assertNotIn("edge", excludes)
        self.assertNotIn("scripts", excludes)
        format_excludes = list(config.get("format", {}).get("exclude", []))
        self.assertEqual(set(format_excludes), set(FORMAT_EXCLUDE_REASONS))
        self.assertEqual(set(format_excludes), {"platform/**", "edge/**"})
        self.assertNotIn("scripts/**", format_excludes)

    def test_header_comment_calls_ruff_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:9])
        self.assertIn("ruff (blocking, #327)", header)
        self.assertNotIn("ruff (advisory)", header)
        self.assertIn("linkcheck (blocking, #326)", header)

    def test_known_bad_fixture_fails(self) -> None:
        if not shutil.which("ruff"):
            self.skipTest("ruff is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, combined)
        self.assertIn("definitely_undefined_aea_327_name", combined)

    def test_clean_baseline_fixture_passes(self) -> None:
        if not shutil.which("ruff"):
            self.skipTest("ruff is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean ruff baseline passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
