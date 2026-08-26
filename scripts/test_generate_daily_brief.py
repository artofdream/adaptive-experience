#!/usr/bin/env python3
"""Unit tests for generate_daily_brief.py and DATE_RE alignment.

Does not execute ``python scripts/generate_daily_brief.py`` (no live write of
today's brief). Renders via ``build_brief`` with fixtures / mocked guards.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_daily_brief_freshness import DATE_RE, check_generator_brief_honesty
from generate_daily_brief import (
    GENERATOR_TITLE,
    ROADMAP_PATH,
    assert_brief_honesty,
    build_brief,
    canonical_brief_filename,
    parse_guard_status,
    parse_roadmap_milestones,
    summarize_milestones,
    unsupported_shipped_claims,
)


SAMPLE_ROADMAP = """
| **M0** | ADR Scope Gate | Decision gate | Architectural |
| **M8** | Returning shopper (Completed) | Durable recall | FR-008 |
| **M14** | Production Go-Live & FinOps (Reference Extension) | Stripe mock | FR-019 |
| **M15** | Edge SSR & Progressive Hydration (Reference Extension) | sub-100ms LCP benchmark scripts | NFR-002 |
| **Future** | Production Hardening Backlog | Unscheduled | Thin-delivered |
"""

LIVE_GUARD_STDOUT = """
==========================================================
SUMMARY: 14/14 guards passed
==========================================================

ALL PRE-FLIGHT GUARDS PASSED CLEANLY! READY FOR MR.
"""


class TestCanonicalFilename(unittest.TestCase):
    def test_filename_matches_date_re(self):
        name = canonical_brief_filename("2026-08-26")
        self.assertEqual(name, "2026-08-26.md")
        self.assertIsNotNone(DATE_RE.match(name))

    def test_legacy_daily_brief_suffix_is_not_date_re(self):
        self.assertIsNone(DATE_RE.match("2026-08-26-daily-brief.md"))


class TestShippedClaimHonesty(unittest.TestCase):
    def test_flags_hardcoded_ratio(self):
        hits = unsupported_shipped_claims(
            "* **Milestone Pipeline Status**: **15/16 Milestones Completed (93.75%)**."
        )
        self.assertTrue(hits)

    def test_flags_sub_100ms_lcp(self):
        hits = unsupported_shipped_claims(
            "* **Active Focus**: **Milestone M15** (Edge SSR & Sub-100ms LCP)."
        )
        self.assertTrue(hits)

    def test_honest_summary_passes(self):
        text = (
            "* **Milestone labels** (parsed from roadmap): "
            "labeled Completed M8; labeled Reference Extension M14, M15."
        )
        self.assertEqual(unsupported_shipped_claims(text), [])
        assert_brief_honesty(text)

    def test_assert_raises_on_shipped_fact(self):
        with self.assertRaises(ValueError):
            assert_brief_honesty("15/16 Milestones Completed")


class TestRoadmapParse(unittest.TestCase):
    def test_sample_labels(self):
        rows = parse_roadmap_milestones(SAMPLE_ROADMAP)
        by_id = {row["id"]: row["label"] for row in rows}
        self.assertEqual(by_id["M0"], "unlabeled")
        self.assertEqual(by_id["M8"], "completed")
        self.assertEqual(by_id["M14"], "reference-extension")
        self.assertEqual(by_id["M15"], "reference-extension")
        self.assertEqual(by_id["Future"], "backlog")

    def test_summary_does_not_copy_lcp_focus_column(self):
        rows = parse_roadmap_milestones(SAMPLE_ROADMAP)
        summary = summarize_milestones(rows)
        self.assertNotIn("15/16", summary)
        self.assertNotRegex(summary, r"sub-100\s*ms\s+lcp", msg=summary)
        self.assertIn("Unknown", summary)
        self.assertIn("M15", summary)
        self.assertIn("Reference Extension", summary)

    def test_live_roadmap_parse(self):
        self.assertTrue(ROADMAP_PATH.is_file())
        rows = parse_roadmap_milestones(ROADMAP_PATH.read_text(encoding="utf-8"))
        ids = [row["id"] for row in rows]
        self.assertIn("M0", ids)
        self.assertIn("M18", ids)
        m15 = next(row for row in rows if row["id"] == "M15")
        self.assertEqual(m15["label"], "reference-extension")


class TestGuardStatus(unittest.TestCase):
    def test_parses_live_summary(self):
        status = parse_guard_status(LIVE_GUARD_STDOUT)
        self.assertIn("14/14", status)
        self.assertNotIn("Unknown", status)

    def test_unknown_without_summary(self):
        status = parse_guard_status("guard runner crashed")
        self.assertTrue(status.startswith("Unknown"))


class TestRenderBrief(unittest.TestCase):
    def test_build_brief_is_honest_and_canonical(self):
        rows = parse_roadmap_milestones(SAMPLE_ROADMAP)
        text = build_brief(
            "2026-08-26",
            milestone_rows=rows,
            guard_output=LIVE_GUARD_STDOUT,
            recent_notes=["2026-08-26-session-memory-log-example.md"],
            generated_at="2026-08-26T00:00:00+00:00",
            run_live_guards=False,
        )
        self.assertIn(GENERATOR_TITLE, text)
        self.assertIn("research/daily-briefs/2026-08-26.md", text)
        self.assertNotIn("daily-brief.md", text)
        self.assertNotIn("15/16", text)
        self.assertNotRegex(text, r"sub-100\s*ms\s+lcp")
        self.assertIn("14/14", text)
        self.assertIn("SUMMARY: 14/14 guards passed", text)
        self.assertEqual(unsupported_shipped_claims(text), [])

    def test_live_roadmap_render_without_running_generator(self):
        text = build_brief(
            "2026-08-26",
            guard_output=LIVE_GUARD_STDOUT,
            recent_notes=[],
            generated_at="2026-08-26T00:00:00+00:00",
            run_live_guards=False,
        )
        self.assertEqual(unsupported_shipped_claims(text), [])
        self.assertNotIn("15/16", text)
        self.assertNotRegex(text, r"sub-100\s*ms\s+lcp")
        self.assertIn("Reference Extension", text)

    def test_committed_date_re_activity_report_is_not_scanned_as_generator_output(self):
        """2026-08-26.md mentions 15/16 as a non-claim; it is not generator output."""
        violations = check_generator_brief_honesty()
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
