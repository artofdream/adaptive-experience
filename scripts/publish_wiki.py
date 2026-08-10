#!/usr/bin/env python3
"""Publish reviewed wiki/*.md pages to the GitLab project wiki via glab.

Requires authenticated `glab` for artof-group/adaptive-experience-architecture.
Does not invent requirement IDs. Canonical SoT remains docs/ + archive/.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"

# slug -> (title, source filename)
PAGES: list[tuple[str, str, str]] = [
    ("home", "home", "home.md"),
    ("product-vision", "product vision", "product-vision.md"),
    ("business-analysis", "business analysis", "business-analysis.md"),
    ("functional-design", "functional design", "functional-design.md"),
    ("technical-architecture", "technical architecture", "technical-architecture.md"),
    ("ux-design-guide", "ux design guide", "ux-design-guide.md"),
    (
        "architecture-decision-records",
        "architecture decision records",
        "architecture-decision-records.md",
    ),
    ("roadmap", "roadmap", "roadmap.md"),
    (
        "florist-reference-design",
        "florist reference design",
        "florist-reference-design.md",
    ),
    ("coherence-workflow", "coherence workflow", "coherence-workflow.md"),
    ("source-of-truth", "source of truth", "source-of-truth.md"),
]


def glab_api(args: list[str], *, input_data: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        "glab",
        "api",
        "-H",
        "Content-Type: application/json",
        *args,
    ]
    return subprocess.run(
        cmd,
        input=input_data,
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
    )


def upsert(slug: str, title: str, content: str) -> None:
    payload = json.dumps({"title": title, "content": content, "format": "markdown"})
    # Try update first
    upd = glab_api(
        ["--method", "PUT", f"projects/:id/wikis/{slug}", "--input", "-"],
        input_data=payload,
    )
    if upd.returncode == 0:
        print(f"ok: updated {slug} ({len(content)} chars)")
        return
    # Create if missing
    cre = glab_api(
        ["--method", "POST", "projects/:id/wikis", "--input", "-"],
        input_data=json.dumps(
            {"title": title, "content": content, "format": "markdown", "slug": slug}
        ),
    )
    if cre.returncode == 0:
        print(f"ok: created {slug} ({len(content)} chars)")
        return
    print(f"FAIL: {slug}", file=sys.stderr)
    print(upd.stderr or upd.stdout, file=sys.stderr)
    print(cre.stderr or cre.stdout, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    fail = 0
    for slug, title, filename in PAGES:
        path = WIKI_DIR / filename
        if not path.is_file():
            print(f"FAIL: missing {path}", file=sys.stderr)
            fail = 1
            continue
        content = path.read_text(encoding="utf-8")
        try:
            upsert(slug, title, content)
        except SystemExit:
            fail = 1
    return fail


if __name__ == "__main__":
    raise SystemExit(main())
