# Technical Architecture

> Coherent with `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`
> and the MVP Functional Architecture (Annex A of the requirements report).

## Style
Asynchronous, event-driven, experience-oriented.

Customer-facing commands receive **synchronous acknowledgement** at application
edges; authoritative domain progression remains **asynchronous** on the bus
(see [ADR-010](../06-adr/ADR-010-command-event-boundaries.md)). Clients do not
publish directly to infrastructure messaging.

## Authority boundary
**AI interprets; domain services validate.** The AI Floral Concierge interprets
natural-language intent and generates explanations, but it is never the
authoritative source of business facts. Customer-visible facts — products,
availability, recommendations, prices, delivery windows, payments, orders, and
status — are validated by dedicated domain services before display.

## Core elements
- Adaptive UI Workspace (persistent; hosts tiles, manages arrangement)
- Backend-for-Frontend / BFF (browser session, CSRF, aggregation, streaming, and
  least-data workspace projections; separately deployed)
- AI Floral Concierge (intent interpretation and explanation)
- Experience Orchestration Engine (shared context, dependencies, workflows, context versioning, selective regeneration)
- Central Message Bus (governed, versioned topic contracts; external broker)
- Shared Understanding / experience state store

Authoritative **experience-state ownership, persistence, context versioning,
projections, and invalidation** are defined in
[ADR-009](../06-adr/ADR-009-experience-state-ownership.md). Domain services remain
authoritative for business facts.

## Initial deployment topology
MVP deployment follows [ADR-007](../06-adr/ADR-007-initial-deployment-topology.md):

- **Modular monolith backend** — Orchestration, Concierge, and authoritative
  domain modules share one deployable process with explicit module boundaries.
- **Separate Adaptive UI** — talks to the BFF, not to domain modules or the
  infrastructure broker directly.
- **Separate BFF** — owns browser-facing transport only; does not own experience
  state, workflow decisions, or domain authority.
- **External message broker** — concrete Central Message Bus for governed MVP
  topics; broker **product** remains deferred (see ADR-007 and CF-016).

## Domain services (MVP)
| Service | Responsibility | Authoritative |
|---|---|---|
| Catalog | Products, descriptions, options, media references | Yes |
| Inventory | Validate availability; reserve stock at checkout | Yes |
| Recommendation | Rank eligible products against structured intent | Yes |
| Pricing | Product, customization, delivery, tax, discounts, total | Yes |
| Delivery | Validate destination and eligible delivery windows | Yes |
| Order | Maintain draft order; create the confirmed order | Yes |
| Payment | Initiate and confirm secure payment via external provider | Yes |

Support Service publishes the thin FR-006 / T-09 human-escalation command
`support.escalation.requested` (allowlisted reason plus an opaque session
context reference) and thin FR-010 situational answers
`support.situation.answered` (order status, session delivery, inventory
availability). Customer Memory / CRM remain **Future** (FR-016 / FR-017).

MVP automated FAQ (FR-009 / ASO) does **not** require Support Service. The
**AI Floral Concierge** publishes `support.faq.answered` from approved product
and policy information (FR-005). Concierge FAQ answers are interpretive
assistance and remain non-authoritative for business facts (see authority
boundary). Contact Florist is the T-09 escalation path; it is distinct from ASO.

## Message contract (versioned envelope)
Each message on the bus carries: message ID, topic, type (event / command /
query / response), schema version, session ID, correlation ID, source, context
version, publication time, security context, minimum authorized payload, and
outcome or recoverable error information.

Authoritative publications use **contract-first JSON Schemas** and a
**transactional outbox** (see [ADR-008](../06-adr/ADR-008-contract-first-messaging.md)).

This envelope backs the governance, auditability, and least-privilege
requirements:
- NFR-015 — every topic has an owner, a versioned schema, and documented publisher/subscriber permissions.
- NFR-016 — message ID, topic, source, correlation ID, context version, publication time, outcome, and security context are recorded for auditable tracing.
- NFR-017 — payloads carry only the minimum fields each authorized subscriber needs.

## Topic groups (MVP)
The governed owner, publisher, subscriber, and minimum-payload registry is
defined in [MVP Topic Contracts](topic-contracts.md).
| Group | Topics |
|---|---|
| Intent | customer.message.submitted; experience.intent.updated |
| Recommendation | product.recommendations.requested; product.recommendations.ready; product.selected |
| Customization | product.customization.updated |
| Inventory | inventory.availability.requested; inventory.availability.validated; inventory.reservation.confirmed |
| Delivery | delivery.details.updated; delivery.slots.ready; delivery.slot.selected |
| Order | order.summary.updated; order.checkout.requested; order.confirmed; order.status.updated |
| Payment | payment.authorization.requested; payment.authorization.succeeded; payment.authorization.failed |
| Support | support.faq.answered (publisher: AI Floral Concierge; ASO / FR-009); support.situation.answered (publisher: Support Service; FR-010); support.escalation.requested (publisher: Support Service; T-09 / FR-006) |
| Workspace | workspace.state.updated |

## Supersession (Latest Relevant Intent Wins)
For the same session and stream, older in-flight responses may finish but must
not overwrite newer accepted intent. Responses whose context version does not
match the active experience state are rejected (FR-022; see ADR-005).

## Selective regeneration
Only tiles affected by a validated state change are refreshed; completed
customer decisions and unrelated state remain stable (FR-020).

## Future performance patterns
- Semantic caching
- Precomputed experience seeds
- Progressive hydration
- Optimistic acknowledgment
