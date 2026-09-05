"""Unit tests for check_traceability.py milestone alignment (#323 baseline)."""

import unittest

from check_traceability import (
    canonical_requirement_ids,
    milestone_aligned,
    roadmap_milestones_for,
)


class TraceabilityBaselineTests(unittest.TestCase):
    def test_canonical_ids_are_40(self):
        self.assertEqual(40, len(canonical_requirement_ids()))

    def test_fr006_claims_m16_and_future(self):
        self.assertEqual(["M16", "Future"], roadmap_milestones_for("FR-006"))

    def test_nfr014_claims_m18_and_future(self):
        self.assertEqual(["M18", "Future"], roadmap_milestones_for("NFR-014"))

    def test_future_backlog_aligns_with_dual_listed_ids(self):
        self.assertTrue(milestone_aligned(roadmap_milestones_for("FR-006"), "Future"))
        self.assertTrue(milestone_aligned(roadmap_milestones_for("NFR-014"), "Future"))

    def test_extension_milestone_also_aligns(self):
        self.assertTrue(milestone_aligned(["M16", "Future"], "M16"))
        self.assertTrue(milestone_aligned(["M18", "Future"], "M18"))

    def test_unrelated_milestone_is_mismatch(self):
        self.assertFalse(milestone_aligned(["M16", "Future"], "M2"))

    def test_missing_gitlab_milestone_is_mismatch_when_roadmap_claims(self):
        self.assertFalse(milestone_aligned(["M8"], None))

    def test_no_roadmap_claim_is_aligned(self):
        self.assertTrue(milestone_aligned([], "M1"))


if __name__ == "__main__":
    unittest.main()
