#!/usr/bin/env python3
"""Unit tests for the #325 markdownlint gate (pin, scope, suppressions)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_markdownlint.py"
CI = ROOT / ".gitlab-ci.yml"
CLI2_CONFIG = ROOT / ".markdownlint-cli2.jsonc"
PINNED_VERSION = "0.23.2"


def markdownlint_job_block() -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(r"^markdownlint:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError("markdownlint job missing from .gitlab-ci.yml")
    return match.group(0)


class MarkdownlintGateTests(unittest.TestCase):
    def test_ci_pins_markdownlint_cli2(self) -> None:
        block = markdownlint_job_block()
        self.assertIn(f"markdownlint-cli2@{PINNED_VERSION}", block)
        self.assertIn("node:22-alpine", block)
        self.assertNotIn("npm install -g markdownlint-cli2\n", block)

    def test_ci_job_is_required(self) -> None:
        block = markdownlint_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_markdownlint.py", block)
        self.assertIn("scripts/test_markdownlint.py", block)

    def test_cli2_config_scopes_published_docs(self) -> None:
        config = CLI2_CONFIG.read_text(encoding="utf-8")
        self.assertIn('"docs/**/*.md"', config)
        self.assertIn('"implementations/**/*.md"', config)
        self.assertIn("research/**", config)
        self.assertNotIn("scripts/fixtures", config)

    def test_header_comment_calls_markdownlint_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:9])
        self.assertIn("markdownlint (blocking, #325)", header)
        self.assertIn("linkcheck (blocking, #326)", header)

    def test_known_bad_fixture_fails(self) -> None:
        if not shutil.which("markdownlint-cli2"):
            self.skipTest("markdownlint-cli2 is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, combined)
        self.assertIn("MD018", combined)

    def test_clean_baseline_fixture_passes(self) -> None:
        if not shutil.which("markdownlint-cli2"):
            self.skipTest("markdownlint-cli2 is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean markdownlint baseline passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
