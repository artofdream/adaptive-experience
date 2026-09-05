#!/usr/bin/env python3
"""Unit tests for the #330 pip-audit Python dependency SCA gate."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_python_sca.py"
CI = ROOT / ".gitlab-ci.yml"
EXCEPTIONS = ROOT / "python-sca-exceptions.json"
PINNED_VERSION = "2.10.1"

sys.path.insert(0, str(ROOT / "scripts"))
from check_python_sca import (  # noqa: E402
    BLOCKING,
    KNOWN_BAD,
    KNOWN_BAD_IDS,
    KNOWN_BAD_PACKAGE,
    KNOWN_BAD_VERSION,
    LOCKS,
    PINNED_PACKAGE,
    blocking_findings,
    ci_job_errors,
    classify_severity,
    collect_findings,
    job_block,
    load_dependencies,
    load_exceptions,
    matching_exception,
    parse_lock_pins,
    severity_from_osv,
    unused_exceptions,
)


def sca_job_block() -> str:
    return job_block("pip-audit")


class PythonScaGateTests(unittest.TestCase):
    def test_ci_pins_pip_audit(self) -> None:
        block = sca_job_block()
        self.assertIn(f"pip-audit=={PINNED_VERSION}", block)
        self.assertEqual(PINNED_PACKAGE, f"pip-audit=={PINNED_VERSION}")
        self.assertIn("python:3.12-alpine", block)
        self.assertNotIn("pip install pip-audit\n", block)
        self.assertNotIn("pip install --no-cache-dir pip-audit\n", block)

    def test_ci_job_is_required(self) -> None:
        block = sca_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_python_sca.py", block)
        self.assertIn("scripts/test_python_sca.py", block)
        self.assertEqual(ci_job_errors(), [])

    def test_ci_retains_report(self) -> None:
        block = sca_job_block()
        self.assertIn("artifacts:", block)
        self.assertIn("when: always", block)
        self.assertIn("pip-audit-report.json", block)

    def test_ci_does_not_stack_later_slices(self) -> None:
        block = sca_job_block()
        lock_block = job_block("python-lock")
        for token in ("trivy", "checkov", "tfsec", "syft", "grype", "cosign"):
            self.assertNotIn(token, block)
        self.assertNotIn("pip-audit==", lock_block)
        self.assertNotIn("osv-scanner", lock_block)
        self.assertNotIn("safety check", lock_block)

    def test_header_comment_calls_pip_audit_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:12])
        self.assertIn("pip-audit (blocking, #330)", header)
        self.assertNotIn("pip-audit (advisory)", header)
        self.assertIn("python-lock (blocking, #329)", header)

    def test_locks_and_fixtures_exist(self) -> None:
        self.assertEqual(
            [path.relative_to(ROOT).as_posix() for path in LOCKS],
            ["platform/requirements.lock", "edge/requirements.lock"],
        )
        for lock in LOCKS:
            self.assertTrue(lock.is_file(), lock)
            self.assertTrue(parse_lock_pins(lock))
        pins = parse_lock_pins(KNOWN_BAD)
        self.assertEqual(pins, [(KNOWN_BAD_PACKAGE, KNOWN_BAD_VERSION)])
        self.assertEqual(parse_lock_pins(ROOT / "scripts" / "fixtures" / "sca" / "clean.lock"), [])

    def test_exceptions_file_is_strict_and_empty_at_baseline(self) -> None:
        items = load_exceptions()
        self.assertEqual(items, [])
        payload = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
        self.assertEqual(payload, {"exceptions": []})

    def test_load_dependencies_accepts_list_and_object(self) -> None:
        listed = load_dependencies('[{"name":"flask","version":"0.5","vulns":[]}]')
        wrapped = load_dependencies('{"dependencies":[{"name":"flask","version":"0.5","vulns":[]}]}')
        self.assertEqual(listed[0]["name"], "flask")
        self.assertEqual(wrapped[0]["name"], "flask")

    def test_collect_findings_and_fail_closed_severity(self) -> None:
        dependencies = [
            {
                "name": "PyYAML",
                "version": "5.3",
                "vulns": [
                    {
                        "id": "GHSA-6757-jp84-gxfx",
                        "aliases": ["CVE-2020-14343"],
                        "fix_versions": ["5.3.1"],
                        "description": "critical incomplete fix",
                    }
                ],
            }
        ]
        findings = collect_findings(dependencies)
        self.assertEqual(findings[0]["package"], "pyyaml")
        self.assertIn("CVE-2020-14343", findings[0]["aliases"])
        self.assertEqual(classify_severity(findings[0], lambda _vid: None), "HIGH")
        blocked = blocking_findings(findings, [], lambda _vid: None)
        self.assertEqual(len(blocked), 1)
        self.assertIn(blocked[0]["severity"], BLOCKING)

    def test_osv_severity_mapping(self) -> None:
        self.assertEqual(
            severity_from_osv({"database_specific": {"severity": "CRITICAL"}}),
            "CRITICAL",
        )
        self.assertEqual(
            severity_from_osv({"database_specific": {"severity": "MODERATE"}}),
            "MEDIUM",
        )
        self.assertEqual(severity_from_osv({"severity": [{"score": "9.8"}]}), "CRITICAL")
        self.assertEqual(severity_from_osv({"severity": [{"score": "7.5"}]}), "HIGH")
        self.assertEqual(severity_from_osv({"severity": [{"score": "5.0"}]}), "MEDIUM")
        self.assertEqual(severity_from_osv({"severity": [{"score": "2.0"}]}), "LOW")
        self.assertIsNone(severity_from_osv(None))

    def test_medium_findings_do_not_block(self) -> None:
        finding = {
            "package": "example",
            "version": "1.0",
            "id": "GHSA-xxxx-yyyy-zzzz",
            "aliases": [],
            "fix_versions": ["1.1"],
        }
        blocked = blocking_findings(
            [finding],
            [],
            lambda _vid: {"database_specific": {"severity": "MEDIUM"}},
        )
        self.assertEqual(blocked, [])
        self.assertEqual(finding["severity"], "MEDIUM")

    def test_exception_requires_owner_reason_expiry(self) -> None:
        finding = {
            "package": "pyyaml",
            "version": "5.3",
            "id": "GHSA-6757-jp84-gxfx",
            "aliases": ["CVE-2020-14343"],
            "fix_versions": ["5.3.1"],
        }
        today = date(2026, 9, 5)
        active = {
            "id": "GHSA-6757-jp84-gxfx",
            "package": "pyyaml",
            "owner": "@aea-appsec-auditor",
            "reason": "recorded policy example",
            "expires": "2026-12-01",
        }
        expired = {**active, "expires": "2026-01-01"}
        self.assertIsNotNone(matching_exception(finding, [active], today))
        self.assertIsNone(matching_exception(finding, [expired], today))
        blocked = blocking_findings([dict(finding)], [active], lambda _vid: None, today)
        self.assertEqual(blocked, [])
        blocked_expired = blocking_findings([dict(finding)], [expired], lambda _vid: None, today)
        self.assertEqual(len(blocked_expired), 1)
        self.assertEqual(unused_exceptions([finding], [expired], today), [expired])

    def test_stale_exception_is_unused(self) -> None:
        today = date(2026, 9, 5)
        leftover = {
            "id": "GHSA-nope",
            "package": "missing",
            "owner": "@aea-appsec-auditor",
            "reason": "stale",
            "expires": "2026-12-01",
        }
        self.assertEqual(unused_exceptions([], [leftover], today), [leftover])

    def test_clean_baseline_mode_passes_without_pip_audit(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean SCA baseline passed", result.stdout)

    def test_known_bad_fixture_fails(self) -> None:
        if not shutil.which("pip-audit"):
            self.skipTest("pip-audit is not installed")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, combined)
        self.assertTrue(any(item in combined for item in KNOWN_BAD_IDS), combined)

    def test_malformed_exceptions_fail(self) -> None:
        original = EXCEPTIONS.read_text(encoding="utf-8")
        try:
            EXCEPTIONS.write_text('{"exceptions": [{"id": "GHSA-x"}]}\n', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("missing", result.stderr)
        finally:
            EXCEPTIONS.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
