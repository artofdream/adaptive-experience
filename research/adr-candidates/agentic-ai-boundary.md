# Draft — Agentic AI boundary

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: **ADR-014+** (after ADR-013 merges).

## Intent

Use the LLM/agent layer to understand intent, retrieve grounded context, reason,
recommend, invoke approved tools, and prepare execution plans. The agent shall
not directly mutate authoritative transactional tables.

Business services validate rules, perform transactions, persist state, and
publish resulting events. Consequential actions require explicit customer
approval where appropriate.

## Notes

Complements ADR-001 (intent confirmation), ADR-009 (AI non-authoritative for
experience state), and ADR-013 (confirmation-driven execution). No Accepted ADR
yet owns this boundary as a first-class decision — keep as a dedicated Draft.
