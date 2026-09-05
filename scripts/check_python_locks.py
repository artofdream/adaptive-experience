#!/usr/bin/env python3
"""Verify committed platform/edge Python locks and that installs consume them (#329)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compile_python_locks import INPUTS, check_locks, lock_path_for  # noqa: E402

CI = ROOT / ".gitlab-ci.yml"
CONSUMER_LOCKS = {
    ROOT / ".gitlab-ci.yml": ("platform/requirements.lock", "edge/requirements.lock"),
    ROOT / "platform" / "Dockerfile.orchestration": (
        "platform/requirements.lock",
        "edge/requirements.lock",
    ),
    ROOT / "edge" / "bff" / "Dockerfile": ("requirements.lock",),
    ROOT / ".cursor" / "install-cloud-agent.sh": (
        "platform/requirements.lock",
        "edge/requirements.lock",
    ),
    ROOT / "platform" / "README.md": ("platform/requirements.lock",),
}


def job_block(name: str) -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"{name} job missing from .gitlab-ci.yml")
    return match.group(0)


def consumer_errors() -> list[str]:
    errors: list[str] = []
    for requirements in INPUTS:
        input_rel = requirements.relative_to(ROOT).as_posix()
        lock_rel = lock_path_for(requirements).relative_to(ROOT).as_posix()
        if not requirements.is_file():
            errors.append(f"missing human-authored input: {input_rel}")
        if not lock_path_for(requirements).is_file():
            errors.append(f"missing lock: {lock_rel}")
    for consumer, needles in CONSUMER_LOCKS.items():
        rel = consumer.relative_to(ROOT).as_posix()
        if not consumer.is_file():
            errors.append(f"missing consumer: {rel}")
            continue
        text = consumer.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} does not consume {needle}")
    ci = CI.read_text(encoding="utf-8")
    if re.search(r"pip install -r platform/requirements\.txt\s*$", ci, re.M):
        errors.append("platform-foundation-integration installs unconstrained platform/requirements.txt")
    integration = job_block("platform-foundation-integration")
    if "-c platform/requirements.lock" not in integration:
        errors.append("platform-foundation-integration does not constrain with platform/requirements.lock")
    return errors


def ci_job_errors() -> list[str]:
    try:
        block = job_block("python-lock")
    except AssertionError as exc:
        return [str(exc)]
    errors: list[str] = []
    if "allow_failure:" in block:
        errors.append("python-lock must not set allow_failure")
    if "|| true" in block:
        errors.append("python-lock must not suppress failures")
    if "scripts/check_python_locks.py" not in block:
        errors.append("python-lock must run scripts/check_python_locks.py")
    if "scripts/test_python_locks.py" not in block:
        errors.append("python-lock must run scripts/test_python_locks.py")
    if "scripts/compile_python_locks.py --check" not in block:
        errors.append("python-lock must run unchanged regeneration via compile_python_locks.py --check")
    if "-c platform/requirements.lock" not in block or "-c edge/requirements.lock" not in block:
        errors.append("python-lock must fresh-install platform and edge under their locks")
    if "pip-audit" in block or "osv-scanner" in block or "safety check" in block:
        errors.append("python-lock must not stack #330 dependency SCA")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    errors = check_locks() + consumer_errors() + ci_job_errors()
    if errors:
        print("FAIL: Python lock gate (#329)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("ok: platform and edge Python locks are current and consumed by build/test installs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
