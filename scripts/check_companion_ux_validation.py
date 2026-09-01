#!/usr/bin/env python3
"""Guard: companion UX validation vault checklist + README section exist.

Phase A of #363 — lightweight path checks only. No Gradle, no network, no secrets.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VAULT_NOTE = (
    ROOT
    / "research"
    / "random-thoughts"
    / "2026-09-02-companion-ux-online-validation-setup.md"
)
ANDROID_README = ROOT / "clients" / "mobile" / "android" / "README.md"

# Markers that must appear in the vault UX checklist / phased note.
VAULT_REQUIRED_MARKERS = (
    "UX checklist",
    "Contrast",
    "Back stack",
    "Single CTA honesty",
    "FR-009",
    "Demo banner until BFF",
    "Budget ask",
    "Chip vs free-text unlock",
    "#357",
    "#358",
    "#359",
    "#360",
    "Phase A",
    "Phase B",
    "Phase C",
)

# README section heading + pointers the sponsor/SSE loop needs.
README_REQUIRED_MARKERS = (
    "UX validation loop",
    "android-build-debug",
    "app-debug.apk",
    "scrcpy",
    "Play internal",
    "2026-09-02-companion-ux-online-validation-setup.md",
    "#363",
)


def _check_file(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"Missing {label}: {path.relative_to(ROOT)}")
        return errors
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            errors.append(
                f"{label} missing required marker {marker!r} "
                f"({path.relative_to(ROOT)})"
            )
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(_check_file(VAULT_NOTE, VAULT_REQUIRED_MARKERS, "vault note"))
    errors.extend(
        _check_file(ANDROID_README, README_REQUIRED_MARKERS, "android README")
    )

    if errors:
        print("FAIL: companion UX validation guard")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS: companion UX validation vault note + README section present")
    print(f"  vault: {VAULT_NOTE.relative_to(ROOT)}")
    print(f"  readme: {ANDROID_README.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
