# Roadmap

> Scope aligned with the canonical MVP / Future split in
> `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`.

## MVP
Conversational discovery and thought completion, Shared Understanding (editable
intent), validated Recommendations, Product Selection with size, card message,
and thin FR-003 options (tile T-04), Delivery planning, itemized **Order Summary**,
**secure Payment & Checkout**, Order Confirmation, Order Tracking, real-time
Inventory availability, and **automated FAQ support** (FR-009).

## MVP+
Prior-order retrieval, Reorder, Modify-before-reorder, and Customer Memory / CRM.
Scheduled as **M8** (returning shopper / FR-008) then **M12** (CRM / FR-016,
FR-017). Workbook scope stays Future.

## Future
Free-form bouquet composition beyond thin T-04 option keys, inventory
forecasting & analytics, occasion reminders and engagement analytics (CRM),
voice, semantic caching, progressive hydration, and additional industry
implementations. Thin **Support Escalation** (FR-006 / T-09 Contact Florist)
is delivered; staff CRM and live chat remain Future.

Thin FR-003 option keys (`flower_type`, `colour`, `ribbon`) plus catalog **size**
and the physical **card message** are delivered on T-04 (ADR-006 amended).

## Group Milestones

The delivery pipeline is structured into 8 MVP milestones (M0–M7), five
post-MVP milestones pulled from Future (M8–M12), and an unscheduled Future
Backlog:

| Milestone | Title | Focus & Primary Deliverables | Requirements Coverage |
|---|---|---|---|
| **M0** | ADR Scope Gate | Decision gate for ADR-006 through ADR-010 (MVP boundary, topology, topic rules, datastore ownership) | Architectural decision gate |
| **M1** | Contracts & Platform Foundation | Publish 21 MVP topic schemas (`schemas/`), establish the PostgreSQL outbox and Kafka integration foundation, establish the BFF & Edge API Gateway perimeter, build CI contract guards, and enforce baseline topic governance, audit tracing, and least-data access controls | NFR-015, NFR-016, NFR-017 baseline implementation; platform & schema foundation |
| **M2** | Shared Understanding | Deliver T-01 Conversation and Intent plus T-02 editable Shared Understanding, progressive thought completion, and context versioning | FR-001, FR-002, FR-004, FR-020, FR-021, FR-022; NFR-001, NFR-002, NFR-004, NFR-005 |
| **M3** | Validated Recommendations | Deliver T-03 availability-aware Curated Recommendations, real-time product availability badges, and selection events | FR-007, FR-011; NFR-006, NFR-009 |
| **M4** | Selection, Delivery & Pricing | Deliver T-04 Product Selection (catalog size, card message, and thin FR-003 options per ADR-006), T-05 Delivery time slot planning, and dynamic pricing | FR-003, FR-013, FR-014, FR-015 |
| **M5** | Checkout & Confirmation | Deliver T-06 Order Summary breakdown, T-07 Payment & Checkout integration, and Order Confirmation | FR-018, FR-019; NFR-007, NFR-012, NFR-013 |
| **M6** | Tracking & Automated Support | Deliver approved product/policy answers, T-08 Order Tracking timeline, Contact Florist action, and Automated Support Overlay (ASO / FR-009) | FR-005, FR-009, FR-023; NFR-011 |
| **M7** | MVP Hardening | End-to-end integration, availability and performance optimization, security audit, reference deployment validation, and final verification of the governance, auditability, and privacy controls introduced in M1 | NFR-003; final validation and hardening of NFR-015, NFR-016, NFR-017 |
| **M8** | Returning shopper (Completed) | Durable prior-order recall (no login), reorder, and modify-before-reorder after same-session T-03 hint (delivered in platform/aea_platform/reorder.py). | FR-008 |
| **M9** | Assistant reliability (Completed) | AI response quality monitoring, automated CI SLO guard, and error tracking (delivered in platform/aea_platform/quality.py and edge/scripts/check_assistant_slo.py). | NFR-008 |
| **M10** | Compositional T-04 (Completed) | Option A Florist-Choice Palette Co-Creation (Pastel Romance, Vibrant Sunburst, Classic Elegant) & Pet Safety Exclusions (delivered in platform/aea_platform/selection.py per ADR-006). | FR-003 (free-form & palette co-creation) |
| **M11** | Inventory analytics depth (Completed) | Forecasting and analytics beyond the thin `/florist` snapshot trends (delivered in platform/aea_platform/forecast.py). | FR-012, NFR-010 |
| **M12** | Engagement CRM (Completed) | Occasion reminders and zero-PII engagement memory (delivered in platform/aea_platform/crm.py). Staff live chat and ticketing stay out. | FR-016, FR-017 |
| **M13** | Load & Anti-Fragile Hardening (Completed) | Option A Locust load engine (LOAD-001..004), WAF bypass token, LLM mock proxy, and Anti-Fragility patch coalescing (AFG-001..004). | NFR-003, NFR-004, NFR-006 |
| **M14** | Production Go-Live & FinOps (Reference Extension) | PaymentSimulationEngine / Stripe mock, `aea.artof.link` reference domain Terraform configuration (with multi-tenant merchant domain mapping demonstrated), and FinOps right-sizing policies. Live Stripe SDK & OAuth2 remain Future. | FR-019, NFR-015, NFR-017 |
| **M15** | Edge SSR & Progressive Hydration (Reference Extension) | Edge Nginx static pre-rendering structure, DOM hydration hooks, and sub-100ms LCP benchmark scripts. | NFR-002, NFR-004 |
| **M16** | Staff Live Chat & Operator CRM (Reference Extension) | SQL 019 ticket assignment schema, Nginx `/florist/livechat` route, and operator console UI. Python WebSocket service remains Future. | FR-006, FR-016, FR-017 |
| **M17** | Advanced Vision & Stem Composition (Reference Extension) | Stem inventory schema (SQL 020), intent cache schema (SQL 021), and dynamic stem pricing. pgvector retrieval schema delivered in Migration 013; WebRTC audio remains Future. | FR-001, FR-003, NFR-004 |
| **M18** | Multi-Domain Adapters & Global Resilience (Reference Extension) | Artisanal Bakery reference catalog (`implementations/bakery/`) and multi-tenant schema isolation (SQL 022). Cross-region RDS replication remains Future. | NFR-014, NFR-003, NFR-015 |
| **M19** | Native Mobile Companion, Android (Reference Extension) | Android/Kotlin/Jetpack Compose client consuming the existing BFF/Gateway endpoints unchanged (product-vision.md multi-surface vision) — J1–J4 parity only, no new product scope. New client surface for already-approved requirements; delivers no new FR/NFR. iOS is out of scope until this phase is validated. Google Play Store distribution is blocked pending Play Developer account activation; internal (Firebase App Distribution / sideload) validation is not blocked. | FR-001, FR-003, FR-007, FR-008, FR-009; NFR-005, NFR-009, NFR-017 (existing coverage, new client) |
| **Future** | Production Hardening Backlog | Unscheduled: Live Stripe SDK, staff OAuth2 SSO, Python WebSocket live chat backend, WebRTC audio capture, cross-region RDS replication. | Thin-delivered FR-006, FR-010, FR-012, FR-019; NFR-014 pin |

## Key Reference Journeys & Persona Mapping

To validate requirement execution across active tiles (T-01 through T-09), the delivery pipeline evaluates four primary customer journeys mapped to key personas:

| Journey | Primary Persona | Core Requirements Covered | Target Milestone Alignment |
|---|---|---|---|
| **J1: High-Urgency Same-Day Delivery** | **Urgent Sam** *(Persona 1: Last-minute giver)* | FR-001, FR-007, FR-011, FR-013, FR-019, NFR-003, NFR-006 | **M3, M4, M5 & M7 Hardening** (Availability-aware stock, immediate slot planning, express checkout) |
| **J2: Planned Family Gift & Customization** | **Planner Sarah** *(Persona 2: Thoughtful planner)* | FR-001..004, FR-013..015, FR-018, FR-019 | **M2, M4, M5** (Canonical MVP baseline: birthday card message, bouquet size, ribbon choice, named slot) |
| **J3: Accountless Instant Reorder & Recall** | **Loyal Alex** *(Persona 3: Returning buyer)* | FR-008, FR-007, ADR-013 | **M8** (Same-browser recall, prior-order T-03 hint, destination reference re-confirmation without login) |
| **J4: Post-Purchase Status & Safety Inquiry** | **Tracker Chris & Selective Taylor** *(Personas 4 & 5)* | FR-005, FR-009, FR-023, FR-003 (Palette/Pet Safety) | **M6 & M10** (T-08 order tracking, ASO FAQ overlay, pet-safety exclusions, Contact Florist escalation) |

## Notes
- Secure Payment / Checkout (FR-019) and the itemized Order Summary (FR-018) are
  MVP, not deferred.
- Human support escalation (FR-006 / T-09) is a thin Contact Florist overlay:
  the customer confirms an allowlisted reason and the system records
  `support.escalation.requested`. Automated FAQ remains ASO / FR-009. Staff
  live chat and ticketing stay in M16 extension scope; FR-016 (AI event reminders)
  and FR-017 (engagement analytics) are delivered in M12 via `crm.py`. A local
  florist operator console is defined as a fail-closed read surface for T-09
  requests and may show prior ASO answers for the same opaque session.
- Thin FR-010 situational answers (order status, session delivery, inventory
  availability) are delivered on ASO via `support.situation.answered`. They do
  not replace T-08 tracking or FR-009 policy FAQ.
- Thin FR-008 same-browser prior-order ranking hint is delivered on T-03
  behind FR-007. It does not implement persistent purchase history or CRM.
- T-04 is MVP for product/arrangement selection, eligible catalog size, the
  physical card message, and thin FR-003 option keys (flower type, colour,
  ribbon). Free-form bouquet composition and compositional inventory/pricing
  remain Future.
- NFR-015, NFR-016, and NFR-017 are implemented as platform baselines in M1 so
  governance, traceability, and least-data security are built into the BFF,
  PostgreSQL outbox, and Kafka foundation. M7 audits, exercises, and hardens
  those controls; it does not defer their first implementation until the end of
  the MVP.
- M8–M12 are delivery milestones pulled from Future. They do not promote
  those requirements to MVP in the workbook. M8 (returning shopper / FR-008)
  and M12 (engagement CRM / FR-016, FR-017) are Completed delivery labels;
  staff live chat and ticketing remain M16 reference-extension scope. AWS
  Path B is unparked and is not a milestone.
