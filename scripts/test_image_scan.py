#!/usr/bin/env python3
"""Unit tests for the #332 image SBOM/scan gate."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_image_scan.py"
CI = ROOT / ".gitlab-ci.yml"
EXCEPTIONS = ROOT / "image-scan-exceptions.json"

sys.path.insert(0, str(ROOT / "scripts"))
from check_image_scan import (  # noqa: E402
    BLOCKING,
    CLEAN_REPORT,
    DEPLOYABLE,
    KNOWN_BAD_DOCKERFILE,
    KNOWN_BAD_IDS,
    KNOWN_BAD_REPORT,
    LATER_SLICES,
    PINNED_TRIVY,
    REPORT,
    blocking_findings,
    ci_job_errors,
    collect_findings,
    job_block,
    load_exceptions,
    load_trivy_report,
    matching_exception,
    prove_clean_baseline,
    prove_known_bad_report,
    unused_exceptions,
)


def scan_job_block() -> str:
    return job_block("image-scan")


class ImageScanGateTests(unittest.TestCase):
    def test_ci_job_is_required(self) -> None:
        block = scan_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_image_scan.py", block)
        self.assertIn("scripts/test_image_scan.py", block)
        self.assertIn("--install-trivy", block)
        self.assertEqual(ci_job_errors(), [])

    def test_ci_retains_sbom_and_report(self) -> None:
        block = scan_job_block()
        self.assertIn("artifacts:", block)
        self.assertIn("when: always", block)
        self.assertIn("image-scan-report.json", block)
        self.assertIn("sbom-", block)
        self.assertIn("trivy-", block)

    def test_ci_builds_with_pinned_dind(self) -> None:
        block = scan_job_block()
        self.assertIn("docker:27.1.1-cli", block)
        self.assertIn("docker:27.1.1-dind", block)
        self.assertIn("--install-trivy", block)
        self.assertEqual(PINNED_TRIVY, "0.74.0")

    def test_ci_does_not_stack_later_slices(self) -> None:
        block = scan_job_block()
        digest_block = job_block("image-digest")
        for token in LATER_SLICES:
            self.assertNotIn(token, block)
        self.assertNotIn("trivy", digest_block)
        self.assertNotIn("sbom-", digest_block)

    def test_deploy_jobs_depend_on_image_scan(self) -> None:
        deploy = job_block("deploy-ecs")
        deploy_agent = job_block("deploy-ecs-agent-runner")
        self.assertIn("job: image-scan", deploy)
        self.assertIn("job: image-scan", deploy_agent)
        self.assertNotRegex(job_block("build-ecr"), r"^  needs:", msg="build-ecr keeps stage order")
        self.assertNotRegex(job_block("build-ecr-agent-runner"), r"^  needs:")

    def test_header_comment_calls_image_scan_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:14])
        self.assertIn("image-scan (blocking, #332)", header)
        self.assertNotIn("image-scan (advisory)", header)
        self.assertIn("image-digest (blocking, #331)", header)

    def test_deployable_inventory_and_fixtures_exist(self) -> None:
        self.assertEqual(
            [name for name, _df, _ctx in DEPLOYABLE],
            ["orchestration", "bff", "gateway", "agent-runner"],
        )
        for _name, dockerfile, context in DEPLOYABLE:
            self.assertTrue((ROOT / dockerfile).is_file(), dockerfile)
            self.assertTrue((ROOT / context).is_dir(), context)
        self.assertTrue(KNOWN_BAD_DOCKERFILE.is_file())
        self.assertTrue(KNOWN_BAD_REPORT.is_file())
        self.assertTrue(CLEAN_REPORT.is_file())
        self.assertTrue(EXCEPTIONS.is_file())

    def test_known_bad_fixture_fails(self) -> None:
        self.assertEqual(prove_known_bad_report(), [])
        findings = collect_findings(load_trivy_report(KNOWN_BAD_REPORT), "known-bad")
        blocked = blocking_findings(findings, [])
        ids = {item["id"] for item in blocked}
        self.assertTrue(ids & KNOWN_BAD_IDS)
        self.assertIn(blocked[0]["severity"], BLOCKING)
        self.assertTrue(blocked[0]["fixed"])

    def test_clean_fixture_passes(self) -> None:
        self.assertEqual(prove_clean_baseline(), [])

    def test_unfixed_high_does_not_block(self) -> None:
        report = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-unfixed",
                            "PkgName": "openssl",
                            "InstalledVersion": "1.0.0",
                            "FixedVersion": "",
                            "Severity": "CRITICAL",
                        }
                    ]
                }
            ]
        }
        findings = collect_findings(report, "gateway")
        self.assertEqual(blocking_findings(findings, []), [])

    def test_exception_requires_owner_reason_expiry(self) -> None:
        finding = {
            "image": "gateway",
            "id": "CVE-2020-14343",
            "aliases": [],
            "package": "pyyaml",
            "installed": "5.3",
            "fixed": "5.3.1",
            "severity": "CRITICAL",
        }
        today = date(2026, 9, 5)
        active = {
            "id": "CVE-2020-14343",
            "image": "gateway",
            "package": "pyyaml",
            "owner": "@aea-devsecops-platform",
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
            "id": "CVE-nope",
            "image": "*",
            "package": "*",
            "owner": "@aea-appsec-auditor",
            "reason": "stale",
            "expires": (today + timedelta(days=30)).isoformat(),
        }
        self.assertEqual(unused_exceptions([], [leftover], today), [leftover])

    def test_exceptions_file_is_strict_and_empty_at_baseline(self) -> None:
        items = load_exceptions()
        self.assertEqual(items, [])
        payload = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
        self.assertEqual(payload, {"exceptions": []})

    def test_clean_baseline_mode_passes_without_trivy(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "clean-baseline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("clean image-scan baseline passed", result.stdout)

    def test_known_bad_mode_passes_without_docker(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "known-bad"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("known-bad Trivy fixture fails", result.stdout)

    def test_malformed_exceptions_fail(self) -> None:
        original = EXCEPTIONS.read_text(encoding="utf-8")
        try:
            EXCEPTIONS.write_text('{"exceptions": [{"id": "CVE-x"}]}\n', encoding="utf-8")
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
        self.assertEqual(REPORT, ROOT / "image-scan-report.json")


if __name__ == "__main__":
    unittest.main()
