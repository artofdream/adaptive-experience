from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

QUESTION_MAX_LENGTH = 500
NO_APPROVED_ANSWER = (
    "I do not have approved information for that question. A florist can help you further."
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
    """Answer customer questions only from approved product/policy information.

    Satisfies FR-005 (approved product/policy answers, grounded in
    `approved_source_references`) and FR-009 (automated FAQ). Answers are drawn
    only from the approved knowledge base; an unmatched question returns a safe
    no-information answer rather than a fabricated one. It publishes the governed
    `support.faq.answered` event for audit and bus consumers.
    """

    def __init__(self, store, *, knowledge=None,
                 new_id: Callable[[], uuid.UUID] | None = None, now=None):
        self.store = store
        self.knowledge = tuple(knowledge if knowledge is not None else REFERENCE_KNOWLEDGE)
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def answer(self, *, session_id: str, question, correlation_id: str,
               subject_reference: str, context_version: int) -> dict:
        text = self._question(question)
        match = self._match(text)
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

    def _match(self, text: str) -> ApprovedAnswer | None:
        tokens = set(text.lower().replace("?", " ").replace(".", " ").split())
        best, best_score = None, 0
        for entry in self.knowledge:
            score = len(entry.keywords & tokens)
            if score > best_score:
                best, best_score = entry, score
        return best if best_score > 0 else None

    @staticmethod
    def _question(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise SupportValidationError("question is required")
        text = value.strip()
        if (len(text) > QUESTION_MAX_LENGTH
                or any(ord(character) < 32 and character not in "\n\t" for character in text)):
            raise SupportValidationError("question is invalid")
        return text
