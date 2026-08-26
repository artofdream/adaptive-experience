#!/usr/bin/env python3
"""AEA Daily Briefing Generator.

Writes the canonical session-start handoff:

    research/daily-briefs/YYYY-MM-DD.md

That path is what ``scripts/check_daily_brief_freshness.py`` DATE_RE matches.
Historical ``YYYY-MM-DD-daily-brief.md`` files are not a live writer.

Milestone lines are parsed from ``docs/07-roadmap/roadmap.md``. Guard lines come
from a live run of ``scripts/run_all_guards.py``. Claims that are not derived
from those evidence paths are omitted or printed as Unknown — never invented.
"""

from __future__ import annotations

import datetime
import glob
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "research" / "daily-briefs"
ROADMAP_PATH = ROOT / "docs" / "07-roadmap" / "roadmap.md"
GENERATOR_TITLE = "AEA Daily Executive & Governance Brief"
GUARD_TIMEOUT_SEC = 120

# Shipped-fact strings the generator must never assert without an evidence path.
SHIPPED_CLAIM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"15/16"),
    re.compile(r"sub-100\s*ms\s+lcp", re.IGNORECASE),
)

MILESTONE_ROW_RE = re.compile(
    r"^\|\s*\*\*(M\d+|Future)\*\*\s*\|\s*([^|]+)\|",
    re.MULTILINE,
)
GUARD_SUMMARY_RE = re.compile(
    r"SUMMARY:\s*(\d+)/(\d+)\s+guards passed",
    re.IGNORECASE,
)


def canonical_brief_filename(day_iso: str) -> str:
    """Return ``YYYY-MM-DD.md`` — the only live daily-brief writer path."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day_iso):
        raise ValueError(f"day_iso must be YYYY-MM-DD, got {day_iso!r}")
    return f"{day_iso}.md"


def canonical_brief_path(day_iso: str) -> Path:
    name = canonical_brief_filename(day_iso)
    _assert_filename_matches_date_re(name)
    return BRIEFS_DIR / name


def _assert_filename_matches_date_re(name: str) -> None:
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from check_daily_brief_freshness import DATE_RE

    if DATE_RE.match(name) is None:
        raise ValueError(f"canonical brief name {name!r} does not match DATE_RE")


def unsupported_shipped_claims(text: str) -> list[str]:
    """Return pattern snippets that look like unsupported shipped-fact claims."""
    hits: list[str] = []
    for pattern in SHIPPED_CLAIM_PATTERNS:
        found = pattern.search(text)
        if found:
            hits.append(found.group(0))
    return hits


def assert_brief_honesty(text: str) -> None:
    hits = unsupported_shipped_claims(text)
    if hits:
        raise ValueError(
            "generated brief asserts unsupported shipped-fact strings "
            f"without an evidence path: {hits}"
        )


def parse_roadmap_milestones(text: str) -> list[dict[str, str]]:
    """Parse Group Milestones table labels from roadmap markdown."""
    rows: list[dict[str, str]] = []
    for match in MILESTONE_ROW_RE.finditer(text):
        milestone_id = match.group(1)
        title = match.group(2).strip()
        if milestone_id == "Future":
            label = "backlog"
        elif "(Completed)" in title:
            label = "completed"
        elif "(Reference Extension)" in title:
            label = "reference-extension"
        else:
            label = "unlabeled"
        rows.append({"id": milestone_id, "title": title, "label": label})
    return rows


def load_roadmap_milestones(roadmap_path: Path | None = None) -> list[dict[str, str]]:
    path = roadmap_path or ROADMAP_PATH
    if not path.is_file():
        return []
    return parse_roadmap_milestones(path.read_text(encoding="utf-8"))


def summarize_milestones(rows: list[dict[str, str]]) -> str:
    """Honest milestone lines: labels from the roadmap table, or Unknown.

    Does not compute a completion ratio. Does not treat Reference Extension
    rows as production-ready. Does not invent an active milestone.
    """
    if not rows:
        return (
            "* **Milestone Pipeline Status**: **Unknown** "
            "(roadmap table was not readable).\n"
            "* **Active Focus**: **Unknown**.\n"
        )

    by_label: dict[str, list[str]] = {
        "unlabeled": [],
        "completed": [],
        "reference-extension": [],
        "backlog": [],
    }
    for row in rows:
        by_label.setdefault(row["label"], []).append(row["id"])

    unlabeled = ", ".join(by_label["unlabeled"]) or "none"
    completed = ", ".join(by_label["completed"]) or "none"
    reference = ", ".join(by_label["reference-extension"]) or "none"

    return (
        "* **Milestone labels** (parsed from `docs/07-roadmap/roadmap.md`; "
        "not a ship-count): "
        f"unlabeled MVP rows {unlabeled}; "
        f"labeled Completed {completed}; "
        f"labeled Reference Extension {reference} "
        "(reference/paper rows — not production-ready).\n"
        "* **Active Focus**: **Unknown** "
        "(generator does not invent a live GitLab milestone).\n"
        "* **Reference extensions**: M14–M18 are not reprinted as "
        "production-ready. Live Stripe, browser LCP / Edge SSR, staff live "
        "chat, and WebRTC are not claimed as shipped.\n"
    )


def parse_guard_status(guard_output: str) -> str:
    """Derive the guard line from live runner stdout, else Unknown."""
    match = GUARD_SUMMARY_RE.search(guard_output)
    if not match:
        return "Unknown (no SUMMARY line in runner output)"
    passed, total = match.group(1), match.group(2)
    if "ALL PRE-FLIGHT GUARDS PASSED CLEANLY" in guard_output:
        return f"{passed}/{total} passed (live `run_all_guards.py`)"
    return f"{passed}/{total} from live runner (not all passed)"


def run_guards() -> str:
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_all_guards.py")],
            capture_output=True,
            text=True,
            timeout=GUARD_TIMEOUT_SEC,
            cwd=ROOT,
        )
        return result.stdout or result.stderr or "Guard runner produced no output"
    except Exception as exc:  # noqa: BLE001 — surface any runner failure honestly
        return f"Guard check error: {exc}"


def recent_knowledge_notes(limit: int = 6) -> list[str]:
    notes = glob.glob(str(ROOT / "research" / "random-thoughts" / "*.md"))
    notes.sort(key=os.path.getmtime, reverse=True)
    return [os.path.basename(n) for n in notes[:limit]]


def render_brief(
    day_iso: str,
    generated_at: str,
    milestone_summary: str,
    guard_status: str,
    recent_notes: list[str],
    guard_output: str,
) -> str:
    notes_block = ""
    for note in recent_notes:
        notes_block += f"* [[{note.replace('.md', '')}]] — {note}\n"
    if not notes_block:
        notes_block = "* Unknown (no notes under `research/random-thoughts/`).\n"

    content = f"""# {GENERATOR_TITLE} — {day_iso}

> **Tags**: #aea #daily-brief #governance #telemetry #second-brain
> **Generated**: {generated_at}
> **Target Domain**: `https://aea.artof.link` (AWS ECS Fargate `aea-pilot`)
> **Canonical path**: `research/daily-briefs/{canonical_brief_filename(day_iso)}`

---

## 1. Executive Summary

{milestone_summary.rstrip()}
* **Pre-Flight Quality Guards**: **{guard_status}**.

### Honesty notes
- Milestone lines are roadmap table labels only. Completion ratio is not asserted.
- M14–M18 stay reference extensions; they are not production-ready.
- Browser LCP and Edge SSR are not claimed as shipped.

---

## 2. Live Telemetry Control Center Links

* **Unified Observability Dashboard**: [https://aea.artof.link/grafana/](https://aea.artof.link/grafana/)
* **Executive Control Center**: [https://aea.artof.link/grafana/d/aea-executive-dashboard](https://aea.artof.link/grafana/d/aea-executive-dashboard)

---

## 3. Recent Second Brain Knowledge Curation Notes

{notes_block}
---

## 4. 14-Role Stakeholder Team Active & Next Matrix

| Stakeholder Role | Domain Authority | Core Focus | Reference Extensions | Status |
|---|---|---|---|---|
| `@aea-project-manager` | Scrum Delivery & SOP Gates | M0-M13 Reference Core | M14-M18 Extensions | `ACTIVE` |
| `@aea-product-owner` | Product Vision & Go/No-Go | MVP Product Acceptance | Extension Schema Audits | `ACTIVE` |
| `@aea-ux-designer` | Workspace UI & Tiles T-01..T-09 | Adaptive Workspace UX | Touch Target & Focus Polish | `ACTIVE` |
| `@aea-performance-guardian` | Web Vitals & LCP audit | LCP & Hydration Audit | Frame Latency Audit | `ACTIVE` |
| `@aea-senior-software-engineer` | Platform Engines & BFF | Core BFF & PostgreSQL | Extension Migrations 018-022 | `ACTIVE` |
| `@aea-devsecops-platform` | AWS ECS Fargate & Terraform | Nginx Edge Gateway | AWS Fargate Infrastructure | `ACTIVE` |
| `@aea-ai-engineer` | AI Quality & ADR-016 Proxy | ADR-016 Mock Proxy | Intent Cache Schemas | `ACTIVE` |
| `@aea-appsec-auditor` | Security & Zero-PII Sanitization | Zero-Hardcoded Secrets | WAF Perimeter Auth | `ACTIVE` |
| `@aea-customer-journey` | E2E Customer Journeys J1-J4 | Journeys J1-J4 Walks | Friction Point Remediation | `ACTIVE` |
| `@aea-support-coordinator` | Support Triage & Operator Inbox | Contact Florist Triage | Operator Console UI | `ACTIVE` |
| `@aea-mr-coordinator` | MR Reviews & Auto-Merge | MR Quality Gate Review | Auto-Merge Verification | `ACTIVE` |
| `@aea-coherence-guardian` | Coherence & Quality Guards | Pre-flight quality guards | Workbook Coherence Checks | `ACTIVE` |
| `@aea-knowledge-guardian` | Second Brain Curation | Session Memory Extraction | Second Brain Vault Index | `ACTIVE` |
| `@aea-cost-guardian` | FinOps & AWS Fargate Scaling | Fargate Container Sizing | Token Budget Efficiency | `ACTIVE` |

---

## 5. Automated Pre-Flight Guard Output

```text
{guard_output.strip()}
```
"""
    return content


def build_brief(
    day_iso: str | None = None,
    *,
    milestone_rows: list[dict[str, str]] | None = None,
    guard_output: str | None = None,
    recent_notes: list[str] | None = None,
    generated_at: str | None = None,
    run_live_guards: bool = False,
) -> str:
    """Compose brief markdown. Does not write a file.

    Live ``run_all_guards.py`` runs only when ``run_live_guards`` is True so
    unit tests can render without executing the full guard network.
    """
    if day_iso is None:
        day_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if generated_at is None:
        generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if milestone_rows is None:
        milestone_rows = load_roadmap_milestones()
    if recent_notes is None:
        recent_notes = recent_knowledge_notes()
    if run_live_guards:
        guard_output = run_guards()
    elif guard_output is None:
        guard_output = "Unknown (guards not run in this build)"

    content = render_brief(
        day_iso=day_iso,
        generated_at=generated_at,
        milestone_summary=summarize_milestones(milestone_rows),
        guard_status=parse_guard_status(guard_output),
        recent_notes=recent_notes,
        guard_output=guard_output,
    )
    assert_brief_honesty(content)
    return content


def main() -> int:
    day_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = canonical_brief_path(day_iso)
    # Guard runner last so section 5 matches the tree as written.
    content = build_brief(day_iso, run_live_guards=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Daily brief successfully generated at: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
