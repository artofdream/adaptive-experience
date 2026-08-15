from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.generative_ai import (
    AvailableIntentInterpreter,
    GenerativeAIUnavailable,
    NON_AI_DISCLOSURE,
    OpenAICompatibleIntentInterpreter,
    PRIMARY_DISCLOSURE,
    disclosure_for_mode,
)
from aea_platform.intent import ReferenceIntentInterpreter


class GenerativeAITests(unittest.TestCase):
    def test_adapter_requests_strict_structured_intent(self):
        captured = {}
        def transport(endpoint, api_key, payload, timeout):
            captured.update(endpoint=endpoint, api_key=api_key, payload=payload, timeout=timeout)
            content = json.dumps({"facets": {"occasion": "birthday", "budget": 75},
                                  "suggestions": ["Who are the flowers for?"]})
            return 200, json.dumps({"choices": [{"message": {"content": content}}]})
        interpreter = OpenAICompatibleIntentInterpreter(
            "https://ai.example/v1/chat/completions", "secret", "model", transport=transport)
        result = interpreter.interpret("Birthday flowers under 75", {})
        self.assertEqual({"occasion": "birthday", "budget": 75}, result.facets)
        self.assertEqual(("Who are the flowers for?",), result.suggestions)
        self.assertEqual({"type": "json_object"}, captured["payload"]["response_format"])
        self.assertLessEqual(captured["timeout"], 2.5)
        self.assertNotIn("secret", json.dumps(captured["payload"]))

    def test_adapter_rejects_provider_scope_escape(self):
        content = json.dumps({"facets": {"product_id": "rose-1"}, "suggestions": []})
        interpreter = OpenAICompatibleIntentInterpreter(
            "https://ai.example", "secret", "model",
            transport=lambda *_: (200, json.dumps({
                "choices": [{"message": {"content": content}}]})))
        with self.assertRaises(Exception):
            interpreter.interpret("flowers", {})

    def test_timeout_falls_back_and_circuit_keeps_assistant_available(self):
        class Down:
            def interpret(self, *_): raise GenerativeAIUnavailable("down")
        clock = [0.0]
        available = AvailableIntentInterpreter(
            Down(), ReferenceIntentInterpreter(), failure_threshold=2,
            recovery_seconds=30, clock=lambda: clock[0])
        first = available.interpret("birthday roses", {})
        second = available.interpret("birthday roses", {})
        self.assertEqual("birthday", first.facets["occasion"])
        self.assertEqual("roses", second.facets["flower_preference"])
        self.assertEqual({"available": True, "mode": "fallback", "circuit": "open"},
                         available.health())
        # An open circuit skips the provider while preserving useful behavior.
        third = available.interpret("for Mum", {})
        self.assertEqual("mother", third.facets["recipient"])

    def test_circuit_recovers_when_the_provider_returns(self):
        clock = [0.0]

        class Flaky:
            def __init__(self):
                self.up = False

            def interpret(self, message_text, current_intent):
                if not self.up:
                    raise GenerativeAIUnavailable("down")
                return ReferenceIntentInterpreter().interpret(message_text, current_intent)

        primary = Flaky()
        available = AvailableIntentInterpreter(
            primary, ReferenceIntentInterpreter(), failure_threshold=1,
            recovery_seconds=30, clock=lambda: clock[0])
        available.interpret("birthday roses", {})
        self.assertEqual("open", available.health()["circuit"])
        # Within the recovery window the provider is skipped.
        available.interpret("more", {})
        self.assertEqual("fallback", available.health()["mode"])
        # After the window, a recovered provider closes the circuit.
        primary.up = True
        clock[0] = 31
        available.interpret("birthday roses for Mum", {})
        self.assertEqual("primary", available.health()["mode"])
        self.assertEqual("closed", available.health()["circuit"])

    def test_assistant_availability_is_maintained_under_provider_failure(self):
        class Down:
            def interpret(self, *_):
                raise GenerativeAIUnavailable("down")

        available = AvailableIntentInterpreter(
            Down(), ReferenceIntentInterpreter(), failure_threshold=3, recovery_seconds=0)
        total, successes = 200, 0
        for _ in range(total):
            result = available.interpret("birthday roses for Mum", {})
            if result is not None and result.facets is not None:
                successes += 1
        availability = successes / total
        # The deterministic fallback keeps the assistant available on every request,
        # well above the NFR-003 99.5% target.
        self.assertGreaterEqual(availability, 0.995)
        self.assertEqual(1.0, availability)
        self.assertTrue(available.health()["available"])

    def test_configuration_rejects_unbounded_timeout(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleIntentInterpreter("https://ai.example", "secret", "model",
                                              timeout_seconds=3)

    def test_disclosure_claims_ai_only_for_primary_mode(self):
        primary = disclosure_for_mode("primary")
        self.assertEqual({
            "ai_generated": True,
            "assistant_mode": "primary",
            "disclosure": PRIMARY_DISCLOSURE,
        }, primary)
        self.assertIn("AI-generated", primary["disclosure"])
        for mode in ("fallback", "reference"):
            payload = disclosure_for_mode(mode)
            self.assertEqual({
                "ai_generated": False,
                "assistant_mode": mode,
                "disclosure": NON_AI_DISCLOSURE,
            }, payload)
            self.assertNotIn("AI-generated", payload["disclosure"])
            self.assertTrue(payload["disclosure"])


if __name__ == "__main__":
    unittest.main()
