"""
Privacy-Preserving Pseudonymous CRM & Customer Intelligence Engine (ADR-020).

Provides least-data customer relationship intelligence without storing plaintext PII.
Enforces Zero-PII (ADR-013 / NFR-017) and 14-day ephemeral fulfillment shredding.
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import os
import uuid
from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Sequence

# Retention window for zero-PII occasion memory. Reminders are annually
# recurring, so ~13 months since the last update covers a full yearly cycle
# plus margin; memory untouched beyond this is purged (privacy lifecycle,
# NFR-017). Overridable by the operational purge job.
DEFAULT_RETENTION_DAYS = 400
ENGAGEMENT_EXPORT_FORMATS = frozenset({"csv", "json"})
ENGAGEMENT_EXPORT_TOTAL_KEYS = (
    "memory_count",
    "unique_browsers",
    "upcoming_within_days",
    "lookahead_days",
)
OUTBOX_STATUS_DRY_RUN = "dry_run"
OUTBOX_SEND_NOT_SENT = "not_sent"
OUTBOX_SEND_NOT_IMPLEMENTED = "not_implemented"
OUTBOX_COPY_AI = "ai"
OUTBOX_COPY_TEMPLATE = "template"


def format_engagement_export(
    analytics: dict[str, Any], *, export_format: str = "csv"
) -> dict[str, Any]:
    """Serialize zero-PII engagement aggregates for operator download.

    Emits counts and categorical cohort keys only. Never includes hashes,
    session ids, subject references, or contact fields (ADR-020 / NFR-017).
    """
    fmt = (export_format or "csv").strip().lower()
    if fmt not in ENGAGEMENT_EXPORT_FORMATS:
        raise CrmValidationError("format must be csv or json")

    def _cohorts(items, name_key, *, month=False) -> list[dict[str, Any]]:
        shaped: list[dict[str, Any]] = []
        for item in items or []:
            if not isinstance(item, dict):
                continue
            try:
                count = int(item.get("count") or 0)
            except (TypeError, ValueError):
                continue
            if count < 1:
                continue
            if month:
                try:
                    month_value = int(item.get("event_month"))
                except (TypeError, ValueError):
                    continue
                if 1 <= month_value <= 12:
                    shaped.append({"event_month": month_value, "count": count})
                continue
            name = item.get(name_key)
            if not isinstance(name, str) or not name.strip() or len(name) > 64:
                continue
            shaped.append({name_key: name.strip().lower(), "count": count})
        return shaped

    def _int(value, default=0) -> int:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return default
        return int(value)

    lookahead = _int(analytics.get("lookahead_days"), 30)
    if lookahead < 1 or lookahead > 366:
        lookahead = 30
    payload = {
        "memory_count": max(0, _int(analytics.get("memory_count"))),
        "unique_browsers": max(0, _int(analytics.get("unique_browsers"))),
        "upcoming_within_days": max(0, _int(analytics.get("upcoming_within_days"))),
        "lookahead_days": lookahead,
        "occasion_cohorts": _cohorts(analytics.get("occasion_cohorts"), "occasion_type"),
        "relation_cohorts": _cohorts(analytics.get("relation_cohorts"), "recipient_relation"),
        "event_month_cohorts": _cohorts(
            analytics.get("event_month_cohorts"), "event_month", month=True),
    }

    if fmt == "json":
        return {
            "format": "json",
            "filename": "florist-engagement-cohorts.json",
            "content_type": "application/json",
            "body": json.dumps(payload, separators=(",", ":"), sort_keys=True),
        }

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["section", "key", "count"])
    for key in ENGAGEMENT_EXPORT_TOTAL_KEYS:
        writer.writerow(["totals", key, payload[key]])
    for item in payload["occasion_cohorts"]:
        writer.writerow(["occasion", item["occasion_type"], item["count"]])
    for item in payload["relation_cohorts"]:
        writer.writerow(["relation", item["recipient_relation"], item["count"]])
    for item in payload["event_month_cohorts"]:
        writer.writerow(["event_month", item["event_month"], item["count"]])
    return {
        "format": "csv",
        "filename": "florist-engagement-cohorts.csv",
        "content_type": "text/csv; charset=utf-8",
        "body": buffer.getvalue(),
    }


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


@dataclass(frozen=True)
class ReminderOutboxItem:
    """Least-data FR-016 dry-run outbox row. No contact fields."""

    outbox_id: str
    occasion_type: str
    recipient_relation: str
    days_until_event: int
    reminder_text: str
    copy_source: str
    status: str
    send_disposition: str
    occasion_year: int


def format_reminder_text(*, occasion_type: str, recipient_relation: str,
                         days_until_event: int) -> str:
    """Deterministic FR-016 pull-card template (fail-closed fallback)."""
    occasion_title = str(occasion_type).strip().title()
    relation_title = str(recipient_relation).strip().title()
    if days_until_event == 0:
        return f"Today is {relation_title}'s {occasion_title}! 1-click same-day flower order."
    return f"Upcoming: {relation_title}'s {occasion_title} in {days_until_event} days."


class EngagementCrmService:
    """Zero-PII occasion memory, pull reminders, and aggregate analytics (FR-016 / FR-017).

    FR-016 leftover after #428 is a live outbound channel. In-session
    `#need-reminder` copy may be AI-authored when a copy_author is wired;
    this service always fail-closes to format_reminder_text. Upcoming
    occasions enqueue least-data dry-run outbox rows (status=dry_run /
    not_sent). attempt_send is stubbed fail-closed and never delivers.
    FR-017 here is manager-visible categorical counts — not staff live chat
    and not a PII customer list.
    """

    def __init__(self, store, *, now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None,
                 copy_author: Any = None):
        self.store = store
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4
        self.copy_author = copy_author

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

        recorded = {
            "memory_id": memory_id,
            "browser_hash": browser_hash.strip(),
            "occasion_type": cleaned_occasion,
            "event_month": event_month,
            "event_day": event_day,
            "recipient_relation": cleaned_relation,
        }
        stored = self._stored_occasion_row(
            browser_hash=recorded["browser_hash"],
            occasion_type=cleaned_occasion,
            recipient_relation=cleaned_relation,
        )
        if stored is not None:
            self._enqueue_row_if_upcoming(stored)
            recorded["memory_id"] = str(stored["memory_id"])
        return recorded

    def _days_until_event(self, month: int, day: int) -> int:
        """Days until the next annual occurrence of month/day (Feb 29 → 28)."""
        today = self.now().astimezone(timezone.utc).date()
        current_year = today.year
        try:
            event_date = datetime(current_year, month, day, tzinfo=timezone.utc).date()
        except ValueError:
            event_date = datetime(current_year, month, 28, tzinfo=timezone.utc).date()
        if event_date < today:
            try:
                event_date = datetime(current_year + 1, month, day, tzinfo=timezone.utc).date()
            except ValueError:
                event_date = datetime(current_year + 1, month, 28, tzinfo=timezone.utc).date()
        return (event_date - today).days

    def _authored_or_template(self, *, occasion_type: str, recipient_relation: str,
                              days_until_event: int) -> str:
        text, _source = self._authored_copy(
            occasion_type=occasion_type, recipient_relation=recipient_relation,
            days_until_event=days_until_event)
        return text

    def _authored_copy(self, *, occasion_type: str, recipient_relation: str,
                       days_until_event: int) -> tuple[str, str]:
        """Return (copy, source). Author success is ai; every failure is template."""
        template = format_reminder_text(
            occasion_type=occasion_type, recipient_relation=recipient_relation,
            days_until_event=days_until_event)
        author = self.copy_author
        if author is None:
            return template, OUTBOX_COPY_TEMPLATE
        try:
            if hasattr(author, "author"):
                text = author.author(
                    occasion_type=occasion_type, recipient_relation=recipient_relation,
                    days_until_event=days_until_event)
            else:
                text = author(
                    occasion_type=occasion_type, recipient_relation=recipient_relation,
                    days_until_event=days_until_event)
        except Exception:
            return template, OUTBOX_COPY_TEMPLATE
        if not isinstance(text, str) or not text.strip():
            return template, OUTBOX_COPY_TEMPLATE
        return text.strip(), OUTBOX_COPY_AI

    def _next_occurrence_year(self, month: int, day: int) -> int:
        today = self.now().astimezone(timezone.utc).date()
        try:
            event_date = datetime(today.year, month, day, tzinfo=timezone.utc).date()
        except ValueError:
            event_date = datetime(today.year, month, 28, tzinfo=timezone.utc).date()
        if event_date < today:
            return today.year + 1
        return today.year

    def _stored_occasion_row(self, *, browser_hash: str, occasion_type: str,
                             recipient_relation: str) -> dict | None:
        for row in self.store.list_occasion_memories(browser_hash=browser_hash):
            if (str(row.get("occasion_type")) == occasion_type
                    and str(row.get("recipient_relation")) == recipient_relation):
                return row
        return None

    def _enqueue_row_if_upcoming(self, row: dict, *, lookahead_days: int = 30) -> str | None:
        """Persist a dry-run outbox row when the annual occurrence is in lookahead."""
        month = int(row["event_month"])
        day = int(row["event_day"])
        days_until = self._days_until_event(month, day)
        if not (0 <= days_until <= lookahead_days):
            return None
        occasion = str(row["occasion_type"])
        relation = str(row["recipient_relation"])
        reminder_text, copy_source = self._authored_copy(
            occasion_type=occasion, recipient_relation=relation,
            days_until_event=days_until)
        created_at = self.now().astimezone(timezone.utc)
        return self.store.upsert_reminder_outbox(
            outbox_id=str(self.new_id()),
            memory_id=str(row["memory_id"]),
            occasion_year=self._next_occurrence_year(month, day),
            occasion_type=occasion,
            recipient_relation=relation,
            days_until_event=days_until,
            reminder_text=reminder_text,
            copy_source=copy_source,
            status=OUTBOX_STATUS_DRY_RUN,
            send_disposition=OUTBOX_SEND_NOT_SENT,
            created_at=created_at,
        )

    def enqueue_upcoming_dry_run(self, *, lookahead_days: int = 30) -> dict[str, Any]:
        """Scan occasion memory and enqueue least-data dry-run outbox rows.

        Operator-triggered. Not a cron that delivers. No contact fields.
        """
        if (not isinstance(lookahead_days, int) or isinstance(lookahead_days, bool)
                or lookahead_days < 1 or lookahead_days > 366):
            raise CrmValidationError("lookahead_days must be an integer between 1 and 366")
        processed = 0
        for row in self.store.list_all_occasion_memories():
            if self._enqueue_row_if_upcoming(row, lookahead_days=lookahead_days):
                processed += 1
        listed = self.list_reminder_outbox(lookahead_days=lookahead_days)
        listed["enqueued"] = processed
        return listed

    def list_reminder_outbox_items(self) -> list[ReminderOutboxItem]:
        rows = self.store.list_reminder_outbox()
        items: list[ReminderOutboxItem] = []
        for row in rows:
            items.append(ReminderOutboxItem(
                outbox_id=str(row["outbox_id"]),
                occasion_type=str(row["occasion_type"]),
                recipient_relation=str(row["recipient_relation"]),
                days_until_event=int(row["days_until_event"]),
                reminder_text=str(row["reminder_text"]),
                copy_source=str(row["copy_source"]),
                status=str(row["status"]),
                send_disposition=str(row["send_disposition"]),
                occasion_year=int(row["occasion_year"]),
            ))
        items.sort(key=lambda item: (item.days_until_event, item.occasion_type,
                                     item.recipient_relation, item.outbox_id))
        return items

    def list_reminder_outbox(self, *, lookahead_days: int = 30) -> dict[str, Any]:
        """Operator-visible dry-run counts and list. No contact PII."""
        if (not isinstance(lookahead_days, int) or isinstance(lookahead_days, bool)
                or lookahead_days < 1 or lookahead_days > 366):
            raise CrmValidationError("lookahead_days must be an integer between 1 and 366")
        items = self.list_reminder_outbox_items()
        not_sent = sum(1 for item in items if item.send_disposition == OUTBOX_SEND_NOT_SENT)
        not_implemented = sum(
            1 for item in items if item.send_disposition == OUTBOX_SEND_NOT_IMPLEMENTED)
        return {
            "pending_dry_run": len(items),
            "not_sent": not_sent,
            "not_implemented": not_implemented,
            "lookahead_days": lookahead_days,
            "items": [self._operator_outbox_item(item) for item in items],
        }

    @staticmethod
    def _operator_outbox_item(item: ReminderOutboxItem) -> dict[str, Any]:
        return {
            "outbox_id": item.outbox_id,
            "occasion_type": item.occasion_type,
            "recipient_relation": item.recipient_relation,
            "days_until_event": item.days_until_event,
            "reminder_text": item.reminder_text,
            "copy_source": item.copy_source,
            "status": item.status,
            "send_disposition": item.send_disposition,
            "occasion_year": item.occasion_year,
        }

    def attempt_send(self, *, outbox_id: str) -> dict[str, Any]:
        """Stub fail-closed send. Never delivers. Marks not_implemented.

        Parent #35 leftover is a live outbound channel. This method is the
        documented send path and must stay dry_run / not_implemented.
        """
        clean_id = (outbox_id or "").strip()
        try:
            clean_id = str(uuid.UUID(clean_id))
        except (ValueError, TypeError, AttributeError) as exc:
            raise CrmValidationError("valid outbox_id is required") from exc
        row = self.store.get_reminder_outbox(outbox_id=clean_id)
        if row is None:
            raise CrmValidationError("reminder outbox row not found")
        updated_at = self.now().astimezone(timezone.utc)
        self.store.mark_reminder_outbox_not_implemented(
            outbox_id=clean_id, updated_at=updated_at)
        refreshed = self.store.get_reminder_outbox(outbox_id=clean_id) or row
        return {
            "code": "not_implemented",
            "status": OUTBOX_STATUS_DRY_RUN,
            "send_disposition": OUTBOX_SEND_NOT_IMPLEMENTED,
            "sent": False,
            "outbox_id": str(refreshed["outbox_id"]),
            "occasion_type": str(refreshed["occasion_type"]),
            "recipient_relation": str(refreshed["recipient_relation"]),
            "days_until_event": int(refreshed["days_until_event"]),
            "reminder_text": str(refreshed["reminder_text"]),
            "copy_source": str(refreshed["copy_source"]),
        }

    def get_reminders(self, *, browser_hash: str, lookahead_days: int = 30) -> list[OccasionReminder]:
        """Compute upcoming annual recurring occasion reminders (FR-016).

        Presence is unchanged from #420 (lookahead + least-data). The soonest
        card line may be AI-authored when copy_author is wired; every other
        item and every author failure stay on format_reminder_text. Pull only.
        """
        if not isinstance(browser_hash, str) or len(browser_hash.strip()) != 64:
            raise CrmValidationError("valid 64-char browser hash is required")

        rows = self.store.list_occasion_memories(browser_hash=browser_hash.strip())
        reminders: list[OccasionReminder] = []

        for row in rows:
            month = row["event_month"]
            day = row["event_day"]
            days_until = self._days_until_event(month, day)

            if 0 <= days_until <= lookahead_days:
                occasion = str(row["occasion_type"])
                relation = str(row["recipient_relation"])
                reminders.append(OccasionReminder(
                    memory_id=str(row["memory_id"]),
                    browser_hash=str(row["browser_hash"]),
                    occasion_type=occasion,
                    event_month=month,
                    event_day=day,
                    recipient_relation=relation,
                    days_until_event=days_until,
                    reminder_text=format_reminder_text(
                        occasion_type=occasion, recipient_relation=relation,
                        days_until_event=days_until),
                ))

        reminders.sort(key=lambda r: r.days_until_event)
        if reminders:
            first = reminders[0]
            reminders[0] = replace(
                first,
                reminder_text=self._authored_or_template(
                    occasion_type=first.occasion_type,
                    recipient_relation=first.recipient_relation,
                    days_until_event=first.days_until_event,
                ),
            )
        return reminders

    def get_engagement_analytics(self, *, lookahead_days: int = 30) -> dict[str, Any]:
        """Zero-PII occasion cohorts for the florist operator console (FR-017).

        Returns counts and categorical keys only. Never includes browser hashes,
        session ids, subject references, names, or addresses (ADR-020 / NFR-017).
        """
        if (not isinstance(lookahead_days, int) or isinstance(lookahead_days, bool)
                or lookahead_days < 1 or lookahead_days > 366):
            raise CrmValidationError("lookahead_days must be an integer between 1 and 366")

        rows = self.store.list_all_occasion_memories()
        browsers: set[str] = set()
        occasion_counts: Counter[str] = Counter()
        relation_counts: Counter[str] = Counter()
        month_counts: Counter[int] = Counter()
        upcoming = 0
        for row in rows:
            browsers.add(str(row.get("browser_hash") or ""))
            occasion = str(row.get("occasion_type") or "").strip()
            relation = str(row.get("recipient_relation") or "").strip()
            month = int(row["event_month"])
            day = int(row["event_day"])
            if occasion:
                occasion_counts[occasion] += 1
            if relation:
                relation_counts[relation] += 1
            month_counts[month] += 1
            if 0 <= self._days_until_event(month, day) <= lookahead_days:
                upcoming += 1
        browsers.discard("")

        def _named_cohorts(counter: Counter[str], key: str) -> list[dict[str, Any]]:
            return [{key: name, "count": count}
                    for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))]

        return {
            "memory_count": len(rows),
            "unique_browsers": len(browsers),
            "upcoming_within_days": upcoming,
            "lookahead_days": lookahead_days,
            "occasion_cohorts": _named_cohorts(occasion_counts, "occasion_type"),
            "relation_cohorts": _named_cohorts(relation_counts, "recipient_relation"),
            "event_month_cohorts": [
                {"event_month": month, "count": count}
                for month, count in sorted(month_counts.items())
            ],
        }

    def export_engagement_analytics(
        self, *, export_format: str = "csv", lookahead_days: int = 30
    ) -> dict[str, Any]:
        """Operator campaign export of the same zero-PII cohort counts (FR-017).

        CSV or JSON of counts and categorical keys only. Not a per-customer
        list and not an ML model.
        """
        analytics = self.get_engagement_analytics(lookahead_days=lookahead_days)
        return format_engagement_export(analytics, export_format=export_format)

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
