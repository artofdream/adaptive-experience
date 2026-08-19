#!/usr/bin/env python3
"""Generate Mermaid and Graphviz DOT graph visualizations for AEA 40-requirement traceability DAG."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_FILE = ROOT / "docs" / "08-traceability" / "requirement-evidence.json"
GRAPHS_DIR = ROOT / "docs" / "08-traceability" / "graphs"


def load_traceability_chains() -> list[dict[str, str]]:
    """Load 40 requirement chains from canonical XLSX workbook."""
    from check_coherence import XLSX, mapping_rows_from_xlsx
    return mapping_rows_from_xlsx(XLSX)


def generate_mermaid_graph(chains: list[dict[str, str]]) -> str:
    """Generate Mermaid flowchart diagram representing BG -> EP -> US/NFR-US -> FR/NFR DAG."""
    lines = [
        "```mermaid",
        "flowchart TD",
        "    classDef bg fill:#1f77b4,stroke:#fff,stroke-width:2px,color:#fff;",
        "    classDef ep fill:#ff7f0e,stroke:#fff,stroke-width:2px,color:#fff;",
        "    classDef story fill:#2ca02c,stroke:#fff,stroke-width:2px,color:#fff;",
        "    classDef req fill:#d62728,stroke:#fff,stroke-width:2px,color:#fff;",
        "",
    ]

    added_nodes = set()

    for item in chains:
        req_id = item["req"]
        story_id = item["story"]
        ep_id = item["ep"]
        bg_id = item["bg"]

        if bg_id not in added_nodes:
            lines.append(f"    {bg_id}[{bg_id}]:::bg")
            added_nodes.add(bg_id)
        if ep_id not in added_nodes:
            lines.append(f"    {ep_id}[{ep_id}]:::ep")
            added_nodes.add(ep_id)
        if story_id not in added_nodes:
            lines.append(f"    {story_id}[{story_id}]:::story")
            added_nodes.add(story_id)
        if req_id not in added_nodes:
            lines.append(f"    {req_id}[{req_id}]:::req")
            added_nodes.add(req_id)

        lines.append(f"    {bg_id} --> {ep_id}")
        lines.append(f"    {ep_id} --> {story_id}")
        lines.append(f"    {story_id} --> {req_id}")

    lines.append("```")
    return "\n".join(lines)


def generate_dot_graph(chains: list[dict[str, str]]) -> str:
    """Generate Graphviz DOT diagram for the requirement DAG."""
    lines = [
        'digraph TraceabilityDAG {',
        '    rankdir=LR;',
        '    node [shape=box, style=filled, fontname="Helvetica"];',
        '    edge [color="#666666"];',
        '',
    ]

    for item in chains:
        req_id = item["req"]
        story_id = item["story"]
        ep_id = item["ep"]
        bg_id = item["bg"]

        lines.append(f'    "{bg_id}" -> "{ep_id}";')
        lines.append(f'    "{ep_id}" -> "{story_id}";')
        lines.append(f'    "{story_id}" -> "{req_id}";')

    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify graph asset freshness")
    args = parser.parse_args()

    chains = load_traceability_chains()
    mermaid_content = generate_mermaid_graph(chains)
    dot_content = generate_dot_graph(chains)

    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    mermaid_file = GRAPHS_DIR / "traceability.mmd"
    dot_file = GRAPHS_DIR / "traceability.dot"

    if args.check:
        if not mermaid_file.is_file() or mermaid_file.read_text(encoding="utf-8") != mermaid_content:
            print(f"FAIL: {mermaid_file.relative_to(ROOT)} is out of sync", file=sys.stderr)
            return 1
        if not dot_file.is_file() or dot_file.read_text(encoding="utf-8") != dot_content:
            print(f"FAIL: {dot_file.relative_to(ROOT)} is out of sync", file=sys.stderr)
            return 1
        print("ok: traceability graph assets are synchronized")
        return 0

    mermaid_file.write_text(mermaid_content, encoding="utf-8")
    dot_file.write_text(dot_content, encoding="utf-8")
    print(f"ok: generated {mermaid_file.relative_to(ROOT)} and {dot_file.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
