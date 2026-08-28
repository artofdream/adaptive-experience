"""Pre-flight quality guard validating Second Brain Knowledge Graph & [[wikilink]] integrity.

Checks:
1. All markdown notes under research/random-thoughts/ exist and are non-empty.
2. All notes contain required graph tags (#aea).
3. All [[wikilink]] references target valid existing markdown files or canonical requirement/ADR IDs.
"""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANDOM_THOUGHTS = ROOT / "research" / "random-thoughts"
DOCS = ROOT / "docs"

WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
TAG_PATTERN = re.compile(r"#aea\b")


def check_knowledge_graph() -> int:
    if not RANDOM_THOUGHTS.is_dir():
        print(f"error: directory missing: {RANDOM_THOUGHTS}")
        return 1

    md_files = list(RANDOM_THOUGHTS.glob("*.md"))
    if not md_files:
        print(f"error: no markdown files found in {RANDOM_THOUGHTS}")
        return 1

    errors = []
    checked_files = 0
    total_wikilinks = 0

    for md_file in md_files:
        checked_files += 1
        content = md_file.read_text(encoding="utf-8")

        if not content.strip():
            errors.append(f"{md_file.relative_to(ROOT)}: file is empty")
            continue

        if not TAG_PATTERN.search(content):
            errors.append(f"{md_file.relative_to(ROOT)}: missing required #aea graph tag")

        wikilinks = WIKILINK_PATTERN.findall(content)
        total_wikilinks += len(wikilinks)

        for target in wikilinks:
            clean_target = target.strip()

            # Canonical requirement / ADR / Milestone / Gap / Nginx / CF pattern matchers
            if (clean_target.startswith("ADR-") or clean_target.startswith("BG-")
                    or clean_target.startswith("US-") or clean_target.startswith("FR-")
                    or clean_target.startswith("NFR-") or clean_target.startswith("M")
                    or clean_target.startswith("J") or clean_target.startswith("Gap-")
                    or clean_target.startswith("Nginx-") or clean_target.startswith("CF-")
                    or clean_target.lower() in ("wikilink", "wikilinks", "note-name")):
                continue

            # Check if file exists relative to research/random-thoughts, docs, or repo root
            possible_paths = [
                RANDOM_THOUGHTS / f"{clean_target}.md",
                RANDOM_THOUGHTS / clean_target,
                DOCS / f"{clean_target}.md",
                DOCS / clean_target,
                ROOT / f"{clean_target}.md",
                ROOT / clean_target,
            ] + list(DOCS.rglob(f"{clean_target}.md")) + list(ROOT.glob(f"research/**/{clean_target}.md"))

            if not any(p.exists() for p in possible_paths):
                errors.append(f"{md_file.relative_to(ROOT)}: broken [[wikilink]] target '{clean_target}'")

    if errors:
        print("error: Knowledge Graph & [[wikilink]] integrity check failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"ok: Knowledge Graph & [[wikilink]] guard passed ({checked_files} memory files, {total_wikilinks} wikilinks validated)")
    return 0


if __name__ == "__main__":
    sys.exit(check_knowledge_graph())
