#!/usr/bin/env python3
"""Build Plain-English Visual Guide PDF (Playwright via Edge).

Reads research/pdf-export/aea-framework-harness-engineering-visual-guide-2026-09-10.html
and emits dated + canonical PDF copies.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "research" / "pdf-export"
ARTIFACT_DIR = Path(r"C:\Users\claud\.gemini\antigravity\brain\9b179aea-00e2-4505-853b-9ccfa0c57ae0")

PDF_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

HTML_DATED = PDF_DIR / "aea-framework-harness-engineering-visual-guide-2026-09-10.html"
HTML_CANON = PDF_DIR / "aea-framework-harness-engineering-visual-guide.html"
PDF_DATED = PDF_DIR / "aea-framework-harness-engineering-visual-guide-2026-09-10.pdf"
PDF_CANON = PDF_DIR / "aea-framework-harness-engineering-visual-guide.pdf"
PDF_ARTIFACT = ARTIFACT_DIR / "aea_framework_harness_engineering_visual_guide_2026_09_10.pdf"

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main() -> int:
    if not HTML_DATED.is_file():
        print(f"FAIL: missing source HTML {HTML_DATED}")
        return 1

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
            margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
        )
        browser.close()

    shutil.copy2(PDF_DATED, PDF_CANON)
    shutil.copy2(PDF_DATED, PDF_ARTIFACT)
    print(f"Generated: {PDF_DATED}")
    print(f"Generated: {PDF_CANON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
