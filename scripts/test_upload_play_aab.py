#!/usr/bin/env python3
"""Offline unit tests for scripts/upload_play_aab.py (#354). No network."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import upload_play_aab as up  # noqa: E402


class TrackGuards(unittest.TestCase):
    def test_internal_allowed(self) -> None:
        self.assertEqual(up.assert_track_allowed("internal"), "internal")
        self.assertEqual(up.assert_track_allowed("Alpha"), "alpha")

    def test_production_forbidden(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            up.assert_track_allowed("production")
        self.assertIn("Production", str(ctx.exception))
        with self.assertRaises(ValueError):
            up.assert_track_allowed("PROD")


class ReleaseBody(unittest.TestCase):
    def test_version_codes_are_strings(self) -> None:
        body = up.build_release_body(3, status="completed")
        self.assertEqual(body["releases"][0]["versionCodes"], ["3"])
        self.assertEqual(body["releases"][0]["status"], "completed")


class PathResolution(unittest.TestCase):
    def test_credentials_missing(self) -> None:
        self.assertIsNone(up.resolve_credentials_path(None))
        self.assertIsNone(up.resolve_credentials_path("/no/such/file.json"))

    def test_credentials_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sa.json"
            path.write_text('{"type":"service_account"}', encoding="utf-8")
            self.assertEqual(up.resolve_credentials_path(str(path)), path)

    def test_aab_default_absent(self) -> None:
        self.assertIsNone(up.resolve_aab_path("/no/such/app-release.aab"))


class DryRunCli(unittest.TestCase):
    def test_dry_run_exit_zero_without_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            code = up.main(["--dry-run", "--json-out", str(out), "--track", "internal"])
            self.assertEqual(code, 0)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "dry-run")
            self.assertFalse(report["credentials_present"])
            self.assertEqual(report["track"], "internal")
            self.assertIn("edits.bundles.upload", report["would_call"])

    def test_cli_rejects_production(self) -> None:
        code = up.main(["--dry-run", "--track", "production"])
        self.assertEqual(code, 2)

    def test_skip_without_credentials_non_dry_run(self) -> None:
        code = up.main(["--track", "internal", "--aab", "/no/such.aab"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
