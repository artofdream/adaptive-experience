# Design note — Thin pgvector RAG scaffolding (#166)

status: accepted (2026-08-14)
for_issues: "#166 (pgvector + hybrid retrieval scaffold)"
affects: "platform retrieval schema; optional SupportService hook"
author: claude
date: 2026-08-14

> **Decisions (2026-08-14):**
> 1. First executable slice for [ADR-014](../../docs/06-adr/ADR-014-postgresql-pgvector.md)
>    and [ADR-015](../../docs/06-adr/ADR-015-rag-hybrid-retrieval.md). Docs ADRs stay as-is.
> 2. Corpus is the existing FR-005/FR-009 `REFERENCE_KNOWLEDGE` in `support.py`. No new
>    knowledge product.
> 3. Live `POST .../support` keeps the deterministic matcher only. Retrieval is an
>    optional constructor hook, not a replacement of the fail-closed FAQ path.

## Model

- **Migration 013**: `CREATE EXTENSION vector` plus `retrieval.knowledge_chunk` (body,
  lexical `terms`, `vector(32)` embedding, generated `tsvector`). Orchestration
  experience-state tables do not reference this schema.
- **`RetrievalService`**: indexes approved chunks with a deterministic hashed embedding
  (scaffold; production model is an ADR-014 implementation detail). Hybrid retrieve
  combines `pgvector` cosine distance with PostgreSQL FTS (OR lexemes), fused by
  reciprocal rank. `allowed_source_references` is the structured filter.
- **`SupportService(retriever=...)`**: after a keyword miss, consults retrieval. A hit
  may become an answer only when it has a keyword/FTS rank **and** maps to this
  service's approved knowledge. The approved answer text is used, never the snippet.
  Vector-only nearest neighbors cannot ground a customer-visible claim.

## Local / CI

Compose and GitLab integration use `pgvector/pgvector:pg16` so `CREATE EXTENSION vector`
succeeds. Recreate the local Postgres volume if it was created from `postgres:16-alpine`.
Unit tests use `InMemoryRetrievalStore` and do not need Docker.

## Deferred

- Wiring a retriever into `InternalOrchestrationApp` / live FAQ
- Production embedding models or vendor APIs
- Recommendation/catalog RAG, FR-008, FR-010
- Agent tool-calling (ADR-016) — see [`adr-016-agentic-runtime.md`](adr-016-agentic-runtime.md)
