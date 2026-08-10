#!/usr/bin/env python3
"""Coherence guard: compare docs markdown counts to the canonical xlsx model.

Canonical source:
  archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx
  (Consolidated Mapping sheet: unique BG / US / NFR-US / FR / NFR)

Also verifies archive/canonical-requirements.csv against workbook
requirement_id, story_id, and scope triples.

Runnable locally:
  python scripts/check_coherence.py
  # or: sh scripts/check-coherence.sh
"""

from __future__ import annotations

import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "archive" / "Quantic_Project_Consolidated_Coherence_Validated.xlsx"
CSV_EXPORT = ROOT / "archive" / "canonical-requirements.csv"
BG_MD = ROOT / "docs" / "02-business-analysis" / "business-goals-epics-stories.md"
REQ_MD = ROOT / "docs" / "02-business-analysis" / "requirements.md"
TRACE_MD = ROOT / "implementations" / "florist" / "requirements" / "traceability-matrix.md"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXPECTED = {
    "BG": 7,
    "US": 23,
    "NFR-US": 17,
    "FR": 23,
    "NFR": 17,
}


def expected_ids(kind: str, count: int) -> set[str]:
    return {f"{kind}-{number:03d}" for number in range(1, count + 1)}


def _shared_strings(zf: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for si in root.findall("m:si", NS):
        texts = [
            (t.text or "")
            for t in si.iter(
                "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
            )
        ]
        strings.append("".join(texts))
    return strings


def _sheet_rows(zf: zipfile.ZipFile, sheet_path: str, strings: list[str]) -> list[dict[str, str]]:
    root = ET.fromstring(zf.read(sheet_path))
    rows: list[dict[str, str]] = []
    for row in root.findall("m:sheetData/m:row", NS):
        cells: dict[str, str] = {}
        for c in row.findall("m:c", NS):
            ref = c.attrib["r"]
            col = re.match(r"[A-Z]+", ref)
            if col is None:
                continue
            node = c.find("m:v", NS)
            if node is None:
                continue
            val = node.text or ""
            if c.attrib.get("t") == "s":
                val = strings[int(val)]
            cells[col.group(0)] = val
        rows.append(cells)
    return rows


def _workbook_sheet_paths(zf: zipfile.ZipFile) -> dict[str, str]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    rid_to_target = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("r:Relationship", rel_ns)
    }
    sheets: dict[str, str] = {}
    for sheet in wb.findall("m:sheets/m:sheet", NS):
        name = sheet.attrib["name"]
        rid = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        target = rid_to_target[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        sheets[name] = target
    return sheets


def ids_from_xlsx(path: Path) -> dict[str, set[str]]:
    with zipfile.ZipFile(path) as zf:
        strings = _shared_strings(zf)
        sheets = _workbook_sheet_paths(zf)
        mapping = sheets["Consolidated Mapping"]
        rows = _sheet_rows(zf, mapping, strings)

    buckets = {
        "BG": set(),
        "US": set(),
        "NFR-US": set(),
        "FR": set(),
        "NFR": set(),
    }
    for row in rows[1:]:
        for value in row.values():
            if re.fullmatch(r"BG-\d+", value):
                buckets["BG"].add(value)
            elif re.fullmatch(r"US-\d+", value):
                buckets["US"].add(value)
            elif re.fullmatch(r"NFR-US-\d+", value):
                buckets["NFR-US"].add(value)
            elif re.fullmatch(r"FR-\d+", value):
                buckets["FR"].add(value)
            elif re.fullmatch(r"NFR-\d+", value):
                buckets["NFR"].add(value)
    return buckets


def ids_from_markdown() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    bg_text = BG_MD.read_text(encoding="utf-8")
    req_text = REQ_MD.read_text(encoding="utf-8")
    inventories = {
        "BG": re.findall(r"^\| (BG-\d+)", bg_text, flags=re.M),
        "US": re.findall(r"^\| (US-\d+)", bg_text, flags=re.M),
        "NFR-US": re.findall(r"^\| (NFR-US-\d+)", bg_text, flags=re.M),
        "FR": re.findall(r"^\| (FR-\d+)", req_text, flags=re.M),
        "NFR": re.findall(r"^\| (NFR-\d+)", req_text, flags=re.M),
    }
    trace_text = TRACE_MD.read_text(encoding="utf-8")
    trace = {
        "US": re.findall(r"^\| BG-\d+ \| EP-\d+ \| (US-\d+) \| FR-\d+ \|", trace_text, flags=re.M),
        "NFR-US": re.findall(r"^\| BG-\d+ \| EP-\d+ \| (NFR-US-\d+) \| NFR-\d+ \|", trace_text, flags=re.M),
        "FR": re.findall(r"^\| BG-\d+ \| EP-\d+ \| US-\d+ \| (FR-\d+) \|", trace_text, flags=re.M),
        "NFR": re.findall(r"^\| BG-\d+ \| EP-\d+ \| NFR-US-\d+ \| (NFR-\d+) \|", trace_text, flags=re.M),
    }
    return inventories, trace


def requirement_triples_from_xlsx(path: Path) -> dict[str, tuple[str, str]]:
    """Map requirement_id -> (story_id, scope) from Consolidated Mapping."""
    with zipfile.ZipFile(path) as zf:
        strings = _shared_strings(zf)
        sheets = _workbook_sheet_paths(zf)
        rows = _sheet_rows(zf, sheets["Consolidated Mapping"], strings)

    triples: dict[str, tuple[str, str]] = {}
    for row in rows[1:]:
        story = row.get("F", "").strip()
        req = row.get("I", "").strip()
        scope = row.get("L", "").strip()
        if not (req and story and scope):
            continue
        triples[req] = (story, scope)
    return triples


def requirement_triples_from_csv(path: Path) -> dict[str, tuple[str, str]]:
    """Map requirement_id -> (story_id, scope) from canonical CSV export."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = {"requirement_id", "story_id", "scope"}
        if reader.fieldnames is None or set(reader.fieldnames) != expected:
            raise ValueError(
                f"CSV header must be exactly {sorted(expected)}, got {reader.fieldnames!r}"
            )
        triples: dict[str, tuple[str, str]] = {}
        for row in reader:
            req = (row.get("requirement_id") or "").strip()
            story = (row.get("story_id") or "").strip()
            scope = (row.get("scope") or "").strip()
            if not (req and story and scope):
                continue
            triples[req] = (story, scope)
    return triples


def main() -> int:
    if not XLSX.is_file():
        print(f"FAIL: missing canonical workbook {XLSX.relative_to(ROOT)}")
        return 1

    xlsx_ids = ids_from_xlsx(XLSX)
    md_ids, trace_ids = ids_from_markdown()
    fail = 0

    print("Canonical workbook (Consolidated Mapping unique IDs):")
    for key, expected in EXPECTED.items():
        expected_set = expected_ids(key, expected)
        actual_set = xlsx_ids[key]
        status = "ok" if actual_set == expected_set else "FAIL"
        if actual_set != expected_set:
            fail = 1
        print(f"  {status}: xlsx {key} IDs = {len(actual_set)} (expected exact 001..{expected:03d})")

    print("Markdown docs:")
    for key, expected in EXPECTED.items():
        actual = md_ids[key]
        expected_set = expected_ids(key, expected)
        status = "ok" if set(actual) == expected_set and len(actual) == len(set(actual)) else "FAIL"
        if status == "FAIL":
            fail = 1
        print(f"  {status}: docs {key} rows = {len(actual)}; unique IDs = {len(set(actual))}")

    print("Docs vs workbook:")
    for key in EXPECTED:
        if set(md_ids[key]) != xlsx_ids[key]:
            print(f"  FAIL: {key} docs and xlsx ID sets differ")
            fail = 1
        else:
            print(f"  ok:   {key} docs ID set == xlsx ID set")

    print("Traceability matrix vs published requirements:")
    for key in ("US", "NFR-US", "FR", "NFR"):
        if len(trace_ids[key]) != len(set(trace_ids[key])) or set(trace_ids[key]) != set(md_ids[key]):
            print(f"  FAIL: {key} traceability rows are missing, duplicated, or divergent")
            fail = 1
        else:
            print(f"  ok:   {key} traceability IDs match published requirements")

    print("Canonical CSV vs workbook:")
    if not CSV_EXPORT.is_file():
        print(f"  FAIL: missing CSV export {CSV_EXPORT.relative_to(ROOT)}")
        fail = 1
    else:
        try:
            xlsx_triples = requirement_triples_from_xlsx(XLSX)
            csv_triples = requirement_triples_from_csv(CSV_EXPORT)
        except ValueError as exc:
            print(f"  FAIL: {exc}")
            fail = 1
        else:
            if xlsx_triples != csv_triples:
                print("  FAIL: canonical-requirements.csv drifts from Consolidated Mapping")
                missing = sorted(set(xlsx_triples) - set(csv_triples))
                extra = sorted(set(csv_triples) - set(xlsx_triples))
                mismatched = sorted(
                    req
                    for req in set(xlsx_triples) & set(csv_triples)
                    if xlsx_triples[req] != csv_triples[req]
                )
                if missing[:5]:
                    print(f"    missing in CSV (sample): {missing[:5]}")
                if extra[:5]:
                    print(f"    extra in CSV (sample): {extra[:5]}")
                if mismatched[:5]:
                    print(f"    mismatched triples (sample): {mismatched[:5]}")
                fail = 1
            else:
                print(f"  ok:   {len(csv_triples)} CSV requirement triples match workbook")

    if fail:
        print("Coherence guard FAILED - docs diverge from the canonical xlsx model.")
        return 1

    print("Coherence guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
