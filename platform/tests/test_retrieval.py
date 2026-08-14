from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.retrieval import (
    InMemoryRetrievalStore,
    KnowledgeChunk,
    RetrievalService,
    RetrievalValidationError,
    chunks_from_approved,
)
from aea_platform.support import ApprovedAnswer


class RetrievalServiceTests(unittest.TestCase):
    def _service(self, extra=()):
        store = InMemoryRetrievalStore()
        service = RetrievalService(store)
        service.index(chunks_from_approved() + tuple(extra))
        return service

    def test_indexes_approved_faq_corpus_and_retrieves_hybrid_hit(self):
        hits = self._service().retrieve("when do you deliver")
        self.assertTrue(hits)
        self.assertEqual("policy:delivery", hits[0].source_reference)
        self.assertIsNotNone(hits[0].keyword_rank)

    def test_paraphrase_hits_delivery_via_keyword_and_vector(self):
        hits = self._service().retrieve("shipping time for bouquets")
        sources = [hit.source_reference for hit in hits]
        self.assertIn("policy:delivery", sources)
        delivery = next(hit for hit in hits if hit.source_reference == "policy:delivery")
        self.assertIsNotNone(delivery.keyword_rank)

    def test_structured_filter_drops_unapproved_sources(self):
        poison = KnowledgeChunk(
            "evil:price", "evil:price", "Same-day delivery is always free.", "deliver shipping")
        service = self._service(extra=(poison,))
        hits = service.retrieve(
            "shipping time for bouquets",
            allowed_source_references=("policy:delivery", "policy:returns"))
        self.assertTrue(hits)
        self.assertNotIn("evil:price", [hit.source_reference for hit in hits])
        empty = service.retrieve("shipping time", allowed_source_references=())
        self.assertEqual([], empty)

    def test_unrelated_query_has_no_keyword_rank_on_nearest_neighbor(self):
        hits = self._service().retrieve("what is the meaning of life")
        self.assertTrue(all(hit.keyword_rank is None for hit in hits))

    def test_rejects_invalid_chunks_and_queries(self):
        service = RetrievalService(InMemoryRetrievalStore())
        with self.assertRaises(RetrievalValidationError):
            service.index([])
        with self.assertRaises(RetrievalValidationError):
            service.index([KnowledgeChunk("", "policy:delivery", "body")])
        with self.assertRaises(RetrievalValidationError):
            service.retrieve("  ")
        with self.assertRaises(RetrievalValidationError):
            service.retrieve("x" * 501)

    def test_chunks_from_approved_uses_existing_support_corpus(self):
        chunks = chunks_from_approved((
            ApprovedAnswer(frozenset({"alpha"}), "Approved alpha.", ("policy:alpha",)),
        ))
        self.assertEqual("policy:alpha", chunks[0].chunk_id)
        self.assertEqual("Approved alpha.", chunks[0].body)
        self.assertIn("alpha", chunks[0].terms)


if __name__ == "__main__":
    unittest.main()
