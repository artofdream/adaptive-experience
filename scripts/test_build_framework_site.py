#!/usr/bin/env python3
"""Unit tests for scripts/build_framework_site.py."""

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from build_framework_site import PAGES, build, inline_md, md_to_html, wrap


class TestBuildFrameworkSite(unittest.TestCase):
    def test_inline_md(self):
        text = "Check `code`, **bold**, *italic*, and [link](https://example.com)"
        formatted = inline_md(text)
        self.assertIn("<code>code</code>", formatted)
        self.assertIn("<strong>bold</strong>", formatted)
        self.assertIn("<em>italic</em>", formatted)
        self.assertIn('<a href="https://example.com">link</a>', formatted)

    def test_md_to_html(self):
        md = "# Heading 1\n\nParagraph text.\n\n## Heading 2\n\n- Item 1\n- Item 2"
        body = md_to_html(md)
        self.assertIn("<h1>Heading 1</h1>", body)
        self.assertIn("<p>Paragraph text.</p>", body)
        self.assertIn('<h2 id="heading-2">Heading 2</h2>', body)
        self.assertIn("<ul>", body)
        self.assertIn("<li>Item 1</li>", body)

    def test_video_md(self):
        body = md_to_html("![Urgent Sam 30s](assets/j1-urgent-sam-30s.mp4)")
        self.assertIn("<video", body)
        self.assertIn("controls", body)
        self.assertIn("/assets/j1-urgent-sam-30s.mp4", body)
        self.assertIn('poster="/assets/j1-urgent-sam-30s.jpg"', body)
        self.assertIn("<figcaption>Urgent Sam 30s</figcaption>", body)

    def test_wrap(self):
        html_doc = wrap("Test Title", "index", "<p>Hello</p>")
        self.assertIn("<title>Test Title", html_doc)
        self.assertIn("architecture.artof.link", html_doc)
        self.assertIn("<p>Hello</p>", html_doc)
        self.assertIn('aria-current="page"', html_doc)
        self.assertIn('href="#main"', html_doc)
        self.assertIn('<main id="main">', html_doc)
        self.assertIn('color-scheme:light dark', html_doc)

    def test_build(self):
        res = build()
        self.assertEqual(res, 0)
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "public" / "index.html").exists())
        self.assertTrue((root / "public" / "path-b.html").exists())
        self.assertTrue((root / "public" / "stack.html").exists())
        self.assertTrue((root / "public" / "companion.html").exists())
        companion = (root / "docs" / "framework" / "companion.md").read_text(
            encoding="utf-8")
        self.assertIn("assets/companion-need-30s-2026-09-02.mp4", companion)
        html = (root / "public" / "companion.html").read_text(encoding="utf-8")
        self.assertIn("/assets/companion-need-30s-2026-09-02.mp4", html)
        self.assertIn('poster="/assets/companion-need-30s-2026-09-02.jpg"', html)

    def test_cf056_honesty_incident_cross_links(self):
        """Daily-brief honesty and Claim vs probe name the same incident and link."""
        root = Path(__file__).resolve().parents[1]
        comparison = (root / "docs" / "framework" / "comparison.md").read_text(
            encoding="utf-8"
        )
        journal = (root / "docs" / "framework" / "journal.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Daily-brief honesty", comparison)
        self.assertIn("journal.html#claim-vs-probe", comparison)
        self.assertIn("## Claim vs probe", journal)
        self.assertIn("Daily-brief honesty", journal)
        self.assertIn("comparison.html#what-aea-claims-here", journal)

        self.assertEqual(build(), 0)
        comparison_html = (root / "public" / "comparison.html").read_text(
            encoding="utf-8"
        )
        journal_html = (root / "public" / "journal.html").read_text(encoding="utf-8")
        self.assertIn('href="journal.html#claim-vs-probe"', comparison_html)
        self.assertIn('id="claim-vs-probe"', journal_html)
        self.assertIn("Daily-brief honesty", journal_html)
        self.assertIn('href="comparison.html#what-aea-claims-here"', journal_html)


if __name__ == "__main__":
    unittest.main()
