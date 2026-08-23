"""Engagement CRM & Occasion Memory Service (FR-016 / FR-017 / NFR-017, M12).

Calculates annual recurring occasion dates (Mother's Birthday, Anniversary) and
surfaces proactive reminder signals. Zero-PII compliance (NFR-017): strictly
persists non-PII attributes (browser_hash, occasion_type, event_month/day,
recipient_relation). Raw names, cards, or addresses are never stored.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Sequence


class CrmValidationError(ValueError):
    """Raised when CRM payload attributes violate zero-PII or date rules."""


@dataclass(frozen=True)
class OccasionReminder:
    memory_id: str
    browser_hash: str
    occasion_type: str
    event_month: int
    event_day: int
    recipient_relation: str
    days_until_event: int
    reminder_text: str


class EngagementCrmService:
    """Zero-PII occasion memory and annual recurring reminder engine (FR-016 / FR-017)."""

    def __init__(self, store, *, now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None):
        self.store = store
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

    @staticmethod
    def hash_browser(raw_identifier: str) -> str:
        """Derive opaque 64-char hex fingerprint (zero-PII NFR-017)."""
        if not isinstance(raw_identifier, str) or not raw_identifier.strip():
            raise CrmValidationError("browser identifier is required")
        return hashlib.sha256(raw_identifier.strip().encode("utf-8")).hexdigest()

    def record_occasion(self, *, browser_hash: str, session_id: str,
                        occasion_type: str, event_month: int, event_day: int,
                        recipient_relation: str = "other") -> dict:
        """Persist zero-PII occasion memory (FR-017)."""
        if not isinstance(browser_hash, str) or len(browser_hash.strip()) != 64:
            raise CrmValidationError("valid 64-char browser hash is required")
        if not isinstance(session_id, str) or not session_id.strip():
            raise CrmValidationError("session ID is required")
        if not isinstance(occasion_type, str) or not occasion_type.strip():
            raise CrmValidationError("occasion type is required")
        if not (isinstance(event_month, int) and 1 <= event_month <= 12):
            raise CrmValidationError("event_month must be an integer between 1 and 12")
        if not (isinstance(event_day, int) and 1 <= event_day <= 31):
            raise CrmValidationError("event_day must be an integer between 1 and 31")

        cleaned_occasion = occasion_type.strip().lower()
        cleaned_relation = recipient_relation.strip().lower() if isinstance(recipient_relation, str) else "other"

        memory_id = str(self.new_id())
        created_at = self.now().astimezone(timezone.utc)

        self.store.upsert_occasion_memory(
            memory_id=memory_id,
            browser_hash=browser_hash.strip(),
            session_id=session_id.strip(),
            occasion_type=cleaned_occasion,
            event_month=event_month,
            event_day=event_day,
            recipient_relation=cleaned_relation,
            created_at=created_at,
        )

        return {
            "memory_id": memory_id,
            "browser_hash": browser_hash.strip(),
            "occasion_type": cleaned_occasion,
            "event_month": event_month,
            "event_day": event_day,
            "recipient_relation": cleaned_relation,
        }

    def get_reminders(self, *, browser_hash: str, lookahead_days: int = 30) -> list[OccasionReminder]:
        """Compute upcoming annual recurring occasion reminders (FR-016)."""
        if not isinstance(browser_hash, str) or len(browser_hash.strip()) != 64:
            raise CrmValidationError("valid 64-char browser hash is required")

        today = self.now().astimezone(timezone.utc).date()
        current_year = today.year

        rows = self.store.list_occasion_memories(browser_hash=browser_hash.strip())
        reminders: list[OccasionReminder] = []

        for row in rows:
            month = row["event_month"]
            day = row["event_day"]

            # Compute next occurrence date
            try:
                event_date = datetime(current_year, month, day, tzinfo=timezone.utc).date()
            except ValueError:
                # Leap year handling (Feb 29 fallback to Feb 28)
                event_date = datetime(current_year, month, 28, tzinfo=timezone.utc).date()

            if event_date < today:
                try:
                    event_date = datetime(current_year + 1, month, day, tzinfo=timezone.utc).date()
                except ValueError:
                    event_date = datetime(current_year + 1, month, 28, tzinfo=timezone.utc).date()

            days_until = (event_date - today).days

            if 0 <= days_until <= lookahead_days:
                occasion_title = row["occasion_type"].title()
                relation_title = row["recipient_relation"].title()
                
                if days_until == 0:
                    text = f"Today is {relation_title}'s {occasion_title}! 1-click same-day flower order."
                else:
                    text = f"Upcoming: {relation_title}'s {occasion_title} in {days_until} days."

                reminders.append(OccasionReminder(
                    memory_id=str(row["memory_id"]),
                    browser_hash=str(row["browser_hash"]),
                    occasion_type=str(row["occasion_type"]),
                    event_month=month,
                    event_day=day,
                    recipient_relation=str(row["recipient_relation"]),
                    days_until_event=days_until,
                    reminder_text=text,
                ))

        reminders.sort(key=lambda r: r.days_until_event)
        return reminders
