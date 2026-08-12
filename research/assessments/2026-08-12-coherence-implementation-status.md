# Coherence + implementation status — 2026-08-12

tags: #aea #coherence-assessment #implementation-status
status: m3-ready
assessed_ref: cb09376
assessed_by: codex

## Scope and verdict

This refresh assesses merged `main` after completion of the M0–M2 delivery
sequence. The canonical workbook, published requirements, traceability matrix,
21 governed MVP payload schemas, executable `platform/` and `edge/` runtimes,
and live GitLab milestones were reconciled.

**M0, M1, and M2 are complete.** The coherence and topic-schema guards pass.
GitLab records M0 as 5/5 closed, M1 as 8/8 closed, and M2 as 11/11 closed.
M2 was closed after this verification.

## Milestone coverage

| MS | GitLab | Implementation assessment |
|----|--------|---------------------------|
| M0 | Closed, 5/5 | ADR-006–012 accepted; scope, topology, messaging, state, datastore, and broker decisions complete |
| M1 | Closed, 8/8 | Contract, PostgreSQL/outbox, Kafka, Edge/BFF, audit, privacy, and CI baseline complete |
| M2 | Closed, 11/11 | T-01/T-02, AI availability/fallback, state preservation, correction, stale-result rejection, browser UX, compatibility, performance, transparency, and Edge wiring complete |
| M3 | Upcoming, 2/4 complete | Accuracy and inventory-integrity NFR baselines closed; inventory (#30) and recommendations (#26) remain |

## M0 implementation coverage

- ADR-006 defines the MVP customization boundary.
- ADR-007 defines the initial modular-monolith deployment topology.
- ADR-008 defines contract-first messaging and the transactional outbox.
- ADR-009 defines experience-state ownership and persistence.
- ADR-010 defines synchronous commands and asynchronous events.
- ADR-011 selects PostgreSQL; ADR-012 selects Kafka.

## M1 implementation coverage

- 21 versioned MVP semantic payload schemas plus the governed envelope.
- PostgreSQL experience state, optimistic mutation, transactional outbox, and
  projection dependencies.
- Kafka provisioning, acknowledged publication, manual offsets, retry/DLQ
  routing, and idempotent consumption.
- TLS Edge Gateway and BFF perimeter with authentication, session, CSRF,
  least-data projections, correlation, and no browser broker access.
- Publisher/consumer authorization, payload-free audit tracing, sensitive-field
  rejection, and CI coherence/schema/unit/container checks.

These are production-oriented baselines. M7 retains deployment, resilience,
security, and operational hardening.

## M2 implementation coverage

| Capability | Evidence | Status |
|------------|----------|--------|
| Conversational discovery | #20 / FR-001 | Complete |
| Structured intent and progressive prompts | #21 / FR-002 | Complete |
| Available provider-neutral AI with fallback | #23 / FR-004 | Complete |
| Preserve unaffected state | #39 / FR-020 | Complete |
| Review and correct inference | #40 / FR-021 | Complete |
| Reject stale/future results | #41 / FR-022 | Complete |
| Intuitive browser interface | #43 / NFR-001 | Complete baseline |
| Desktop/tablet/mobile compatibility | #44 / NFR-002 | Complete baseline |
| Standard-query response within three seconds | #46 / NFR-004 | Complete reference-path evidence |
| AI-generated response disclosure | #47 / NFR-005 | Complete |
| Edge-to-Orchestration runtime path | #130 / CF-034 | Complete |

The reference integration exercises TLS, authentication, BFF, Orchestration,
PostgreSQL, AI fallback, context versions, and least-data projections. The
latest ten-query guard measured about 0.09 seconds p95/max against NFR-004's
three-second limit.

## M3 readiness and dependency order

M3 is **Validated Recommendations** and covers FR-007, FR-011, NFR-006, and
NFR-009. GitLab already records #48/NFR-006 and #51/NFR-009 complete. The clean
implementation order is:

1. **#30 / FR-011 — Inventory:** establish the authoritative availability read
   model, governed availability validation, freshness, and selection-time
   revalidation.
2. **#26 / FR-007 — Recommendations:** consume current intent plus validated
   availability and produce explainable, selectable recommendations.

FR-005 remains in M6 with approved product/policy answers. NFR-003 remains in
M7 for measured 99.5% assistant availability and operational hardening. This
placement matches live GitLab and prevents those requirements from being
silently treated as M3 completion criteria.

## Remaining coherence queue before M3 code

- P1: CF-030 Wiki ADR index, CF-031 obsolete docs-only repository description,
  CF-033 stale platform introduction, and post-merge verification of CF-034.
- P2: CF-032 root README repository-area navigation.

No unresolved M0–M2 implementation issue blocks M3 after those documentation
and audit-trail corrections.
