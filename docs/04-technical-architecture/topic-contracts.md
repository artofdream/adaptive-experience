# MVP Topic Contracts

This catalog assigns the ownership and access boundaries required by NFR-015.
Every payload uses the versioned envelope defined in
`technical-architecture.md`; detailed JSON Schemas are versioned under the
topic name before implementation.

| Topic | Owner / publisher | Authorized subscribers | Minimum payload |
|---|---|---|---|
| customer.message.submitted | Workspace | AI Concierge, Orchestration | message text |
| experience.intent.updated | Orchestration | Workspace, Recommendation, Delivery | structured intent |
| product.recommendations.requested | Orchestration | Recommendation | intent reference |
| product.recommendations.ready | Recommendation | Orchestration, Workspace | eligible product IDs, ranking |
| product.selected | Workspace | Orchestration, Inventory, Pricing, Order | product ID, options |
| product.customization.updated | Workspace | Orchestration, Pricing, Order | product ID, basic options |
| inventory.availability.requested | Orchestration | Inventory | product IDs, delivery date |
| inventory.availability.validated | Inventory | Orchestration, Recommendation, Workspace | product IDs, availability |
| inventory.reservation.confirmed | Inventory | Order, Orchestration | reservation ID, product IDs |
| delivery.details.updated | Workspace | Orchestration, Delivery, Order | destination reference, timing |
| delivery.slots.ready | Delivery | Orchestration, Workspace | eligible slot IDs |
| delivery.slot.selected | Workspace | Orchestration, Pricing, Order | slot ID |
| order.summary.updated | Pricing | Orchestration, Workspace, Order | itemized charges, total |
| order.checkout.requested | Workspace | Orchestration, Order, Payment | draft order ID, total |
| payment.authorization.requested | Orchestration | Payment | draft order ID, amount, payment token |
| payment.authorization.succeeded | Payment | Orchestration, Order | authorization ID, draft order ID |
| payment.authorization.failed | Payment | Orchestration, Workspace | draft order ID, recoverable error |
| order.confirmed | Order | Orchestration, Workspace, Inventory, Delivery | order ID, confirmation state |
| order.status.updated | Order | Orchestration, Workspace | order ID, authoritative status |
| support.faq.answered | AI Concierge | Workspace | answer, approved-source references |
| workspace.state.updated | Orchestration | Workspace | affected tiles, state version |

## Contract rules

- Schema versions use semantic versioning; incompatible payload changes require
  a new major version.
- Owners approve schemas and subscriber access. The bus rejects unregistered
  publishers and subscribers.
- Customer, recipient, and payment fields are references or tokens wherever
  possible. Subscribers receive only fields in the table above (NFR-017).
- The envelope and outcome are recorded for every publication (NFR-016).
- Consumers must be idempotent by message ID and reject stale context versions.
