#!/usr/bin/env python3
"""
AEA Repository Hygiene Maintenance Script
Executes local repository hygiene checks, cleans temporary scratch artifacts,
verifies git status, and validates the 14 pre-flight quality guards.
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SCRATCH_PATTERNS = [
    "*.tmp", "*.bak", "conv*.json", "sel*.json", "session*.json",
    "served-app.js", "ws*.json", "Untitled.base"
]

def clean_scratch_files():
    print("[CLEAN] [1/4] Cleaning temporary scratch artifacts...")
    cleaned = 0
    for pattern in SCRATCH_PATTERNS:
        for file in REPO_ROOT.glob(pattern):
            try:
                file.unlink()
                cleaned += 1
                print(f"   Removed: {file.name}")
            except Exception as e:
                print(f"   Warning: Could not remove {file.name}: {e}")
    if cleaned == 0:
        print("   No temporary scratch files found.")


def check_git_status():
    print("\n[GIT] [2/4] Checking Git working tree cleanliness...")
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO_ROOT)
    if result.stdout.strip():
        print("   [WARNING] Working tree has unstaged/untracked changes:")
        for line in result.stdout.strip().splitlines():
            print(f"      {line}")
    else:
        print("   [PASS] Working tree is 100% clean.")

def run_coherence_and_guards():
    print("\n[GUARDS] [3/4] Running pre-flight quality guards...")
    res = subprocess.run([sys.executable, "scripts/run_all_guards.py"], cwd=REPO_ROOT)
    if res.returncode != 0:
        print("   [FAIL] Pre-flight quality guards failed!")
        sys.exit(1)

def update_daily_brief():
    print("\n[BRIEF] [4/4] Regenerating daily brief...")
    res = subprocess.run([sys.executable, "scripts/generate_daily_brief.py"], cwd=REPO_ROOT)
    if res.returncode == 0:
        print("   [PASS] Daily brief updated successfully.")

def main():
    print("==========================================================")
    print("           AEA REPOSITORY HYGIENE RUNNER                  ")
    print("==========================================================")
    clean_scratch_files()
    check_git_status()
    run_coherence_and_guards()
    update_daily_brief()
    print("\n==========================================================")
    print("   [PASS] REPOSITORY HYGIENE CHECK COMPLETE & PRISTINE    ")
    print("==========================================================")

if __name__ == "__main__":
    main()
