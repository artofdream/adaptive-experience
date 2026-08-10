#!/usr/bin/env python3
"""Coherence guard: compare docs markdown counts to the canonical xlsx model.

Canonical source:
  archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx
  (Consolidated Mapping sheet: unique BG / US / NFR-US / FR / NFR)

Runnable locally:
  python scripts/check_coherence.py
  # or: sh scripts/check-coherence.sh
"""

from __future__ import annotations

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "archive" / "Quantic_Project_Consolidated_Coherence_Validated.xlsx"
BG_MD = ROOT / "docs" / "02-business-analysis" / "business-goals-epics-stories.md"
REQ_MD = ROOT / "docs" / "02-business-analysis" / "requirements.md"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXPECTED = {
    "BG": 7,
    "US": 23,
    "NFR-US": 17,
    "FR": 23,
    "NFR": 17,
}


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


def counts_from_xlsx(path: Path) -> dict[str, int]:
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
    return {key: len(values) for key, values in buckets.items()}


def counts_from_markdown() -> dict[str, int]:
    bg_text = BG_MD.read_text(encoding="utf-8")
    req_text = REQ_MD.read_text(encoding="utf-8")
    return {
        "BG": len(re.findall(r"^\| BG-", bg_text, flags=re.M)),
        "US": len(re.findall(r"^\| US-\d", bg_text, flags=re.M)),
        "NFR-US": len(re.findall(r"^\| NFR-US-", bg_text, flags=re.M)),
        "FR": len(re.findall(r"^\| FR-\d", req_text, flags=re.M)),
        "NFR": len(re.findall(r"^\| NFR-\d", req_text, flags=re.M)),
    }


def main() -> int:
    if not XLSX.is_file():
        print(f"FAIL: missing canonical workbook {XLSX.relative_to(ROOT)}")
        return 1

    xlsx = counts_from_xlsx(XLSX)
    md = counts_from_markdown()
    fail = 0

    print("Canonical workbook (Consolidated Mapping unique IDs):")
    for key, expected in EXPECTED.items():
        actual = xlsx[key]
        status = "ok" if actual == expected else "FAIL"
        if actual != expected:
            fail = 1
        print(f"  {status}: xlsx {key} = {actual} (expected {expected})")

    print("Markdown docs:")
    for key, expected in EXPECTED.items():
        actual = md[key]
        status = "ok" if actual == expected else "FAIL"
        if actual != expected:
            fail = 1
        print(f"  {status}: docs {key} = {actual} (expected {expected})")

    print("Docs vs workbook:")
    for key in EXPECTED:
        if md[key] != xlsx[key]:
            print(f"  FAIL: {key} docs={md[key]} xlsx={xlsx[key]}")
            fail = 1
        else:
            print(f"  ok:   {key} docs == xlsx ({md[key]})")

    if fail:
        print("Coherence guard FAILED - docs diverge from the canonical xlsx model.")
        return 1

    print("Coherence guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
