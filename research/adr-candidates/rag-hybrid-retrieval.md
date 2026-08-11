# Draft — RAG and hybrid retrieval

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: ADR-011+. Depends on a datastore/pgvector decision.

## Intent

Ground recommendations in Lily's product knowledge using retrieval-augmented
generation. Use structured PostgreSQL filters for exact business constraints and
pgvector semantic search for fuzzy intent. Combine both when appropriate.

Retrieved candidates must be validated against authoritative product, inventory,
pricing, and delivery data before claims are displayed or transactions are
executed.

## Notes

Promote only after PostgreSQL/pgvector (or equivalent) is an Accepted ADR under
a correct number.
