# Draft — PostgreSQL + pgvector

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: ADR-011+.

## Intent

Use PostgreSQL as the authoritative transactional datastore and pgvector as the
semantic retrieval extension. This supports relational consistency, structured
filtering, flexible product metadata, and vector similarity without introducing
a separate vector database for the MVP.

Embeddings support retrieval; transactional facts such as price, stock, order
state, and payment state remain authoritative structured data.

## Notes

Do not Accept until experience-state / datastore ownership ADRs from the M0
gate (#107 area) are settled and a free ADR number is assigned.
