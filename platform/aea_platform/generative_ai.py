from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request

from .crm import format_reminder_text
from .intent import (IntentInterpretation, IntentInterpreter, IntentValidationError,
                     ReferenceIntentInterpreter, SUPPORTED_FACETS)


class GenerativeAIUnavailable(RuntimeError):
    pass


PRIMARY_DISCLOSURE = "AI-generated interpretation; review and correct before ordering."
NON_AI_DISCLOSURE = "Automated interpretation; review and correct before ordering."
REMINDER_COPY_MAX_CHARS = 160
_REMINDER_PII_MARKERS = ("@", "http://", "https://", "www.")
_REMINDER_PHONE_RE = re.compile(r"\d{6,}")


def complete_chat_json(endpoint: str, api_key: str, model: str, messages: list,
                       *, timeout_seconds: float = 2.5, transport=None,
                       temperature: float = 0) -> dict:
    """Shared OpenAI-compatible chat-completions JSON call (LiteLLM / Path B)."""
    if not endpoint or not api_key or not model:
        raise ValueError("AI endpoint, API key, and model are required")
    if timeout_seconds <= 0 or timeout_seconds > 2.5:
        raise ValueError("AI timeout must be within 2.5 seconds")
    transport = transport or OpenAICompatibleIntentInterpreter._urllib
    request = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": messages,
    }
    try:
        status, raw = transport(endpoint, api_key, request, timeout_seconds)
        if status != 200:
            raise GenerativeAIUnavailable(f"AI provider status {status}")
        outer = json.loads(raw)
        content = outer["choices"][0]["message"]["content"]
        result = json.loads(content)
        if not isinstance(result, dict):
            raise GenerativeAIUnavailable("AI provider unavailable or invalid")
        return result
    except (TimeoutError, OSError, urllib.error.URLError, KeyError, IndexError,
            TypeError, json.JSONDecodeError) as error:
        raise GenerativeAIUnavailable("AI provider unavailable or invalid") from error


def disclosure_for_mode(mode: str) -> dict:
    """NFR-005: claim AI generation only when the primary interpreter ran."""
    generated = mode == "primary"
    return {
        "ai_generated": generated,
        "assistant_mode": mode,
        "disclosure": PRIMARY_DISCLOSURE if generated else NON_AI_DISCLOSURE,
    }


class OpenAICompatibleIntentInterpreter:
    """Vendor-neutral chat-completions adapter with a strict JSON boundary."""

    def __init__(self, endpoint: str, api_key: str, model: str, *,
                 timeout_seconds: float = 2.5, transport=None):
        if not endpoint or not api_key or not model:
            raise ValueError("AI endpoint, API key, and model are required")
        if timeout_seconds <= 0 or timeout_seconds > 2.5:
            raise ValueError("AI timeout must be within 2.5 seconds")
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.transport = transport or self._urllib

    def interpret(self, message_text: str, current_intent: dict) -> IntentInterpretation:
        result = complete_chat_json(
            self.endpoint, self.api_key, self.model,
            [{"role": "system", "content":
                "Extract only occasion, budget, recipient, style, flower_preference, timing. "
                "Return JSON with facets object and up to three short suggestions. Do not include PII."},
             {"role": "user", "content": json.dumps({
                 "message": message_text, "current_intent": current_intent})}],
            timeout_seconds=self.timeout_seconds, transport=self.transport)
        if set(result) != {"facets", "suggestions"}:
            raise IntentValidationError("AI response shape is invalid")
        facets = result["facets"]
        if not isinstance(facets, dict) or set(facets) - set(SUPPORTED_FACETS):
            raise IntentValidationError("AI returned unsupported facets")
        suggestions = result["suggestions"]
        if not isinstance(suggestions, list):
            raise IntentValidationError("AI suggestions are invalid")
        return IntentInterpretation(facets, tuple(suggestions))

    @staticmethod
    def _urllib(endpoint, api_key, payload, timeout):
        request = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers={
            "authorization": f"Bearer {api_key}", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, response.read().decode()
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode()


class AvailableIntentInterpreter:
    """Keeps the assistant available with bounded failures and local degradation."""

    def __init__(self, primary: IntentInterpreter, fallback: IntentInterpreter | None = None,
                 *, failure_threshold: int = 3, recovery_seconds: float = 30, clock=None):
        self.primary = primary
        self.fallback = fallback or ReferenceIntentInterpreter()
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.clock = clock or time.monotonic
        self.failures = 0
        self.opened_at = None
        self.last_mode = "primary"
        self.last_error_code = None

    def interpret(self, message_text, current_intent):
        now = self.clock()
        if self.opened_at is not None and now - self.opened_at < self.recovery_seconds:
            self.last_mode = "fallback"
            return self.fallback.interpret(message_text, current_intent)
        try:
            result = self.primary.interpret(message_text, current_intent)
            self.failures, self.opened_at, self.last_mode = 0, None, "primary"
            self.last_error_code = None
            return result
        except (GenerativeAIUnavailable, IntentValidationError) as error:
            self.last_error_code = (
                "provider_unavailable" if isinstance(error, GenerativeAIUnavailable)
                else "invalid_output")
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.opened_at = now
            self.last_mode = "fallback"
            return self.fallback.interpret(message_text, current_intent)

    def health(self) -> dict:
        return {"available": True, "mode": self.last_mode,
                "circuit": "open" if self.opened_at is not None else "closed"}


def validate_reminder_copy(text, *, occasion_type: str, recipient_relation: str,
                           days_until_event: int) -> str:
    """Fail closed unless reminder copy is a short categorical pull-card line."""
    if not isinstance(text, str):
        raise IntentValidationError("AI reminder copy is invalid")
    cleaned = " ".join(text.split()).strip()
    if not cleaned or len(cleaned) > REMINDER_COPY_MAX_CHARS:
        raise IntentValidationError("AI reminder copy is invalid")
    lowered = cleaned.lower()
    if any(marker in lowered for marker in _REMINDER_PII_MARKERS):
        raise IntentValidationError("AI reminder copy is invalid")
    if _REMINDER_PHONE_RE.search(cleaned):
        raise IntentValidationError("AI reminder copy is invalid")
    if not isinstance(days_until_event, int) or isinstance(days_until_event, bool):
        raise IntentValidationError("AI reminder copy is invalid")
    if not occasion_type or not recipient_relation:
        raise IntentValidationError("AI reminder copy is invalid")
    return cleaned


class OpenAICompatibleReminderCopyAuthor:
    """Same LiteLLM chat-completions path as intent; categorical FR-016 pull copy only."""

    def __init__(self, endpoint: str, api_key: str, model: str, *,
                 timeout_seconds: float = 2.5, transport=None):
        if not endpoint or not api_key or not model:
            raise ValueError("AI endpoint, API key, and model are required")
        if timeout_seconds <= 0 or timeout_seconds > 2.5:
            raise ValueError("AI timeout must be within 2.5 seconds")
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.transport = transport or OpenAICompatibleIntentInterpreter._urllib

    def author(self, *, occasion_type: str, recipient_relation: str,
               days_until_event: int) -> str:
        occasion = (occasion_type or "").strip().lower()
        relation = (recipient_relation or "").strip().lower()
        if not occasion or not relation:
            raise IntentValidationError("AI reminder inputs are invalid")
        if (not isinstance(days_until_event, int) or isinstance(days_until_event, bool)
                or days_until_event < 0 or days_until_event > 366):
            raise IntentValidationError("AI reminder inputs are invalid")
        result = complete_chat_json(
            self.endpoint, self.api_key, self.model,
            [{"role": "system", "content":
                "Write one short in-session florist pull-card reminder. "
                "Use only occasion_type, recipient_relation, and days_until_event. "
                "Do not invent names, addresses, emails, phone numbers, or URLs. "
                "Do not mention email, SMS, or push. Return JSON {\"reminder_text\": \"...\"}."},
             {"role": "user", "content": json.dumps({
                 "occasion_type": occasion,
                 "recipient_relation": relation,
                 "days_until_event": days_until_event})}],
            timeout_seconds=self.timeout_seconds, transport=self.transport)
        if set(result) != {"reminder_text"}:
            raise IntentValidationError("AI reminder response shape is invalid")
        return validate_reminder_copy(
            result["reminder_text"], occasion_type=occasion,
            recipient_relation=relation, days_until_event=days_until_event)


class AvailableReminderCopyAuthor:
    """Fail closed to the deterministic FR-016 template when LiteLLM is unhealthy."""

    def __init__(self, primary, fallback=None, *,
                 failure_threshold: int = 3, recovery_seconds: float = 30, clock=None):
        self.primary = primary
        self.fallback = fallback or format_reminder_text
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.clock = clock or time.monotonic
        self.failures = 0
        self.opened_at = None
        self.last_mode = "primary"
        self.last_error_code = None

    def author(self, *, occasion_type: str, recipient_relation: str,
               days_until_event: int) -> str:
        now = self.clock()
        if self.opened_at is not None and now - self.opened_at < self.recovery_seconds:
            self.last_mode = "fallback"
            return self.fallback(
                occasion_type=occasion_type, recipient_relation=recipient_relation,
                days_until_event=days_until_event)
        try:
            text = self.primary.author(
                occasion_type=occasion_type, recipient_relation=recipient_relation,
                days_until_event=days_until_event)
            self.failures, self.opened_at, self.last_mode = 0, None, "primary"
            self.last_error_code = None
            return text
        except (GenerativeAIUnavailable, IntentValidationError) as error:
            self.last_error_code = (
                "provider_unavailable" if isinstance(error, GenerativeAIUnavailable)
                else "invalid_output")
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.opened_at = now
            self.last_mode = "fallback"
            return self.fallback(
                occasion_type=occasion_type, recipient_relation=recipient_relation,
                days_until_event=days_until_event)

    def health(self) -> dict:
        return {"available": True, "mode": self.last_mode,
                "circuit": "open" if self.opened_at is not None else "closed"}
