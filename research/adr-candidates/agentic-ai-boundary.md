# Draft — Agentic AI boundary

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: ADR-011+.

## Intent

Use the LLM/agent layer to understand intent, retrieve grounded context, reason,
recommend, invoke approved tools, and prepare execution plans. The agent shall
not directly mutate authoritative transactional tables.

Business services validate rules, perform transactions, persist state, and
publish resulting events. Consequential actions require explicit customer
approval where appropriate.

## Notes

Aligns directionally with the technical architecture authority boundary.
Promote only with a free ADR number after M0 gate ADRs land.
