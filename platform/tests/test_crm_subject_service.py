"""
Unit tests for Privacy-Preserving CRM & Subject Intelligence Engine (ADR-020).
"""

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.crm import CrmService, compute_spend_band, compute_subject_reference


class TestCrmSubjectService(unittest.TestCase):

    def test_compute_subject_reference_is_deterministic_and_salted(self):
        ref1 = compute_subject_reference("client-session-12345", salt="salt-a")
        ref2 = compute_subject_reference("client-session-12345", salt="salt-a")
        ref3 = compute_subject_reference("client-session-12345", salt="salt-b")

        self.assertEqual(ref1, ref2)
        self.assertNotEqual(ref1, ref3)
        self.assertTrue(ref1.startswith("sub_"))
        self.assertEqual(len(ref1), 36)  # "sub_" + 32 chars

    def test_compute_spend_band(self):
        self.assertEqual(compute_spend_band(35.0), "band_0_50")
        self.assertEqual(compute_spend_band(50.0), "band_50_100")
        self.assertEqual(compute_spend_band(95.0), "band_50_100")
        self.assertEqual(compute_spend_band(100.0), "band_50_100")
        self.assertEqual(compute_spend_band(137.0), "band_100_250")
        self.assertEqual(compute_spend_band(300.0), "band_250_plus")

    def test_get_subject_insights_for_unseen_subject(self):
        store = MagicMock()
        store.get_crm_profile.return_value = None
        service = CrmService(store)

        insights = service.get_subject_insights("sub_test_unseen")
        self.assertIsNotNone(insights)
        self.assertEqual(insights["customer_segment"], "new_shopper")
        self.assertEqual(insights["total_orders"], 0)
        self.assertEqual(insights["lifetime_spend_band"], "band_0_50")

    def test_get_subject_insights_for_frequent_buyer(self):
        store = MagicMock()
        store.get_crm_profile.return_value = {
            "subject_reference": "sub_test_frequent",
            "total_orders": 4,
            "lifetime_spend_band": "band_100_250",
            "primary_occasion": "birthday",
            "preferred_channel": "companion",
            "first_seen_at": "2026-08-01T10:00:00Z",
            "last_seen_at": "2026-09-02T19:28:40Z",
        }
        service = CrmService(store)

        insights = service.get_subject_insights("sub_test_frequent")
        self.assertIsNotNone(insights)
        self.assertEqual(insights["customer_segment"], "frequent_buyer")
        self.assertEqual(insights["total_orders"], 4)
        self.assertEqual(insights["primary_occasion"], "birthday")
        self.assertEqual(insights["preferred_channel"], "companion")


if __name__ == "__main__":
    unittest.main()
