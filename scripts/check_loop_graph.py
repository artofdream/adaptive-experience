#!/usr/bin/env python3
"""Governance Loop Network Guard: verify research/loop-graph.md nodes against repo scripts & CI jobs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP_GRAPH_MD = ROOT / "research" / "loop-graph.md"
GITLAB_CI_YML = ROOT / ".gitlab-ci.yml"


def load_loop_graph_scripts() -> set[str]:
    """Extract all script paths cited in research/loop-graph.md and normalize to repo-relative paths."""
    if not LOOP_GRAPH_MD.is_file():
        raise FileNotFoundError(f"Missing loop graph doc: {LOOP_GRAPH_MD}")

    content = LOOP_GRAPH_MD.read_text(encoding="utf-8")
    matches = re.findall(r"`([a-zA-Z0-9_\-\./]+\.py)`", content)
    normalized = set()

    for match in matches:
        if (ROOT / match).is_file():
            normalized.add(match)
        elif (ROOT / "scripts" / match).is_file():
            normalized.add(f"scripts/{match}")
        elif (ROOT / "edge" / "scripts" / match).is_file():
            normalized.add(f"edge/scripts/{match}")
        else:
            normalized.add(match)

    return normalized


def check_loop_graph_integrity() -> tuple[list[str], list[str]]:
    """Check that all script references in loop-graph.md exist and are referenced in CI or SOPs."""
    scripts = load_loop_graph_scripts()
    missing_files: list[str] = []
    uncovered_in_ci: list[str] = []

    ci_content = GITLAB_CI_YML.read_text(encoding="utf-8") if GITLAB_CI_YML.is_file() else ""

    for script in sorted(scripts):
        script_path = ROOT / script
        if not script_path.is_file():
            missing_files.append(script)
        # Check if python guard scripts are present in CI or runnable tools
        if script.startswith(("scripts/check_", "edge/scripts/check_")):
            script_name = Path(script).name
            if script_name not in ci_content:
                uncovered_in_ci.append(script)

    return missing_files, uncovered_in_ci


def main() -> int:
    missing_files, uncovered_in_ci = check_loop_graph_integrity()

    if missing_files:
        print("FAIL: The following scripts cited in research/loop-graph.md do not exist:", file=sys.stderr)
        for path in missing_files:
            print(f"  - {path}", file=sys.stderr)
        return 1

    if uncovered_in_ci:
        print("FAIL: The following guard scripts cited in research/loop-graph.md are missing from .gitlab-ci.yml:", file=sys.stderr)
        for path in uncovered_in_ci:
            print(f"  - {path}", file=sys.stderr)
        return 1

    print("ok: governance loop graph node references match existing repo scripts and CI jobs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
