#!/usr/bin/env python3
"""Build full research format PDF for AEA harness engineering paper (Playwright).

Reads research/pdf-export/aea-framework-harness-engineering-full-research-2026-09-14.html
and emits both the dated and un-dated PDF copies.
Prefers system Edge on Windows when present; otherwise Playwright Chromium (Linux box).
"""
from __future__ import annotations

import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "research" / "pdf-export"
ARTIFACT_DIR = Path(r"C:\Users\claud\.gemini\antigravity\brain\9b179aea-00e2-4505-853b-9ccfa0c57ae0")

PDF_DIR.mkdir(parents=True, exist_ok=True)

HTML_DATED = PDF_DIR / "aea-framework-harness-engineering-full-research-2026-09-14.html"
HTML_CANON = PDF_DIR / "aea-framework-harness-engineering-full-research.html"

PDF_DATED = PDF_DIR / "aea-framework-harness-engineering-full-research-2026-09-14.pdf"
PDF_CANON = PDF_DIR / "aea-framework-harness-engineering-full-research.pdf"
PDF_ARTIFACT = ARTIFACT_DIR / "aea_framework_harness_engineering_full_research_2026_09_14.pdf"

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main() -> int:
    if not HTML_DATED.is_file():
        print(f"FAIL: missing source HTML {HTML_DATED}")
        return 1

    # Keep canonical html in sync
    shutil.copy2(HTML_DATED, HTML_CANON)

    launch_kwargs = {"headless": True}
    if EDGE.is_file():
        launch_kwargs["executable_path"] = str(EDGE)

    print(f"Reading {HTML_DATED}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.goto(HTML_DATED.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(PDF_DATED),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "13mm", "right": "13mm"},
        )
        browser.close()

    # Also emit canonical un-dated pdf
    shutil.copy2(PDF_DATED, PDF_CANON)
    # Optional Windows antigravity artifact mirror (skip on Linux box)
    if EDGE.is_file():
        try:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PDF_DATED, PDF_ARTIFACT)
            print(f"Copied to artifact: {PDF_ARTIFACT}")
        except OSError as exc:
            print(f"Artifact copy skipped: {exc}")

    print(f"Generated: {PDF_DATED}")
    print(f"Generated: {PDF_CANON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
