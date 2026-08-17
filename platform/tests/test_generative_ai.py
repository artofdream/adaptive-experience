from __future__ import annotations

import ast
import inspect
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import get_type_hints

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
from aea_platform.intent import (
    IntentAnalysisService,
    IntentInterpretation,
    IntentInterpreter,
    ReferenceIntentInterpreter,
)
from aea_platform.inventory import InventoryAvailabilityService
from aea_platform.order import OrderService
from aea_platform.recommendation import RecommendationService


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
        self.assertEqual("provider_unavailable", available.last_error_code)
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


class _FakeStateStore:
    def __init__(self, current=None):
        self.current = current
        self.applied = []

    def load(self, session_id):
        return self.current

    def apply_patch(self, session_id, expected, schema_version, patch, messages):
        self.applied.append((session_id, expected, schema_version, patch, messages))
        return expected + 1


class _ReplacementPrimary:
    """Stand-in for a future model adapter; same IntentInterpretation contract."""

    def interpret(self, message_text: str, current_intent: dict) -> IntentInterpretation:
        return IntentInterpretation(
            {"occasion": "birthday", "recipient": "mother"},
            ("What budget should I work within?",),
        )


class AdapterReplacementArchitectureTests(unittest.TestCase):
    """ADR-007 / NFR-014: model enhancement does not redesign domain modules."""

    DOMAIN_MODULES = (
        "intent.py", "order.py", "inventory.py", "recommendation.py",
        "pricing.py", "delivery.py", "payment.py",
    )
    VENDOR_MODULES = frozenset({
        "openai", "anthropic", "litellm", "generative_ai",
    })
    AI_PARAMETER_NAMES = frozenset({
        "interpreter", "openai", "anthropic", "api_key", "model", "endpoint",
    })

    def test_shipped_and_replacement_adapters_satisfy_intent_interpreter(self):
        shipped = (
            ReferenceIntentInterpreter(),
            OpenAICompatibleIntentInterpreter(
                "https://ai.example", "secret", "model",
                transport=lambda *_: (200, "{}")),
            AvailableIntentInterpreter(_ReplacementPrimary()),
        )
        for adapter in (*shipped, _ReplacementPrimary()):
            self.assertIsInstance(adapter, IntentInterpreter)
            self.assertTrue(callable(adapter.interpret))

    def test_available_interpreter_swaps_primary_without_new_contract(self):
        available = AvailableIntentInterpreter(_ReplacementPrimary())
        result = available.interpret("flowers for Mum", {})
        self.assertIsInstance(result, IntentInterpretation)
        self.assertEqual({"occasion": "birthday", "recipient": "mother"}, result.facets)
        self.assertEqual("primary", available.health()["mode"])

    def test_intent_analysis_accepts_replacement_primary_without_redesign(self):
        store = _FakeStateStore({
            "state_schema_version": 1, "context_version": 2,
            "state": {"shared_understanding": {}},
        })
        service = IntentAnalysisService(
            store, AvailableIntentInterpreter(_ReplacementPrimary()),
            now=lambda: datetime(2026, 8, 16, tzinfo=timezone.utc),
        )
        result = service.analyze(
            session_id="session", message_text="birthday flowers for Mum",
            observed_context_version=2, correlation_id="correlation",
            subject_reference="subject",
        )
        self.assertEqual({"occasion": "birthday", "recipient": "mother"},
                         result.structured_intent)
        self.assertEqual(("What budget should I work within?",), result.suggestions)
        self.assertEqual("experience.intent.updated", store.applied[0][4][0]["topic"])

    def test_intent_analysis_depends_on_interpreter_protocol_not_vendor(self):
        annotation = get_type_hints(IntentAnalysisService.__init__)["interpreter"]
        self.assertEqual(annotation, IntentInterpreter)
        source = (ROOT / "aea_platform" / "intent.py").read_text(encoding="utf-8")
        self.assertNotIn("OpenAICompatibleIntentInterpreter", source)
        self.assertNotIn("AEA_AI_API_KEY", source)
        self.assertNotIn("openai", source)

    def test_authoritative_domain_modules_do_not_import_ai_vendors(self):
        for name in self.DOMAIN_MODULES:
            imported = _top_level_imports(ROOT / "aea_platform" / name)
            leaked = imported & self.VENDOR_MODULES
            self.assertFalse(leaked, f"{name} imports AI vendor modules: {sorted(leaked)}")

    def test_generative_adapter_does_not_import_authoritative_domain_modules(self):
        imported = _top_level_imports(ROOT / "aea_platform" / "generative_ai.py")
        leaked = imported & {
            "order", "inventory", "recommendation", "pricing", "delivery", "payment",
        }
        self.assertFalse(leaked, f"generative_ai imports domain modules: {sorted(leaked)}")
        self.assertIn("intent", imported)

    def test_domain_service_constructors_do_not_take_vendor_clients(self):
        for service in (OrderService, InventoryAvailabilityService, RecommendationService):
            names = set(inspect.signature(service.__init__).parameters)
            leaked = names & self.AI_PARAMETER_NAMES
            self.assertFalse(
                leaked, f"{service.__name__} constructor takes AI parameters: {sorted(leaked)}")
        generate = inspect.signature(RecommendationService.generate).parameters
        self.assertIn("intent", generate)
        self.assertNotIn("interpreter", generate)
        self.assertEqual(get_type_hints(RecommendationService.generate)["intent"], dict)

    def test_runtime_constructs_adapter_outside_domain_modules(self):
        runtime = (ROOT / "aea_platform" / "internal_runtime.py").read_text(encoding="utf-8")
        self.assertIn("AvailableIntentInterpreter(OpenAICompatibleIntentInterpreter(", runtime)
        self.assertIn("InternalOrchestrationApp(", runtime)
        for name in self.DOMAIN_MODULES:
            source = (ROOT / "aea_platform" / name).read_text(encoding="utf-8")
            self.assertNotIn("OpenAICompatibleIntentInterpreter", source)
            self.assertNotIn("AEA_AI_ENDPOINT", source)
            self.assertNotIn("AEA_AI_API_KEY", source)
            self.assertNotIn("AEA_AI_MODEL", source)


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
            for alias in node.names:
                names.add(alias.name.split(".")[0])
    return names


if __name__ == "__main__":
    unittest.main()
