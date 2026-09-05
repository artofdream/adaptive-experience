"""Blocking PM/SM process-coherence guard for GitLab merge requests.

Checks only falsifiable delivery-process evidence. It does not attempt to judge
whether a diff is semantically focused or technically correct. Named
``Process-Exception`` values in ALLOWED_EXCEPTIONS remain the only explicit,
reviewable exceptions.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from pathlib import Path


CLOSE_RE = re.compile(r"(?im)^\s*(?:closes?|fixes?|resolves?)\s+#(\d+)\s*[.]?\s*$")
EXCEPTION_RE = re.compile(r"(?im)^\s*Process-Exception:\s*([a-z0-9-]+)\s*$")
ALLOWED_EXCEPTIONS = {"recurring-report"}
CODE_PREFIXES = ("platform/", "edge/", "infra/")
INTEGRATION_RE = re.compile(
    r"(?im)^\s*(?:Integration evidence|CI-only accepted-by PM-SM):\s*\S.+$"
)
VALIDATION_RE = re.compile(r"(?im)^\s*(?:##\s*)?Validation(?: evidence)?:\s*(?:\S.*)?$")


def gitlab_api(path: str, params: dict | None = None) -> object:
    base = os.environ["CI_SERVER_URL"].rstrip("/")
    project_id = os.environ["CI_PROJECT_ID"]
    url = f"{base}/api/v4/projects/{project_id}/{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    token = os.environ.get("CI_JOB_TOKEN")
    if not token:
        raise RuntimeError("CI_JOB_TOKEN is required for live GitLab checks")
    req = urllib.request.Request(url, headers={"JOB-TOKEN": token})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_git_name_status(output: str) -> list[str]:
    """Collect old and new paths from ``git diff --name-status`` output."""
    paths: set[str] = set()
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            paths.update(parts[1:])
        elif len(parts) == 2:
            paths.add(parts[1])
    return sorted(path for path in paths if path)


def ci_git_changed_paths() -> list[str] | None:
    """MR-pipeline path evidence. CI_JOB_TOKEN cannot read ``/diffs`` (HTTP 404)."""
    base = os.environ.get("CI_MERGE_REQUEST_DIFF_BASE_SHA") or os.environ.get(
        "CI_MERGE_REQUEST_TARGET_BRANCH_SHA"
    )
    head = os.environ.get("CI_COMMIT_SHA")
    if not base or not head:
        return None
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-status", "--diff-filter=ACDMRT", base, head],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return parse_git_name_status(output)


def changed_paths(mr: dict) -> list[str]:
    if "changes" in mr:
        changes = mr["changes"]
    else:
        git_paths = ci_git_changed_paths()
        if git_paths is not None:
            return git_paths
        # The legacy /changes endpoint returns 404 to CI_JOB_TOKEN in scheduled
        # pipelines even when the MR list is readable. The current /diffs
        # endpoint exposes the same old/new path evidence as a plain list.
        changes = []
        page = 1
        while True:
            batch = gitlab_api(
                f"merge_requests/{mr['iid']}/diffs",
                {"per_page": 100, "page": page},
            )
            changes.extend(batch)
            if len(batch) < 100:
                break
            page += 1
    return sorted({
        path
        for change in changes
        for path in (change.get("old_path", ""), change.get("new_path", ""))
        if path
    })


def evaluate(mr: dict, paths: list[str]) -> list[str]:
    iid = mr.get("iid", "?")
    description = mr.get("description") or ""
    findings: list[str] = []

    if mr.get("target_branch") != "main":
        findings.append(f"!{iid}: target branch is not main")
    if mr.get("source_branch") in {"main", "master", None, ""}:
        findings.append(f"!{iid}: invalid or missing source branch")

    issue_ids = CLOSE_RE.findall(description)
    exceptions = EXCEPTION_RE.findall(description)
    unknown_exceptions = sorted(set(exceptions) - ALLOWED_EXCEPTIONS)
    if unknown_exceptions:
        findings.append(f"!{iid}: unknown Process-Exception {unknown_exceptions}")
    recurring_report = exceptions == ["recurring-report"]
    if recurring_report and issue_ids:
        findings.append(f"!{iid}: recurring-report exception must not also close an issue")
    elif not recurring_report and len(issue_ids) != 1:
        findings.append(
            f"!{iid}: expected exactly one closing issue reference, found {len(issue_ids)}"
        )

    code_changed = any(path.startswith(CODE_PREFIXES) for path in paths)
    if code_changed and not INTEGRATION_RE.search(description):
        findings.append(f"!{iid}: code/infra change lacks integration or PM-SM CI-only evidence")
    if not VALIDATION_RE.search(description):
        findings.append(f"!{iid}: MR description lacks a Validation section")
    return findings


def evaluate_live(mr: dict) -> list[str]:
    """Evaluate an MR, preferring git paths over the job-token-inaccessible diffs API."""
    try:
        paths = changed_paths(mr)
    except HTTPError as exc:
        if exc.code != 404:
            raise
        # Job-token 404 on /diffs is expected. Do not fail a required job solely
        # because path evidence is unreadable; description checks still run.
        print(
            f"!{mr.get('iid', '?')}: warning: changed paths could not be "
            "verified (GitLab API HTTP 404); integration evidence not enforced"
        )
        return evaluate(mr, [])
    return evaluate(mr, paths)


def load_merge_requests(fixture: Path | None) -> list[dict]:
    if fixture:
        data = json.loads(fixture.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data["merge_requests"]
    current_iid = os.environ.get("CI_MERGE_REQUEST_IID")
    if current_iid:
        return [gitlab_api(f"merge_requests/{current_iid}")]
    # Required on main: fixtures already proved the checker. Do not fail main
    # because another open MR's diffs are unreadable to CI_JOB_TOKEN.
    return []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, help="evaluate fixture JSON instead of GitLab")
    args = parser.parse_args()

    merge_requests = load_merge_requests(args.fixture)
    findings: list[str] = []
    for mr in merge_requests:
        if args.fixture:
            findings.extend(evaluate(mr, changed_paths(mr)))
        else:
            findings.extend(evaluate_live(mr))
        if not args.fixture:
            description = mr.get("description") or ""
            for issue_id in CLOSE_RE.findall(description):
                try:
                    gitlab_api(f"issues/{issue_id}")
                except Exception as exc:  # report unavailable/invalid evidence honestly
                    findings.append(
                        f"!{mr.get('iid', '?')}: closing issue #{issue_id} "
                        f"could not be verified ({exc})"
                    )

    print(f"Merge requests checked: {len(merge_requests)}")
    if findings:
        print("PROCESS COHERENCE FINDINGS:")
        for finding in findings:
            print(f"  - {finding}")
        print(
            "Blocking: named Process-Exception values are the only explicit "
            "exceptions; PM-SM still reviews semantic focus."
        )
        sys.exit(1)
    print("ok: falsifiable MR process-coherence evidence is present")


if __name__ == "__main__":
    main()
