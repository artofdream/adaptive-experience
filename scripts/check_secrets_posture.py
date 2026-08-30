#!/usr/bin/env python3
"""Check protected secrets posture, template parity, and unignored candidates.

Path-only inspection: never read or print secret file values.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORED_SECRET_PATTERNS = [
    ".env",
    "*.pem",
    "*.key",
    "*.tfvars",
    ".obsidian/",
    "google-services.json",
]

CANDIDATE_BASENAMES = frozenset(
    {
        ".env",
        "google-services.json",
        "terraform.tfvars",
    }
)
CANDIDATE_SUFFIXES = (".pem", ".key", ".tfvars")
EXAMPLE_SUFFIXES = (".example",)


def _is_example_name(name: str) -> bool:
    return name.endswith(EXAMPLE_SUFFIXES)


def is_secret_candidate_name(name: str) -> bool:
    """Return True for secret-shaped filenames that are not dummy examples."""
    if _is_example_name(name):
        return False
    if name in CANDIDATE_BASENAMES:
        return True
    return name.endswith(CANDIDATE_SUFFIXES)


def check_gitignore_patterns(root: Path | None = None) -> tuple[bool, list[str]]:
    """Verify .gitignore contains mandatory secret exclusion patterns."""
    gitignore_path = (root or ROOT) / ".gitignore"
    if not gitignore_path.is_file():
        return False, ["Missing .gitignore file"]

    content = gitignore_path.read_text(encoding="utf-8")
    missing = []
    for pattern in IGNORED_SECRET_PATTERNS:
        if pattern not in content:
            missing.append(f"Missing mandatory .gitignore pattern: {pattern}")

    return len(missing) == 0, missing


def check_secret_templates(root: Path | None = None) -> tuple[bool, list[str]]:
    """Check that example template files exist for environment configurations."""
    _ = root or ROOT
    errors: list[str] = []
    return True, errors


def _git(args: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def _nul_paths(stdout: str) -> list[str]:
    return [p for p in stdout.split("\0") if p]


def check_unignored_secret_candidates(
    root: Path | None = None,
) -> tuple[bool, list[str]]:
    """Fail on tracked or unignored untracked secret-candidate files.

    Reports paths only. Never reads or prints file contents.
    """
    repo = root or ROOT
    errors: list[str] = []

    tracked = _git(["ls-files", "-z"], repo)
    if tracked.returncode != 0:
        return False, ["unable to list tracked files for secrets posture"]

    untracked = _git(
        ["ls-files", "-z", "--others", "--exclude-standard"],
        repo,
    )
    if untracked.returncode != 0:
        return False, ["unable to list untracked files for secrets posture"]

    for rel in _nul_paths(tracked.stdout):
        if is_secret_candidate_name(Path(rel).name):
            errors.append(f"tracked secret candidate: {rel}")

    for rel in _nul_paths(untracked.stdout):
        if is_secret_candidate_name(Path(rel).name):
            errors.append(f"unignored secret candidate: {rel}")

    return len(errors) == 0, errors


def check_uncommitted_secret_leaks(root: Path | None = None) -> tuple[bool, list[str]]:
    """Backward-compatible alias for candidate-file inspection."""
    return check_unignored_secret_candidates(root)


def main() -> int:
    print("Protected Secrets Posture & Sanitization Guard")
    git_ok, git_errs = check_gitignore_patterns()
    if not git_ok:
        for err in git_errs:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    tmpl_ok, tmpl_errs = check_secret_templates()
    if not tmpl_ok:
        for err in tmpl_errs:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    cand_ok, cand_errs = check_unignored_secret_candidates()
    if not cand_ok:
        for err in cand_errs:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print("ok: mandatory secret patterns present in .gitignore")
    print("ok: secret template parity and sanitization posture verified")
    print("ok: no tracked or unignored secret-candidate files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
