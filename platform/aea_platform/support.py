from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

QUESTION_MAX_LENGTH = 500
NO_APPROVED_ANSWER = (
    "I do not have approved information for that question. A florist can help you further."
)
ESCALATION_REASONS = frozenset({
    "unresolved_request",
    "order_issue",
    "delivery_issue",
    "product_question",
})
ESCALATION_ACKNOWLEDGEMENT = (
    "A florist has received your request and will follow up. "
    "You can keep using this workspace in the meantime."
)


class SupportValidationError(ValueError):
    """A support question is missing or malformed."""


@dataclass(frozen=True)
class ApprovedAnswer:
    keywords: frozenset[str]
    answer: str
    source_references: tuple[str, ...]


# Reference approved knowledge base: FAQ plus product and policy facts, each
# grounded in an approved source. Not an authoritative content system.
REFERENCE_KNOWLEDGE: tuple[ApprovedAnswer, ...] = (
    ApprovedAnswer(frozenset({"deliver", "delivery", "arrive", "when", "ship"}),
        "Standard orders placed before 2 PM are delivered the same day; later orders arrive the next day.",
        ("policy:delivery",)),
    ApprovedAnswer(frozenset({"return", "refund", "cancel", "change"}),
        "Fresh-flower orders can be changed or cancelled up to 24 hours before the delivery window.",
        ("policy:returns",)),
    ApprovedAnswer(frozenset({"care", "fresh", "last", "water", "vase", "wilt"}),
        "Keep the arrangement in clean water away from direct sun and refresh the water every two days.",
        ("product:care",)),
    ApprovedAnswer(frozenset({"substitute", "substitution", "availability", "unavailable"}),
        "If a stem is unavailable we substitute a similar flower of equal or greater value, preserving the style.",
        ("policy:substitution",)),
    ApprovedAnswer(frozenset({"card", "message", "note", "gift"}),
        "A physical card message is included at no extra charge; add it during product selection.",
        ("policy:card-message",)),
)


class SupportService:
    """Approved FAQ answers (FR-005/FR-009) and thin human escalation (FR-006).

    FAQ answers are drawn only from the approved knowledge base; an unmatched
    question returns a safe no-information answer rather than a fabricated one
    and publishes `support.faq.answered`. Human escalation records a governed
    `support.escalation.requested` command (T-09) with an opaque session
    reference and an allowlisted reason — not a CRM ticket (FR-016/FR-017).
    """

    def __init__(self, store, *, knowledge=None, retriever=None,
                 new_id: Callable[[], uuid.UUID] | None = None, now=None):
        self.store = store
        self.knowledge = tuple(knowledge if knowledge is not None else REFERENCE_KNOWLEDGE)
        self.retriever = retriever
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def answer(self, *, session_id: str, question, correlation_id: str,
               subject_reference: str, context_version: int) -> dict:
        text = self._question(question)
        match = self._match(text)
        if match is None and self.retriever is not None:
            match = self._from_retrieval(text)
        if match is None:
            result = {"answer": NO_APPROVED_ANSWER, "approved_source_references": [],
                      "matched": False}
        else:
            result = {"answer": match.answer,
                      "approved_source_references": list(match.source_references),
                      "matched": True}
        self.store.record_answer(
            session_id=session_id, answer=result["answer"],
            approved_source_references=result["approved_source_references"],
            message_id=str(self.new_id()), correlation_id=correlation_id,
            subject_reference=subject_reference,
            published_at=self.now().astimezone(timezone.utc), context_version=context_version)
        return result

    def escalate(self, *, session_id: str, reason, correlation_id: str,
                 subject_reference: str, context_version: int) -> dict:
        """Record a T-09 human-escalation request (FR-006).

        Payload is least-data: allowlisted reason plus an opaque session
        context reference. Raw contact, address, and payment fields are not
        accepted (NFR-017).
        """
        escalation_reason = self._reason(reason)
        message_id = str(self.new_id())
        self.store.record_escalation(
            session_id=session_id, escalation_reason=escalation_reason,
            context_reference=session_id, message_id=message_id,
            correlation_id=correlation_id, subject_reference=subject_reference,
            published_at=self.now().astimezone(timezone.utc),
            context_version=context_version)
        return {
            "accepted": True,
            "code": "escalation_recorded",
            "message_id": message_id,
            "acknowledgement": ESCALATION_ACKNOWLEDGEMENT,
            "escalation_reason": escalation_reason,
        }

    def _match(self, text: str) -> ApprovedAnswer | None:
        tokens = set(text.lower().replace("?", " ").replace(".", " ").split())
        best, best_score = None, 0
        for entry in self.knowledge:
            score = len(entry.keywords & tokens)
            if score > best_score:
                best, best_score = entry, score
        return best if best_score > 0 else None

    def _from_retrieval(self, text: str) -> ApprovedAnswer | None:
        """Optional candidate source. Never replaces approved answer text.

        Vector-only nearest neighbors cannot become answers (ADR-015): a hit
        must also have a keyword/FTS rank and map to this service's approved
        knowledge. Live InternalOrchestrationApp does not wire a retriever.
        """
        allowed = []
        by_ref: dict[str, ApprovedAnswer] = {}
        for entry in self.knowledge:
            for reference in entry.source_references:
                by_ref[reference] = entry
                if reference not in allowed:
                    allowed.append(reference)
        hits = self.retriever.retrieve(text, allowed_source_references=tuple(allowed))
        for hit in hits:
            if getattr(hit, "keyword_rank", None) is None:
                continue
            entry = by_ref.get(getattr(hit, "source_reference", None))
            if entry is not None:
                return entry
        return None

    @staticmethod
    def _question(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise SupportValidationError("question is required")
        text = value.strip()
        if (len(text) > QUESTION_MAX_LENGTH
                or any(ord(character) < 32 and character not in "\n\t" for character in text)):
            raise SupportValidationError("question is invalid")
        return text

    @staticmethod
    def _reason(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise SupportValidationError("escalation reason is required")
        reason = value.strip()
        if reason not in ESCALATION_REASONS:
            raise SupportValidationError("escalation reason is invalid")
        return reason
