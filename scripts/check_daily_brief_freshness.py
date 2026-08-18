"""Fail if the latest research/daily-briefs/*.md is stale.

Read by session-start-briefing.mdc's watchdog: every session is supposed to
read the latest brief before acting, so a brief that nobody is producing
defeats that SOP silently. This script makes the staleness visible on a
GitLab CI schedule instead of relying on a human or an AI session noticing.
"""

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "research" / "daily-briefs"
STALE_AFTER_DAYS = 1
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def latest_brief_date() -> datetime.date | None:
    dates = []
    for path in BRIEFS_DIR.glob("*.md"):
        m = DATE_RE.match(path.name)
        if m:
            dates.append(datetime.date.fromisoformat(m.group(1)))
    return max(dates) if dates else None


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


if __name__ == "__main__":
    main()
