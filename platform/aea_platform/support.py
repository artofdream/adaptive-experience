from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from .quality import QualityMonitor

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
SITUATION_STATUS_TOKENS = frozenset({
    "status", "tracking", "track", "delayed", "dispatched", "preparing",
    "delivered", "completed",
})
SITUATION_AVAIL_TOKENS = frozenset({
    "available", "availability", "stock", "inventory", "unavailable", "sold",
})
SITUATION_DELIVERY_HINTS = frozenset({"window", "destination", "slot"})
SITUATION_DELIVERY_GENERIC = frozenset({
    "deliver", "delivery", "arrive", "arriving", "ship",
})
SITUATION_SESSION_HINTS = frozenset({"my", "this", "order", "session"})
NO_ORDER_SITUATION = "This session does not have an order to track yet."
NO_DELIVERY_SITUATION = "This session does not have delivery details yet."
NO_AVAILABILITY_PRODUCT = (
    "Name a catalog product or select one to check current availability."
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
    """Approved FAQ (FR-005/FR-009), situational answers (FR-010), escalation (FR-006).

    FAQ answers are drawn only from the approved knowledge base; an unmatched
    question returns a safe no-information answer rather than a fabricated one
    and publishes `support.faq.answered`. Situational questions about order
    status, session delivery, or product availability are answered from
    supplied session/inventory facts and publish `support.situation.answered`
    — they do not invent tracking or stock. Human escalation records a
    governed `support.escalation.requested` command (T-09).
    """

    def __init__(self, store, *, knowledge=None, retriever=None,
                 new_id: Callable[[], uuid.UUID] | None = None, now=None,
                 quality: QualityMonitor | None = None):
        self.store = store
        self.knowledge = tuple(knowledge if knowledge is not None else REFERENCE_KNOWLEDGE)
        self.retriever = retriever
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.quality = quality or QualityMonitor()

    def lookup(self, question) -> dict:
        """Read-only approved-knowledge match. Does not persist or publish."""
        text = self._question(question)
        match = self._match(text)
        if match is None and self.retriever is not None:
            match = self._from_retrieval(text)
        if match is None:
            return {"kind": "faq", "answer": NO_APPROVED_ANSWER,
                    "approved_source_references": [], "matched": False,
                    "fact_references": []}
        return {"kind": "faq", "answer": match.answer,
                "approved_source_references": list(match.source_references),
                "matched": True, "fact_references": []}

    def answer(self, *, session_id: str, question, correlation_id: str,
               subject_reference: str, context_version: int,
               situation: dict | None = None) -> dict:
        text = self._question(question)
        situational = self._situational_answer(text, situation or {})
        if situational is not None:
            self.store.record_situation(
                session_id=session_id, answer=situational["answer"],
                situation_kind=situational["situation_kind"],
                fact_references=situational["fact_references"],
                message_id=str(self.new_id()), correlation_id=correlation_id,
                subject_reference=subject_reference,
                published_at=self.now().astimezone(timezone.utc),
                context_version=context_version)
            return situational
        result = self.lookup(question)
        self.quality.assess_faq(
            result,
            approved_answers={entry.answer: tuple(entry.source_references)
                              for entry in self.knowledge},
            unmatched_answer=NO_APPROVED_ANSWER)
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

    def _situational_answer(self, text: str, situation: dict) -> dict | None:
        """Answer order/delivery/availability from session facts (FR-010).

        Returns None when the question is not situational so FR-009 FAQ can run.
        Never invents a status, window, or stock figure.
        """
        tokens = set(text.lower().replace("?", " ").replace(".", " ").replace("-", " ").split())
        kind = self._situation_kind(tokens, situation)
        if kind is None:
            return None
        if kind == "order_status":
            return self._order_status_answer(situation.get("order"))
        if kind == "delivery":
            return self._delivery_answer(situation.get("delivery"))
        return self._availability_answer(text, tokens, situation)

    @staticmethod
    def _situation_kind(tokens: set[str], situation: dict) -> str | None:
        if tokens & SITUATION_STATUS_TOKENS or {"where", "order"} <= tokens:
            return "order_status"
        if tokens & SITUATION_AVAIL_TOKENS:
            return "availability"
        delivery_generic = bool(tokens & SITUATION_DELIVERY_GENERIC)
        if tokens & SITUATION_DELIVERY_HINTS:
            return "delivery"
        if delivery_generic and (tokens & SITUATION_SESSION_HINTS or situation.get("delivery")):
            return "delivery"
        return None

    @staticmethod
    def _order_status_answer(order) -> dict:
        if not isinstance(order, dict) or not order.get("order_id"):
            return {
                "kind": "situation", "matched": True, "situation_kind": "order_status",
                "answer": NO_ORDER_SITUATION, "approved_source_references": [],
                "fact_references": [],
            }
        status = order.get("authoritative_status") or order.get("status") or "unknown"
        label = str(status).replace("_", " ")
        return {
            "kind": "situation", "matched": True, "situation_kind": "order_status",
            "answer": f"Your order is currently {label}.",
            "approved_source_references": [],
            "fact_references": ["session:order"],
        }

    @staticmethod
    def _delivery_answer(delivery) -> dict:
        if not isinstance(delivery, dict):
            return {
                "kind": "situation", "matched": True, "situation_kind": "delivery",
                "answer": NO_DELIVERY_SITUATION, "approved_source_references": [],
                "fact_references": [],
            }
        timing = delivery.get("timing") if isinstance(delivery.get("timing"), dict) else {}
        date = timing.get("date")
        window = timing.get("window")
        destination = delivery.get("destination_reference")
        if not date or not window:
            return {
                "kind": "situation", "matched": True, "situation_kind": "delivery",
                "answer": NO_DELIVERY_SITUATION, "approved_source_references": [],
                "fact_references": [],
            }
        dest = f" to destination {destination}" if isinstance(destination, str) and destination else ""
        return {
            "kind": "situation", "matched": True, "situation_kind": "delivery",
            "answer": f"Delivery is scheduled for {date} ({window}){dest}.",
            "approved_source_references": [],
            "fact_references": ["session:delivery"],
        }

    def _availability_answer(self, text: str, tokens: set[str], situation: dict) -> dict:
        product_id = self._named_product(text, tokens, situation.get("selection"))
        if product_id is None:
            return {
                "kind": "situation", "matched": True, "situation_kind": "availability",
                "answer": NO_AVAILABILITY_PRODUCT, "approved_source_references": [],
                "fact_references": [],
            }
        snapshots = situation.get("availability") if isinstance(situation.get("availability"), dict) else {}
        snapshot = snapshots.get(product_id) if isinstance(snapshots.get(product_id), dict) else {}
        status = snapshot.get("status") or snapshot.get("availability_status")
        if snapshot.get("available") is True or status == "available":
            label = "available"
        elif status == "unavailable" or snapshot.get("available") is False:
            label = "unavailable"
        else:
            label = "unknown"
        return {
            "kind": "situation", "matched": True, "situation_kind": "availability",
            "answer": f"{product_id} is {label} in the current inventory snapshot.",
            "approved_source_references": [],
            "fact_references": ["inventory:availability"],
        }

    @staticmethod
    def _named_product(text: str, tokens: set[str], selection) -> str | None:
        from .recommendation import REFERENCE_CATALOG
        lowered = text.lower()
        for product in REFERENCE_CATALOG:
            if product.product_id in lowered or product.product_id.replace("-", " ") in lowered:
                return product.product_id
            if any(flower in tokens for flower in product.flowers if flower != "mixed"):
                return product.product_id
        if isinstance(selection, dict) and isinstance(selection.get("product_id"), str):
            return selection["product_id"]
        return None

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


def route_support_ticket(session_id, reason, details=None):
    details = details or {}
    r = str(reason or 'general').lower()
    p = 'P1_CRITICAL' if any(k in r for k in ['urgent', 'payment', 'delivery']) else 'P3_NORMAL'
    return {'session_id': session_id, 'reason': r, 'priority': p, 'queue': 'florist_inbox', 'details': details}
