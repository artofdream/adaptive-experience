from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable

PATHS = frozenset({"intent", "faq"})
OUTCOMES = frozenset({"ok", "fallback", "unmatched", "error"})
ERROR_CODES = frozenset({
    "provider_unavailable",
    "invalid_output",
    "unsupported_facets",
    "unapproved_answer",
})
QUALITY_FLAGS = frozenset({
    "approved_source",
    "supported_facets",
    "no_fabrication",
    "degraded",
})
ASSISTANT_MODES = frozenset({"primary", "fallback", "reference"})
EVENT_FIELDS = frozenset({
    "path", "outcome", "error_code", "quality_flags", "assistant_mode", "matched",
})
FORBIDDEN_FIELDS = frozenset({
    "access_token", "address", "answer", "api_key", "authorization",
    "card_number", "cardholder_name", "customer_email", "customer_name", "cvv",
    "email", "message", "message_text", "password", "payload", "phone",
    "question", "recipient_address", "recipient_email", "recipient_name",
    "refresh_token",
})


class QualityTrackingError(ValueError):
    """A quality event or AI-output gate was rejected (fail-closed)."""


class MemoryQualityStore:
    """In-process ring used by unit tests and default service wiring."""

    def __init__(self):
        self.events: list[dict] = []

    def record(self, event: dict) -> None:
        self.events.append(dict(event))

    def summary(self) -> dict:
        return summarize_events(self.events)


def summarize_events(events: list[dict], *, recent_limit: int = 20) -> dict:
    counts = {
        path: {outcome: 0 for outcome in ("ok", "fallback", "unmatched", "error")}
        for path in ("intent", "faq")
    }
    for event in events:
        counts[event["path"]][event["outcome"]] += 1
    recent = []
    for event in reversed(events):
        if event["outcome"] not in {"error", "fallback"}:
            continue
        recent.append({
            "path": event["path"],
            "outcome": event["outcome"],
            "error_code": event.get("error_code"),
            "assistant_mode": event.get("assistant_mode"),
            "quality_flags": list(event.get("quality_flags") or ()),
            "recorded_at": event.get("recorded_at"),
        })
        if len(recent) >= recent_limit:
            break
    return {"paths": ["intent", "faq"], "counts": counts, "recent_errors": recent}


class QualityMonitor:
    """Fail-closed NFR-008 tracker for the live intent and FAQ paths.

    Events are least-data: path, outcome, allowlisted flags/codes, and optional
    assistant mode. Raw prompts, answers, and sensitive fields are rejected
    rather than stored. FAQ answers that are not from approved knowledge fail
    closed instead of being served.
    """

    def __init__(self, store=None, *,
                 new_id: Callable[[], uuid.UUID] | None = None,
                 now: Callable[[], datetime] | None = None):
        self.store = store or MemoryQualityStore()
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def record(self, **fields) -> dict:
        leaked = sorted(set(fields) & FORBIDDEN_FIELDS)
        if leaked:
            raise QualityTrackingError(
                f"quality events must not include sensitive or raw-text fields: {leaked}")
        unknown = sorted(set(fields) - EVENT_FIELDS)
        if unknown:
            raise QualityTrackingError(f"quality event has unknown fields: {unknown}")
        path = fields.get("path")
        outcome = fields.get("outcome")
        if path not in PATHS:
            raise QualityTrackingError("quality path is invalid")
        if outcome not in OUTCOMES:
            raise QualityTrackingError("quality outcome is invalid")
        error_code = fields.get("error_code")
        if error_code is not None and error_code not in ERROR_CODES:
            raise QualityTrackingError("quality error_code is invalid")
        if outcome == "error" and error_code is None:
            raise QualityTrackingError("error outcome requires an error_code")
        if error_code is not None and outcome not in {"error", "fallback"}:
            raise QualityTrackingError("error_code is only valid for error or fallback")
        flags = tuple(fields.get("quality_flags") or ())
        if any(flag not in QUALITY_FLAGS for flag in flags):
            raise QualityTrackingError("quality_flags are invalid")
        mode = fields.get("assistant_mode")
        if mode is not None and mode not in ASSISTANT_MODES:
            raise QualityTrackingError("assistant_mode is invalid")
        matched = fields.get("matched")
        if path == "intent" and mode is None:
            raise QualityTrackingError("intent events require assistant_mode")
        if path == "faq" and matched is None:
            raise QualityTrackingError("faq events require matched")
        if matched is not None and not isinstance(matched, bool):
            raise QualityTrackingError("matched must be a boolean")
        event = {
            "event_id": str(self.new_id()),
            "path": path,
            "outcome": outcome,
            "error_code": error_code,
            "quality_flags": flags,
            "assistant_mode": mode,
            "matched": matched,
            "recorded_at": self.now().astimezone(timezone.utc).isoformat(),
        }
        self.store.record(event)
        return event

    def observe_intent(self, interpreter) -> dict:
        """Record a completed live intent interpretation (NFR-008 first slice)."""
        health = getattr(interpreter, "health", lambda: {
            "available": True, "mode": "reference", "circuit": "closed"})()
        mode = health.get("mode") if isinstance(health, dict) else None
        if mode not in ASSISTANT_MODES:
            mode = getattr(interpreter, "last_mode", "reference")
        if mode not in ASSISTANT_MODES:
            mode = "reference"
        raw_code = getattr(interpreter, "last_error_code", None)
        error_code = raw_code if raw_code in ERROR_CODES else None
        if mode == "fallback":
            return self.record(
                path="intent", outcome="fallback", assistant_mode="fallback",
                error_code=error_code,
                quality_flags=("supported_facets", "degraded"))
        return self.record(
            path="intent", outcome="ok", assistant_mode=mode,
            quality_flags=("supported_facets",))

    def record_intent_error(self, error_code: str, interpreter=None) -> dict:
        mode = "reference"
        if interpreter is not None:
            health = getattr(interpreter, "health", lambda: {})()
            candidate = health.get("mode") if isinstance(health, dict) else None
            if candidate not in ASSISTANT_MODES:
                candidate = getattr(interpreter, "last_mode", "reference")
            if candidate in ASSISTANT_MODES:
                mode = candidate
        return self.record(
            path="intent", outcome="error", assistant_mode=mode,
            error_code=error_code, quality_flags=())

    def assess_faq(self, result: dict, *, approved_answers: dict,
                   unmatched_answer: str) -> dict:
        """Fail closed unless a FAQ result is approved knowledge or the safe unmatched text."""
        if not isinstance(result, dict) or result.get("kind") != "faq":
            raise QualityTrackingError("FAQ quality gate requires a faq result")
        matched = bool(result.get("matched"))
        answer = result.get("answer")
        sources = tuple(result.get("approved_source_references") or ())
        if matched:
            expected_sources = approved_answers.get(answer)
            if (not sources or expected_sources is None
                    or any(reference not in expected_sources for reference in sources)):
                self.record(
                    path="faq", outcome="error", matched=True,
                    error_code="unapproved_answer", quality_flags=())
                raise QualityTrackingError("FAQ answer is not from approved knowledge")
            return self.record(
                path="faq", outcome="ok", matched=True,
                quality_flags=("approved_source", "no_fabrication"))
        if answer != unmatched_answer or sources:
            self.record(
                path="faq", outcome="error", matched=False,
                error_code="unapproved_answer", quality_flags=())
            raise QualityTrackingError("unmatched FAQ must use the safe no-information answer")
        return self.record(
            path="faq", outcome="unmatched", matched=False,
            quality_flags=("no_fabrication",))

    def summary(self) -> dict:
        return self.store.summary()
