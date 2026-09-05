#!/usr/bin/env python3
"""Run the pinned Bandit Python SAST gate (#328)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "bandit.yaml"
PINNED_PACKAGE = "bandit==1.9.4"
FIXTURES = ROOT / "scripts" / "fixtures" / "sast"
KNOWN_BAD = FIXTURES / "known_bad.py"
CLEAN_BASELINE = FIXTURES / "clean_baseline.py"
SCOPED_TREES = ("scripts", "platform", "edge")
REPORT = ROOT / "bandit-report.json"
HIGH = "HIGH"
KNOWN_BAD_TEST_ID = "B602"

# Every exclude_dirs entry in bandit.yaml must have a reason here.
# Do not add a path to silence an unclassified High finding.
EXCLUDE_REASONS = {
    "scripts/fixtures/sast": (
        "Gate fixtures. Known-bad must fail when invoked explicitly; it is not part of the repository baseline."
    ),
}

# Every skips entry in bandit.yaml must have a reason here.
# This baseline skips no High test IDs.
SKIP_REASONS: dict[str, str] = {}


def find_bandit() -> str:
    binary = shutil.which("bandit")
    if not binary:
        print(
            f"FAIL: bandit is not on PATH. Install the pinned CLI: pip install {PINNED_PACKAGE}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def run_bandit(binary: str, *args: str) -> subprocess.CompletedProcess[str]:
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


def parse_yaml_str_list(text: str, key: str) -> list[str]:
    """Parse a block or empty YAML list for one top-level key."""
    lines = text.splitlines()
    values: list[str] = []
    in_key = False
    for raw in lines:
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped.strip():
            continue
        if stripped.startswith(f"{key}:"):
            rest = stripped.split(":", 1)[1].strip()
            in_key = True
            if rest in {"", "[]"}:
                continue
            raise ValueError(f"bandit.yaml {key} must be a block list or []")
        if in_key:
            item = stripped.strip()
            if item.startswith("- "):
                values.append(item[2:].strip().strip("'\""))
                continue
            if not raw.startswith((" ", "\t")):
                break
            raise ValueError(f"bandit.yaml {key} has an unsupported line: {raw}")
    return values


def load_config() -> dict[str, list[str]]:
    text = CONFIG.read_text(encoding="utf-8")
    return {
        "exclude_dirs": parse_yaml_str_list(text, "exclude_dirs"),
        "skips": parse_yaml_str_list(text, "skips"),
    }


def check_config_reasons() -> None:
    if not CONFIG.is_file():
        print("FAIL: bandit.yaml is missing", file=sys.stderr)
        sys.exit(1)
    config = load_config()
    excludes = list(config["exclude_dirs"])
    skips = list(config["skips"])
    missing = [pattern for pattern in excludes if pattern not in EXCLUDE_REASONS]
    extra = [pattern for pattern in EXCLUDE_REASONS if pattern not in excludes]
    if missing or extra:
        print("FAIL: bandit.yaml exclude_dirs and EXCLUDE_REASONS drifted", file=sys.stderr)
        for pattern in missing:
            print(f"  undocumented exclude: {pattern}", file=sys.stderr)
        for pattern in extra:
            print(f"  unused reason: {pattern}", file=sys.stderr)
        sys.exit(1)
    missing_skips = [test_id for test_id in skips if test_id not in SKIP_REASONS]
    extra_skips = [test_id for test_id in SKIP_REASONS if test_id not in skips]
    if missing_skips or extra_skips:
        print("FAIL: bandit.yaml skips and SKIP_REASONS drifted", file=sys.stderr)
        for test_id in missing_skips:
            print(f"  undocumented skip: {test_id}", file=sys.stderr)
        for test_id in extra_skips:
            print(f"  unused skip reason: {test_id}", file=sys.stderr)
        sys.exit(1)
    if skips:
        print(
            "FAIL: #328 baseline skips no High test IDs. Broader skips belong in a later slice.",
            file=sys.stderr,
        )
        sys.exit(1)


def load_results(payload: str) -> list[dict[str, object]]:
    data = json.loads(payload)
    results = data.get("results", [])
    if not isinstance(results, list):
        raise ValueError("bandit JSON results must be a list")
    return [item for item in results if isinstance(item, dict)]


def high_findings(results: list[dict[str, object]]) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    for item in results:
        severity = str(item.get("issue_severity", "")).upper()
        if severity == HIGH:
            found.append(item)
    return found


def summarize_high(results: list[dict[str, object]]) -> None:
    for item in results:
        test_id = item.get("test_id", "?")
        path = item.get("filename", "?")
        line = item.get("line_number", "?")
        text = item.get("issue_text", "")
        print(f"  HIGH {test_id} {path}:{line} {text}", file=sys.stderr)


def prove_known_bad(binary: str) -> subprocess.CompletedProcess[str]:
    result = run_bandit(
        binary,
        "-q",
        "-f",
        "json",
        str(KNOWN_BAD.relative_to(ROOT)),
    )
    print_output(result)
    if result.returncode not in {0, 1}:
        print("FAIL: bandit crashed on the known-bad fixture", file=sys.stderr)
        return result
    try:
        highs = high_findings(load_results(result.stdout))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: known-bad bandit JSON was unreadable: {exc}", file=sys.stderr)
        result.returncode = 1
        return result
    test_ids = {str(item.get("test_id", "")) for item in highs}
    if not highs or KNOWN_BAD_TEST_ID not in test_ids:
        print("FAIL: known-bad SAST fixture unexpectedly passed High", file=sys.stderr)
        result.returncode = 0
        return result
    print(f"ok: known-bad SAST fixture failed as expected ({KNOWN_BAD_TEST_ID})")
    result.returncode = 1
    return result


def prove_clean_baseline(binary: str) -> None:
    result = run_bandit(
        binary,
        "-q",
        "-f",
        "json",
        str(CLEAN_BASELINE.relative_to(ROOT)),
    )
    print_output(result)
    if result.returncode not in {0, 1}:
        print("FAIL: bandit crashed on the clean SAST baseline", file=sys.stderr)
        sys.exit(result.returncode or 1)
    try:
        highs = high_findings(load_results(result.stdout))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: clean SAST baseline JSON was unreadable: {exc}", file=sys.stderr)
        sys.exit(1)
    if highs:
        print("FAIL: clean SAST baseline produced High findings", file=sys.stderr)
        summarize_high(highs)
        sys.exit(1)
    print("ok: clean SAST baseline passed")


def write_report(payload: str) -> None:
    REPORT.write_text(payload if payload.endswith("\n") else payload + "\n", encoding="utf-8")
    print(f"ok: retained Bandit report {REPORT.relative_to(ROOT)}")


def check_scoped_repository(binary: str) -> None:
    missing = [tree for tree in SCOPED_TREES if not (ROOT / tree).is_dir()]
    if missing:
        print(f"FAIL: scoped SAST trees missing: {missing}", file=sys.stderr)
        sys.exit(1)
    result = run_bandit(
        binary,
        "-c",
        str(CONFIG.relative_to(ROOT)),
        "-q",
        "-f",
        "json",
        "-r",
        *SCOPED_TREES,
    )
    print_output(result)
    write_report(result.stdout or '{"results":[]}\n')
    if result.returncode not in {0, 1}:
        print("FAIL: scoped repository bandit scan crashed", file=sys.stderr)
        sys.exit(result.returncode or 1)
    try:
        results = load_results(result.stdout or '{"results":[]}')
        highs = high_findings(results)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: scoped repository bandit JSON was unreadable: {exc}", file=sys.stderr)
        sys.exit(1)
    if highs:
        print("FAIL: scoped repository bandit scan reported unaccepted High findings", file=sys.stderr)
        summarize_high(highs)
        sys.exit(1)
    print(
        f"ok: scoped repository bandit scan exited 0 for High "
        f"({len(results)} retained finding(s), 0 High)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo"),
        default="all",
    )
    args = parser.parse_args()
    check_config_reasons()
    binary = find_bandit()
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
