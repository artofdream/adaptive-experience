#!/usr/bin/env python3
"""Coherence guard: compare docs markdown to the canonical xlsx model.

Canonical source:
  archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx
  (Consolidated Mapping sheet: unique BG / US / NFR-US / FR / NFR,
   plus BG→EP→US/NFR-US→FR/NFR chains and MVP/Future scope)

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
TRACE_MD = ROOT / "implementations" / "florist" / "requirements" / "traceability-matrix.md"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXPECTED = {
    "BG": 7,
    "US": 23,
    "NFR-US": 17,
    "FR": 23,
    "NFR": 17,
}
EXPECTED_EP = 7


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


def mapping_rows_from_xlsx(path: Path) -> list[dict[str, str]]:
    """Return Consolidated Mapping data rows as BG/EP/story/req/scope dicts."""
    with zipfile.ZipFile(path) as zf:
        strings = _shared_strings(zf)
        sheets = _workbook_sheet_paths(zf)
        mapping = sheets["Consolidated Mapping"]
        rows = _sheet_rows(zf, mapping, strings)

    parsed: list[dict[str, str]] = []
    for row in rows[1:]:
        bg = row.get("A", "").strip()
        ep = row.get("C", "").strip()
        story = row.get("F", "").strip()
        req = row.get("I", "").strip()
        scope = row.get("L", "").strip()
        if not (bg and ep and story and req and scope):
            continue
        parsed.append(
            {
                "bg": bg,
                "ep": ep,
                "story": story,
                "req": req,
                "scope": scope,
            }
        )
    return parsed


def ids_from_mapping(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    buckets = {
        "BG": set(),
        "EP": set(),
        "US": set(),
        "NFR-US": set(),
        "FR": set(),
        "NFR": set(),
    }
    for row in rows:
        buckets["BG"].add(row["bg"])
        buckets["EP"].add(row["ep"])
        if row["story"].startswith("NFR-US-"):
            buckets["NFR-US"].add(row["story"])
        elif row["story"].startswith("US-"):
            buckets["US"].add(row["story"])
        if row["req"].startswith("NFR-"):
            buckets["NFR"].add(row["req"])
        elif row["req"].startswith("FR-"):
            buckets["FR"].add(row["req"])
    return buckets


def chain_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["bg"], row["ep"], row["story"], row["req"])


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
        "NFR-US": re.findall(
            r"^\| BG-\d+ \| EP-\d+ \| (NFR-US-\d+) \| NFR-\d+ \|", trace_text, flags=re.M
        ),
        "FR": re.findall(r"^\| BG-\d+ \| EP-\d+ \| US-\d+ \| (FR-\d+) \|", trace_text, flags=re.M),
        "NFR": re.findall(
            r"^\| BG-\d+ \| EP-\d+ \| NFR-US-\d+ \| (NFR-\d+) \|", trace_text, flags=re.M
        ),
    }
    return inventories, trace


def chains_from_traceability() -> list[dict[str, str]]:
    text = TRACE_MD.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for match in re.finditer(
        r"^\| (BG-\d+) \| (EP-\d+) \| ((?:NFR-)?US-\d+) \| ((?:NFR|FR)-\d+) \| (MVP|Future) \|",
        text,
        flags=re.M,
    ):
        rows.append(
            {
                "bg": match.group(1),
                "ep": match.group(2),
                "story": match.group(3),
                "req": match.group(4),
                "scope": match.group(5),
            }
        )
    return rows


def scopes_from_requirements() -> dict[str, str]:
    text = REQ_MD.read_text(encoding="utf-8")
    scopes: dict[str, str] = {}
    for match in re.finditer(
        r"^\| ((?:FR|NFR)-\d+) \| ((?:NFR-)?US-\d+) \| [^|]+ \| (MVP|Future) \|",
        text,
        flags=re.M,
    ):
        scopes[match.group(1)] = match.group(3)
    return scopes


def scopes_from_stories() -> dict[str, str]:
    text = BG_MD.read_text(encoding="utf-8")
    scopes: dict[str, str] = {}
    for match in re.finditer(
        r"^\| (US-\d+) \| EP-\d+ \| (MVP|Future) \|",
        text,
        flags=re.M,
    ):
        scopes[match.group(1)] = match.group(2)
    for match in re.finditer(
        r"^\| (NFR-US-\d+) \| EP-\d+ \| [^|]+ \| (MVP|Future) \|",
        text,
        flags=re.M,
    ):
        scopes[match.group(1)] = match.group(2)
    return scopes


def story_ep_from_stories() -> dict[str, str]:
    text = BG_MD.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for match in re.finditer(r"^\| (US-\d+) \| (EP-\d+) \|", text, flags=re.M):
        mapping[match.group(1)] = match.group(2)
    for match in re.finditer(r"^\| (NFR-US-\d+) \| (EP-\d+) \|", text, flags=re.M):
        mapping[match.group(1)] = match.group(2)
    return mapping


def req_story_from_requirements() -> dict[str, str]:
    text = REQ_MD.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for match in re.finditer(
        r"^\| ((?:FR|NFR)-\d+) \| ((?:NFR-)?US-\d+) \|",
        text,
        flags=re.M,
    ):
        mapping[match.group(1)] = match.group(2)
    return mapping


def bg_ep_from_goals() -> dict[str, str]:
    text = BG_MD.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for match in re.finditer(r"^\| (BG-\d+) [^|]*\| (EP-\d+)", text, flags=re.M):
        mapping[match.group(1)] = match.group(2)
    return mapping


def main() -> int:
    if not XLSX.is_file():
        print(f"FAIL: missing canonical workbook {XLSX.relative_to(ROOT)}")
        return 1

    mapping_rows = mapping_rows_from_xlsx(XLSX)
    xlsx_ids = ids_from_mapping(mapping_rows)
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

    ep_expected = expected_ids("EP", EXPECTED_EP)
    if xlsx_ids["EP"] != ep_expected:
        print(f"  FAIL: xlsx EP IDs = {len(xlsx_ids['EP'])} (expected exact 001..{EXPECTED_EP:03d})")
        fail = 1
    else:
        print(f"  ok: xlsx EP IDs = {len(xlsx_ids['EP'])} (expected exact 001..{EXPECTED_EP:03d})")

    if len(mapping_rows) != EXPECTED["FR"] + EXPECTED["NFR"]:
        print(
            f"  FAIL: xlsx mapping rows = {len(mapping_rows)} "
            f"(expected {EXPECTED['FR'] + EXPECTED['NFR']})"
        )
        fail = 1
    else:
        print(f"  ok: xlsx mapping rows = {len(mapping_rows)}")

    print("Markdown docs:")
    for key, expected in EXPECTED.items():
        actual = md_ids[key]
        expected_set = expected_ids(key, expected)
        status = (
            "ok"
            if set(actual) == expected_set and len(actual) == len(set(actual))
            else "FAIL"
        )
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
        if len(trace_ids[key]) != len(set(trace_ids[key])) or set(trace_ids[key]) != set(
            md_ids[key]
        ):
            print(f"  FAIL: {key} traceability rows are missing, duplicated, or divergent")
            fail = 1
        else:
            print(f"  ok:   {key} traceability IDs match published requirements")

    print("BG->EP->US/NFR-US->FR/NFR chains:")
    xlsx_chains = {chain_key(row): row["scope"] for row in mapping_rows}
    trace_rows = chains_from_traceability()
    trace_chains = {chain_key(row): row["scope"] for row in trace_rows}
    if set(xlsx_chains) != set(trace_chains):
        missing = sorted(set(xlsx_chains) - set(trace_chains))
        extra = sorted(set(trace_chains) - set(xlsx_chains))
        print("  FAIL: traceability chains diverge from workbook Consolidated Mapping")
        if missing[:5]:
            print(f"    missing in matrix (sample): {missing[:5]}")
        if extra[:5]:
            print(f"    extra in matrix (sample): {extra[:5]}")
        fail = 1
    else:
        print(f"  ok:   {len(xlsx_chains)} chain tuples match workbook")

    print("Scope fidelity (MVP/Future):")
    req_scopes = scopes_from_requirements()
    story_scopes = scopes_from_stories()
    scope_fail = 0
    for row in mapping_rows:
        req = row["req"]
        story = row["story"]
        scope = row["scope"]
        if req_scopes.get(req) != scope:
            print(f"  FAIL: {req} scope docs={req_scopes.get(req)!r} xlsx={scope!r}")
            scope_fail = 1
        if story_scopes.get(story) != scope:
            print(f"  FAIL: {story} scope docs={story_scopes.get(story)!r} xlsx={scope!r}")
            scope_fail = 1
        if xlsx_chains.get(chain_key(row)) != trace_chains.get(chain_key(row)):
            print(
                f"  FAIL: chain {chain_key(row)} scope matrix="
                f"{trace_chains.get(chain_key(row))!r} xlsx={scope!r}"
            )
            scope_fail = 1
    if scope_fail:
        fail = 1
    else:
        print("  ok:   requirement, story, and matrix scopes match workbook")

    print("Published membership links:")
    bg_ep = bg_ep_from_goals()
    story_ep = story_ep_from_stories()
    req_story = req_story_from_requirements()
    link_fail = 0
    for row in mapping_rows:
        if bg_ep.get(row["bg"]) != row["ep"]:
            print(
                f"  FAIL: {row['bg']}->{row['ep']} goals table has "
                f"{bg_ep.get(row['bg'])!r}"
            )
            link_fail = 1
        if story_ep.get(row["story"]) != row["ep"]:
            print(
                f"  FAIL: {row['story']}->{row['ep']} stories table has "
                f"{story_ep.get(row['story'])!r}"
            )
            link_fail = 1
        if req_story.get(row["req"]) != row["story"]:
            print(
                f"  FAIL: {row['req']}->{row['story']} requirements table has "
                f"{req_story.get(row['req'])!r}"
            )
            link_fail = 1
    if link_fail:
        fail = 1
    else:
        print("  ok:   BG->EP, story->EP, and req->story links match workbook")

    if fail:
        print("Coherence guard FAILED - docs diverge from the canonical xlsx model.")
        return 1

    print("Coherence guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
