#!/usr/bin/env python3
"""Compile tracked Python under scripts/, platform/, and edge/.

Fails on syntax errors (the Locust-class miss). Uses git ls-files when git
is available; walks those three trees when git is missing (CI alpine).
"""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCOPED_PREFIXES = ("scripts/", "platform/", "edge/")
SKIP_WALK_DIRS = frozenset(
    {
        ".git",
        ".terraform",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".worktrees",
    }
)


def _nul_paths(stdout: str) -> list[str]:
    return [p.replace("\\", "/") for p in stdout.split("\0") if p]


def _in_scope(rel_posix: str) -> bool:
    return rel_posix.endswith(".py") and rel_posix.startswith(SCOPED_PREFIXES)


def _git_ls_python(root: Path) -> list[str] | None:
    if shutil.which("git") is None:
        return None
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.py"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return [rel for rel in _nul_paths(result.stdout) if _in_scope(rel)]


def _walk_python(root: Path) -> list[str]:
    found: list[str] = []
    for prefix in ("scripts", "platform", "edge"):
        base = root / prefix
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(root).parts
            if any(part in SKIP_WALK_DIRS for part in rel_parts):
                continue
            found.append(path.relative_to(root).as_posix())
    return sorted(found)


def list_scoped_python(root: Path | None = None, *, prefer_walk: bool = False) -> list[str]:
    """Return repo-relative POSIX paths of scoped Python files."""
    repo = root or ROOT
    if not prefer_walk:
        via_git = _git_ls_python(repo)
        if via_git is not None:
            return sorted(via_git)
    return _walk_python(repo)


def compile_paths(root: Path, rel_paths: list[str]) -> list[str]:
    """Compile each path. Return error strings (paths + py_compile message)."""
    errors: list[str] = []
    for rel in rel_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing: {rel}")
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{rel}: {exc.msg}")
    return errors


def check_python_compile(
    root: Path | None = None,
    *,
    prefer_walk: bool = False,
) -> tuple[bool, list[str], int]:
    repo = root or ROOT
    paths = list_scoped_python(repo, prefer_walk=prefer_walk)
    errors = compile_paths(repo, paths)
    return len(errors) == 0, errors, len(paths)


def main() -> int:
    ok, errors, count = check_python_compile()
    if not ok:
        print("FAIL: tracked Python under scripts/, platform/, edge/ did not compile:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"ok: {count} tracked Python files compiled under scripts/, platform/, edge/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
