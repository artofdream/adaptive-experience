# ADR promotion candidates

Quarantined CF-014 stubs and related promotion Drafts. **Do not** put issue
design notes or Accepted ADR copies here.

Gate ADRs **ADR-006…015** are Accepted when ADR-014 and ADR-015 have merged.
Next free number after ADR-015: **ADR-016+**.

## Active Drafts (promote via dedicated ADR MR)

| Candidate | Topic | Promote when | Slot |
|---|---|---|---|
| [`agentic-ai-boundary.md`](agentic-ai-boundary.md) | Agent prepares plans; services mutate; customer approves consequential acts | Free slot; complements ADR-001/009/013/015 | ADR-016 |

## Historical (do not re-promote)

| Candidate | Outcome |
|---|---|
| [`postgresql-pgvector.md`](postgresql-pgvector.md) | **Promoted → [ADR-014](../../docs/06-adr/ADR-014-postgresql-pgvector.md)** (depends on !151) |
| [`rag-hybrid-retrieval.md`](rag-hybrid-retrieval.md) | **Promoted → [ADR-015](../../docs/06-adr/ADR-015-rag-hybrid-retrieval.md)** |
| [`confirmation-driven-experience.md`](confirmation-driven-experience.md) | **Promoted → [ADR-013](../../docs/06-adr/ADR-013-confirmation-driven-experience.md)** |
| [`kafka-event-backbone.md`](kafka-event-backbone.md) | **Kafka remains Accepted via [ADR-012](../../docs/06-adr/ADR-012-external-message-broker.md)** — Draft kept for CF-014 history only |

## Design notes (not ADR candidates)

Issue-endorsed contracts live under [`../design-notes/`](../design-notes/).
They are not ADR Drafts and must not be numbered as ADRs.
