#!/usr/bin/env python3
"""Unit tests for the #416 Path B multi-arch ECR push helper."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ecr_multiarch_push.sh"
CI = ROOT / ".gitlab-ci.yml"


def job_block(name: str) -> str:
    text = CI.read_text(encoding="utf-8")
    import re

    match = re.search(rf"^{re.escape(name)}:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"{name} job missing from .gitlab-ci.yml")
    return match.group(0)


class EcrMultiarchPushTests(unittest.TestCase):
    def test_script_is_posix_and_lists_both_platforms(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#!/bin/sh"))
        self.assertIn("linux/amd64,linux/arm64", text)
        self.assertIn("docker buildx build", text)
        self.assertIn("--push", text)
        self.assertIn("shop)", text)
        self.assertIn("agent-runner)", text)
        self.assertIn("grafana/grafana:10.4.0", text)
        self.assertIn("tonistiigi/binfmt", text)
        self.assertNotIn("terraform apply", text)

    def test_ci_jobs_call_the_helper_and_keep_sha_latest_tags(self) -> None:
        shop = job_block("build-ecr")
        agent = job_block("build-ecr-agent-runner")
        self.assertIn("scripts/ecr_multiarch_push.sh shop", shop)
        self.assertIn("scripts/ecr_multiarch_push.sh agent-runner", agent)
        self.assertIn("linux/amd64,linux/arm64", shop)
        self.assertNotIn("docker build -f platform/Dockerfile.orchestration", shop)
        self.assertNotIn("docker build -f platform/docker/Dockerfile.agent-runner", agent)
        self.assertIn("CI_COMMIT_SHA", SCRIPT.read_text(encoding="utf-8"))
        self.assertIn(":latest", SCRIPT.read_text(encoding="utf-8"))

    def test_grafana_default_pin_stays_on_arg(self) -> None:
        dockerfile = (ROOT / "platform" / "docker" / "Dockerfile.grafana").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "grafana/grafana:10.4.0@sha256:f9811e4e687ffecf1a43adb9b64096c50bc0d7a782f8608530f478b6542de7d5",
            dockerfile,
        )
        self.assertIn("ARG AEA_GRAFANA_BASE=", dockerfile)
        self.assertIn("FROM ${AEA_GRAFANA_BASE}", dockerfile)

    def test_materialize_from_rewrites_plain_from_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "Dockerfile"
            dest = Path(tmp) / "out"
            src.write_text(
                "ARG AEA_GRAFANA_BASE=keep\n"
                "FROM python:3.12-alpine@sha256:" + ("a" * 64) + "\n"
                "COPY x y\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "sh",
                    str(SCRIPT),
                    "materialize-from",
                    str(src),
                    "grafana/grafana:10.4.0",
                    str(dest),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            rewritten = dest.read_text(encoding="utf-8")
            self.assertIn("FROM grafana/grafana:10.4.0\n", rewritten)
            self.assertIn("ARG AEA_GRAFANA_BASE=keep\n", rewritten)
            self.assertIn("COPY x y\n", rewritten)


if __name__ == "__main__":
    unittest.main()
