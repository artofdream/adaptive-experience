"""Validate the committed FR/NFR ADR, implementation, and test evidence inventory."""

import json
import re
import sys

from generate_requirement_evidence import (
    OUTPUT,
    ROOT,
    adr_related_ids,
    canonical_requirements,
)

ID_RE = re.compile(r"\b(?:FR|NFR)-\d{3}\b")
KINDS = ("adr", "implementation", "test")
DISPOSITIONS = {"evidenced", "planned", "not-applicable", "unclaimed"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    canonical = canonical_requirements()
    records = data.get("records", [])
    by_id = {record.get("requirement_id"): record for record in records}
    if set(by_id) != set(canonical):
        errors.append(f"inventory mismatch: missing={sorted(set(canonical) - set(by_id))}, extra={sorted(set(by_id) - set(canonical))}")
    if len(by_id) != len(records):
        errors.append("duplicate requirement IDs in evidence inventory")
    for req_id, record in by_id.items():
        if req_id not in canonical:
            continue
        if record.get("scope") != canonical[req_id]:
            errors.append(f"{req_id}: scope differs from canonical requirements")
        for kind in KINDS:
            claim = record.get(kind, {})
            disposition = claim.get("disposition")
            paths = claim.get("paths", [])
            if disposition not in DISPOSITIONS:
                errors.append(f"{req_id}/{kind}: invalid disposition {disposition!r}")
                continue
            if disposition == "evidenced" and not paths:
                errors.append(f"{req_id}/{kind}: evidenced requires at least one path")
            if disposition != "evidenced" and paths:
                errors.append(f"{req_id}/{kind}: {disposition} must not claim paths")
            for relative in paths:
                path = ROOT / relative
                if not path.is_file():
                    errors.append(f"{req_id}/{kind}: missing path {relative}")
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if req_id not in ID_RE.findall(text):
                    errors.append(f"{req_id}/{kind}: {relative} does not cite {req_id}")
                if kind == "adr":
                    if req_id not in adr_related_ids(text):
                        errors.append(f"{req_id}/adr: {relative} does not declare it in Related requirements")
    return errors


def main() -> None:
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    errors = validate(data)
    records = data.get("records", [])
    for kind in KINDS:
        counts = {value: 0 for value in DISPOSITIONS}
        for record in records:
            value = record.get(kind, {}).get("disposition")
            if value in counts:
                counts[value] += 1
        print(f"{kind}: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    if errors:
        print("EVIDENCE INVENTORY ERRORS:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print(f"ok: {len(records)} canonical requirement evidence dispositions are valid")


if __name__ == "__main__":
    main()
