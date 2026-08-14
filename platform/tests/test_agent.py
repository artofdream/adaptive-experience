from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.agent import (
    LOOKUP_APPROVED_KNOWLEDGE,
    AgentRuntime,
    AgentToolError,
    ToolSpec,
    approved_knowledge_tool,
    reference_concierge_runtime,
)
from aea_platform.retrieval import RetrievalHit
from aea_platform.support import NO_APPROVED_ANSWER, SupportService


class AgentRuntimeTests(unittest.TestCase):
    def test_allowlist_exposes_only_registered_tools(self):
        runtime = reference_concierge_runtime()
        self.assertEqual((LOOKUP_APPROVED_KNOWLEDGE,), runtime.allowed_tools())

    def test_unknown_tool_fails_closed(self):
        runtime = reference_concierge_runtime()
        with self.assertRaises(AgentToolError) as raised:
            runtime.invoke("http_fetch", {"url": "https://example.invalid"})
        self.assertIn("unknown tool", str(raised.exception))
        with self.assertRaises(AgentToolError):
            runtime.invoke("place_order", {"product_id": "rose-1"})
        with self.assertRaises(AgentToolError):
            runtime.invoke("not_a_real_tool")

    def test_happy_path_lookup_returns_approved_knowledge(self):
        result = reference_concierge_runtime().invoke(
            LOOKUP_APPROVED_KNOWLEDGE, {"question": "When do you deliver?"})
        self.assertTrue(result.ok)
        self.assertFalse(result.authoritative)
        self.assertEqual(LOOKUP_APPROVED_KNOWLEDGE, result.tool)
        self.assertTrue(result.result["matched"])
        self.assertIn("policy:delivery", result.result["approved_source_references"])
        self.assertIn("2 PM", result.result["answer"])
        self.assertFalse(result.result["authoritative"])

    def test_unmatched_lookup_is_safe_and_does_not_fabricate(self):
        result = reference_concierge_runtime().invoke(
            LOOKUP_APPROVED_KNOWLEDGE, {"question": "what is the meaning of life"})
        self.assertFalse(result.result["matched"])
        self.assertEqual([], result.result["approved_source_references"])
        self.assertEqual(NO_APPROVED_ANSWER, result.result["answer"])

    def test_knowledge_tool_may_use_retrieval_without_replacing_approved_text(self):
        class Hits:
            def retrieve(self, query, allowed_source_references=None):
                return [RetrievalHit(
                    "policy:delivery", "policy:delivery", "ignored retrieved body",
                    0.9, vector_rank=1, keyword_rank=1)]

        result = reference_concierge_runtime(retriever=Hits()).invoke(
            LOOKUP_APPROVED_KNOWLEDGE, {"question": "shipping time for bouquets"})
        self.assertTrue(result.result["matched"])
        self.assertIn("2 PM", result.result["answer"])
        self.assertNotIn("ignored retrieved body", result.result["answer"])

    def test_knowledge_tool_does_not_persist_faq_answers(self):
        class Probe:
            def __init__(self):
                self.recorded = None

            def record_answer(self, **kwargs):
                self.recorded = kwargs

        store = Probe()
        runtime = AgentRuntime((approved_knowledge_tool(
            SupportService(store, new_id=lambda: "m")),))
        runtime.invoke(LOOKUP_APPROVED_KNOWLEDGE, {"question": "When do you deliver?"})
        self.assertIsNone(store.recorded)

    def test_unknown_argument_and_empty_question_fail_closed(self):
        runtime = reference_concierge_runtime()
        with self.assertRaises(AgentToolError):
            runtime.invoke(LOOKUP_APPROVED_KNOWLEDGE, {"question": "delivery?", "url": "x"})
        with self.assertRaises(AgentToolError):
            runtime.invoke(LOOKUP_APPROVED_KNOWLEDGE, {"question": ""})
        with self.assertRaises(AgentToolError):
            runtime.invoke(LOOKUP_APPROVED_KNOWLEDGE, "delivery?")
        with self.assertRaises(AgentToolError):
            runtime.invoke(LOOKUP_APPROVED_KNOWLEDGE)

    def test_forbidden_and_write_tools_cannot_be_registered(self):
        def boom(_arguments):
            return {}

        with self.assertRaises(AgentToolError):
            AgentRuntime((ToolSpec("http_fetch", "no", boom, frozenset()),))
        with self.assertRaises(AgentToolError):
            AgentRuntime((ToolSpec(
                "place_order", "no", boom, frozenset(), side_effect="read"),))
        with self.assertRaises(AgentToolError):
            AgentRuntime((ToolSpec(
                "lookup_approved_knowledge", "no", boom, frozenset({"question"}),
                side_effect="write"),))

    def test_allowlist_cannot_name_unregistered_tools(self):
        def handler(_arguments):
            return {"ok": True}

        spec = ToolSpec(LOOKUP_APPROVED_KNOWLEDGE, "lookup", handler, frozenset({"question"}))
        with self.assertRaises(AgentToolError) as raised:
            AgentRuntime((spec,), allowlist=(LOOKUP_APPROVED_KNOWLEDGE, "sql"))
        self.assertIn("unknown tools", str(raised.exception))
        runtime = AgentRuntime((spec,), allowlist=(LOOKUP_APPROVED_KNOWLEDGE,))
        self.assertEqual((LOOKUP_APPROVED_KNOWLEDGE,), runtime.allowed_tools())


if __name__ == "__main__":
    unittest.main()
