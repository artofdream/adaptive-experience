#!/usr/bin/env python3
"""Unit tests for check_secrets_posture.py.

Fixture leaks use dummy values only. Tests assert those values never appear
in checker stdout/stderr. Git-backed cases skip when git is absent (CI alpine).
"""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_secrets_posture import (
    check_gitignore_patterns,
    check_secret_templates,
    check_unignored_secret_candidates,
    is_secret_candidate_name,
    main,
    path_ignored_by_gitignore,
)


CANARY = "LEAK-VALUE-MUST-NEVER-PRINT-9f3c2a"
HAS_GIT = shutil.which("git") is not None


def _init_repo(root: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.test"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "fixture"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_ignore(root: Path, lines: list[str]) -> None:
    _write(root / ".gitignore", "\n".join(lines) + "\n")


def _capture_main() -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        code = main()
    return code, buf.getvalue()


class TestSecretsPosture(unittest.TestCase):
    def test_gitignore_patterns(self):
        ok, errors = check_gitignore_patterns()
        self.assertTrue(ok, f"Gitignore pattern check failed: {errors}")

    def test_secret_templates(self):
        ok, errors = check_secret_templates()
        self.assertTrue(ok, f"Secret template check failed: {errors}")

    def test_current_tree_has_no_unignored_candidates(self):
        ok, errors = check_unignored_secret_candidates()
        self.assertTrue(ok, f"Current tree leaked candidate paths: {errors}")
        combined = " ".join(errors)
        self.assertNotIn(CANARY, combined)

    def test_example_names_are_not_candidates(self):
        self.assertFalse(is_secret_candidate_name("google-services.json.example"))
        self.assertFalse(is_secret_candidate_name(".env.example"))
        self.assertFalse(is_secret_candidate_name("terraform.tfvars.example"))
        self.assertTrue(is_secret_candidate_name("google-services.json"))
        self.assertTrue(is_secret_candidate_name(".env"))
        self.assertTrue(is_secret_candidate_name("id_rsa.pem"))
        self.assertTrue(is_secret_candidate_name("deploy.key"))
        self.assertTrue(is_secret_candidate_name("secret.tfvars"))

    def test_repo_main_output_hides_values(self):
        code, output = _capture_main()
        self.assertEqual(code, 0)
        self.assertNotIn(CANARY, output)
        self.assertIn("ok: no tracked or unignored secret-candidate files", output)


class TestSecretCandidateWalkFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write_ignore(
            self.root,
            [
                ".env",
                "*.pem",
                "*.key",
                "*.tfvars",
                ".obsidian/",
                "**/google-services.json",
                "!**/google-services.json.example",
            ],
        )
        _write(self.root / "README.md", "fixture\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _assert_fail_without_canary(self, relpath: str) -> None:
        _write(self.root / relpath, f"dummy={CANARY}\n")
        ok, errors = check_unignored_secret_candidates(self.root, prefer_walk=True)
        self.assertFalse(ok, f"expected fail for {relpath}")
        self.assertTrue(errors)
        joined = "\n".join(errors)
        self.assertIn(Path(relpath).name, joined)
        self.assertNotIn(CANARY, joined)
        for err in errors:
            self.assertFalse(err.startswith("dummy="))
            self.assertNotIn(CANARY, err)

    def test_unignored_env_fails_and_hides_value(self):
        _write_ignore(self.root, ["*.pem"])
        self._assert_fail_without_canary(".env")

    def test_unignored_google_services_fails_and_hides_value(self):
        _write_ignore(self.root, [".env"])
        self._assert_fail_without_canary("app/google-services.json")

    def test_unignored_pem_fails_and_hides_value(self):
        _write_ignore(self.root, [".env"])
        self._assert_fail_without_canary("certs/dev.pem")

    def test_unignored_key_fails_and_hides_value(self):
        _write_ignore(self.root, [".env"])
        self._assert_fail_without_canary("certs/dev.key")

    def test_unignored_tfvars_fails_and_hides_value(self):
        _write_ignore(self.root, [".env"])
        self._assert_fail_without_canary("infra/aws/terraform.tfvars")

    def test_ignored_candidates_pass(self):
        _write(self.root / ".env", f"SECRET={CANARY}\n")
        _write(self.root / "app/google-services.json", f'{{"current_key":"{CANARY}"}}\n')
        _write(self.root / "infra/aws/terraform.tfvars", f"token={CANARY}\n")
        _write(self.root / "certs/dev.pem", CANARY)
        _write(self.root / "certs/dev.key", CANARY)
        ok, errors = check_unignored_secret_candidates(self.root, prefer_walk=True)
        self.assertTrue(ok, errors)
        self.assertEqual(errors, [])

    def test_walk_fallback_fails_on_unignored_google_services(self):
        _write_ignore(self.root, [".env"])
        _write(self.root / "app/google-services.json", f'{{"current_key":"{CANARY}"}}\n')
        ok, errors = check_unignored_secret_candidates(self.root, prefer_walk=True)
        self.assertFalse(ok)
        joined = "\n".join(errors)
        self.assertIn("google-services.json", joined)
        self.assertNotIn(CANARY, joined)

    def test_walk_fallback_respects_gitignore(self):
        _write(self.root / ".env", f"SECRET={CANARY}\n")
        _write(self.root / "app/google-services.json", f'{{"current_key":"{CANARY}"}}\n')
        self.assertTrue(path_ignored_by_gitignore(".env", self.root))
        self.assertTrue(path_ignored_by_gitignore("app/google-services.json", self.root))
        ok, errors = check_unignored_secret_candidates(self.root, prefer_walk=True)
        self.assertTrue(ok, errors)
        self.assertEqual(errors, [])

    def test_example_files_pass(self):
        _write(
            self.root / "app/google-services.json.example",
            '{"current_key":"EXAMPLE-not-a-secret"}\n',
        )
        _write(self.root / ".env.example", "AEA_AI_API_KEY=\n")
        _write(self.root / "infra/aws/terraform.tfvars.example", "region=us-east-1\n")
        ok, errors = check_unignored_secret_candidates(self.root, prefer_walk=True)
        self.assertTrue(ok, errors)


@unittest.skipUnless(HAS_GIT, "git not installed (CI alpine fallback uses walk tests)")
class TestSecretCandidateGitFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _init_repo(self.root)
        _write_ignore(
            self.root,
            [
                ".env",
                "*.pem",
                "*.key",
                "*.tfvars",
                ".obsidian/",
                "**/google-services.json",
                "!**/google-services.json.example",
            ],
        )
        _write(self.root / "README.md", "fixture\n")
        subprocess.run(
            ["git", "add", ".gitignore", "README.md"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "fixture base"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_tracked_google_services_fails_and_hides_value(self):
        rel = "clients/mobile/android/app/google-services.json"
        _write(self.root / rel, f'{{"api_key":"{CANARY}"}}\n')
        subprocess.run(
            ["git", "add", "-f", rel],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        ok, errors = check_unignored_secret_candidates(self.root)
        self.assertFalse(ok)
        joined = "\n".join(errors)
        self.assertIn("tracked secret candidate:", joined)
        self.assertIn("google-services.json", joined)
        self.assertNotIn(CANARY, joined)


if __name__ == "__main__":
    unittest.main()
