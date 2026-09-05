#!/usr/bin/env python3
"""Unit tests for the #326 linkcheck gate (pin, scope, suppressions)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_linkcheck.py"
CI = ROOT / ".gitlab-ci.yml"
CONFIG = ROOT / ".mlc.json"
PINNED_VERSION = "3.15.0"

sys.path.insert(0, str(ROOT / "scripts"))
from check_linkcheck import IGNORE_REASONS, PUBLISHED_GLOBS  # noqa: E402


def linkcheck_job_block() -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(r"^linkcheck:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError("linkcheck job missing from .gitlab-ci.yml")
    return match.group(0)


class LinkcheckGateTests(unittest.TestCase):
    def test_ci_pins_markdown_link_check(self) -> None:
        block = linkcheck_job_block()
        self.assertIn(f"markdown-link-check@{PINNED_VERSION}", block)
        self.assertIn("node:22-alpine", block)
        self.assertNotIn("npm install -g markdown-link-check\n", block)

    def test_ci_job_is_required(self) -> None:
        block = linkcheck_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_linkcheck.py", block)
        self.assertIn("scripts/test_linkcheck.py", block)

    def test_config_has_reasoned_ignores_only(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        patterns = [item["pattern"] for item in config.get("ignorePatterns", [])]
        self.assertTrue(patterns, "expected narrow ignorePatterns, not an empty config")
        self.assertEqual(set(patterns), set(IGNORE_REASONS))
        for pattern in patterns:
            self.assertFalse(
                re.search(pattern, "https://aea.artof.link"),
                f"{pattern} must not blanket-ignore first-party HTTPS",
            )
            self.assertFalse(
                re.search(pattern, "https://architecture.artof.link"),
                f"{pattern} must not blanket-ignore the Pages hostname",
            )
        self.assertFalse(
            any(
                re.search(pattern, "https://gitlab.com/other-group/other-project")
                for pattern in patterns
            ),
            "GitLab ignore must stay project-scoped",
        )
        replacements = config.get("replacementPatterns", [])
        self.assertTrue(replacements, "framework .html pages must map to .md")
        self.assertTrue(any(".html" in item.get("pattern", "") for item in replacements))
        self.assertTrue(config.get("retryOn429"))
        self.assertGreaterEqual(int(config.get("retryCount", 0)), 3)

    def test_scope_matches_published_docs(self) -> None:
        self.assertIn("docs/**/*.md", PUBLISHED_GLOBS)
        self.assertIn("implementations/**/*.md", PUBLISHED_GLOBS)
        self.assertIn("README.md", PUBLISHED_GLOBS)
        self.assertNotIn("research/**/*.md", PUBLISHED_GLOBS)
        self.assertNotIn("wiki/**/*.md", PUBLISHED_GLOBS)

    def test_header_comment_calls_linkcheck_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:8])
        self.assertIn("linkcheck (blocking, #326)", header)
        self.assertNotIn("linkcheck (advisory)", header)

    def test_known_bad_fixture_fails(self) -> None:
        if not shutil.which("markdown-link-check"):
            self.skipTest("markdown-link-check is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, combined)
        self.assertIn("aea-326-broken-link.invalid", combined)

    def test_clean_baseline_fixture_passes(self) -> None:
        if not shutil.which("markdown-link-check"):
            self.skipTest("markdown-link-check is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean linkcheck baseline passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
