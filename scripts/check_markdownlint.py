#!/usr/bin/env python3
"""Run the pinned markdownlint-cli2 gate (#325)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_PACKAGE = "markdownlint-cli2@0.23.2"
FIXTURES = ROOT / "scripts" / "fixtures" / "markdownlint"
KNOWN_BAD = FIXTURES / "known_bad.md"
CLEAN_BASELINE = FIXTURES / "clean_baseline.md"


def find_markdownlint() -> str:
    binary = shutil.which("markdownlint-cli2")
    if not binary:
        print(
            "FAIL: markdownlint-cli2 is not on PATH. Install the pinned CLI: "
            f"npm install -g {PINNED_PACKAGE}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def run_markdownlint(binary: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [binary, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)


def prove_known_bad(binary: str) -> subprocess.CompletedProcess[str]:
    result = run_markdownlint(binary, str(KNOWN_BAD.relative_to(ROOT)))
    print_output(result)
    if result.returncode == 0:
        print("FAIL: known-bad markdownlint fixture unexpectedly passed", file=sys.stderr)
    else:
        print("ok: known-bad markdownlint fixture failed as expected")
    return result


def prove_clean_baseline(binary: str) -> None:
    result = run_markdownlint(binary, str(CLEAN_BASELINE.relative_to(ROOT)))
    print_output(result)
    if result.returncode != 0:
        print("FAIL: clean markdownlint baseline did not pass", file=sys.stderr)
        sys.exit(result.returncode or 1)
    print("ok: clean markdownlint baseline passed")


def lint_scoped_repository(binary: str) -> None:
    result = run_markdownlint(binary)
    print_output(result)
    if result.returncode != 0:
        print("FAIL: scoped repository markdownlint did not exit 0", file=sys.stderr)
        sys.exit(result.returncode or 1)
    print("ok: scoped repository markdownlint exited 0")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo"),
        default="all",
    )
    args = parser.parse_args()
    binary = find_markdownlint()
    if args.mode == "known-bad":
        result = prove_known_bad(binary)
        return 1 if result.returncode == 0 else result.returncode
    if args.mode == "all":
        result = prove_known_bad(binary)
        if result.returncode == 0:
            return 1
    if args.mode in {"all", "clean-baseline"}:
        prove_clean_baseline(binary)
    if args.mode in {"all", "repo"}:
        lint_scoped_repository(binary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
