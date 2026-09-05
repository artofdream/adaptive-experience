#!/usr/bin/env python3
"""Run the pinned markdown-link-check gate (#326)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_PACKAGE = "markdown-link-check@3.15.0"
CONFIG = ROOT / ".mlc.json"
FIXTURES = ROOT / "scripts" / "fixtures" / "linkcheck"
KNOWN_BAD = FIXTURES / "known_bad.md"
CLEAN_BASELINE = FIXTURES / "clean_baseline.md"
PUBLISHED_GLOBS = (
    "docs/**/*.md",
    "implementations/**/*.md",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
)

# Every ignorePatterns.pattern in .mlc.json must have a reason here.
# Do not add a pattern to silence an unclassified failure.
IGNORE_REASONS = {
    "^https?://localhost(:[0-9]+)?(/|$)": (
        "Path A Compose URLs. The lint job has no edge stack, so localhost "
        "cannot be fetched."
    ),
    "^https?://127\\.0\\.0\\.1(:[0-9]+)?(/|$)": (
        "Loopback aliases of Path A Compose URLs. Same reason as localhost."
    ),
    "^file://": (
        "Laptop-absolute file URLs in published docs. CI cannot open a "
        "workstation path; repo-relative links remain checked."
    ),
    "^#": (
        "In-page heading fragments. Same class as markdownlint MD051: "
        "framework TOC slugs do not always match generated heading IDs. "
        "File targets are still checked after .html to .md rewrite."
    ),
}


def find_linkcheck() -> str:
    binary = shutil.which("markdown-link-check")
    if not binary:
        print(
            "FAIL: markdown-link-check is not on PATH. Install the pinned CLI: "
            f"npm install -g {PINNED_PACKAGE}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def published_markdown() -> list[Path]:
    files: set[Path] = set()
    for pattern in PUBLISHED_GLOBS:
        files.update(ROOT.glob(pattern))
    return sorted(path for path in files if path.is_file())


def run_linkcheck(binary: str, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [binary, "-c", str(CONFIG), str(path.relative_to(ROOT))],
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
    result = run_linkcheck(binary, KNOWN_BAD)
    print_output(result)
    if result.returncode == 0:
        print("FAIL: known-bad linkcheck fixture unexpectedly passed", file=sys.stderr)
    else:
        print("ok: known-bad linkcheck fixture failed as expected")
    return result


def prove_clean_baseline(binary: str) -> None:
    result = run_linkcheck(binary, CLEAN_BASELINE)
    print_output(result)
    if result.returncode != 0:
        print("FAIL: clean linkcheck baseline did not pass", file=sys.stderr)
        sys.exit(result.returncode or 1)
    print("ok: clean linkcheck baseline passed")


def check_config_reasons() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    patterns = [item["pattern"] for item in config.get("ignorePatterns", [])]
    missing = [pattern for pattern in patterns if pattern not in IGNORE_REASONS]
    extra = [pattern for pattern in IGNORE_REASONS if pattern not in patterns]
    if missing or extra:
        print("FAIL: .mlc.json ignorePatterns and IGNORE_REASONS drifted", file=sys.stderr)
        for pattern in missing:
            print(f"  undocumented ignore: {pattern}", file=sys.stderr)
        for pattern in extra:
            print(f"  unused reason: {pattern}", file=sys.stderr)
        sys.exit(1)


def check_scoped_repository(binary: str) -> None:
    files = published_markdown()
    if not files:
        print("FAIL: published markdown glob matched no files", file=sys.stderr)
        sys.exit(1)
    failed: list[Path] = []
    for path in files:
        result = run_linkcheck(binary, path)
        if result.returncode != 0:
            print(f"FAIL: {path.relative_to(ROOT)}", file=sys.stderr)
            print_output(result)
            failed.append(path)
    if failed:
        print(
            f"FAIL: scoped repository linkcheck failed for {len(failed)} file(s)",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"ok: scoped repository linkcheck exited 0 ({len(files)} files)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo"),
        default="all",
    )
    args = parser.parse_args()
    check_config_reasons()
    binary = find_linkcheck()
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
