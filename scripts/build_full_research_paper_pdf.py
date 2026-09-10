#!/usr/bin/env python3
"""Build full research format PDF for AEA harness engineering paper (Playwright via Edge).

Reads research/pdf-export/aea-framework-harness-engineering-full-research-2026-09-10.html
and emits both the dated and un-dated PDF copies.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "research" / "pdf-export"
ARTIFACT_DIR = Path(r"C:\Users\claud\.gemini\antigravity\brain\9b179aea-00e2-4505-853b-9ccfa0c57ae0")

PDF_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

HTML_DATED = PDF_DIR / "aea-framework-harness-engineering-full-research-2026-09-10.html"
HTML_CANON = PDF_DIR / "aea-framework-harness-engineering-full-research.html"

PDF_DATED = PDF_DIR / "aea-framework-harness-engineering-full-research-2026-09-10.pdf"
PDF_CANON = PDF_DIR / "aea-framework-harness-engineering-full-research.pdf"
PDF_ARTIFACT = ARTIFACT_DIR / "aea_framework_harness_engineering_full_research_2026_09_10.pdf"

def main() -> int:
    if not HTML_DATED.is_file():
        print(f"FAIL: missing source HTML {HTML_DATED}")
        return 1

    # Keep canonical html in sync
    shutil.copy2(HTML_DATED, HTML_CANON)

    print(f"Reading {HTML_DATED}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True
        )
        page = browser.new_page()
        page.goto(HTML_DATED.resolve().as_uri(), wait_until='networkidle')
        page.pdf(
            path=str(PDF_DATED),
            format='A4',
            print_background=True,
            margin={'top': '15mm', 'bottom': '15mm', 'left': '13mm', 'right': '13mm'}
        )
        browser.close()

    # Also emit canonical un-dated pdf
    shutil.copy2(PDF_DATED, PDF_CANON)
    shutil.copy2(PDF_DATED, PDF_ARTIFACT)

    print(f"Generated: {PDF_DATED}")
    print(f"Generated: {PDF_CANON}")
    print(f"Copied to artifact: {PDF_ARTIFACT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
