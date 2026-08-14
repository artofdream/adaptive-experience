# Requirements Traceability Matrix

> Full BG -> EP -> US -> FR/NFR traceability, canonical with
> `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`.

## Functional requirements

| Business Goal | Epic | User Story | Requirement | Scope |
|---|---|---|---|---|
| BG-001 | EP-001 | US-001 | FR-001 | MVP |
| BG-001 | EP-001 | US-002 | FR-002 | MVP |
| BG-001 | EP-001 | US-003 | FR-003 | MVP |
| BG-002 | EP-002 | US-004 | FR-004 | MVP |
| BG-002 | EP-002 | US-005 | FR-005 | MVP |
| BG-002 | EP-002 | US-006 | FR-006 | Future |
| BG-003 | EP-003 | US-007 | FR-007 | MVP |
| BG-003 | EP-003 | US-008 | FR-008 | Future |
| BG-004 | EP-004 | US-009 | FR-009 | MVP |
| BG-004 | EP-004 | US-010 | FR-010 | Future |
| BG-005 | EP-005 | US-011 | FR-011 | MVP |
| BG-005 | EP-005 | US-012 | FR-012 | Future |
| BG-006 | EP-006 | US-013 | FR-013 | MVP |
| BG-006 | EP-006 | US-014 | FR-014 | MVP |
| BG-006 | EP-006 | US-015 | FR-015 | MVP |
| BG-007 | EP-007 | US-016 | FR-016 | Future |
| BG-007 | EP-007 | US-017 | FR-017 | Future |
| BG-006 | EP-006 | US-018 | FR-018 | MVP |
| BG-006 | EP-006 | US-019 | FR-019 | MVP |
| BG-001 | EP-001 | US-020 | FR-020 | MVP |
| BG-001 | EP-001 | US-021 | FR-021 | MVP |
| BG-001 | EP-001 | US-022 | FR-022 | MVP |
| BG-006 | EP-006 | US-023 | FR-023 | MVP |

## Non-functional requirements

| Business Goal | Epic | User Story | Requirement | Scope |
|---|---|---|---|---|
| BG-001 | EP-001 | NFR-US-001 | NFR-001 | MVP |
| BG-001 | EP-001 | NFR-US-002 | NFR-002 | MVP |
| BG-002 | EP-002 | NFR-US-003 | NFR-003 | MVP |
| BG-002 | EP-002 | NFR-US-004 | NFR-004 | MVP |
| BG-002 | EP-002 | NFR-US-005 | NFR-005 | MVP |
| BG-003 | EP-003 | NFR-US-006 | NFR-006 | MVP |
| BG-003 | EP-003 | NFR-US-007 | NFR-007 | MVP |
| BG-004 | EP-004 | NFR-US-008 | NFR-008 | Future |
| BG-005 | EP-005 | NFR-US-009 | NFR-009 | MVP |
| BG-005 | EP-005 | NFR-US-010 | NFR-010 | Future |
| BG-006 | EP-006 | NFR-US-011 | NFR-011 | MVP |
| BG-006 | EP-006 | NFR-US-012 | NFR-012 | MVP |
| BG-007 | EP-007 | NFR-US-013 | NFR-013 | MVP |
| BG-007 | EP-007 | NFR-US-014 | NFR-014 | Future |
| BG-001 | EP-001 | NFR-US-015 | NFR-015 | MVP |
| BG-001 | EP-001 | NFR-US-016 | NFR-016 | MVP |
| BG-001 | EP-001 | NFR-US-017 | NFR-017 | MVP |

## Representative architecture traceability

This section is **intentionally representative**, not a full FR→service→topic
inventory. Full BG→EP→US→FR/NFR chain coverage lives in the tables above and in
the workbook; service/topic ownership for every MVP topic lives in
`docs/04-technical-architecture/topic-contracts.md`.

**Inclusion criteria** (a row is listed here when all apply):

1. The requirement is **MVP** scope.
2. It has a **primary governed topic** (or a short, ordered MVP topic chain)
   already named in technical architecture.
3. It illustrates a distinct **authority boundary** (AI Concierge interpretive
   assist vs domain-service validation vs payment/order confirmation).

Rows are omitted when the FR is Future, when it is satisfied by another listed
MVP refinement (for example FR-015 via FR-023), or when it is workspace behavior
without a unique domain topic of its own (FR-020–FR-022 map through
`workspace.state.updated` / envelope rules rather than a separate domain stream).

| Requirement | Title | Service | Topic |
|---|---|---|---|
| FR-001 | Conversation | AI Concierge | customer.message.submitted |
| FR-007 | Recommendations | Recommendation | product.recommendations.ready |
| FR-009 | Automated FAQ (ASO) | AI Concierge | support.faq.answered |
| FR-011 | Inventory | Inventory | inventory.availability.validated |
| FR-014 | Delivery | Delivery | delivery.slot.selected |
| FR-018 | Order Summary | Pricing | order.summary.updated |
| FR-019 | Checkout and authoritative payment | Orchestration / Payment / Order | order.checkout.requested → payment.authorization.requested → payment.authorization.succeeded / payment.authorization.failed → order.confirmed |
| FR-023 | Tracking | Order | order.status.updated |
