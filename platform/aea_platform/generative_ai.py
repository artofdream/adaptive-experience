from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from .intent import (IntentInterpretation, IntentInterpreter, IntentValidationError,
                     ReferenceIntentInterpreter, SUPPORTED_FACETS)


class GenerativeAIUnavailable(RuntimeError):
    pass


PRIMARY_DISCLOSURE = "AI-generated interpretation; review and correct before ordering."
NON_AI_DISCLOSURE = "Automated interpretation; review and correct before ordering."


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
                 timeout_seconds: float = 2.0, transport=None):
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
        request = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content":
                "Extract only occasion, budget, recipient, style, flower_preference, timing. "
                "Return JSON with facets object and up to three short suggestions. Do not include PII."},
                {"role": "user", "content": json.dumps({
                    "message": message_text, "current_intent": current_intent})}],
        }
        try:
            status, raw = self.transport(self.endpoint, self.api_key, request,
                                         self.timeout_seconds)
            if status != 200:
                raise GenerativeAIUnavailable(f"AI provider status {status}")
            outer = json.loads(raw)
            content = outer["choices"][0]["message"]["content"]
            result = json.loads(content)
            if set(result) != {"facets", "suggestions"}:
                raise IntentValidationError("AI response shape is invalid")
            facets = result["facets"]
            if not isinstance(facets, dict) or set(facets) - set(SUPPORTED_FACETS):
                raise IntentValidationError("AI returned unsupported facets")
            suggestions = result["suggestions"]
            if not isinstance(suggestions, list):
                raise IntentValidationError("AI suggestions are invalid")
            return IntentInterpretation(facets, tuple(suggestions))
        except (TimeoutError, OSError, urllib.error.URLError, KeyError, IndexError,
                TypeError, json.JSONDecodeError) as error:
            raise GenerativeAIUnavailable("AI provider unavailable or invalid") from error

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
