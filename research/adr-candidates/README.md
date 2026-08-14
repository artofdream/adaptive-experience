# ADR promotion candidates

Quarantined CF-014 stubs and related promotion Drafts. **Do not** put issue
design notes or Accepted ADR copies here.

Gate ADRs **ADR-006…014** are Accepted on `main` (014 may be pending merge).
Next free number after ADR-014: **ADR-015+**.

## Active Drafts (promote via dedicated ADR MR)

| Candidate | Topic | Promote when | Slot |
|---|---|---|---|
| [`rag-hybrid-retrieval.md`](rag-hybrid-retrieval.md) | Hybrid structured + semantic RAG with authority validation | After [ADR-014](../../docs/06-adr/ADR-014-postgresql-pgvector.md) (pgvector) is Accepted | ADR-015+ |
| [`agentic-ai-boundary.md`](agentic-ai-boundary.md) | Agent prepares plans; services mutate; customer approves consequential acts | Free slot; complements ADR-001/009/013 | ADR-015+ |

Promotion order preference: **RAG → agentic** after pgvector (or agentic in
parallel with RAG; do not merge RAG into the pgvector ADR).

## Historical (do not re-promote)

| Candidate | Outcome |
|---|---|
| [`postgresql-pgvector.md`](postgresql-pgvector.md) | **Promoted → [ADR-014](../../docs/06-adr/ADR-014-postgresql-pgvector.md)** |
| [`confirmation-driven-experience.md`](confirmation-driven-experience.md) | **Promoted → [ADR-013](../../docs/06-adr/ADR-013-confirmation-driven-experience.md)** |
| [`kafka-event-backbone.md`](kafka-event-backbone.md) | **Kafka remains Accepted via [ADR-012](../../docs/06-adr/ADR-012-external-message-broker.md)** — Draft kept for CF-014 history only |

## Design notes (not ADR candidates)

Issue-endorsed contracts live under [`../design-notes/`](../design-notes/).
They are not ADR Drafts and must not be numbered as ADRs.
