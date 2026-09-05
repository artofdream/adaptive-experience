#!/usr/bin/env python3
"""Run the pinned Ruff gate (#327)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "ruff.toml"
PINNED_PACKAGE = "ruff==0.16.5"
FIXTURES = ROOT / "scripts" / "fixtures" / "ruff"
KNOWN_BAD = FIXTURES / "known_bad.py"
CLEAN_BASELINE = FIXTURES / "clean_baseline.py"
SCOPED_TREES = ("scripts", "platform", "edge")

# Every extend-exclude entry in ruff.toml must have a reason here.
# Do not add a pattern to silence an unclassified failure.
EXCLUDE_REASONS = {
    "scripts/fixtures/ruff": (
        "Gate fixtures. Known-bad must fail when invoked explicitly; "
        "it is not part of the repository baseline."
    ),
}

# format.exclude only. Lint still covers these trees. Do not add a path
# here to hide a lint finding.
FORMAT_EXCLUDE_REASONS = {
    "platform/**": (
        "Existing platform modules would be rewritten (unwrap/reflow). "
        "That leftover dirty ruff --fix rewrite is out of this slice. "
        "ruff check still covers platform/."
    ),
    "edge/**": (
        "Existing edge/BFF/test modules would be rewritten (unwrap/reflow). "
        "Same class of change as platform/**. ruff check still covers edge/."
    ),
}


def find_ruff() -> str:
    binary = shutil.which("ruff")
    if not binary:
        print(
            "FAIL: ruff is not on PATH. Install the pinned CLI: "
            f"pip install {PINNED_PACKAGE}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def run_ruff(binary: str, *args: str) -> subprocess.CompletedProcess[str]:
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


def check_config_reasons() -> None:
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    patterns = list(config.get("extend-exclude", []))
    missing = [pattern for pattern in patterns if pattern not in EXCLUDE_REASONS]
    extra = [pattern for pattern in EXCLUDE_REASONS if pattern not in patterns]
    if missing or extra:
        print("FAIL: ruff.toml extend-exclude and EXCLUDE_REASONS drifted", file=sys.stderr)
        for pattern in missing:
            print(f"  undocumented exclude: {pattern}", file=sys.stderr)
        for pattern in extra:
            print(f"  unused reason: {pattern}", file=sys.stderr)
        sys.exit(1)
    select = config.get("lint", {}).get("select", [])
    unexpected = [code for code in select if code not in {"E9", "F63", "F7", "F82"}]
    if unexpected:
        print(
            "FAIL: ruff lint select grew beyond the #327 baseline "
            f"(extra {unexpected}). Broader families belong in a later slice.",
            file=sys.stderr,
        )
        sys.exit(1)
    format_excludes = list(config.get("format", {}).get("exclude", []))
    missing_fmt = [p for p in format_excludes if p not in FORMAT_EXCLUDE_REASONS]
    extra_fmt = [p for p in FORMAT_EXCLUDE_REASONS if p not in format_excludes]
    if missing_fmt or extra_fmt:
        print("FAIL: ruff.toml format.exclude and FORMAT_EXCLUDE_REASONS drifted", file=sys.stderr)
        for pattern in missing_fmt:
            print(f"  undocumented format exclude: {pattern}", file=sys.stderr)
        for pattern in extra_fmt:
            print(f"  unused format reason: {pattern}", file=sys.stderr)
        sys.exit(1)
    leaked = [
        path
        for path in format_excludes
        if not path.startswith(("platform/", "edge/"))
    ]
    if leaked:
        print(
            "FAIL: format.exclude must stay limited to documented platform/ "
            f"and edge/ trees, not {leaked}",
            file=sys.stderr,
        )
        sys.exit(1)


def prove_known_bad(binary: str) -> subprocess.CompletedProcess[str]:
    result = run_ruff(binary, "check", "--no-cache", str(KNOWN_BAD.relative_to(ROOT)))
    print_output(result)
    if result.returncode == 0:
        print("FAIL: known-bad ruff fixture unexpectedly passed", file=sys.stderr)
    else:
        print("ok: known-bad ruff fixture failed as expected")
    return result


def prove_clean_baseline(binary: str) -> None:
    check = run_ruff(binary, "check", "--no-cache", str(CLEAN_BASELINE.relative_to(ROOT)))
    print_output(check)
    if check.returncode != 0:
        print("FAIL: clean ruff baseline did not pass check", file=sys.stderr)
        sys.exit(check.returncode or 1)
    fmt = run_ruff(binary, "format", "--check", str(CLEAN_BASELINE.relative_to(ROOT)))
    print_output(fmt)
    if fmt.returncode != 0:
        print("FAIL: clean ruff baseline did not pass format-check", file=sys.stderr)
        sys.exit(fmt.returncode or 1)
    print("ok: clean ruff baseline passed")


def check_scoped_repository(binary: str) -> None:
    missing = [tree for tree in SCOPED_TREES if not (ROOT / tree).is_dir()]
    if missing:
        print(f"FAIL: scoped Ruff trees missing: {missing}", file=sys.stderr)
        sys.exit(1)
    check = run_ruff(binary, "check", "--no-cache", *SCOPED_TREES)
    print_output(check)
    if check.returncode != 0:
        print("FAIL: scoped repository ruff check did not exit 0", file=sys.stderr)
        sys.exit(check.returncode or 1)
    print("ok: scoped repository ruff check exited 0")
    fmt = run_ruff(binary, "format", "--check", *SCOPED_TREES)
    print_output(fmt)
    if fmt.returncode != 0:
        print("FAIL: scoped repository ruff format-check did not exit 0", file=sys.stderr)
        sys.exit(fmt.returncode or 1)
    print("ok: scoped repository ruff format-check exited 0")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo"),
        default="all",
    )
    args = parser.parse_args()
    check_config_reasons()
    binary = find_ruff()
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
        check_scoped_repository(binary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
