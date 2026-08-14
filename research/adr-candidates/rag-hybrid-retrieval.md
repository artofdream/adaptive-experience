# Draft — RAG and hybrid retrieval

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: **ADR-014+** after a pgvector (or equivalent) ADR. Depends on
[`postgresql-pgvector.md`](postgresql-pgvector.md).

## Intent

Ground recommendations in Lily's product knowledge using retrieval-augmented
generation. Use structured PostgreSQL filters for exact business constraints and
pgvector semantic search for fuzzy intent. Combine both when appropriate.

Retrieved candidates must be validated against authoritative product, inventory,
pricing, and delivery data before claims are displayed or transactions are
executed.

## Notes

Do not promote until pgvector (or an equivalent retrieval store) is Accepted.
Keep this Draft separate from the pgvector ADR (infrastructure vs retrieval
pattern). MVP support FAQ ([design note](../design-notes/m6-support-answers-contract.md))
uses approved reference answers — not this RAG path.
