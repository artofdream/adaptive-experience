"""Thin annual occasion reminders (M12 Engagement CRM).

Governed intake from research/daily-briefs/2026-08-21.md: implement
platform/aea_platform/crm.py annual occasion reminders.

Existing published requirement for those reminders is FR-016 (Future in the
workbook). This slice does not implement the full CRM product, staff live
chat, ticketing, or engagement analytics. Reminder copy is approved-template
only (ADR-016). Payments stay mockup — this module does not import or call
Stripe.
"""

from __future__ import annotations

import calendar
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Callable

ANNUAL_OCCASIONS = frozenset({"birthday", "anniversary", "event"})
MONTH_DAY_RE = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
EMAIL_LIKE_RE = re.compile(r"[^@\s]+@[^@\s]+")
LEAD_DAYS_MIN = 1
LEAD_DAYS_MAX = 30
DEFAULT_LEAD_DAYS = 7

APPROVED_TEMPLATES = {
    "birthday": "An upcoming birthday occasion is due for a reminder.",
    "anniversary": "An upcoming anniversary occasion is due for a reminder.",
    "event": "An upcoming event occasion is due for a reminder.",
}

FORBIDDEN_FIELDS = frozenset({
    "access_token", "address", "answer", "api_key", "authorization",
    "card_number", "cardholder_name", "customer_email", "customer_name", "cvv",
    "email", "message", "message_text", "password", "payload", "phone",
    "question", "recipient_address", "recipient_email", "recipient_name",
    "refresh_token", "stripe", "stripe_customer_id", "stripe_key",
})

REMEMBER_FIELDS = frozenset({
    "browser_token", "occasion", "month_day", "lead_days",
})


class CrmValidationError(ValueError):
    """An occasion reminder was rejected (fail-closed)."""


@dataclass(frozen=True)
class OccasionMemory:
    memory_id: str
    browser_token: str
    occasion: str
    month_day: str
    lead_days: int
    created_at: str
    suppressed: bool = False


@dataclass(frozen=True)
class ReminderCandidate:
    reminder_id: str
    memory_id: str
    occasion: str
    month_day: str
    status: str
    template_id: str
    message: str
    due_on: str


class MemoryCrmStore:
    """In-process store used by unit tests and default service wiring."""

    def __init__(self):
        self.memories: dict[str, OccasionMemory] = {}

    def upsert(self, memory: OccasionMemory) -> OccasionMemory:
        self.memories[memory.memory_id] = memory
        return memory

    def get(self, memory_id: str) -> OccasionMemory | None:
        return self.memories.get(memory_id)

    def list_active(self) -> list[OccasionMemory]:
        return [row for row in self.memories.values() if not row.suppressed]

    def find(self, *, browser_token: str, occasion: str,
             month_day: str) -> OccasionMemory | None:
        for row in self.memories.values():
            if (row.browser_token == browser_token
                    and row.occasion == occasion
                    and row.month_day == month_day
                    and not row.suppressed):
                return row
        return None


class EngagementCrmService:
    """Deterministic annual occasion reminders bound to an opaque browser token."""

    def __init__(self, store=None, *,
                 new_id: Callable[[], uuid.UUID] | None = None,
                 now: Callable[[], datetime] | None = None):
        self.store = store or MemoryCrmStore()
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def remember_occasion(self, **fields) -> OccasionMemory:
        self._reject_sensitive(fields)
        unknown = sorted(set(fields) - REMEMBER_FIELDS)
        if unknown:
            raise CrmValidationError(f"occasion memory has unknown fields: {unknown}")
        token = self._browser_token(fields.get("browser_token"))
        occasion = self._occasion(fields.get("occasion"))
        month_day = self._month_day(fields.get("month_day"))
        lead_days = self._lead_days(fields.get("lead_days", DEFAULT_LEAD_DAYS))
        existing = self.store.find(
            browser_token=token, occasion=occasion, month_day=month_day)
        created_at = (
            existing.created_at if existing
            else self.now().astimezone(timezone.utc).isoformat()
        )
        memory = OccasionMemory(
            memory_id=existing.memory_id if existing else str(self.new_id()),
            browser_token=token,
            occasion=occasion,
            month_day=month_day,
            lead_days=lead_days,
            created_at=created_at,
        )
        return self.store.upsert(memory)

    def suppress(self, memory_id: str) -> OccasionMemory:
        if not isinstance(memory_id, str) or not memory_id.strip():
            raise CrmValidationError("memory ID is required")
        current = self.store.get(memory_id.strip())
        if current is None:
            raise CrmValidationError("occasion memory was not found")
        updated = OccasionMemory(
            memory_id=current.memory_id,
            browser_token=current.browser_token,
            occasion=current.occasion,
            month_day=current.month_day,
            lead_days=current.lead_days,
            created_at=current.created_at,
            suppressed=True,
        )
        return self.store.upsert(updated)

    def due_reminders(self, *, on_date: date | None = None) -> tuple[ReminderCandidate, ...]:
        today = on_date or self.now().astimezone(timezone.utc).date()
        if not isinstance(today, date):
            raise CrmValidationError("on_date must be a date")
        reminders: list[ReminderCandidate] = []
        for memory in sorted(
            self.store.list_active(),
            key=lambda row: (row.month_day, row.occasion, row.memory_id),
        ):
            due_on = next_annual_occurrence(memory.month_day, today)
            days_until = (due_on - today).days
            if days_until > memory.lead_days:
                continue
            reminders.append(ReminderCandidate(
                reminder_id=str(self.new_id()),
                memory_id=memory.memory_id,
                occasion=memory.occasion,
                month_day=memory.month_day,
                status="due",
                template_id=memory.occasion,
                message=APPROVED_TEMPLATES[memory.occasion],
                due_on=due_on.isoformat(),
            ))
        return tuple(reminders)

    @staticmethod
    def _reject_sensitive(fields: dict) -> None:
        leaked = sorted(set(fields) & FORBIDDEN_FIELDS)
        if leaked:
            raise CrmValidationError(
                f"occasion memories must not include sensitive fields: {leaked}")

    @staticmethod
    def _browser_token(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise CrmValidationError("browser token is required")
        token = value.strip()
        if EMAIL_LIKE_RE.search(token) or any(character.isspace() for character in token):
            raise CrmValidationError("browser token must be an opaque reference")
        if not TOKEN_RE.fullmatch(token):
            raise CrmValidationError("browser token is invalid")
        return token

    @staticmethod
    def _occasion(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise CrmValidationError("occasion is required")
        occasion = value.strip().casefold()
        if occasion not in ANNUAL_OCCASIONS:
            raise CrmValidationError("occasion is not an annual reminder type")
        return occasion

    @staticmethod
    def _month_day(value) -> str:
        if not isinstance(value, str) or not MONTH_DAY_RE.fullmatch(value.strip()):
            raise CrmValidationError("month_day must be MM-DD")
        month_day = value.strip()
        month, day = (int(part) for part in month_day.split("-"))
        # Feb 29 is a valid annual mark; next_annual_occurrence clamps non-leap years.
        if month == 2 and day == 29:
            return month_day
        last = calendar.monthrange(2001, month)[1]
        if day > last:
            raise CrmValidationError("month_day is not a valid calendar day")
        return month_day

    @staticmethod
    def _lead_days(value) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise CrmValidationError("lead_days must be an integer")
        if value < LEAD_DAYS_MIN or value > LEAD_DAYS_MAX:
            raise CrmValidationError(
                f"lead_days must be between {LEAD_DAYS_MIN} and {LEAD_DAYS_MAX}")
        return value


def next_annual_occurrence(month_day: str, today: date) -> date:
    """Return the next calendar date for an annual MM-DD, including today."""
    month, day = (int(part) for part in month_day.split("-"))
    candidate = _safe_date(today.year, month, day)
    if candidate < today:
        candidate = _safe_date(today.year + 1, month, day)
    return candidate


def _safe_date(year: int, month: int, day: int) -> date:
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last))
