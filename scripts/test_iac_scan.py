#!/usr/bin/env python3
"""Unit tests for the #334 Terraform validation and IaC scan gate."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_iac_scan.py"
CI = ROOT / ".gitlab-ci.yml"
EXCEPTIONS = ROOT / "iac-scan-exceptions.json"

sys.path.insert(0, str(ROOT / "scripts"))
from check_iac_scan import (  # noqa: E402
    BLOCKING_CHECKOV,
    CLEAN,
    KNOWN_BAD,
    LATER_SLICES,
    PINNED_CHECKOV,
    PINNED_CHECKOV_PKG,
    PINNED_TERRAFORM,
    REPORT,
    STACK,
    WORLD_OPEN_ID,
    blocking_findings,
    ci_job_errors,
    collect_checkov_findings,
    collect_world_open,
    job_block,
    load_exceptions,
    matching_exception,
    prove_clean_baseline,
    prove_known_bad,
    terraform_files,
    unused_exceptions,
)


def iac_job_block() -> str:
    return job_block("iac-scan")


class IacScanGateTests(unittest.TestCase):
    def test_ci_job_is_required(self) -> None:
        block = iac_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_iac_scan.py", block)
        self.assertIn("scripts/test_iac_scan.py", block)
        self.assertIn("--install-terraform", block)
        self.assertIn(PINNED_CHECKOV_PKG, block)
        self.assertEqual(ci_job_errors(), [])

    def test_ci_pins_terraform_and_checkov(self) -> None:
        block = iac_job_block()
        self.assertEqual(PINNED_TERRAFORM, "1.9.8")
        self.assertEqual(PINNED_CHECKOV, "3.2.447")
        self.assertIn(PINNED_CHECKOV_PKG, block)
        self.assertIn("--install-terraform", block)
        self.assertIn("python:3.12@", block)
        self.assertNotIn("AWS_ACCESS_KEY_ID", block)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", block)

    def test_ci_retains_report(self) -> None:
        block = iac_job_block()
        self.assertIn("artifacts:", block)
        self.assertIn("when: always", block)
        self.assertIn("iac-scan-report.json", block)

    def test_ci_does_not_stack_later_slices(self) -> None:
        block = iac_job_block()
        scan_block = job_block("image-scan")
        for token in LATER_SLICES:
            self.assertNotIn(token, block)
        self.assertNotIn("checkov", scan_block)
        self.assertNotIn("tfsec", scan_block)
        self.assertNotIn("terraform fmt", scan_block)

    def test_header_comment_calls_iac_scan_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:15])
        self.assertIn("iac-scan (blocking, #334)", header)
        self.assertNotIn("iac-scan (advisory)", header)
        self.assertIn("image-scan (blocking, #332)", header)

    def test_stack_and_fixtures_exist(self) -> None:
        self.assertTrue(STACK.is_dir())
        self.assertTrue((STACK / "security_groups.tf").is_file())
        self.assertTrue((STACK / "versions.tf").is_file())
        self.assertTrue(terraform_files(KNOWN_BAD))
        self.assertTrue(terraform_files(CLEAN))
        self.assertTrue(EXCEPTIONS.is_file())

    def test_known_bad_fixture_fails(self) -> None:
        self.assertEqual(prove_known_bad(), [])
        findings = collect_world_open(terraform_files(KNOWN_BAD))
        blocked = blocking_findings(findings, [])
        self.assertTrue(blocked)
        self.assertEqual(blocked[0]["id"], WORLD_OPEN_ID)
        self.assertIn("rds", blocked[0]["resource"])
        self.assertNotIn("alb", blocked[0]["resource"])

    def test_clean_fixture_allows_alb_and_private_rds(self) -> None:
        self.assertEqual(prove_clean_baseline(), [])
        findings = collect_world_open(terraform_files(CLEAN))
        self.assertEqual(blocking_findings(findings, []), [])

    def test_current_stack_has_no_world_open_non_alb(self) -> None:
        findings = collect_world_open(terraform_files(STACK))
        blocked = blocking_findings(findings, [])
        self.assertEqual(blocked, [])

    def test_checkov_public_ingress_ids_are_blocking(self) -> None:
        report = {
            "results": {
                "failed_checks": [
                    {
                        "check_id": "CKV_AWS_260",
                        "resource": "aws_security_group.alb",
                        "file_path": "infra/aws/security_groups.tf",
                        "severity": "HIGH",
                        "check_name": "Ensure no security groups allow ingress from 0.0.0.0:0 to port 80",
                    },
                    {
                        "check_id": "CKV_AWS_23",
                        "resource": "aws_security_group.rds",
                        "file_path": "infra/aws/security_groups.tf",
                        "severity": "LOW",
                        "check_name": "Ensure every security group and rule has a description",
                    },
                ]
            }
        }
        findings = collect_checkov_findings(report)
        blocked = blocking_findings(findings, [])
        self.assertEqual([item["id"] for item in blocked], ["CKV_AWS_260"])
        self.assertIn("CKV_AWS_260", BLOCKING_CHECKOV)

    def test_exception_requires_owner_reason_expiry(self) -> None:
        finding = {
            "id": WORLD_OPEN_ID,
            "aliases": [],
            "resource": "aws_security_group.rds",
            "file": "open_rds.tf",
            "severity": "HIGH",
        }
        today = date(2026, 9, 5)
        active = {
            "id": WORLD_OPEN_ID,
            "resource": "aws_security_group.rds",
            "owner": "@aea-appsec-auditor",
            "reason": "recorded policy example",
            "expires": "2026-12-01",
        }
        expired = {**active, "expires": "2026-01-01"}
        self.assertIsNotNone(matching_exception(finding, [active], today))
        self.assertIsNone(matching_exception(finding, [expired], today))
        self.assertEqual(blocking_findings([dict(finding)], [active], today), [])
        self.assertEqual(len(blocking_findings([dict(finding)], [expired], today)), 1)
        self.assertEqual(unused_exceptions([finding], [expired], today), [expired])

    def test_expired_and_stale_exceptions_are_unused(self) -> None:
        today = date.today()
        leftover = {
            "id": "CKV_AWS_260",
            "resource": "*",
            "owner": "@aea-devsecops-platform",
            "reason": "stale",
            "expires": (today + timedelta(days=30)).isoformat(),
        }
        self.assertEqual(unused_exceptions([], [leftover], today), [leftover])

    def test_exceptions_file_is_strict_and_empty_at_baseline(self) -> None:
        items = load_exceptions()
        self.assertEqual(items, [])
        payload = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
        self.assertEqual(payload, {"exceptions": []})

    def test_clean_baseline_mode_passes_without_tools(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean IaC baseline passed", result.stdout)

    def test_known_bad_mode_passes_without_tools(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("known-bad world-open non-ALB fixture fails", result.stdout)

    def test_malformed_exceptions_fail(self) -> None:
        original = EXCEPTIONS.read_text(encoding="utf-8")
        try:
            EXCEPTIONS.write_text('{"exceptions": [{"id": "CKV_AWS_260"}]}\n', encoding="utf-8")
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

    def test_report_path_is_repo_root(self) -> None:
        self.assertEqual(REPORT, ROOT / "iac-scan-report.json")


if __name__ == "__main__":
    unittest.main()
