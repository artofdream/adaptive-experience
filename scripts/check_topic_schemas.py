#!/usr/bin/env python3
"""Verify MVP topic JSON Schema files match topic-contracts.md (ADR-008 / CF-021)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs" / "04-technical-architecture" / "topic-contracts.md"
SCHEMAS = ROOT / "docs" / "04-technical-architecture" / "schemas"

# MVP table rows: | topic | version | owner | subscribers | payload |
ROW = re.compile(
    r"^\|\s*([a-z0-9_.]+)\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)\s*\|",
    re.MULTILINE,
)


def mvp_topics() -> list[tuple[str, str]]:
    text = CONTRACTS.read_text(encoding="utf-8")
    # Stop before Future topics section
    cut = text.find("## Future topics")
    body = text if cut < 0 else text[:cut]
    return [(m.group(1), m.group(2)) for m in ROW.finditer(body)]


def schema_path(topic: str, version: str) -> Path:
    return SCHEMAS / f"{topic}.v{version}.json"


def main() -> int:
    topics = mvp_topics()
    if len(topics) != 21:
        print(f"FAIL: expected 21 MVP topics, found {len(topics)}", file=sys.stderr)
        return 1

    missing: list[str] = []
    invalid: list[str] = []
    for topic, version in topics:
        path = schema_path(topic, version)
        if not path.is_file():
            missing.append(path.name)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            invalid.append(f"{path.name}: {exc}")
            continue
        if data.get("type") != "object":
            invalid.append(f"{path.name}: root type must be object")

    if missing or invalid:
        for name in missing:
            print(f"FAIL: missing schema {name}", file=sys.stderr)
        for msg in invalid:
            print(f"FAIL: {msg}", file=sys.stderr)
        return 1

    print(f"ok: {len(topics)} MVP topic schemas present under schemas/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
