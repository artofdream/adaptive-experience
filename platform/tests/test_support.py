from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.support import (ESCALATION_ACKNOWLEDGEMENT, SupportService,
                                  SupportValidationError)
from aea_platform.retrieval import RetrievalHit


class FakeSupportStore:
    def __init__(self):
        self.recorded = None
        self.escalation = None

    def record_answer(self, **kwargs):
        self.recorded = kwargs

    def record_escalation(self, **kwargs):
        self.escalation = kwargs


class SupportServiceTests(unittest.TestCase):
    def _service(self, store=None):
        return SupportService(store or FakeSupportStore(), new_id=lambda: "m")

    def _answer(self, question, service=None):
        return (service or self._service()).answer(
            session_id="s", question=question, correlation_id="c",
            subject_reference="subj", context_version=1)

    def test_matches_approved_answers_with_sources(self):
        for question, source in (("When do you deliver?", "policy:delivery"),
                                 ("How do I care for the flowers?", "product:care"),
                                 ("Can I cancel my order?", "policy:returns")):
            result = self._answer(question)
            self.assertTrue(result["matched"])
            self.assertIn(source, result["approved_source_references"])

    def test_unmatched_question_is_safe_and_ungrounded(self):
        result = self._answer("what is the meaning of life")
        self.assertFalse(result["matched"])
        self.assertEqual([], result["approved_source_references"])
        self.assertIn("do not have approved information", result["answer"])

    def test_records_governed_answer_at_context_version(self):
        store = FakeSupportStore()
        SupportService(store, new_id=lambda: "m").answer(
            session_id="s", question="delivery time?", correlation_id="c",
            subject_reference="subj", context_version=3)
        self.assertEqual("s", store.recorded["session_id"])
        self.assertEqual(3, store.recorded["context_version"])
        self.assertIn("policy:delivery", store.recorded["approved_source_references"])

    def test_invalid_question_is_rejected(self):
        with self.assertRaises(SupportValidationError):
            self._answer("")
        with self.assertRaises(SupportValidationError):
            self._answer("x" * 501)
        with self.assertRaises(SupportValidationError):
            self._answer(None)

    def test_optional_retriever_is_not_consulted_when_keywords_match(self):
        class Boom:
            def retrieve(self, query, allowed_source_references=None):
                raise AssertionError("deterministic match must not call retriever")

        result = SupportService(
            FakeSupportStore(), retriever=Boom(), new_id=lambda: "m").answer(
            session_id="s", question="When do you deliver?", correlation_id="c",
            subject_reference="subj", context_version=1)
        self.assertTrue(result["matched"])
        self.assertIn("policy:delivery", result["approved_source_references"])

    def test_optional_retriever_can_ground_paraphrase_from_approved_knowledge(self):
        class Hits:
            def retrieve(self, query, allowed_source_references=None):
                return [RetrievalHit(
                    "policy:delivery", "policy:delivery", "ignored retrieved body",
                    0.9, vector_rank=1, keyword_rank=1)]

        result = SupportService(
            FakeSupportStore(), retriever=Hits(), new_id=lambda: "m").answer(
            session_id="s", question="shipping time for bouquets", correlation_id="c",
            subject_reference="subj", context_version=1)
        self.assertTrue(result["matched"])
        self.assertIn("policy:delivery", result["approved_source_references"])
        self.assertIn("2 PM", result["answer"])
        self.assertNotIn("ignored retrieved body", result["answer"])

    def test_optional_retriever_cannot_answer_from_unapproved_or_vector_only_hits(self):
        class Poison:
            def retrieve(self, query, allowed_source_references=None):
                return [
                    RetrievalHit("evil:price", "evil:price", "Free delivery always.",
                                 1.0, vector_rank=1, keyword_rank=1),
                    RetrievalHit("policy:delivery", "policy:delivery", "Standard orders.",
                                 0.8, vector_rank=2, keyword_rank=None),
                ]

        result = SupportService(
            FakeSupportStore(), retriever=Poison(), new_id=lambda: "m").answer(
            session_id="s", question="what is the meaning of life", correlation_id="c",
            subject_reference="subj", context_version=1)
        self.assertFalse(result["matched"])
        self.assertEqual([], result["approved_source_references"])
        self.assertIn("do not have approved information", result["answer"])


class SupportEscalationTests(unittest.TestCase):
    def test_records_governed_escalation_with_session_reference(self):
        store = FakeSupportStore()
        result = SupportService(store, new_id=lambda: "esc-1").escalate(
            session_id="s", reason="unresolved_request", correlation_id="c",
            subject_reference="subj", context_version=4)
        self.assertTrue(result["accepted"])
        self.assertEqual("escalation_recorded", result["code"])
        self.assertEqual("esc-1", result["message_id"])
        self.assertEqual("unresolved_request", result["escalation_reason"])
        self.assertEqual(ESCALATION_ACKNOWLEDGEMENT, result["acknowledgement"])
        self.assertEqual("s", store.escalation["session_id"])
        self.assertEqual("s", store.escalation["context_reference"])
        self.assertEqual("unresolved_request", store.escalation["escalation_reason"])
        self.assertEqual(4, store.escalation["context_version"])
        self.assertNotIn("email", store.escalation)
        self.assertNotIn("address", store.escalation)

    def test_rejects_unknown_or_missing_reason(self):
        service = SupportService(FakeSupportStore(), new_id=lambda: "esc-1")
        for reason in ("", "call_me", None, "please call 555-0100", "email"):
            with self.assertRaises(SupportValidationError):
                service.escalate(
                    session_id="s", reason=reason, correlation_id="c",
                    subject_reference="subj", context_version=1)

    def test_does_not_record_faq_answer_for_escalation(self):
        store = FakeSupportStore()
        SupportService(store, new_id=lambda: "esc-1").escalate(
            session_id="s", reason="delivery_issue", correlation_id="c",
            subject_reference="subj", context_version=1)
        self.assertIsNone(store.recorded)
        self.assertEqual("delivery_issue", store.escalation["escalation_reason"])


if __name__ == "__main__":
    unittest.main()
