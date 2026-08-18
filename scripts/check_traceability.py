"""Requirements-to-issue traceability guard (loop-graph.md gap #1, v1).

Scope, deliberately narrow (see "What this does not check" below):
for each of the 40 canonical FR/NFR IDs, verify:

1. A canonical GitLab issue exists for it (via the `[US-NNN]` /
   `[NFR-US-NNN]` title convention used by the original 40 requirement
   issues -- verified against live data before writing this, not assumed).
2. That issue's GitLab milestone matches what docs/07-roadmap/roadmap.md
   claims for that FR/NFR (the CF-039 class of drift, checked continuously
   instead of caught once by hand).
3. If the issue is closed, it was actually closed by a merged MR
   (`closed_by` is non-empty) -- not closed with no evidence.

This is a read-only report, like check_coherence.py: it does not write to
research/coherence-findings-loop.md or open anything. A human or
aea-coherence-guardian promotes a real finding into the CF queue.

## What this does not check (out of scope for v1, not silently assumed)

- FR/NFR -> ADR linkage. ADRs are prose; there is no structured,
  parseable convention citing which FR/NFR each ADR governs. Enforcing
  this would need that convention established first, not guessed at.
- FR/NFR -> code/test linkage. Code comments and test names cite FR/NFR
  IDs inconsistently across the codebase; a checker built on that
  inconsistency would produce more false negatives than signal.
- Any issue outside the original 40 canonical requirement issues
  (bugs, infra tickets, UX findings, etc.) -- those are downstream
  implementation work, not the canonical requirement tickets themselves,
  and don't use the `[US-NNN]` title convention.

Required environment: CI_JOB_TOKEN, CI_SERVER_URL, CI_PROJECT_ID (all
GitLab-provided; CI_JOB_TOKEN, unlike a user-defined "Protected" CI/CD
variable, is available on every branch regardless of protection, so this
guard -- being read-only -- can be fully live-tested on a feature branch
before merging).
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_DOC = ROOT / "docs" / "02-business-analysis" / "requirements.md"
ROADMAP_DOC = ROOT / "docs" / "07-roadmap" / "roadmap.md"

REQ_ID_RE = re.compile(r"\b((?:NFR-)?FR-\d{3}|NFR-\d{3})\b")
ROADMAP_ROW_RE = re.compile(
    r"^\|\s*\*\*(M\d+)\*\*\s*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE
)


def gitlab_api(path: str, params: dict | None = None) -> object:
    base = os.environ["CI_SERVER_URL"].rstrip("/")
    project_id = os.environ["CI_PROJECT_ID"]
    url = f"{base}/api/v4/projects/{project_id}/{path}"
    if params:
        query = "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url, headers={"JOB-TOKEN": os.environ["CI_JOB_TOKEN"]})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def canonical_requirement_ids() -> set[str]:
    """The 40 canonical IDs, parsed the same way check_coherence.py trusts
    docs/ (which is itself guarded to match the workbook)."""
    text = REQUIREMENTS_DOC.read_text(encoding="utf-8")
    ids = set()
    for m in re.finditer(r"\bFR-\d{3}\b|\bNFR-\d{3}\b", text):
        ids.add(m.group(0))
    return ids


def roadmap_milestone_for(req_id: str) -> str | None:
    """Which roadmap milestone (short code, e.g. 'M4') claims this ID."""
    text = ROADMAP_DOC.read_text(encoding="utf-8")
    for m in ROADMAP_ROW_RE.finditer(text):
        milestone, coverage_cell = m.group(1), m.group(2)
        if req_id in REQ_ID_RE.findall(coverage_cell):
            return milestone
    return None


def fetch_canonical_issues() -> dict[str, list[dict]]:
    """req_id -> list of issues whose TITLE cites it (title only, not
    description, to avoid matching unrelated downstream tickets that
    happen to mention an FR/NFR ID in passing)."""
    by_req: dict[str, list[dict]] = {}
    page = 1
    while True:
        # No "scope" param here: valid for the global /issues endpoint,
        # not the project-scoped one used here (that returned every
        # project issue already, live-tested confirmed).
        issues = gitlab_api("issues", {
            "per_page": 100, "page": page, "order_by": "iid", "sort": "asc",
        })
        if not issues:
            break
        for issue in issues:
            title_ids = REQ_ID_RE.findall(issue["title"])
            if not title_ids:
                continue
            # Canonical issues cite exactly one requirement in the title
            # (e.g. "[US-013] FR-013 - Ordering and Delivery"); a title
            # matching more than one is not this convention and is skipped.
            if len(set(title_ids)) != 1:
                continue
            by_req.setdefault(title_ids[0], []).append(issue)
        page += 1
    return by_req


def check_closed_by_merged_mr(issue_iid: int) -> bool:
    try:
        closed_by = gitlab_api(f"issues/{issue_iid}/closed_by")
    except (urllib.error.URLError, KeyError, json.JSONDecodeError):
        return False  # can't verify -> treat as unverified, not as passing
    return any(mr.get("state") == "merged" for mr in closed_by)


def main() -> None:
    req_ids = canonical_requirement_ids()
    try:
        issues_by_req = fetch_canonical_issues()
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        # Report a clean, honest failure -- not a raw traceback -- and
        # make it distinguishable from a genuine traceability finding.
        print(f"UNVERIFIED: could not fetch issues from the GitLab API: {exc}")
        print("This is a data-gathering failure, not a traceability finding "
              "-- do not treat it as evidence the 40 requirements are untraceable.")
        sys.exit(2)

    orphans, milestone_mismatches, unevidenced_closures = [], [], []

    for req_id in sorted(req_ids):
        matches = issues_by_req.get(req_id, [])
        if not matches:
            orphans.append(req_id)
            continue
        if len(matches) > 1:
            print(f"note: {req_id} has {len(matches)} canonical issues "
                  f"({', '.join('#' + str(m['iid']) for m in matches)}) -- ambiguous, "
                  "checking the first")
        issue = matches[0]

        roadmap_milestone = roadmap_milestone_for(req_id)
        gitlab_milestone = (issue.get("milestone") or {}).get("title", "")
        gitlab_milestone_code = gitlab_milestone.split(" ", 1)[0] if gitlab_milestone else None
        if roadmap_milestone and gitlab_milestone_code and roadmap_milestone != gitlab_milestone_code:
            milestone_mismatches.append(
                f"{req_id} (#{issue['iid']}): roadmap says {roadmap_milestone}, "
                f"GitLab says {gitlab_milestone_code or '(none)'}"
            )
        elif roadmap_milestone and not gitlab_milestone_code:
            milestone_mismatches.append(
                f"{req_id} (#{issue['iid']}): roadmap says {roadmap_milestone}, "
                "GitLab has no milestone set"
            )

        if issue["state"] == "closed" and not check_closed_by_merged_mr(issue["iid"]):
            unevidenced_closures.append(f"{req_id} (#{issue['iid']}): closed, no merged MR on record")

    print(f"Canonical requirement IDs checked: {len(req_ids)}")
    print(f"Canonical issues found: {sum(len(v) for v in issues_by_req.values())}")

    ok = True
    if orphans:
        ok = False
        print(f"\nORPHANED (no canonical GitLab issue found): {len(orphans)}")
        for req_id in orphans:
            print(f"  - {req_id}")
    if milestone_mismatches:
        ok = False
        print(f"\nMILESTONE MISMATCH (roadmap vs GitLab): {len(milestone_mismatches)}")
        for line in milestone_mismatches:
            print(f"  - {line}")
    if unevidenced_closures:
        ok = False
        print(f"\nCLOSED WITHOUT A MERGED MR ON RECORD: {len(unevidenced_closures)}")
        for line in unevidenced_closures:
            print(f"  - {line}")

    if ok:
        print("\nok: all canonical FR/NFR IDs have a traceable issue, "
              "matching roadmap milestone, and evidenced closure")
    else:
        print("\nSee the module docstring for what this guard does not check "
              "(ADR linkage, code/test linkage) -- those are known-out-of-scope, "
              "not silently passing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
