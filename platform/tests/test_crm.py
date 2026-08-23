"""Unit tests for Engagement CRM & Occasion Memory Service (FR-016 / FR-017 / NFR-017, M12)."""

import unittest
from datetime import datetime, timezone
from aea_platform.crm import EngagementCrmService, CrmValidationError, OccasionReminder


class InMemoryCrmStore:
    """In-memory store mock for CrmService testing."""

    def __init__(self):
        self.memories = []

    def upsert_occasion_memory(self, *, memory_id, browser_hash, session_id,
                               occasion_type, event_month, event_day,
                               recipient_relation, created_at):
        # Update if exists
        for item in self.memories:
            if (item["browser_hash"] == browser_hash and
                item["occasion_type"] == occasion_type and
                item["recipient_relation"] == recipient_relation):
                item["event_month"] = event_month
                item["event_day"] = event_day
                item["session_id"] = session_id
                return
        self.memories.append({
            "memory_id": memory_id,
            "browser_hash": browser_hash,
            "session_id": session_id,
            "occasion_type": occasion_type,
            "event_month": event_month,
            "event_day": event_day,
            "recipient_relation": recipient_relation,
            "created_at": created_at,
        })

    def list_occasion_memories(self, *, browser_hash):
        return [m for m in self.memories if m["browser_hash"] == browser_hash]


class TestEngagementCrmService(unittest.TestCase):

    def setUp(self):
        self.store = InMemoryCrmStore()
        self.now_time = datetime(2026, 8, 22, 12, 0, 0, tzinfo=timezone.utc)
        self.service = EngagementCrmService(self.store, now=lambda: self.now_time)
        self.browser_hash = self.service.hash_browser("test-browser-session-123")

    def test_browser_hash_generation(self):
        h1 = self.service.hash_browser("session-abc")
        h2 = self.service.hash_browser("session-abc")
        self.assertEqual(h1, h2)
        self.assertEqual(64, len(h1))

    def test_record_occasion_success(self):
        result = self.service.record_occasion(
            browser_hash=self.browser_hash,
            session_id="sess-001",
            occasion_type="Birthday",
            event_month=9,
            event_day=15,
            recipient_relation="Mother",
        )
        self.assertEqual("birthday", result["occasion_type"])
        self.assertEqual("mother", result["recipient_relation"])
        self.assertEqual(9, result["event_month"])
        self.assertEqual(15, result["event_day"])

    def test_record_occasion_validation_errors(self):
        with self.assertRaises(CrmValidationError):
            self.service.record_occasion(
                browser_hash="short_hash",
                session_id="sess-001",
                occasion_type="Birthday",
                event_month=9,
                event_day=15,
            )

        with self.assertRaises(CrmValidationError):
            self.service.record_occasion(
                browser_hash=self.browser_hash,
                session_id="sess-001",
                occasion_type="Birthday",
                event_month=13,  # Invalid month
                event_day=15,
            )

    def test_get_reminders_upcoming_in_lookahead_window(self):
        # Current date: Aug 22. Record event on Sept 5 (14 days later)
        self.service.record_occasion(
            browser_hash=self.browser_hash,
            session_id="sess-001",
            occasion_type="Birthday",
            event_month=9,
            event_day=5,
            recipient_relation="Mother",
        )

        reminders = self.service.get_reminders(browser_hash=self.browser_hash, lookahead_days=30)
        self.assertEqual(1, len(reminders))
        r = reminders[0]
        self.assertEqual(14, r.days_until_event)
        self.assertEqual("birthday", r.occasion_type)
        self.assertIn("Upcoming: Mother's Birthday in 14 days", r.reminder_text)

    def test_get_reminders_ignores_past_events_outside_window(self):
        # Current date: Aug 22. Event on Jan 10 (over 30 days away)
        self.service.record_occasion(
            browser_hash=self.browser_hash,
            session_id="sess-001",
            occasion_type="Anniversary",
            event_month=1,
            event_day=10,
            recipient_relation="Partner",
        )

        reminders = self.service.get_reminders(browser_hash=self.browser_hash, lookahead_days=30)
        self.assertEqual(0, len(reminders))


if __name__ == "__main__":
    unittest.main()
