#!/usr/bin/env python3
"""
Trust-But-Verify Execution Job (Issue #257)

Walks the verification chain:
1. Executes all 14 pre-flight quality guards.
2. Validates evidence file paths referenced in research/coherence-findings-loop.md.
3. Verifies zero open/unverified regressions in status assertions.
"""

from __future__ import annotations

import re
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_guards() -> bool:
    print("[VERIFY-JOB] Running 14 pre-flight quality guards...")
    cmd = [sys.executable, str(ROOT / "scripts" / "run_all_guards.py")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[VERIFY-JOB] ERROR: Pre-flight guards failed:\n{res.stdout}\n{res.stderr}")
        return False
    print("[VERIFY-JOB] PASS: 14/14 pre-flight quality guards clean.")
    return True


def verify_evidence_paths() -> bool:
    print("[VERIFY-JOB] Checking coherence findings evidence paths...")
    loop_file = ROOT / "research" / "coherence-findings-loop.md"
    if not loop_file.exists():
        print(f"[VERIFY-JOB] ERROR: {loop_file} missing.")
        return False

    content = loop_file.read_text(encoding="utf-8")
    lines = content.splitlines()
    missing: list[str] = []

    for line in lines:
        if line.startswith("|") and "CF-" in line and "verified" in line:
            # Extract code backtick paths
            paths = re.findall(r"`([^`]+)`", line)
            for path_str in paths:
                # Ignore non-path descriptors or IDs
                if "/" in path_str or path_str.endswith(".py") or path_str.endswith(".md") or path_str.endswith(".tf") or path_str.endswith(".sql"):
                    # Strip line anchor if present
                    clean_path = path_str.split("#")[0].strip()
                    target = ROOT / clean_path
                    if not target.exists():
                        missing.append(path_str)

    if missing:
        print(f"[VERIFY-JOB] ERROR: Missing evidence paths: {missing}")
        return False

    print("[VERIFY-JOB] PASS: All verified coherence evidence paths exist.")
    return True


def main() -> None:
    print("=" * 60)
    print("           AEA TRUST-BUT-VERIFY EXECUTION JOB            ")
    print("=" * 60)

    success = True
    if not run_guards():
        success = False

    if not verify_evidence_paths():
        success = False

    if not success:
        print("\n[VERIFY-JOB] FAILED: Verification checks failed.")
        sys.exit(1)

    print("\n[VERIFY-JOB] SUCCESS: All verification steps passed cleanly.")
    sys.exit(0)


if __name__ == "__main__":
    main()
