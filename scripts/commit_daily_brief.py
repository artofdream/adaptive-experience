#!/usr/bin/env python3
"""Commit and push today's DATE_RE from GitLab CI only.

Scheduled job ``daily-brief-generate`` writes
``research/daily-briefs/YYYY-MM-DD.md`` then this script lands it on the
branch the pipeline ran for (usually ``main``). A local invocation without
CI credentials is refused so a laptop cannot push.

The commit message includes ``[skip ci]`` to avoid a pipeline loop.
Push uses ``CI_JOB_TOKEN``. The GitLab project setting
CI/CD -> Job token permissions -> Allow Git push requests to the repository
must be enabled, or push fails closed (no PAT fallback).
"""

from __future__ import annotations

import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOT_NAME = "AEA daily-brief bot"
BOT_EMAIL = "aea-daily-brief@noreply.gitlab.com"
AUTHOR_RE = re.compile(r"^(?P<name>.*) <(?P<email>[^>]+)>$")


def _require_ci() -> None:
    if os.environ.get("CI") == "true" or os.environ.get("CI_JOB_TOKEN"):
        return
    print(
        "refuse: scripts/commit_daily_brief.py only runs in GitLab CI "
        "(CI=true or CI_JOB_TOKEN). It will not push from a laptop.",
        file=sys.stderr,
    )
    sys.exit(1)


def _today_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def _canonical_today() -> Path:
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from generate_daily_brief import canonical_brief_path

    return canonical_brief_path(_today_iso())


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def _git_config_get(key: str) -> str:
    result = _git("config", "--get", key, check=False)
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def _parse_ci_author(raw: str) -> tuple[str, str]:
    match = AUTHOR_RE.match(raw.strip())
    if not match:
        return "", ""
    return match.group("name").strip(), match.group("email").strip()


def _ensure_local_identity() -> None:
    """Set repo-local user.name / user.email only when missing. Never --global."""
    name = _git_config_get("user.name")
    email = _git_config_get("user.email")
    if name and email:
        return
    parsed_name, parsed_email = _parse_ci_author(os.environ.get("CI_COMMIT_AUTHOR", ""))
    if not name:
        _git("config", "--local", "user.name", parsed_name or BOT_NAME)
    if not email:
        _git("config", "--local", "user.email", parsed_email or BOT_EMAIL)


def _redact(text: str, token: str) -> str:
    if not text:
        return ""
    if token:
        text = text.replace(token, "***")
    return text


def _push_head(ref_name: str) -> None:
    token = os.environ.get("CI_JOB_TOKEN", "")
    host = os.environ.get("CI_SERVER_HOST", "")
    project = os.environ.get("CI_PROJECT_PATH", "")
    if not token or not host or not project:
        print(
            "push failed: CI_JOB_TOKEN, CI_SERVER_HOST, and CI_PROJECT_PATH "
            "are required. Enable CI/CD -> Job token permissions -> "
            "Allow Git push requests to the repository (sponsor/DSO). "
            "No PAT fallback.",
            file=sys.stderr,
        )
        sys.exit(1)
    remote = f"https://gitlab-ci-token:{token}@{host}/{project}.git"
    dest = f"HEAD:refs/heads/{ref_name}"
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        ["git", "push", remote, dest],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )
    stdout = _redact(result.stdout or "", token)
    stderr = _redact(result.stderr or "", token)
    if stdout:
        print(stdout.rstrip())
    if result.returncode != 0:
        if stderr:
            print(stderr.rstrip(), file=sys.stderr)
        print(
            f"push failed: could not push {dest} with CI_JOB_TOKEN. "
            "Enable GitLab project setting CI/CD -> Job token permissions -> "
            "Allow Git push requests to the repository, or the scheduled "
            "job cannot land DATE_RE on the branch. No PAT fallback.",
            file=sys.stderr,
        )
        sys.exit(1)
    if stderr:
        print(stderr.rstrip())
    print(f"pushed DATE_RE to {ref_name}")


def main() -> int:
    _require_ci()
    if not os.environ.get("CI_JOB_TOKEN"):
        print(
            "refuse: CI_JOB_TOKEN is required before git add/commit/push "
            "so a laptop with only CI=true cannot mutate the clone.",
            file=sys.stderr,
        )
        return 1

    path = _canonical_today()
    if not path.is_file():
        print(f"missing DATE_RE file: {path}", file=sys.stderr)
        return 1

    rel = path.resolve().relative_to(ROOT.resolve()).as_posix()
    _ensure_local_identity()
    _git("add", "--", rel)

    staged = _git("diff", "--cached", "--quiet", check=False)
    if staged.returncode == 0:
        print(f"nothing to commit: {rel} already matches HEAD")
        return 0
    if staged.returncode != 1:
        err = (staged.stderr or staged.stdout or "").strip()
        print(f"git diff --cached failed: {err}", file=sys.stderr)
        return 1

    day_iso = _today_iso()
    message = f"chore(daily-brief): {day_iso}.md [skip ci]"
    commit = _git("commit", "-m", message, check=False)
    if commit.returncode != 0:
        print((commit.stderr or commit.stdout or "").strip(), file=sys.stderr)
        print("commit failed", file=sys.stderr)
        return 1
    print(f"committed {rel} as {message}")

    ref_name = os.environ.get("CI_COMMIT_REF_NAME", "").strip()
    if not ref_name:
        print(
            "push failed: CI_COMMIT_REF_NAME is empty "
            "(GitLab CI checkout is detached; need the branch to push to).",
            file=sys.stderr,
        )
        return 1
    _push_head(ref_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
