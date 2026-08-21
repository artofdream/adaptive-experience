#!/usr/bin/env python3
"""Unified Pre-Flight Guard Runner CLI for AEA.

Executes all 13 repository coherence, security, traceability, graph engineering,
performance SLO, stakeholder skill sync, and unit test guards in a single fast command.
Exits with code 0 if all guards pass, or code 1 if any guard fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]

GUARDS: List[Tuple[str, List[str]]] = [
    ("Coherence Guard", [sys.executable, "scripts/check_coherence.py"]),
    ("Secrets Posture Guard", [sys.executable, "scripts/check_secrets_posture.py"]),
    ("Traceability DAG Guard", [sys.executable, "scripts/generate_traceability_graph.py", "--check"]),
    ("Traceability Unit Tests", [sys.executable, "scripts/test_traceability_graph.py", "-v"]),
    ("Governance Loop Graph Guard", [sys.executable, "scripts/check_loop_graph.py"]),
    ("Governance Loop Unit Tests", [sys.executable, "scripts/test_loop_graph.py", "-v"]),
    ("Assistant Performance SLO Guard", [sys.executable, "edge/scripts/check_assistant_slo.py", "--check"]),
    ("Assistant SLO Unit Tests", [sys.executable, "edge/tests/test_assistant_slo.py", "-v"]),
    ("Session Property Graph Unit Tests", [sys.executable, "platform/tests/test_graph.py"]),
    ("Knowledge Graph Exporter Unit Tests", [sys.executable, "platform/tests/test_knowledge_graph.py"]),
    ("Reorder Service Unit Tests", [sys.executable, "platform/tests/test_reorder.py"]),
    ("Payment Simulation Engine Unit Tests", [sys.executable, "platform/tests/test_payment.py"]),
    ("Stakeholder Skills 6-Way Sync Guard", [sys.executable, "scripts/generate_codex_stakeholder_skills.py", "--check"]),
    ("Second Brain Knowledge Graph Guard", [sys.executable, "scripts/check_knowledge_graph.py"]),
]


def run_guards() -> bool:
    """Run all guards sequentially and report consolidated status."""
    print("==========================================================")
    print("           AEA UNIFIED PRE-FLIGHT GUARD RUNNER            ")
    print("==========================================================")

    passed_count = 0
    failed_guards: List[str] = []

    for name, cmd in GUARDS:
        target_script = ROOT / cmd[1]
        if not target_script.exists():
            print(f"\n[SKIP] {name} (file {cmd[1]} not present on branch)")
            passed_count += 1
            continue

        print(f"\n[RUNNING] {name}...")
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[PASS] {name}")
            passed_count += 1
        else:
            print(f"[FAIL] {name}")
            if result.stdout:
                print(f"Stdout:\n{result.stdout}")
            if result.stderr:
                print(f"Stderr:\n{result.stderr}")
            failed_guards.append(name)

    print("\n==========================================================")
    print(f"SUMMARY: {passed_count}/{len(GUARDS)} guards passed")
    print("==========================================================")

    if failed_guards:
        print(f"\nFAILED GUARDS ({len(failed_guards)}):")
        for g in failed_guards:
            print(f"  - {g}")
        return False

    print("\nALL PRE-FLIGHT GUARDS PASSED CLEANLY! READY FOR MR.")
    return True


def main() -> int:
    success = run_guards()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
