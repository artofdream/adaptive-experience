from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Callable, Sequence

EMBEDDING_DIMENSION = 32
CHUNK_ID_MAX_LENGTH = 100
SOURCE_MAX_LENGTH = 100
BODY_MAX_LENGTH = 4000
TERMS_MAX_LENGTH = 500
_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from",
    "in", "is", "it", "of", "on", "or", "the", "to", "you", "your", "what",
    "with",
})


class RetrievalValidationError(ValueError):
    """A retrieval chunk or query is missing or malformed."""


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    source_reference: str
    body: str
    terms: str = ""


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    source_reference: str
    body: str
    score: float
    vector_rank: int | None = None
    keyword_rank: int | None = None


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(_TOKEN.findall(text.lower()))


def lexical_tokens(text: str) -> tuple[str, ...]:
    return tuple(token for token in tokenize(text) if len(token) >= 3 and token not in _STOP)


def embed_text(text: str, dimension: int = EMBEDDING_DIMENSION) -> tuple[float, ...]:
    """Deterministic hashed bag-of-words embedding for the retrieval scaffold.

    Production model choice is an implementation detail under ADR-014. Prefix
    features let close spellings such as ship/shipping share a dimension.
    """
    if not isinstance(text, str) or not text.strip():
        raise RetrievalValidationError("text is required")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 2:
        raise RetrievalValidationError("embedding dimension is invalid")
    vector = [0.0] * dimension
    for token in tokenize(text):
        pieces = [token]
        if len(token) >= 4:
            pieces.append(token[:4])
        for piece in pieces:
            digest = hashlib.sha256(piece.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % dimension
            vector[index] += 1.0 if digest[2] % 2 == 0 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return tuple(vector)
    return tuple(value / norm for value in vector)


def vector_literal(values: Sequence[float]) -> str:
    if len(values) != EMBEDDING_DIMENSION:
        raise RetrievalValidationError("embedding dimension is invalid")
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def fts_or_query(text: str) -> str | None:
    tokens = lexical_tokens(text)
    if not tokens:
        return None
    return " | ".join(tokens)


def chunks_from_approved(knowledge=None) -> tuple[KnowledgeChunk, ...]:
    """Index the existing FR-005/FR-009 approved FAQ/policy corpus only."""
    from .support import REFERENCE_KNOWLEDGE
    entries = REFERENCE_KNOWLEDGE if knowledge is None else knowledge
    chunks = []
    for entry in entries:
        source = entry.source_references[0]
        chunks.append(KnowledgeChunk(
            chunk_id=source, source_reference=source, body=entry.answer,
            terms=" ".join(sorted(entry.keywords))))
    return tuple(chunks)


class InMemoryRetrievalStore:
    """Hybrid retrieval double for unit tests (no PostgreSQL / pgvector)."""

    def __init__(self):
        self.chunks: dict[str, dict] = {}

    def upsert(self, rows: Sequence[dict]) -> None:
        for row in rows:
            self.chunks[row["chunk_id"]] = dict(row)

    def vector_search(self, embedding, *, allowed, limit) -> list[dict]:
        ranked = []
        for row in self._filtered(allowed):
            score = sum(left * right for left, right in zip(embedding, row["embedding"]))
            ranked.append((score, row))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [self._hit(row, vector_rank=index) for index, (_, row) in enumerate(ranked[:limit], start=1)]

    def keyword_search(self, query: str, *, allowed, limit) -> list[dict]:
        needles = set(lexical_tokens(query))
        prefixes = {token[:4] for token in needles if len(token) >= 4} | {
            token for token in needles if len(token) < 4}
        if not needles:
            return []
        ranked = []
        for row in self._filtered(allowed):
            haystack = set(tokenize(f"{row['body']} {row['terms']}"))
            hay_prefixes = {token[:4] for token in haystack if len(token) >= 4} | {
                token for token in haystack if len(token) < 4}
            score = len(needles & haystack) + len(prefixes & hay_prefixes)
            if score > 0:
                ranked.append((score, row))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [self._hit(row, keyword_rank=index) for index, (_, row) in enumerate(ranked[:limit], start=1)]

    def _filtered(self, allowed):
        if allowed is not None and len(allowed) == 0:
            return []
        allowed_set = None if allowed is None else set(allowed)
        for row in self.chunks.values():
            if allowed_set is None or row["source_reference"] in allowed_set:
                yield row

    @staticmethod
    def _hit(row, vector_rank=None, keyword_rank=None):
        return {"chunk_id": row["chunk_id"], "source_reference": row["source_reference"],
                "body": row["body"], "vector_rank": vector_rank, "keyword_rank": keyword_rank}


class RetrievalService:
    """Hybrid retrieval port (ADR-014 store, ADR-015 combine + validate).

    Structured filter is the allowed `source_reference` set. Vector search
    ranks fuzzy intent; keyword/FTS ranks lexical overlap. Similarity rank is
    never business truth — callers must validate hits against an authority.
    """

    def __init__(self, store, *, embed: Callable[[str], tuple[float, ...]] | None = None,
                 limit: int = 5):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 50:
            raise ValueError("retrieval limit must be between 1 and 50")
        self.store = store
        self.embed = embed or embed_text
        self.limit = limit

    def index(self, chunks: Sequence[KnowledgeChunk]) -> int:
        if not chunks:
            raise RetrievalValidationError("at least one chunk is required")
        rows = []
        for chunk in chunks:
            chunk_id = self._token(chunk.chunk_id, "chunk id", CHUNK_ID_MAX_LENGTH)
            source = self._token(chunk.source_reference, "source reference", SOURCE_MAX_LENGTH)
            body = self._body(chunk.body)
            terms = self._terms(chunk.terms)
            embedding = self.embed(f"{body} {terms}".strip())
            rows.append({"chunk_id": chunk_id, "source_reference": source, "body": body,
                         "terms": terms, "embedding": embedding})
        self.store.upsert(rows)
        return len(rows)

    def retrieve(self, query: str, *, allowed_source_references=None) -> list[RetrievalHit]:
        text = self._query(query)
        if allowed_source_references is not None:
            allowed = tuple(self._token(item, "source reference", SOURCE_MAX_LENGTH)
                            for item in allowed_source_references)
            if not allowed:
                return []
        else:
            allowed = None
        embedding = self.embed(text)
        vector_hits = self.store.vector_search(embedding, allowed=allowed, limit=self.limit)
        keyword_hits = self.store.keyword_search(text, allowed=allowed, limit=self.limit)
        return self._fuse(vector_hits, keyword_hits)

    def _fuse(self, vector_hits, keyword_hits) -> list[RetrievalHit]:
        by_id: dict[str, dict] = {}
        vector_ids = []
        keyword_ids = []
        for rank, row in enumerate(vector_hits, start=1):
            vector_ids.append(row["chunk_id"])
            by_id.setdefault(row["chunk_id"], dict(row))
            by_id[row["chunk_id"]]["vector_rank"] = row.get("vector_rank") or rank
        for rank, row in enumerate(keyword_hits, start=1):
            keyword_ids.append(row["chunk_id"])
            by_id.setdefault(row["chunk_id"], dict(row))
            by_id[row["chunk_id"]]["keyword_rank"] = row.get("keyword_rank") or rank
        scores: dict[str, float] = {}
        for rank, chunk_id in enumerate(vector_ids, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (60 + rank)
        for rank, chunk_id in enumerate(keyword_ids, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (60 + rank)
        ordered = sorted(scores, key=lambda chunk_id: scores[chunk_id], reverse=True)
        hits = []
        for chunk_id in ordered[:self.limit]:
            row = by_id[chunk_id]
            hits.append(RetrievalHit(
                chunk_id=row["chunk_id"], source_reference=row["source_reference"],
                body=row["body"], score=scores[chunk_id],
                vector_rank=row.get("vector_rank"), keyword_rank=row.get("keyword_rank")))
        return hits

    @staticmethod
    def _token(value, label, maximum) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RetrievalValidationError(f"{label} is required")
        text = value.strip()
        if len(text) > maximum:
            raise RetrievalValidationError(f"{label} is invalid")
        return text

    @staticmethod
    def _body(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RetrievalValidationError("body is required")
        text = value.strip()
        if len(text) > BODY_MAX_LENGTH:
            raise RetrievalValidationError("body is invalid")
        return text

    @staticmethod
    def _terms(value) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise RetrievalValidationError("terms are invalid")
        text = value.strip()
        if len(text) > TERMS_MAX_LENGTH:
            raise RetrievalValidationError("terms are invalid")
        return text

    @staticmethod
    def _query(value) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RetrievalValidationError("query is required")
        text = value.strip()
        if len(text) > 500:
            raise RetrievalValidationError("query is invalid")
        return text
