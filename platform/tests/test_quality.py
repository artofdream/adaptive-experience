from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.generative_ai import AvailableIntentInterpreter, GenerativeAIUnavailable
from aea_platform.intent import (
    IntentAnalysisService,
    IntentInterpretation,
    IntentValidationError,
    ReferenceIntentInterpreter,
)
from aea_platform.quality import QualityMonitor, QualityTrackingError
from aea_platform.support import NO_APPROVED_ANSWER, SupportService


class FakeStateStore:
    def __init__(self, current):
        self.current = current
        self.applied = []

    def load(self, session_id):
        return dict(self.current)

    def apply_patch(self, session_id, expected, schema_version, patch, messages):
        self.applied.append((session_id, expected, schema_version, patch, messages))
        return expected + 1


class FakeSupportStore:
    def __init__(self):
        self.recorded = None

    def record_answer(self, **kwargs):
        self.recorded = kwargs


class QualityMonitorTests(unittest.TestCase):
    def test_record_rejects_raw_text_and_unknown_fields(self):
        monitor = QualityMonitor()
        with self.assertRaises(QualityTrackingError):
            monitor.record(path="intent", outcome="ok", assistant_mode="reference",
                           quality_flags=("supported_facets",), message_text="birthday roses")
        with self.assertRaises(QualityTrackingError):
            monitor.record(path="faq", outcome="ok", matched=True,
                           quality_flags=("approved_source",), email="a@b.c")
        with self.assertRaises(QualityTrackingError):
            monitor.record(path="crm", outcome="ok")
        self.assertEqual([], monitor.store.events)

    def test_faq_unmatched_and_approved_answers_are_tracked(self):
        service = SupportService(FakeSupportStore(), new_id=lambda: "m")
        matched = service.answer(
            session_id="s", question="When do you deliver?", correlation_id="c",
            subject_reference="subj", context_version=1)
        self.assertTrue(matched["matched"])
        miss = service.answer(
            session_id="s", question="what is the meaning of life", correlation_id="c",
            subject_reference="subj", context_version=1)
        self.assertFalse(miss["matched"])
        outcomes = [event["outcome"] for event in service.quality.store.events]
        self.assertEqual(["ok", "unmatched"], outcomes)
        self.assertIn("approved_source", service.quality.store.events[0]["quality_flags"])
        self.assertIn("no_fabrication", service.quality.store.events[1]["quality_flags"])
        self.assertNotIn("question", service.quality.store.events[0])
        self.assertNotIn("answer", service.quality.store.events[0])

    def test_faq_unapproved_answer_fails_closed_and_is_not_published(self):
        store = FakeSupportStore()
        service = SupportService(store, new_id=lambda: "m")
        with self.assertRaises(QualityTrackingError):
            service.quality.assess_faq(
                {"kind": "faq", "matched": True, "answer": "Invented policy text",
                 "approved_source_references": ["policy:delivery"]},
                approved_answers={NO_APPROVED_ANSWER: ()},
                unmatched_answer=NO_APPROVED_ANSWER)
        self.assertIsNone(store.recorded)
        self.assertEqual("error", service.quality.store.events[-1]["outcome"])
        self.assertEqual("unapproved_answer", service.quality.store.events[-1]["error_code"])

    def test_intent_fallback_and_invalid_output_are_tracked(self):
        class Down:
            def interpret(self, *_):
                raise GenerativeAIUnavailable("down")

        available = AvailableIntentInterpreter(
            Down(), ReferenceIntentInterpreter(), failure_threshold=3)
        store = FakeStateStore({
            "state_schema_version": 1, "context_version": 0, "state": {},
        })
        service = IntentAnalysisService(
            store, available,
            now=lambda: datetime(2026, 8, 17, tzinfo=timezone.utc),
        )
        result = service.analyze(
            session_id="session", message_text="birthday roses for Mum",
            observed_context_version=0, correlation_id="correlation",
            subject_reference="subject")
        self.assertEqual("birthday", result.structured_intent["occasion"])
        event = service.quality.store.events[-1]
        self.assertEqual("intent", event["path"])
        self.assertEqual("fallback", event["outcome"])
        self.assertEqual("provider_unavailable", event["error_code"])
        self.assertEqual("fallback", event["assistant_mode"])
        self.assertIn("degraded", event["quality_flags"])

        class Escape:
            def interpret(self, *_):
                return IntentInterpretation({"product_id": "rose-1"})

        escaping = IntentAnalysisService(
            FakeStateStore({"state_schema_version": 1, "context_version": 0, "state": {}}),
            Escape())
        with self.assertRaises(IntentValidationError):
            escaping.analyze(
                session_id="session", message_text="flowers", observed_context_version=0,
                correlation_id="correlation", subject_reference="subject")
        error = escaping.quality.store.events[-1]
        self.assertEqual("error", error["outcome"])
        self.assertEqual("unsupported_facets", error["error_code"])

    def test_reference_intent_success_is_tracked_without_vendor_mode(self):
        service = IntentAnalysisService(
            FakeStateStore({"state_schema_version": 1, "context_version": 0, "state": {}}),
            ReferenceIntentInterpreter())
        service.analyze(
            session_id="session", message_text="birthday roses",
            observed_context_version=0, correlation_id="correlation",
            subject_reference="subject")
        event = service.quality.store.events[-1]
        self.assertEqual("ok", event["outcome"])
        self.assertEqual("reference", event["assistant_mode"])
        self.assertIn("supported_facets", event["quality_flags"])

    def test_summary_counts_recent_errors_without_payloads(self):
        monitor = QualityMonitor()
        monitor.record(path="intent", outcome="ok", assistant_mode="reference",
                       quality_flags=("supported_facets",))
        monitor.record(path="faq", outcome="unmatched", matched=False,
                       quality_flags=("no_fabrication",))
        monitor.record(path="intent", outcome="error", assistant_mode="primary",
                       error_code="invalid_output", quality_flags=())
        summary = monitor.summary()
        self.assertEqual(["intent", "faq"], summary["paths"])
        self.assertEqual(1, summary["counts"]["intent"]["ok"])
        self.assertEqual(1, summary["counts"]["intent"]["error"])
        self.assertEqual(1, summary["counts"]["faq"]["unmatched"])
        self.assertEqual("invalid_output", summary["recent_errors"][0]["error_code"])
        self.assertNotIn("message_text", summary["recent_errors"][0])


if __name__ == "__main__":
    unittest.main()
