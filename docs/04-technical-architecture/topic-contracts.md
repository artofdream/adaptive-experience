# MVP Topic Contracts

This catalog assigns the ownership and access boundaries required by NFR-015.
Every payload uses the versioned envelope defined in
`technical-architecture.md`. Each topic below declares an explicit **schema
version**; machine-readable JSON Schemas use the same topic name and version
under [`schemas/`](schemas/) before implementation (for example,
`schemas/support.faq.answered.v1.0.0.json`).

**Owner / publisher** means the **bus publisher** of the governed topic (ADR-008
outbox). The Adaptive UI Workspace is a **projection** (ADR-009): it never
publishes directly to the infrastructure broker (ADR-007, ADR-010). Browser
commands enter through the BFF; **Orchestration** accepts them and publishes the
corresponding MVP topics below.

| Topic | Schema version | Owner / publisher | Authorized subscribers | Minimum payload |
|---|---|---|---|---|
| customer.message.submitted | 1.0.0 | Orchestration | AI Concierge, Workspace | message text |
| experience.intent.updated | 1.0.0 | Orchestration | Workspace, Recommendation, Delivery | structured intent |
| product.recommendations.requested | 1.0.0 | Orchestration | Recommendation | intent reference |
| product.recommendations.ready | 1.0.0 | Recommendation | Orchestration, Workspace | eligible product IDs, ranking |
| product.selected | 1.0.0 | Orchestration | Inventory, Pricing, Order, Workspace | product ID, options |
| product.customization.updated | 1.0.0 | Orchestration | Pricing, Order, Workspace | product ID, basic options |
| inventory.availability.requested | 1.0.0 | Orchestration | Inventory | product IDs, delivery date |
| inventory.availability.validated | 1.0.0 | Inventory | Orchestration, Recommendation, Workspace | product IDs, availability |
| inventory.reservation.confirmed | 1.0.0 | Inventory | Order, Orchestration | reservation ID, product IDs |
| delivery.details.updated | 1.0.0 | Orchestration | Delivery, Order, Workspace | destination reference, timing |
| delivery.slots.ready | 1.0.0 | Delivery | Orchestration, Workspace | eligible slot IDs |
| delivery.slot.selected | 1.0.0 | Orchestration | Pricing, Order, Workspace | slot ID |
| order.summary.updated | 1.0.0 | Pricing | Orchestration, Workspace, Order | itemized charges, total |
| order.checkout.requested | 1.0.0 | Orchestration | Order, Payment, Workspace | draft order ID, total |
| payment.authorization.requested | 1.0.0 | Orchestration | Payment | draft order ID, amount, payment token |
| payment.authorization.succeeded | 1.0.0 | Payment | Orchestration, Order | authorization ID, draft order ID |
| payment.authorization.failed | 1.0.0 | Payment | Orchestration, Workspace | draft order ID, recoverable error |
| order.confirmed | 1.0.0 | Order | Orchestration, Workspace, Inventory, Delivery | order ID, confirmation state |
| order.status.updated | 1.0.0 | Order | Orchestration, Workspace | order ID, authoritative status |
| support.faq.answered | 1.0.0 | AI Concierge | Workspace | answer, approved-source references |
| workspace.state.updated | 1.0.0 | Orchestration | Workspace | affected tiles, state version |

## Contract rules

- Schema versions use semantic versioning; incompatible payload changes require
  a new major version.
- Owners approve schemas and subscriber access. The bus rejects unregistered
  publishers and subscribers.
- Customer, recipient, and payment fields are references or tokens wherever
  possible. Subscribers receive only fields in the table above (NFR-017).
- The envelope and outcome are recorded for every publication (NFR-016).
- Consumers must be idempotent by message ID and reject stale context versions.

## Future topics (not MVP)

| Topic | Schema version | Owner / publisher | Authorized subscribers | Minimum payload | Scope |
|---|---|---|---|---|---|
| support.escalation.requested | 1.0.0 | Support Service | Orchestration, Workspace | escalation reason, session / context reference | Future (FR-006 / T-09) |
