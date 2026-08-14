# ADR promotion candidates

Quarantined CF-014 stubs and related promotion Drafts. **Do not** put issue
design notes or Accepted ADR copies here.

Gate ADRs **ADR-006…012** are Accepted on `main`. **ADR-013** (confirmation-
driven experience) is Accepted on branch
`docs/adr-013-confirmation-driven-experience` pending merge.

Next free Accepted number after ADR-013 merges: **ADR-014+**.

## Active Drafts (promote via dedicated ADR MR)

| Candidate | Topic | Promote when | Slot |
|---|---|---|---|
| [`postgresql-pgvector.md`](postgresql-pgvector.md) | `pgvector` (and retrieval-store) on PostgreSQL | Semantic retrieval justified; keep experience-state independent of vectors ([ADR-011](../../docs/06-adr/ADR-011-experience-state-datastore.md)) | ADR-014+ |
| [`rag-hybrid-retrieval.md`](rag-hybrid-retrieval.md) | Hybrid structured + semantic RAG with authority validation | After pgvector (or equivalent) is Accepted | ADR-014+ (after pgvector) |
| [`agentic-ai-boundary.md`](agentic-ai-boundary.md) | Agent prepares plans; services mutate; customer approves consequential acts | Free slot; complements ADR-001/009/013 | ADR-014+ |

Promotion order preference: **pgvector → RAG → agentic** (or agentic in
parallel; do not merge RAG into the pgvector ADR).

## Historical (do not re-promote)

| Candidate | Outcome |
|---|---|
| [`confirmation-driven-experience.md`](confirmation-driven-experience.md) | **Promoted → [ADR-013](../../docs/06-adr/ADR-013-confirmation-driven-experience.md)** |
| [`kafka-event-backbone.md`](kafka-event-backbone.md) | **Kafka remains Accepted via [ADR-012](../../docs/06-adr/ADR-012-external-message-broker.md)** — Draft kept for CF-014 history only |

## Design notes (not ADR candidates)

Issue-endorsed contracts live under [`../design-notes/`](../design-notes/).
They are not ADR Drafts and must not be numbered as ADRs.
