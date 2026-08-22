"""Unit tests for annual occasion reminders in platform/aea_platform/crm.py."""

from __future__ import annotations

import inspect
import sys
import unittest
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.crm import (
    APPROVED_TEMPLATES,
    CrmValidationError,
    EngagementCrmService,
    next_annual_occurrence,
)


class CrmReminderTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 22, 12, 0, tzinfo=timezone.utc)
        self.service = EngagementCrmService(
            now=lambda: self.now,
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000012"),
        )

    def remember(self, **overrides):
        fields = {
            "browser_token": "recall-token-abc",
            "occasion": "birthday",
            "month_day": "08-29",
            "lead_days": 7,
        }
        fields.update(overrides)
        return self.service.remember_occasion(**fields)

    def test_remembers_annual_birthday_without_pii(self):
        memory = self.remember()
        self.assertEqual("00000000-0000-0000-0000-000000000012", memory.memory_id)
        self.assertEqual("recall-token-abc", memory.browser_token)
        self.assertEqual("birthday", memory.occasion)
        self.assertEqual("08-29", memory.month_day)
        self.assertFalse(memory.suppressed)
        self.assertNotIn("email", memory.__dict__)
        self.assertNotIn("customer_name", memory.__dict__)

    def test_upserts_same_token_occasion_and_day(self):
        first = self.remember(lead_days=7)
        second = self.remember(lead_days=14)
        self.assertEqual(first.memory_id, second.memory_id)
        self.assertEqual(14, second.lead_days)
        self.assertEqual(1, len(self.service.store.memories))

    def test_due_reminder_uses_approved_template_only(self):
        self.remember()
        due = self.service.due_reminders(on_date=date(2026, 8, 22))
        self.assertEqual(1, len(due))
        reminder = due[0]
        self.assertEqual("due", reminder.status)
        self.assertEqual("2026-08-29", reminder.due_on)
        self.assertEqual("birthday", reminder.template_id)
        self.assertEqual(APPROVED_TEMPLATES["birthday"], reminder.message)

    def test_outside_lead_window_is_not_due(self):
        self.remember(month_day="12-25", lead_days=7)
        self.assertEqual((), self.service.due_reminders(on_date=date(2026, 8, 22)))

    def test_suppress_hides_future_reminders(self):
        memory = self.remember()
        self.service.suppress(memory.memory_id)
        self.assertEqual((), self.service.due_reminders(on_date=date(2026, 8, 22)))

    def test_rejects_pii_and_unknown_fields(self):
        with self.assertRaises(CrmValidationError):
            self.remember(email="mom@example.invalid")
        with self.assertRaises(CrmValidationError):
            self.remember(customer_name="Ada")
        with self.assertRaises(CrmValidationError):
            self.remember(stripe_customer_id="cus_123")
        with self.assertRaises(CrmValidationError):
            self.remember(nickname="Ada")
        self.assertEqual({}, self.service.store.memories)

    def test_rejects_email_like_browser_token(self):
        with self.assertRaises(CrmValidationError):
            self.remember(browser_token="shopper@example.invalid")

    def test_rejects_unknown_occasion_and_invalid_day(self):
        with self.assertRaises(CrmValidationError):
            self.remember(occasion="graduation")
        with self.assertRaises(CrmValidationError):
            self.remember(month_day="02-30")
        with self.assertRaises(CrmValidationError):
            self.remember(lead_days=0)

    def test_feb_29_clamps_on_non_leap_year(self):
        self.assertEqual(date(2026, 2, 28), next_annual_occurrence("02-29", date(2026, 2, 1)))
        self.assertEqual(date(2028, 2, 29), next_annual_occurrence("02-29", date(2028, 2, 1)))

    def test_module_does_not_import_stripe_or_payment(self):
        source = inspect.getsource(sys.modules["aea_platform.crm"])
        self.assertNotIn("import stripe", source)
        self.assertNotIn("from stripe", source)
        self.assertNotIn("aea_platform.payment", source)
        self.assertNotIn("from .payment", source)


if __name__ == "__main__":
    unittest.main()
