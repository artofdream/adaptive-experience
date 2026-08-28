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
        self.assertIn("<h2>Heading 2</h2>", body)
        self.assertIn("<ul>", body)
        self.assertIn("<li>Item 1</li>", body)

    def test_wrap(self):
        html_doc = wrap("Test Title", "index", "<p>Hello</p>")
        self.assertIn("<title>Test Title — Adaptive Experience Architecture</title>", html_doc)
        self.assertIn("<p>Hello</p>", html_doc)
        self.assertIn('aria-current="page"', html_doc)

    def test_build(self):
        res = build()
        self.assertEqual(res, 0)
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "public" / "index.html").exists())
        self.assertTrue((root / "public" / "path-b.html").exists())


if __name__ == "__main__":
    unittest.main()
