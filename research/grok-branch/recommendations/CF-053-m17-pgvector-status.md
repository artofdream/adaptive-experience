# Recommendation: CF-053 — M17 / Future pgvector status

> **Finding:** CF-053 (Medium)  
> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Suggested owner:** `@aea-coherence-guardian` / `@aea-ai-engineer`  
> **Suggested branch:** `fix/cf-053-m17-pgvector-status`  
> **Do not merge from this sandbox.**

## Problem

- Roadmap **M17** and **Future** backlog say **pgvector extension remain Future**.
- Runtime already has:
  - `platform/migrations/013_retrieval_pgvector.sql`
  - Compose image `pgvector/pgvector:pg16`
  - ADR-014 PostgreSQL pgvector
- “Extension not enabled in repo” is false; “full hybrid retrieval product complete” may still be Future.

## Desired outcome

- Distinguish **extension available in reference platform** vs **productized hybrid retrieval / vision features**.
- M17/Future stop saying the extension itself is Future.
- Optional: Future backlog lists “deeper hybrid retrieval / embedding ops” rather than “pgvector extension.”

## Proposed change (focused)

### `docs/07-roadmap/roadmap.md`

- **M17:** Stem/intent-cache schemas and dynamic stem pricing as today; WebRTC audio remains Future; **pgvector extension is already enabled via migration 013 + Compose** (retrieval product depth may still be thin).
- **Future backlog:** Remove “pgvector extension” as an unscheduled enablement item; replace with retrieval/product depth if needed.

### Optional

- One cross-link to `docs/06-adr/ADR-014-postgresql-pgvector.md` and `013_retrieval_pgvector.sql`.

## Out of scope

- Building full RAG quality stack or vision pipelines
- Changing migration 013

## Acceptance checks

- [ ] No roadmap line claims pgvector extension is still Future
- [ ] ADR/migration references remain accurate
- [ ] Doc-only; coherence guard passes

## Manual GitLab steps

1. Issue CF-053 → `fix/cf-053-m17-pgvector-status`
2. Roadmap (+ optional ADR touch for consistency)
3. MR

## Evidence paths

- `docs/07-roadmap/roadmap.md` (M17, Future)
- `platform/migrations/013_retrieval_pgvector.sql`
- `platform/docker-compose.yml`
- `docs/06-adr/ADR-014-postgresql-pgvector.md`
