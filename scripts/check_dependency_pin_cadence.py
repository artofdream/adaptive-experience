#!/usr/bin/env python3
"""Validate the DSO+SSE dependency pin cadence ledger.

Monthly review procedure:
``.cursor/skills/aea-devsecops-platform/dependency-cadence.md``
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research" / "random-thoughts" / "dependency-pin-ledger.csv"
HEADERS = (
    "month",
    "reviewed",
    "dso_images",
    "sse_app",
    "collision",
    "notes",
)


def ledger_ok(path: Path = LEDGER) -> tuple[bool, str]:
    if not path.is_file():
        return False, "dependency-pin-ledger.csv missing"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(HEADERS):
            return False, "dependency-pin-ledger.csv header mismatch"
        rows = list(reader)
    if not rows:
        return False, "dependency-pin-ledger.csv has no review rows"
    last = rows[-1]
    try:
        datetime.strptime(last["reviewed"], "%Y-%m-%d")
        datetime.strptime(last["month"], "%Y-%m")
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"dependency-pin-ledger.csv bad dates: {exc}"
    collision = (last.get("collision") or "").strip().lower()
    if collision not in {"yes", "no", "skipped"}:
        return False, "collision must be yes, no, or skipped"
    return True, f"ok: {len(rows)} pin-cadence row(s), latest {last['month']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        print("need --check", file=sys.stderr)
        return 2
    ok, msg = ledger_ok()
    print(msg, file=sys.stderr if not ok else sys.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
