# ADR promotion candidates (quarantined)

These drafts were briefly staged under `docs/06-adr/` with **wrong ADR numbers**
and premature **Accepted** status (CF-014). They were quarantined here so
**ADR-006…010** could land as the correctly numbered M0 gate ADRs (#104–#108).
Those gate ADRs are now **Accepted** on `main`.

| Candidate file | Topic | Future slot (tentative) |
|---|---|---|
| `postgresql-pgvector.md` | PostgreSQL + pgvector | ADR-014+ |
| `kafka-event-backbone.md` | Kafka event backbone | **Kafka remains the Accepted choice** via [ADR-012](../../docs/06-adr/ADR-012-external-message-broker.md). This Draft is historical only — do not re-promote as a second broker ADR. |
| `agentic-ai-boundary.md` | Agentic AI boundary | ADR-014+ |
| `confirmation-driven-experience.md` | Confirmation-driven experience | **Promoted → [ADR-013](../../docs/06-adr/ADR-013-confirmation-driven-experience.md)** |
| `rag-hybrid-retrieval.md` | RAG hybrid retrieval | ADR-014+ |

Remaining candidates stay **Draft** (research only). Promote into `docs/06-adr/`
only via a dedicated ADR MR with the next free number (**ADR-014+**).
