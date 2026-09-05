#!/usr/bin/env python3
"""Unit tests for the #331 image digest pin gate."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".gitlab-ci.yml"

sys.path.insert(0, str(ROOT / "scripts"))
from check_image_digests import (  # noqa: E402
    CLEAN_DOCKERFILE,
    EXCEPTIONS,
    INVENTORY,
    KNOWN_BAD_COMPOSE,
    KNOWN_BAD_DOCKERFILE,
    LATER_SLICES,
    LEDGER,
    MATERIAL_FILES,
    REPORT,
    ci_job_errors,
    collect_findings,
    extract_refs,
    job_block,
    load_exceptions,
    load_inventory,
    prove_clean_baseline,
    prove_known_bad,
    split_ref,
)


def digest_job_block() -> str:
    return job_block("image-digest")


class ImageDigestGateTests(unittest.TestCase):
    def test_ci_job_is_required(self) -> None:
        block = digest_job_block()
        self.assertNotIn("allow_failure:", block)
        self.assertNotIn("|| true", block)
        self.assertIn("scripts/check_image_digests.py", block)
        self.assertIn("scripts/test_image_digests.py", block)
        self.assertEqual(ci_job_errors(), [])

    def test_ci_retains_report(self) -> None:
        block = digest_job_block()
        self.assertIn("artifacts:", block)
        self.assertIn("when: always", block)
        self.assertIn("image-digest-report.json", block)

    def test_ci_does_not_stack_later_slices(self) -> None:
        block = digest_job_block()
        sca_block = job_block("pip-audit")
        for token in LATER_SLICES:
            self.assertNotIn(token, block)
        self.assertNotIn("image-digest", sca_block)
        self.assertNotIn("trivy", sca_block)
        self.assertNotIn("checkov", sca_block)

    def test_header_comment_calls_image_digest_blocking(self) -> None:
        header = "\n".join(CI.read_text(encoding="utf-8").splitlines()[:13])
        self.assertIn("image-digest (blocking, #331)", header)
        self.assertNotIn("image-digest (advisory)", header)
        self.assertIn("pip-audit (blocking, #330)", header)

    def test_inventory_and_fixtures_exist(self) -> None:
        inventory = load_inventory()
        self.assertIn("python:3.12-alpine", inventory)
        self.assertTrue(INVENTORY.is_file())
        self.assertTrue(KNOWN_BAD_DOCKERFILE.is_file())
        self.assertTrue(KNOWN_BAD_COMPOSE.is_file())
        self.assertTrue(CLEAN_DOCKERFILE.is_file())
        self.assertTrue(LEDGER.is_file())
        self.assertTrue(EXCEPTIONS.is_file())

    def test_known_bad_fixtures_fail(self) -> None:
        self.assertEqual(prove_known_bad(), [])
        self.assertTrue(any(split_ref(ref)[1] is None for ref in extract_refs(KNOWN_BAD_DOCKERFILE)))
        self.assertTrue(any(split_ref(ref)[1] is None for ref in extract_refs(KNOWN_BAD_COMPOSE)))

    def test_clean_fixture_passes(self) -> None:
        self.assertEqual(prove_clean_baseline(), [])

    def test_material_files_are_pinned_or_excepted(self) -> None:
        inventory = load_inventory()
        exceptions = load_exceptions()
        errors, seen = collect_findings(list(MATERIAL_FILES), inventory, exceptions)
        self.assertEqual(errors, [])
        self.assertTrue(seen)
        self.assertTrue(any(item["image"] == "python:3.12-alpine" for item in seen))
        self.assertTrue(any(item["image"] == "ghcr.io/berriai/litellm:main-latest" and item["exception"] for item in seen))

    def test_mismatching_digest_fails(self) -> None:
        inventory = load_inventory()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Dockerfile"
            path.write_text(
                "FROM python:3.12-alpine@sha256:" + ("a" * 64) + "\n",
                encoding="utf-8",
            )
            errors, _seen = collect_findings([path], inventory, [])
        self.assertTrue(any("does not match inventory" in error for error in errors))

    def test_expired_exception_fails(self) -> None:
        inventory = load_inventory()
        exceptions = [
            {
                "image": "ghcr.io/berriai/litellm:main-latest",
                "owner": "@aea-devsecops-platform",
                "reason": "expired fixture",
                "expires": (date.today() - timedelta(days=1)).isoformat(),
            }
        ]
        errors, _seen = collect_findings(
            [ROOT / "edge" / "docker-compose.litellm.yml"],
            inventory,
            exceptions,
        )
        self.assertTrue(any("expired" in error for error in errors))

    def test_exceptions_require_owner_reason_expiry(self) -> None:
        rows = load_exceptions()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["image"], "ghcr.io/berriai/litellm:main-latest")
        self.assertTrue(rows[0]["owner"].startswith("@"))
        self.assertTrue(rows[0]["reason"])
        date.fromisoformat(rows[0]["expires"])

    def test_report_path_is_repo_root(self) -> None:
        self.assertEqual(REPORT, ROOT / "image-digest-report.json")
        self.assertTrue(EXCEPTIONS.name.endswith(".json"))
        json.loads(EXCEPTIONS.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
