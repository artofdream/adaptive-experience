# Draft — PostgreSQL + pgvector

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: **ADR-014+**.

## Intent

Use PostgreSQL as the authoritative transactional datastore and pgvector as the
semantic retrieval extension. This supports relational consistency, structured
filtering, flexible product metadata, and vector similarity without introducing
a separate vector database for the MVP.

Embeddings support retrieval; transactional facts such as price, stock, order
state, and payment state remain authoritative structured data.

## Notes

[ADR-011](../../docs/06-adr/ADR-011-experience-state-datastore.md) already
Accepted PostgreSQL for **experience-state** and **explicitly deferred
`pgvector`**. This Draft is only the vector-extension / retrieval-store
decision — do not re-decide experience-state persistence.

Promote before or with [`rag-hybrid-retrieval.md`](rag-hybrid-retrieval.md);
keep experience-state independent of vector search.
