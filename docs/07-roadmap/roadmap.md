# Roadmap

> Scope aligned with the canonical MVP / Future split in
> `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`.

## MVP
Conversational discovery and thought completion, Shared Understanding (editable
intent), validated Recommendations, Product Selection with basic options and a
card message (tile T-04), Delivery planning, itemized **Order Summary**, **secure
Payment & Checkout**, Order Confirmation, Order Tracking, real-time Inventory
availability, and **automated FAQ support** (FR-009).

## MVP+
Prior-order retrieval, Reorder, Modify-before-reorder, and Customer Memory / CRM.

## Future
Advanced compositional customization — flower type, colour, and ribbon as
free-form composition choices (FR-003) — plus human **Support Escalation**
(FR-006 / T-09), inventory forecasting & analytics, occasion reminders and
engagement analytics (CRM), voice, semantic caching, progressive hydration, and
additional industry implementations.

MVP catalog **size** selection and the physical **card message** on T-04 are not
FR-003; they are MVP per ADR-006.

## Group Milestones

The delivery pipeline is structured into 8 implementation milestones (M0–M7) plus Future Backlog:

| Milestone | Title | Focus & Primary Deliverables | Requirements Coverage |
|---|---|---|---|
| **M0** | ADR Scope Gate | Decision gate for ADR-006 through ADR-010 (MVP boundary, topology, topic rules, datastore ownership) | Architectural decision gate |
| **M1** | Contracts & Platform Foundation | Publish 21 MVP topic schemas (`schemas/`), establish BFF & Edge API Gateway perimeter, build CI contract guards | Platform & schema foundation |
| **M2** | Shared Understanding | Deliver T-01 Conversation and Intent plus T-02 editable Shared Understanding, progressive thought completion, and context versioning | FR-001, FR-002, FR-004, FR-020, FR-021, FR-022; NFR-001, NFR-002, NFR-004, NFR-005 |
| **M3** | Validated Recommendations | Deliver T-03 Curated Recommendations, real-time product availability badges, and selection events | FR-005, FR-011; NFR-003 |
| **M4** | Selection, Delivery & Pricing | Deliver T-04 Product Selection (catalog size & card message per ADR-006), T-05 Delivery time slot planning, and dynamic pricing | FR-013, FR-014, FR-015; NFR-006, NFR-007 |
| **M5** | Checkout & Confirmation | Deliver T-06 Order Summary breakdown, T-07 Payment & Checkout integration, and Order Confirmation | FR-018, FR-019; NFR-013, NFR-014 |
| **M6** | Tracking & Automated Support | Deliver T-08 Order Tracking timeline, Contact Florist action, and Automated Support Overlay (ASO / FR-009) | FR-009, FR-023; NFR-008, NFR-009 |
| **M7** | MVP Hardening | End-to-end integration, performance optimization, security audit, and reference deployment validation | NFR-010, NFR-011, NFR-012, NFR-015, NFR-016, NFR-017 |
| **Future** | Future Backlog | Advanced compositional customization (FR-003), human support escalation (FR-006/T-09), CRM analytics (FR-007, FR-008, FR-016, FR-017), inventory forecasting (FR-012) | FR-003, FR-006, FR-007, FR-008, FR-010, FR-012, FR-016, FR-017; NFR-014 |

## Notes
- Secure Payment / Checkout (FR-019) and the itemized Order Summary (FR-018) are
  MVP, not deferred.
- Human support escalation is Future; only automated FAQ support is in the MVP,
  delivered as the Automated Support Overlay (ASO / FR-009), distinct from T-09.
- T-04 is MVP for product/arrangement selection, eligible catalog size, and the
  physical card message (ADR-006). FR-003 Future covers advanced compositional
  customization (flower type, colour, ribbon), not those MVP fields.

