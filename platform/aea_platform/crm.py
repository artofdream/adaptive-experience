"""
Privacy-Preserving Pseudonymous CRM & Customer Intelligence Engine (ADR-020).

Provides least-data customer relationship intelligence without storing plaintext PII.
Enforces Zero-PII (ADR-013 / NFR-017) and 14-day ephemeral fulfillment shredding.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Sequence

# Retention window for zero-PII occasion memory. Reminders are annually
# recurring, so ~13 months since the last update covers a full yearly cycle
# plus margin; memory untouched beyond this is purged (privacy lifecycle,
# NFR-017). Overridable by the operational purge job.
DEFAULT_RETENTION_DAYS = 400


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

    def forget(self, *, browser_hash: str) -> int:
        """Erase all occasion memory for a browser (customer opt-out; NFR-017).

        Returns the number of memories removed. Idempotent: forgetting an
        unknown browser hash returns 0.
        """
        if not isinstance(browser_hash, str) or len(browser_hash.strip()) != 64:
            raise CrmValidationError("valid 64-char browser hash is required")
        return int(self.store.delete_occasion_memories(browser_hash=browser_hash.strip()))

    def purge_expired(self, *, retention_days: int = DEFAULT_RETENTION_DAYS) -> int:
        """Purge occasion memory untouched beyond the retention window.

        Time-based privacy lifecycle (NFR-017): rows whose ``updated_at`` is
        older than ``retention_days`` are deleted. Returns the count purged.
        """
        if (not isinstance(retention_days, int) or isinstance(retention_days, bool)
                or retention_days < 1):
            raise CrmValidationError("retention_days must be a positive integer")
        cutoff = self.now().astimezone(timezone.utc) - timedelta(days=retention_days)
        return int(self.store.purge_expired_memories(cutoff=cutoff))


DEFAULT_SUBJECT_SALT = os.environ.get("AEA_CRM_SUBJECT_SALT", "aea-privacy-crm-salt-2026")


def compute_subject_reference(client_identifier: str, salt: str = DEFAULT_SUBJECT_SALT) -> str:
    """Computes deterministic salted HMAC-SHA256 subject reference token."""
    clean_id = (client_identifier or "").strip().encode("utf-8")
    clean_salt = salt.encode("utf-8")
    digest = hmac.new(clean_salt, clean_id, hashlib.sha256).hexdigest()
    return f"sub_{digest[:32]}"


def compute_spend_band(total_amount: float) -> str:
    """Categorizes spend into privacy-preserving spend bands."""
    if total_amount < 50.0:
        return "band_0_50"
    elif total_amount <= 100.0:
        return "band_50_100"
    elif total_amount <= 250.0:
        return "band_100_250"
    else:
        return "band_250_plus"


class CrmService:
    """Manages pseudonymous customer profiles and relationship intelligence."""

    def __init__(self, store: Any, now: Callable[[], datetime] | None = None):
        self.store = store
        self.now = now or (lambda: datetime.now(timezone.utc))

    def record_completed_order(
        self,
        *,
        subject_reference: str,
        order_total: float,
        occasion: str | None = None,
        channel: str = "web",
    ) -> dict[str, Any]:
        """Updates pseudonymous subject profile upon order payment confirmation."""
        clean_ref = (subject_reference or "").strip()
        if not clean_ref:
            raise ValueError("subject_reference is required")

        return self.store.record_crm_order(
            subject_reference=clean_ref,
            order_total=float(order_total),
            occasion=occasion,
            channel=channel,
            now=self.now(),
        )

    def get_subject_insights(self, subject_reference: str) -> dict[str, Any] | None:
        """Retrieves least-data relationship summary for operator console."""
        clean_ref = (subject_reference or "").strip()
        if not clean_ref:
            return None

        profile = self.store.get_crm_profile(clean_ref)
        if not profile:
            return {
                "subject_reference": clean_ref,
                "customer_segment": "new_shopper",
                "total_orders": 0,
                "lifetime_spend_band": "band_0_50",
                "primary_occasion": None,
                "preferred_channel": "web",
            }

        total_orders = int(profile.get("total_orders", 0))
        segment = "frequent_buyer" if total_orders >= 3 else ("returning_buyer" if total_orders > 1 else "new_shopper")

        return {
            "subject_reference": clean_ref,
            "customer_segment": segment,
            "total_orders": total_orders,
            "lifetime_spend_band": profile.get("lifetime_spend_band", "band_0_50"),
            "primary_occasion": profile.get("primary_occasion"),
            "preferred_channel": profile.get("preferred_channel", "web"),
            "first_seen_at": profile.get("first_seen_at"),
            "last_seen_at": profile.get("last_seen_at"),
        }

    def forget_subject(self, subject_reference: str) -> int:
        """Erase a pseudonymous subject profile (subject erasure parity, NFR-017)."""
        clean_ref = (subject_reference or "").strip()
        if not clean_ref:
            raise ValueError("subject_reference is required")
        return int(self.store.delete_subject_profile(subject_reference=clean_ref))

    def purge_expired(self, cutoff: datetime) -> int:
        """Retention sweep of subject profiles not seen since the cutoff (NFR-017)."""
        return int(self.store.purge_expired_subject_profiles(before=cutoff))
