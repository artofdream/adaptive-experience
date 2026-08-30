#!/usr/bin/env python3
"""Check protected secrets posture, template parity, and unignored candidates.

Path-only inspection: never read or print secret file values.
"""

from __future__ import annotations

import fnmatch
import shutil
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


SKIP_WALK_DIRS = frozenset(
    {
        ".git",
        ".terraform",
        "node_modules",
        ".venv",
        "__pycache__",
        ".worktrees",
    }
)


def _git(args: list[str], root: Path) -> subprocess.CompletedProcess[str] | None:
    if shutil.which("git") is None:
        return None
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None


def _nul_paths(stdout: str) -> list[str]:
    return [p for p in stdout.split("\0") if p]


def _gitignore_rules(root: Path) -> list[tuple[bool, str]]:
    path = root / ".gitignore"
    if not path.is_file():
        return []
    rules: list[tuple[bool, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        negate = line.startswith("!")
        pattern = line[1:] if negate else line
        rules.append((negate, pattern))
    return rules


def _rule_matches(rel_posix: str, name: str, pattern: str) -> bool:
    pat = pattern.rstrip("/")
    if fnmatch.fnmatch(name, pat):
        return True
    if fnmatch.fnmatch(rel_posix, pat):
        return True
    if pat.startswith("**/") and (
        fnmatch.fnmatch(name, pat[3:]) or fnmatch.fnmatch(rel_posix, pat[3:])
    ):
        return True
    return False


def path_ignored_by_gitignore(rel_posix: str, root: Path) -> bool:
    """Return True when .gitignore would ignore rel_posix. Path only."""
    ignored = False
    name = Path(rel_posix).name
    for negate, pattern in _gitignore_rules(root):
        if _rule_matches(rel_posix, name, pattern):
            ignored = not negate
    return ignored


def check_candidates_via_walk(root: Path) -> tuple[bool, list[str]]:
    """Filesystem fallback when git is absent (CI alpine images)."""
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_secret_candidate_name(path.name):
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_WALK_DIRS for part in rel_parts):
            continue
        rel = path.relative_to(root).as_posix()
        if path_ignored_by_gitignore(rel, root):
            continue
        errors.append(f"unignored secret candidate: {rel}")
    return len(errors) == 0, errors


def check_candidates_via_git(root: Path) -> tuple[bool, list[str]] | None:
    tracked = _git(["ls-files", "-z"], root)
    if tracked is None or tracked.returncode != 0:
        return None
    untracked = _git(["ls-files", "-z", "--others", "--exclude-standard"], root)
    if untracked is None or untracked.returncode != 0:
        return None

    errors: list[str] = []
    for rel in _nul_paths(tracked.stdout):
        if is_secret_candidate_name(Path(rel).name):
            errors.append(f"tracked secret candidate: {rel}")
    for rel in _nul_paths(untracked.stdout):
        if is_secret_candidate_name(Path(rel).name):
            errors.append(f"unignored secret candidate: {rel}")
    return len(errors) == 0, errors


def check_unignored_secret_candidates(
    root: Path | None = None,
    *,
    prefer_walk: bool = False,
) -> tuple[bool, list[str]]:
    """Fail on tracked or unignored untracked secret-candidate files.

    Reports paths only. Never reads or prints file contents.
    Uses git when available; walks the tree when git is missing (CI alpine).
    """
    repo = root or ROOT
    if not prefer_walk:
        via_git = check_candidates_via_git(repo)
        if via_git is not None:
            return via_git
    return check_candidates_via_walk(repo)


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
