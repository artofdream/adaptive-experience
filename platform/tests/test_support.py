from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.support import SupportService, SupportValidationError


class FakeSupportStore:
    def __init__(self):
        self.recorded = None

    def record_answer(self, **kwargs):
        self.recorded = kwargs


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


if __name__ == "__main__":
    unittest.main()
