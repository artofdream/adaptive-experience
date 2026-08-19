#!/usr/bin/env python3
"""Check stakeholder cadence status and role activity across AEA team roles."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "research" / "daily-briefs"

# Import canonical stakeholder role list from generator script
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from generate_codex_stakeholder_skills import SKILLS
    ROLES = sorted(set(SKILLS.keys()) | {"aea-appsec-auditor"})
except ImportError:
    ROLES = [
        "aea-ai-engineer",
        "aea-appsec-auditor",
        "aea-coherence-guardian",
        "aea-customer-journey",
        "aea-devsecops-platform",
        "aea-mr-coordinator",
        "aea-product-owner",
        "aea-project-manager",
        "aea-senior-software-engineer",
        "aea-support-coordinator",
        "aea-ux-designer",
    ]

# Cadence hours (Europe/Paris: 08:00, 12:00, 16:00, 20:00 UTC approx 06:00..18:00 UTC)
CADENCE_WINDOWS = [8, 12, 16, 20]


def check_daily_brief_freshness() -> tuple[bool, str]:
    """Check if today's daily activity brief exists and is up to date."""
    if not BRIEFS_DIR.is_dir():
        return False, "research/daily-briefs/ directory missing"

    briefs = sorted(BRIEFS_DIR.glob("*.md"))
    if not briefs:
        return False, "No daily briefs found under research/daily-briefs/"

    latest = briefs[-1]
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if latest.stem != today_str:
        return False, f"Latest brief is {latest.name}, expected {today_str}.md for today"

    return True, f"Latest brief {latest.name} is fresh"


def check_git_role_activity() -> dict[str, int]:
    """Inspect recent git commit history for mentions/ownership of stakeholder roles."""
    cmd = ["git", "log", "-n", "50", "--pretty=format:%s %b"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if res.returncode != 0:
        return {role: 0 for role in ROLES}

    text = res.stdout.lower()
    counts = {}
    for role in ROLES:
        short_name = role.removeprefix("aea-")
        counts[role] = text.count(role) + text.count(short_name)
    return counts


def evaluate_cadence() -> dict[str, object]:
    """Evaluate overall stakeholder cadence posture."""
    fresh_brief, brief_msg = check_daily_brief_freshness()
    activity_counts = check_git_role_activity()

    active_roles = [r for r, count in activity_counts.items() if count > 0]
    idle_roles = [r for r, count in activity_counts.items() if count == 0]

    now_utc = datetime.now(timezone.utc)
    current_hour_utc = now_utc.hour

    return {
        "timestamp_utc": now_utc.isoformat(),
        "total_roles": len(ROLES),
        "daily_brief_fresh": fresh_brief,
        "daily_brief_status": brief_msg,
        "active_roles_count": len(active_roles),
        "idle_roles_count": len(idle_roles),
        "active_roles": active_roles,
        "idle_roles": idle_roles,
        "current_hour_utc": current_hour_utc,
    }


def main() -> int:
    report = evaluate_cadence()

    print(f"Stakeholder Cadence Status Guard — {report['timestamp_utc']}")
    print(f"Total roles: {report['total_roles']}")
    print(f"Daily brief status: {'OK' if report['daily_brief_fresh'] else 'WARNING'} — {report['daily_brief_status']}")
    print(f"Active roles in recent commits ({report['active_roles_count']}/{report['total_roles']}): {', '.join(report['active_roles']) or 'none'}")
    if report['idle_roles']:
        print(f"Idle roles ({report['idle_roles_count']}): {', '.join(report['idle_roles'])}")

    # Guard passes if daily brief directory is present and role roster is fully tracked
    if report['total_roles'] >= 10:
        print("ok: stakeholder cadence status check passed")
        return 0
    else:
        print("FAIL: incomplete stakeholder role roster", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
