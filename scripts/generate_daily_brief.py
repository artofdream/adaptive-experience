"""Generate research/daily-briefs/<today>.md for the scheduled CI job.

Design intent (see .cursor/skills/aea-coherence-guardian/SKILL.md and
research/coherence-findings-loop.md, which this script implements a
narrow, unattended slice of):

- All evidence gathering is deterministic script/API code -- GitLab REST
  API via CI_JOB_TOKEN, local guard scripts, a local file read of the
  coherence queue. The model never runs a command and never decides what
  to gather.
- Exactly ONE bounded call to the Anthropic Messages API, given the
  gathered facts as input, asked only to write narrative prose from them.
  It has no tool access and cannot take any action.
- File writing, git, and MR creation are deterministic code, done by the
  CI job that calls this script (git-shell.py handles git; this script
  only writes the markdown file and prints the CI-job's next steps as
  JSON on the last stdout line).
- Reporting only: never edits research/coherence-findings-loop.md, never
  opens a remediation issue/branch/MR. If the queue has a queued/regressed
  row, note it in the brief for a human or an interactive session.
- Idempotent: refuses to overwrite an existing same-day brief.

Required environment (all provided natively by GitLab CI except the key):
  ANTHROPIC_API_KEY   -- masked/protected CI variable, added by the sponsor
  CI_JOB_TOKEN        -- GitLab-provided, scoped to this project
  CI_PROJECT_ID       -- GitLab-provided
  CI_SERVER_URL       -- GitLab-provided
"""

import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_daily_brief_freshness import latest_brief_date  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "research" / "daily-briefs"
QUEUE_FILE = ROOT / "research" / "coherence-findings-loop.md"
ANTHROPIC_MODEL = "claude-sonnet-5"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class MethodNote(list):
    """Collects honest "could not verify X" notes instead of guessing."""

    def add(self, text: str) -> None:
        self.append(text)


def gitlab_api(path: str, params: dict | None = None) -> object:
    """GET against this project's GitLab API using the CI job token."""
    base = os.environ["CI_SERVER_URL"].rstrip("/")
    project_id = os.environ["CI_PROJECT_ID"]
    url = f"{base}/api/v4/projects/{project_id}/{path}"
    if params:
        query = "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url, headers={"JOB-TOKEN": os.environ["CI_JOB_TOKEN"]})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def gitlab_api_post(path: str, body: dict) -> object:
    base = os.environ["CI_SERVER_URL"].rstrip("/")
    project_id = os.environ["CI_PROJECT_ID"]
    url = f"{base}/api/v4/projects/{project_id}/{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"JOB-TOKEN": os.environ["CI_JOB_TOKEN"], "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=ROOT)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as exc:  # noqa: BLE001 -- report, don't crash the whole run
        return 1, f"exception running {cmd}: {exc}"


def gather_guard_results(notes: MethodNote) -> dict:
    results = {}
    for name, cmd in (
        ("check_coherence.py", [sys.executable, "scripts/check_coherence.py"]),
        ("check_topic_schemas.py", [sys.executable, "scripts/check_topic_schemas.py"]),
        ("generate_codex_stakeholder_skills.py --check",
         [sys.executable, "scripts/generate_codex_stakeholder_skills.py", "--check"]),
        ("check_daily_brief_freshness.py",
         [sys.executable, "scripts/check_daily_brief_freshness.py"]),
    ):
        code, output = run(cmd)
        results[name] = {"passed": code == 0, "output": output[-2000:]}
        if code != 0 and name != "check_daily_brief_freshness.py":
            notes.add(f"Guard `{name}` failed (see raw output in the brief).")
    return results


def gather_merged_mrs(since: datetime.date | None, notes: MethodNote) -> list[dict]:
    try:
        params = {"state": "merged", "order_by": "updated_at", "sort": "desc", "per_page": 50}
        mrs = gitlab_api("merge_requests", params)
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        notes.add(f"Could not fetch merged MRs from GitLab API: {exc}")
        return []
    if since is None:
        return mrs[:20]
    cutoff = datetime.datetime.combine(since, datetime.time.min, tzinfo=datetime.timezone.utc)
    out = []
    for mr in mrs:
        merged_at = mr.get("merged_at")
        if merged_at and datetime.datetime.fromisoformat(merged_at.replace("Z", "+00:00")) > cutoff:
            out.append(mr)
    return out


def gather_milestones(notes: MethodNote) -> list[dict]:
    try:
        return gitlab_api("milestones", {"state": "active", "per_page": 20})
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        notes.add(f"Could not fetch milestones from GitLab API: {exc}")
        return []


def gather_queue_rows(notes: MethodNote) -> dict:
    if not QUEUE_FILE.is_file():
        notes.add(f"{QUEUE_FILE.relative_to(ROOT)} not found.")
        return {"queued": [], "regressed": [], "total": 0}
    text = QUEUE_FILE.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.startswith("| ") and "CF-" in ln]
    queued = [ln for ln in lines if "| queued |" in ln]
    regressed = [ln for ln in lines if "| regressed |" in ln]
    return {"queued": queued, "regressed": regressed, "total": len(lines)}


def call_anthropic(facts: dict, notes: MethodNote) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        notes.add("ANTHROPIC_API_KEY not set -- narrative synthesis skipped.")
        return None
    prompt = (
        "You are drafting the narrative sections of a daily repo activity brief for "
        "the AEA / Lily's Florist reference-architecture repository. You are given "
        "structured facts gathered by deterministic scripts -- you have no tool access "
        "and cannot verify anything further, so use ONLY what is given. Do not invent "
        "commits, MR numbers, dates, or counts not present in the facts. Write concise "
        "markdown with these sections, matching the tone of prior briefs (factual, "
        "terse, no marketing language): '## Commits / MRs merged', "
        "'## Coherence queue movement', '## Milestone movement'. If a section's facts "
        "are empty, write one line saying so -- do not pad it out. Do not include a "
        "'## Guard status' section; that is appended separately from raw script output.\n\n"
        f"Facts (JSON):\n{json.dumps(facts, indent=2, default=str)}"
    )
    body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return "".join(block.get("text", "") for block in data.get("content", []))
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        notes.add(f"Anthropic API call failed: {exc}")
        return None


def push_and_open_mr(today: datetime.date, path: Path) -> dict:
    """Deterministic git + GitLab API steps -- no model involvement past this point."""
    required = ("CI_JOB_TOKEN", "CI_SERVER_URL", "CI_PROJECT_ID", "CI_PROJECT_PATH", "CI_SERVER_HOST")
    if any(k not in os.environ for k in required):
        return {"pushed": False, "reason": "not running in GitLab CI (required CI_* vars absent)"}

    branch = f"docs/daily-brief-{today.isoformat()}"
    rel_path = str(path.relative_to(ROOT)).replace("\\", "/")
    steps = [
        ["git", "config", "user.email", "aea-coherence-guardian@ci.local"],
        ["git", "config", "user.name", "AEA Coherence Guardian (CI)"],
        ["git", "checkout", "-b", branch],
        ["git", "add", rel_path],
        ["git", "commit", "-m", f"docs: daily brief {today.isoformat()}"],
    ]
    for step in steps:
        code, output = run(step)
        if code != 0:
            return {"pushed": False, "reason": f"`{' '.join(step)}` failed: {output}"}

    push_url = (
        f"https://gitlab-ci-token:{os.environ['CI_JOB_TOKEN']}@"
        f"{os.environ['CI_SERVER_HOST']}/{os.environ['CI_PROJECT_PATH']}.git"
    )
    code, output = run(["git", "push", push_url, f"HEAD:refs/heads/{branch}"])
    if code != 0:
        return {"pushed": False, "reason": f"git push failed: {output}"}

    try:
        mr = gitlab_api_post("merge_requests", {
            "source_branch": branch,
            "target_branch": "main",
            "title": f"docs: daily brief {today.isoformat()}",
            "description": (
                "Scheduled `daily-brief-generate` CI job. Narrative prose is "
                "LLM-synthesized from deterministically-gathered facts only "
                "(no tool access); guard output and git/MR actions are plain "
                "script code, not model-driven. Not merged automatically -- "
                "see .cursor/skills/aea-mr-coordinator/SKILL.md."
            ),
            "remove_source_branch": True,
        })
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        return {"pushed": True, "mr_created": False, "reason": f"MR creation failed: {exc}"}

    return {"pushed": True, "mr_created": True, "mr_url": mr.get("web_url")}


def main() -> None:
    today = datetime.datetime.now(datetime.timezone.utc).date()
    today_file = BRIEFS_DIR / f"{today.isoformat()}.md"
    if today_file.is_file():
        print(json.dumps({"wrote_brief": False, "reason": f"{today_file} already exists"}))
        return

    notes = MethodNote()
    since = latest_brief_date()
    guard_results = gather_guard_results(notes)
    merged_mrs = gather_merged_mrs(since, notes)
    milestones = gather_milestones(notes)
    queue = gather_queue_rows(notes)

    facts = {
        "today": today.isoformat(),
        "since": since.isoformat() if since else None,
        "merged_mrs": [
            {"iid": mr.get("iid"), "title": mr.get("title"), "merged_at": mr.get("merged_at"),
             "web_url": mr.get("web_url")}
            for mr in merged_mrs
        ],
        "milestones": [
            {"title": m.get("title"), "state": m.get("state")} for m in milestones
        ],
        "coherence_queue": {
            "total_rows": queue["total"],
            "queued_count": len(queue["queued"]),
            "regressed_count": len(queue["regressed"]),
            "queued_rows": queue["queued"][:10],
            "regressed_rows": queue["regressed"][:10],
        },
    }

    narrative = call_anthropic(facts, notes)

    lines = [
        f"# Adaptive Experience — Daily Activity Report — {today.isoformat()}",
        "",
        "tags: #aea #daily-brief",
        "",
        "*Generated by the scheduled `daily-brief-generate` CI job "
        "(`scripts/generate_daily_brief.py`). Facts below are deterministic script/API "
        "output; narrative prose is LLM-synthesized from those facts only, with no "
        "tool access of its own. See "
        "`.cursor/skills/aea-coherence-guardian/SKILL.md`.*",
        "",
    ]
    if narrative:
        lines.append(narrative.strip())
    else:
        lines.append("## Narrative synthesis unavailable")
        lines.append("")
        lines.append("See Method note below.")
    lines += ["", "## Guard status", ""]
    for name, result in guard_results.items():
        status = "pass" if result["passed"] else "FAIL"
        lines.append(f"- `{name}`: **{status}**")
    lines += ["", "```", *[f"{name}: {r['output']}" for name, r in guard_results.items()], "```"]

    if notes:
        lines += ["", "## Method note", ""]
        for note in notes:
            lines.append(f"- {note}")

    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    today_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    push_result = push_and_open_mr(today, today_file)

    print(json.dumps({
        "wrote_brief": True,
        "path": str(today_file.relative_to(ROOT)),
        "guard_all_passed": all(r["passed"] for r in guard_results.values()),
        "method_notes": len(notes),
        **push_result,
    }))


if __name__ == "__main__":
    main()
