"""Unit tests for Engagement CRM & Occasion Memory Service (FR-016 / FR-017 / NFR-017, M12)."""

import json
import unittest
from datetime import datetime, timezone
from aea_platform.crm import (
    EngagementCrmService,
    CrmValidationError,
    OccasionReminder,
    format_engagement_export,
    format_reminder_text,
)


class InMemoryCrmStore:
    """In-memory store mock for CrmService testing."""

    def __init__(self):
        self.memories = []
        self.outbox = []

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
                item["updated_at"] = created_at
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
            "updated_at": created_at,
        })

    def list_occasion_memories(self, *, browser_hash):
        return [m for m in self.memories if m["browser_hash"] == browser_hash]

    def list_all_occasion_memories(self):
        return list(self.memories)

    def upsert_reminder_outbox(self, *, outbox_id, memory_id, occasion_year,
                               occasion_type, recipient_relation, days_until_event,
                               reminder_text, copy_source, status, send_disposition,
                               created_at):
        for item in self.outbox:
            if item["memory_id"] == memory_id and item["occasion_year"] == occasion_year:
                item["occasion_type"] = occasion_type
                item["recipient_relation"] = recipient_relation
                item["days_until_event"] = days_until_event
                item["reminder_text"] = reminder_text
                item["copy_source"] = copy_source
                item["updated_at"] = created_at
                return item["outbox_id"]
        self.outbox.append({
            "outbox_id": outbox_id,
            "memory_id": memory_id,
            "occasion_year": occasion_year,
            "occasion_type": occasion_type,
            "recipient_relation": recipient_relation,
            "days_until_event": days_until_event,
            "reminder_text": reminder_text,
            "copy_source": copy_source,
            "status": status,
            "send_disposition": send_disposition,
            "created_at": created_at,
            "updated_at": created_at,
        })
        return outbox_id

    def list_reminder_outbox(self):
        return [{
            "outbox_id": item["outbox_id"],
            "occasion_type": item["occasion_type"],
            "recipient_relation": item["recipient_relation"],
            "days_until_event": item["days_until_event"],
            "reminder_text": item["reminder_text"],
            "copy_source": item["copy_source"],
            "status": item["status"],
            "send_disposition": item["send_disposition"],
            "occasion_year": item["occasion_year"],
        } for item in self.outbox]

    def get_reminder_outbox(self, *, outbox_id):
        for item in self.outbox:
            if item["outbox_id"] == outbox_id:
                return {
                    "outbox_id": item["outbox_id"],
                    "occasion_type": item["occasion_type"],
                    "recipient_relation": item["recipient_relation"],
                    "days_until_event": item["days_until_event"],
                    "reminder_text": item["reminder_text"],
                    "copy_source": item["copy_source"],
                    "status": item["status"],
                    "send_disposition": item["send_disposition"],
                    "occasion_year": item["occasion_year"],
                }
        return None

    def mark_reminder_outbox_not_implemented(self, *, outbox_id, updated_at):
        for item in self.outbox:
            if item["outbox_id"] == outbox_id:
                item["send_disposition"] = "not_implemented"
                item["status"] = "dry_run"
                item["updated_at"] = updated_at
                return 1
        return 0

    def delete_occasion_memories(self, *, browser_hash):
        removed_ids = {m["memory_id"] for m in self.memories if m["browser_hash"] == browser_hash}
        before = len(self.memories)
        self.memories = [m for m in self.memories if m["browser_hash"] != browser_hash]
        self.outbox = [item for item in self.outbox if item["memory_id"] not in removed_ids]
        return before - len(self.memories)

    def purge_expired_memories(self, *, cutoff):
        keep = [m for m in self.memories if m.get("updated_at", m["created_at"]) >= cutoff]
        removed_ids = {m["memory_id"] for m in self.memories if m not in keep}
        before = len(self.memories)
        self.memories = keep
        self.outbox = [item for item in self.outbox if item["memory_id"] not in removed_ids]
        return before - len(self.memories)


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
        self.assertEqual(
            format_reminder_text(occasion_type="birthday", recipient_relation="mother",
                                 days_until_event=14),
            r.reminder_text)

    def test_format_reminder_text_today_is_same_day_template(self):
        self.assertEqual(
            "Today is Mother's Birthday! 1-click same-day flower order.",
            format_reminder_text(occasion_type="birthday", recipient_relation="mother",
                                 days_until_event=0))

    def test_get_reminders_uses_copy_author_for_soonest_item_only(self):
        # FR-016 #425: AI/author path may rewrite the card line; later items stay template.
        self.service.copy_author = lambda **_: "Mum's birthday is 14 days out — flowers ready?"
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Anniversary", event_month=9, event_day=10,
            recipient_relation="Partner")
        reminders = self.service.get_reminders(browser_hash=self.browser_hash, lookahead_days=30)
        self.assertEqual(2, len(reminders))
        self.assertEqual(14, reminders[0].days_until_event)
        self.assertEqual("Mum's birthday is 14 days out — flowers ready?", reminders[0].reminder_text)
        self.assertEqual(
            format_reminder_text(occasion_type="anniversary", recipient_relation="partner",
                                 days_until_event=19),
            reminders[1].reminder_text)

    def test_get_reminders_fails_closed_to_template_when_author_errors(self):
        def boom(**_):
            raise RuntimeError("provider down")
        self.service.copy_author = boom
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        reminders = self.service.get_reminders(browser_hash=self.browser_hash, lookahead_days=30)
        self.assertEqual(1, len(reminders))
        self.assertEqual(
            format_reminder_text(occasion_type="birthday", recipient_relation="mother",
                                 days_until_event=14),
            reminders[0].reminder_text)

    def test_get_reminders_fails_closed_when_author_returns_blank(self):
        self.service.copy_author = lambda **_: "   "
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        reminders = self.service.get_reminders(browser_hash=self.browser_hash, lookahead_days=30)
        self.assertIn("Upcoming: Mother's Birthday in 14 days", reminders[0].reminder_text)

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

    def test_forget_erases_all_memories_for_browser(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Anniversary", event_month=6, event_day=1,
            recipient_relation="Partner")
        other = self.service.hash_browser("someone-else")
        self.service.record_occasion(
            browser_hash=other, session_id="sess-002",
            occasion_type="Birthday", event_month=3, event_day=3)

        deleted = self.service.forget(browser_hash=self.browser_hash)
        self.assertEqual(2, deleted)
        self.assertEqual(0, len(self.service.get_reminders(browser_hash=self.browser_hash, lookahead_days=366)))
        # Other browsers are untouched.
        self.assertEqual(1, len(self.store.list_occasion_memories(browser_hash=other)))
        # Idempotent: forgetting again removes nothing.
        self.assertEqual(0, self.service.forget(browser_hash=self.browser_hash))

    def test_forget_rejects_invalid_hash(self):
        with self.assertRaises(CrmValidationError):
            self.service.forget(browser_hash="too-short")

    def test_purge_expired_removes_stale_memory_only(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        # Advance well past the retention window; the memory is now stale.
        self.now_time = datetime(2028, 8, 22, 12, 0, 0, tzinfo=timezone.utc)
        purged = self.service.purge_expired(retention_days=400)
        self.assertEqual(1, purged)
        self.assertEqual(0, len(self.store.list_occasion_memories(browser_hash=self.browser_hash)))

    def test_purge_expired_keeps_recent_memory(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        # Same day: nothing is beyond the retention window.
        purged = self.service.purge_expired(retention_days=400)
        self.assertEqual(0, purged)
        self.assertEqual(1, len(self.store.list_occasion_memories(browser_hash=self.browser_hash)))

    def test_purge_expired_rejects_bad_retention(self):
        with self.assertRaises(CrmValidationError):
            self.service.purge_expired(retention_days=0)

    def test_engagement_analytics_empty_is_zero_counts(self):
        analytics = self.service.get_engagement_analytics()
        self.assertEqual(0, analytics["memory_count"])
        self.assertEqual(0, analytics["unique_browsers"])
        self.assertEqual(0, analytics["upcoming_within_days"])
        self.assertEqual(30, analytics["lookahead_days"])
        self.assertEqual([], analytics["occasion_cohorts"])
        self.assertEqual([], analytics["relation_cohorts"])
        self.assertEqual([], analytics["event_month_cohorts"])
        self.assertNotIn("browser_hash", analytics)
        self.assertNotIn("session_id", analytics)

    def test_engagement_analytics_cohorts_are_zero_pii_counts(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Anniversary", event_month=6, event_day=1,
            recipient_relation="Partner")
        other = self.service.hash_browser("someone-else")
        self.service.record_occasion(
            browser_hash=other, session_id="sess-002",
            occasion_type="Birthday", event_month=9, event_day=15,
            recipient_relation="Mother")

        analytics = self.service.get_engagement_analytics(lookahead_days=30)
        self.assertEqual(3, analytics["memory_count"])
        self.assertEqual(2, analytics["unique_browsers"])
        # 22 Aug 2026 → 5 Sep (14d) and 15 Sep (24d) are inside 30d; June is not.
        self.assertEqual(2, analytics["upcoming_within_days"])
        self.assertEqual(
            [{"occasion_type": "birthday", "count": 2},
             {"occasion_type": "anniversary", "count": 1}],
            analytics["occasion_cohorts"])
        self.assertEqual(
            [{"recipient_relation": "mother", "count": 2},
             {"recipient_relation": "partner", "count": 1}],
            analytics["relation_cohorts"])
        self.assertEqual(
            [{"event_month": 6, "count": 1}, {"event_month": 9, "count": 2}],
            analytics["event_month_cohorts"])
        blob = str(analytics)
        self.assertNotIn(self.browser_hash, blob)
        self.assertNotIn(other, blob)
        self.assertNotIn("sess-001", blob)

    def test_engagement_analytics_rejects_bad_lookahead(self):
        with self.assertRaises(CrmValidationError):
            self.service.get_engagement_analytics(lookahead_days=0)

    def test_engagement_export_is_zero_pii_counts_and_keys(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        other = self.service.hash_browser("someone-else")
        self.service.record_occasion(
            browser_hash=other, session_id="sess-002",
            occasion_type="Birthday", event_month=9, event_day=15,
            recipient_relation="Mother")

        csv_export = self.service.export_engagement_analytics(export_format="csv")
        self.assertEqual("csv", csv_export["format"])
        self.assertEqual("florist-engagement-cohorts.csv", csv_export["filename"])
        self.assertIn("text/csv", csv_export["content_type"])
        self.assertIn("section,key,count", csv_export["body"])
        self.assertIn("totals,memory_count,2", csv_export["body"])
        self.assertIn("occasion,birthday,2", csv_export["body"])
        self.assertIn("relation,mother,2", csv_export["body"])
        self.assertIn("event_month,9,2", csv_export["body"])
        self.assertNotIn(self.browser_hash, csv_export["body"])
        self.assertNotIn(other, csv_export["body"])
        self.assertNotIn("sess-001", csv_export["body"])
        self.assertNotIn("browser_hash", csv_export["body"])
        self.assertNotIn("session_id", csv_export["body"])

        json_export = self.service.export_engagement_analytics(export_format="json")
        self.assertEqual("json", json_export["format"])
        self.assertEqual("florist-engagement-cohorts.json", json_export["filename"])
        payload = json.loads(json_export["body"])
        self.assertEqual(2, payload["memory_count"])
        self.assertEqual(2, payload["unique_browsers"])
        self.assertEqual([{"occasion_type": "birthday", "count": 2}], payload["occasion_cohorts"])
        self.assertNotIn("browser_hash", payload)
        self.assertNotIn("session_id", payload)
        self.assertNotIn(self.browser_hash, json_export["body"])
        self.assertNotIn("sess-002", json_export["body"])

        dirty = format_engagement_export({
            "memory_count": 1,
            "unique_browsers": 1,
            "upcoming_within_days": 1,
            "lookahead_days": 30,
            "occasion_cohorts": [{"occasion_type": "birthday", "count": 1}],
            "relation_cohorts": [],
            "event_month_cohorts": [],
            "browser_hash": "a" * 64,
            "email": "private@example.invalid",
        })
        self.assertNotIn("browser_hash", dirty["body"])
        self.assertNotIn("private@example.invalid", dirty["body"])
        self.assertNotIn("email", dirty["body"])

    def test_engagement_export_rejects_bad_format(self):
        with self.assertRaises(CrmValidationError):
            self.service.export_engagement_analytics(export_format="xlsx")

    def test_record_occasion_enqueues_dry_run_outbox_inside_lookahead(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        listed = self.service.list_reminder_outbox()
        self.assertEqual(1, listed["pending_dry_run"])
        self.assertEqual(1, listed["not_sent"])
        self.assertEqual(0, listed["not_implemented"])
        item = listed["items"][0]
        self.assertEqual("dry_run", item["status"])
        self.assertEqual("not_sent", item["send_disposition"])
        self.assertEqual("birthday", item["occasion_type"])
        self.assertEqual("mother", item["recipient_relation"])
        self.assertEqual(14, item["days_until_event"])
        self.assertEqual(2026, item["occasion_year"])
        self.assertEqual("template", item["copy_source"])
        self.assertEqual(
            format_reminder_text(occasion_type="birthday", recipient_relation="mother",
                                 days_until_event=14),
            item["reminder_text"])
        blob = str(listed)
        self.assertNotIn(self.browser_hash, blob)
        self.assertNotIn("sess-001", blob)
        self.assertNotIn("email", blob)
        self.assertNotIn("phone", blob)
        self.assertNotIn("browser_hash", listed)
        self.assertNotIn("memory_id", item)

    def test_outbox_reuses_ai_copy_when_author_is_wired(self):
        self.service.copy_author = lambda **_: "Mum's birthday is 14 days out — flowers ready?"
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        item = self.service.list_reminder_outbox()["items"][0]
        self.assertEqual("ai", item["copy_source"])
        self.assertEqual("Mum's birthday is 14 days out — flowers ready?", item["reminder_text"])

    def test_outbox_fails_closed_to_template_when_author_errors(self):
        def boom(**_):
            raise RuntimeError("provider down")
        self.service.copy_author = boom
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        item = self.service.list_reminder_outbox()["items"][0]
        self.assertEqual("template", item["copy_source"])
        self.assertEqual(
            format_reminder_text(occasion_type="birthday", recipient_relation="mother",
                                 days_until_event=14),
            item["reminder_text"])

    def test_enqueue_skips_outside_lookahead_and_is_idempotent(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Anniversary", event_month=1, event_day=10,
            recipient_relation="Partner")
        self.assertEqual(0, self.service.list_reminder_outbox()["pending_dry_run"])
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        first = self.service.enqueue_upcoming_dry_run()
        second = self.service.enqueue_upcoming_dry_run()
        self.assertEqual(1, first["pending_dry_run"])
        self.assertEqual(1, second["pending_dry_run"])
        self.assertEqual(1, second["enqueued"])
        self.assertEqual(first["items"][0]["outbox_id"], second["items"][0]["outbox_id"])

    def test_attempt_send_is_fail_closed_and_never_marks_sent(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        outbox_id = self.service.list_reminder_outbox()["items"][0]["outbox_id"]
        result = self.service.attempt_send(outbox_id=outbox_id)
        self.assertEqual("not_implemented", result["code"])
        self.assertEqual("dry_run", result["status"])
        self.assertEqual("not_implemented", result["send_disposition"])
        self.assertFalse(result["sent"])
        listed = self.service.list_reminder_outbox()
        self.assertEqual(1, listed["pending_dry_run"])
        self.assertEqual(0, listed["not_sent"])
        self.assertEqual(1, listed["not_implemented"])
        self.assertEqual("dry_run", listed["items"][0]["status"])
        self.assertEqual("not_implemented", listed["items"][0]["send_disposition"])
        again = self.service.attempt_send(outbox_id=outbox_id)
        self.assertFalse(again["sent"])
        self.assertEqual("dry_run", again["status"])

    def test_attempt_send_rejects_unknown_and_invalid_ids(self):
        with self.assertRaises(CrmValidationError):
            self.service.attempt_send(outbox_id="not-a-uuid")
        with self.assertRaises(CrmValidationError):
            self.service.attempt_send(outbox_id="11111111-1111-4111-8111-111111111111")

    def test_forget_removes_outbox_rows_for_that_browser(self):
        self.service.record_occasion(
            browser_hash=self.browser_hash, session_id="sess-001",
            occasion_type="Birthday", event_month=9, event_day=5,
            recipient_relation="Mother")
        other = self.service.hash_browser("someone-else")
        self.service.record_occasion(
            browser_hash=other, session_id="sess-002",
            occasion_type="Birthday", event_month=9, event_day=15,
            recipient_relation="Mother")
        self.assertEqual(2, self.service.list_reminder_outbox()["pending_dry_run"])
        self.assertEqual(1, self.service.forget(browser_hash=self.browser_hash))
        leftover = self.service.list_reminder_outbox()
        self.assertEqual(1, leftover["pending_dry_run"])
        self.assertEqual("birthday", leftover["items"][0]["occasion_type"])
        self.assertNotIn(self.browser_hash, str(leftover))


if __name__ == "__main__":
    unittest.main()
