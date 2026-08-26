"""Fail if the latest research/daily-briefs/*.md is stale.

Read by session-start-briefing.mdc's watchdog: every session is supposed to
read the latest brief before acting, so a brief that nobody is producing
defeats that SOP silently. This script makes the staleness visible on a
GitLab CI schedule instead of relying on a human or an AI session noticing.

Canonical handoff is ``YYYY-MM-DD.md`` (DATE_RE). Historical
``YYYY-MM-DD-daily-brief.md`` files are not the live bus and are ignored.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "research" / "daily-briefs"
STALE_AFTER_DAYS = 1
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
GENERATOR_TITLE = "AEA Daily Executive & Governance Brief"


def latest_brief_date() -> datetime.date | None:
    dates = []
    for path in BRIEFS_DIR.glob("*.md"):
        m = DATE_RE.match(path.name)
        if m:
            dates.append(datetime.date.fromisoformat(m.group(1)))
    return max(dates) if dates else None


def check_generator_brief_honesty() -> list[str]:
    """Fail generator-shaped DATE_RE briefs that assert unsupported shipped facts.

    Activity reports that happen to mention those strings as findings or
    non-claims are not scanned. Only files whose title matches the generator.
    """
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from generate_daily_brief import unsupported_shipped_claims

    violations: list[str] = []
    if not BRIEFS_DIR.is_dir():
        return violations
    for path in sorted(BRIEFS_DIR.glob("*.md")):
        if DATE_RE.match(path.name) is None:
            continue
        text = path.read_text(encoding="utf-8")
        if GENERATOR_TITLE not in text:
            continue
        hits = unsupported_shipped_claims(text)
        if hits:
            violations.append(f"{path.name}: {hits}")
    return violations


def main() -> None:
    latest = latest_brief_date()
    today = datetime.datetime.now(datetime.timezone.utc).date()

    if latest is None:
        print(f"stale: no dated file found under {BRIEFS_DIR.relative_to(ROOT)}/")
        sys.exit(1)

    age_days = (today - latest).days
    if age_days > STALE_AFTER_DAYS:
        print(
            f"stale: latest daily brief is {latest.isoformat()} "
            f"({age_days} days old, threshold is {STALE_AFTER_DAYS}). "
            "Every session-start reads this brief per "
            ".cursor/rules/session-start-briefing.mdc -- run "
            "aea-coherence-guardian to produce a fresh one."
        )
        sys.exit(1)

    print(f"ok: latest daily brief is {latest.isoformat()} ({age_days} days old)")

    honesty = check_generator_brief_honesty()
    if honesty:
        print(
            "honesty: generator-shaped DATE_RE brief asserts unsupported "
            "shipped-fact strings without an evidence path:"
        )
        for row in honesty:
            print(f"  - {row}")
        sys.exit(1)
    print("ok: no generator-shaped DATE_RE brief asserts unsupported shipped facts")


if __name__ == "__main__":
    main()
