"""Generate or verify the explicit FR/NFR evidence inventory."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "docs" / "02-business-analysis" / "requirements.md"
OUTPUT = ROOT / "docs" / "08-traceability" / "requirement-evidence.json"
ROW_RE = re.compile(r"^\|\s*((?:NFR-)?FR-\d{3}|NFR-\d{3})\s*\|[^|]*\|[^|]*\|\s*(MVP|Future)\s*\|", re.MULTILINE)
ID_RE = re.compile(r"\b(?:FR|NFR)-\d{3}\b")
SOURCE_SUFFIXES = {".py", ".js", ".html", ".sql"}


def canonical_requirements() -> dict[str, str]:
    return dict(ROW_RE.findall(REQUIREMENTS.read_text(encoding="utf-8")))


def cited_paths(root: Path, req_id: str, tests: bool) -> list[str]:
    paths = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        is_test = "tests" in path.parts or path.name.startswith("test_")
        if is_test != tests:
            continue
        if req_id in ID_RE.findall(path.read_text(encoding="utf-8", errors="ignore")):
            paths.append(path.relative_to(ROOT).as_posix())
    return paths


def adr_related_ids(text: str) -> set[str]:
    """Parse only the labeled Related requirements field and continuations."""
    captured: list[str] = []
    collecting = False
    for line in text.splitlines():
        if line.startswith("Related requirements:"):
            collecting = True
            captured.append(line.split(":", 1)[1])
            continue
        if not collecting:
            continue
        stripped = line.strip()
        if (not stripped or stripped.startswith("(") or
                re.match(r"^[A-Z][A-Za-z /-]+:\s*", stripped)):
            break
        captured.append(stripped)
    return set(ID_RE.findall("\n".join(captured)))


def adr_paths(req_id: str) -> list[str]:
    paths = []
    for path in sorted((ROOT / "docs" / "06-adr").glob("ADR-*.md")):
        if req_id in adr_related_ids(path.read_text(encoding="utf-8")):
            paths.append(path.relative_to(ROOT).as_posix())
    return paths


def evidence(paths: list[str], empty_disposition: str) -> dict:
    return {"disposition": "evidenced" if paths else empty_disposition, "paths": paths}


def build() -> dict:
    records = []
    for req_id, scope in sorted(canonical_requirements().items()):
        implementation = cited_paths(ROOT / "platform", req_id, False)
        implementation += cited_paths(ROOT / "edge", req_id, False)
        tests = cited_paths(ROOT / "platform", req_id, True)
        tests += cited_paths(ROOT / "edge", req_id, True)
        empty = "planned" if scope == "Future" else "unclaimed"
        records.append({
            "requirement_id": req_id,
            "scope": scope,
            "adr": evidence(adr_paths(req_id), "unclaimed"),
            "implementation": evidence(sorted(set(implementation)), empty),
            "test": evidence(sorted(set(tests)), empty),
        })
    return {
        "schema_version": 1,
        "meaning": "Citation evidence only; a citation does not by itself prove behavior.",
        "records": records,
    }


def rendered() -> str:
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = rendered()
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if actual.replace("\r\n", "\n") != expected:
            raise SystemExit("requirement evidence inventory is stale; run `python scripts/generate_requirement_evidence.py`")
        print(f"ok: {len(build()['records'])} requirement evidence records are current")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
