from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Callable, Protocol

from .state import StatePatch


SUPPORTED_FACETS = (
    "occasion", "budget", "recipient", "style", "flower_preference", "timing",
)

MISSING_FACET_PROMPTS = {
    "occasion": "What is the occasion?",
    "budget": "What budget should I work within?",
    "recipient": "Who are the flowers for?",
    "style": "What style or mood would you prefer?",
    "flower_preference": "Any flower preferences?",
    "timing": "When should they arrive?",
}


class IntentValidationError(ValueError):
    pass


class IntentSessionNotFound(LookupError):
    pass


@dataclass(frozen=True)
class IntentInterpretation:
    facets: dict
    suggestions: tuple[str, ...] = ()


class IntentInterpreter(Protocol):
    def interpret(self, message_text: str, current_intent: dict) -> IntentInterpretation: ...


class ReferenceIntentInterpreter:
    """Deterministic local interpreter; replaceable through IntentInterpreter."""

    OCCASIONS = ("birthday", "anniversary", "wedding", "sympathy", "thank you")
    STYLES = ("romantic", "bright", "pastel", "modern", "classic", "wildflower")
    FLOWERS = ("roses", "tulips", "lilies", "orchids", "sunflowers", "peonies")
    RECIPIENTS = {
        "mum": "mother", "mom": "mother", "mother": "mother",
        "wife": "wife", "husband": "husband", "partner": "partner",
        "friend": "friend", "colleague": "colleague",
    }

    def interpret(self, message_text: str, current_intent: dict) -> IntentInterpretation:
        text = message_text.casefold()
        facets: dict = {}
        for occasion in self.OCCASIONS:
            if occasion in text:
                facets["occasion"] = occasion
                break
        budget = re.search(r"(?:€|eur|£|gbp|\$|usd)\s*(\d+(?:[.,]\d{1,2})?)|"
                           r"(\d+(?:[.,]\d{1,2})?)\s*(?:€|eur|£|gbp|\$|usd)", text)
        if budget:
            raw = next(value for value in budget.groups() if value is not None).replace(",", ".")
            try:
                amount = Decimal(raw)
            except InvalidOperation:
                amount = Decimal(0)
            if Decimal("1") <= amount <= Decimal("10000"):
                facets["budget"] = float(amount)
        for word, recipient in self.RECIPIENTS.items():
            if re.search(rf"\b{re.escape(word)}\b", text):
                facets["recipient"] = recipient
                break
        for style in self.STYLES:
            if style in text:
                facets["style"] = style
                break
        for flower in self.FLOWERS:
            if flower in text:
                facets["flower_preference"] = flower
                break
        timing = re.search(r"\b(today|tomorrow|this weekend|next week)\b", text)
        if timing:
            facets["timing"] = timing.group(1)

        understood = set(current_intent) | set(facets)
        suggestions = missing_facet_suggestions(understood)
        return IntentInterpretation(facets, suggestions)


def missing_facet_suggestions(understood) -> tuple[str, ...]:
    return tuple(MISSING_FACET_PROMPTS[key] for key in SUPPORTED_FACETS
                 if key not in understood)[:3]


@dataclass(frozen=True)
class IntentAnalysisResult:
    message_id: str
    context_version: int
    structured_intent: dict
    suggestions: tuple[str, ...]


class IntentAnalysisService:
    """Apply one interpretation to Shared Understanding atomically (FR-002)."""

    def __init__(self, state_store, interpreter: IntentInterpreter, *,
                 now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None):
        self.state_store = state_store
        self.interpreter = interpreter
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

    def analyze(self, *, session_id: str, message_text: str,
                observed_context_version: int, correlation_id: str,
                subject_reference: str) -> IntentAnalysisResult:
        if not isinstance(message_text, str) or not message_text.strip():
            raise IntentValidationError("message text is required")
        if (not isinstance(observed_context_version, int)
                or isinstance(observed_context_version, bool)
                or observed_context_version < 0):
            raise IntentValidationError("observed context version is invalid")
        if not isinstance(subject_reference, str) or not subject_reference.strip():
            raise IntentValidationError("subject reference is required")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            raise IntentValidationError("correlation ID is required")
        current = self.state_store.load(session_id)
        if current is None:
            raise IntentSessionNotFound(session_id)
        state = current.get("state") or {}
        existing = self._facets(state.get("shared_understanding") or {})
        interpretation = self.interpreter.interpret(message_text.strip(), dict(existing))
        facets = self._facets(interpretation.facets)
        suggestions = self._suggestions(interpretation.suggestions)
        merged = {**existing, **facets}
        values = {"shared_understanding": facets,
                  "thought_completion": {"suggestions": list(suggestions)}}
        changed = [f"shared_understanding.{key}" for key in facets]
        changed.append("thought_completion.suggestions")
        message_id = ""
        messages = []
        if facets:
            message_id = str(self.new_id())
            published_at = self.now().astimezone(timezone.utc).isoformat()
            envelope = {
                "message_id": message_id, "topic": "experience.intent.updated",
                "message_type": "event", "schema_version": "1.0.0",
                "session_id": session_id, "correlation_id": correlation_id,
                "source": "orchestration", "context_version": observed_context_version + 1,
                "publication_time": published_at,
                "security_context": {"classification": "confidential",
                                     "subject_reference": subject_reference.strip()},
                "payload": {"structured_intent": merged}, "outcome": {},
            }
            messages = [{"message_id": message_id, "topic": "experience.intent.updated",
                         "aggregate_key": session_id, "envelope": envelope}]
        version = self.state_store.apply_patch(
            session_id, observed_context_version, int(current["state_schema_version"]),
            StatePatch.create(values, changed), messages,
        )
        return IntentAnalysisResult(message_id, version, merged, suggestions)

    @staticmethod
    def _facets(value: dict) -> dict:
        if not isinstance(value, dict):
            raise IntentValidationError("interpreter facets must be an object")
        unknown = set(value) - set(SUPPORTED_FACETS)
        if unknown:
            raise IntentValidationError(f"unsupported intent facets: {sorted(unknown)}")
        result = {}
        for key, item in value.items():
            if key == "budget":
                if (not isinstance(item, (int, float)) or isinstance(item, bool)
                        or item < 1 or item > 10000):
                    raise IntentValidationError("budget is invalid")
                result[key] = item
            elif not isinstance(item, str) or not item.strip() or len(item.strip()) > 120:
                raise IntentValidationError(f"{key} is invalid")
            else:
                result[key] = item.strip()
        return result

    @staticmethod
    def _suggestions(value) -> tuple[str, ...]:
        if not isinstance(value, (tuple, list)):
            raise IntentValidationError("suggestions must be a list")
        suggestions = tuple(item.strip() for item in value
                            if isinstance(item, str) and item.strip())
        if len(suggestions) > 3 or any(len(item) > 160 for item in suggestions):
            raise IntentValidationError("suggestions are invalid")
        return suggestions


@dataclass(frozen=True)
class SharedUnderstandingProjection:
    context_version: int
    structured_intent: dict
    suggestions: tuple[str, ...]


@dataclass(frozen=True)
class IntentCorrectionResult:
    message_id: str
    context_version: int
    structured_intent: dict
    suggestions: tuple[str, ...]


class SharedUnderstandingService:
    """Review and correct governed inferred intent without replacing sibling state (FR-021)."""

    def __init__(self, state_store, *,
                 now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None):
        self.state_store = state_store
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

    def projection(self, *, session_id: str) -> SharedUnderstandingProjection:
        current = self.state_store.load(session_id)
        if current is None:
            raise IntentSessionNotFound(session_id)
        state = current.get("state") or {}
        facets = IntentAnalysisService._facets(state.get("shared_understanding") or {})
        suggestions = IntentAnalysisService._suggestions(
            (state.get("thought_completion") or {}).get("suggestions") or ()
        )
        return SharedUnderstandingProjection(
            int(current["context_version"]), facets, suggestions,
        )

    def correct(self, *, session_id: str, corrections: dict,
                observed_context_version: int, correlation_id: str,
                subject_reference: str) -> IntentCorrectionResult:
        if (not isinstance(observed_context_version, int)
                or isinstance(observed_context_version, bool)
                or observed_context_version < 0):
            raise IntentValidationError("observed context version is invalid")
        if not isinstance(subject_reference, str) or not subject_reference.strip():
            raise IntentValidationError("subject reference is required")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            raise IntentValidationError("correlation ID is required")
        correction = IntentAnalysisService._facets(corrections)
        if not correction:
            raise IntentValidationError("at least one correction is required")

        current = self.state_store.load(session_id)
        if current is None:
            raise IntentSessionNotFound(session_id)
        state = current.get("state") or {}
        existing = IntentAnalysisService._facets(state.get("shared_understanding") or {})
        changed = {key: value for key, value in correction.items()
                   if existing.get(key) != value}
        if not changed:
            raise IntentValidationError("correction does not change shared understanding")
        merged = {**existing, **changed}
        suggestions = missing_facet_suggestions(merged)
        message_id = str(self.new_id())
        published_at = self.now().astimezone(timezone.utc).isoformat()
        envelope = {
            "message_id": message_id, "topic": "experience.intent.updated",
            "message_type": "event", "schema_version": "1.0.0",
            "session_id": session_id, "correlation_id": correlation_id.strip(),
            "source": "orchestration", "context_version": observed_context_version + 1,
            "publication_time": published_at,
            "security_context": {"classification": "confidential",
                                 "subject_reference": subject_reference.strip()},
            "payload": {"structured_intent": merged}, "outcome": {},
        }
        values = {
            "shared_understanding": changed,
            "thought_completion": {"suggestions": list(suggestions)},
        }
        changed_facets = [f"shared_understanding.{key}" for key in changed]
        changed_facets.append("thought_completion.suggestions")
        version = self.state_store.apply_patch(
            session_id, observed_context_version, int(current["state_schema_version"]),
            StatePatch.create(values, changed_facets), [{
                "message_id": message_id, "topic": "experience.intent.updated",
                "aggregate_key": session_id, "envelope": envelope,
            }],
        )
        return IntentCorrectionResult(message_id, version, merged, suggestions)
