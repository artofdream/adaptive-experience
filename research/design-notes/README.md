# Design notes (not ADRs)

Issue-endorsed implementation contracts. Status `accepted` here means the
**issue design option** was endorsed — not that the note is an Architecture
Decision Record under `docs/06-adr/`.

Moved out of `research/adr-candidates/` (2026-08-14) so ADR Drafts stay
unambiguous.

| Note | Topic | Issue(s) |
|---|---|---|
| [`edge-workspace-projection-contract.md`](edge-workspace-projection-contract.md) | Aggregate workspace + `changed_facets` SSE | #144 |
| [`order-delivery-domain-contract.md`](order-delivery-domain-contract.md) | M4 order / delivery / status domain | #33, #32, #34 |
| [`m5-checkout-payment-contract.md`](m5-checkout-payment-contract.md) | M5 checkout / payment / confirmed | #38, #55 |
| [`m6-order-tracking-contract.md`](m6-order-tracking-contract.md) | M6 tracking completed / delayed | #42 |
| [`m6-support-answers-contract.md`](m6-support-answers-contract.md) | M6 FAQ / approved answers | #28, #24 |
| [`pgvector-rag-scaffold.md`](pgvector-rag-scaffold.md) | Thin pgvector hybrid retrieval | #166 |

Canonical platform decisions remain in `docs/06-adr/`. ADR promotion Drafts
remain in [`../adr-candidates/`](../adr-candidates/).
