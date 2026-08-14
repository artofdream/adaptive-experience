# ADR-010 — Synchronous Command and Asynchronous Event Boundaries

Status: Accepted

Date: 2026-08-11

Related requirements: NFR-004, FR-020, FR-022

Related decisions: [ADR-005](ADR-005-latest-relevant-intent-wins.md),
[ADR-008](ADR-008-contract-first-messaging.md),
[ADR-009](ADR-009-experience-state-ownership.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md)

## Context

AEA is event-driven, but customer interactions also need immediate
acknowledgement and validation. Without an explicit synchronous/asynchronous
boundary, every click risks broker round-trips that miss NFR-004 targets, or
synchronous chains that block selective regeneration (FR-020).

## Alternatives

1. **Broker-mediated interaction for every operation** — uniform; high latency
   and couples the client to infrastructure messaging.
2. **Fully synchronous workflow chains** — simple mental model; blocks the
   adaptive workspace and couples tiles to domain latency.
3. **Synchronous acknowledgement plus asynchronous domain progression** —
   immediate UX feedback; domain facts and projections advance on the bus.

## Decision

**Clients talk synchronously to application edges (UI → BFF/API → orchestration
as applicable). Authoritative domain progression and cross-service coordination
are asynchronous on the Central Message Bus.** Clients never publish directly to
infrastructure messaging.

### Interaction classes

| Flow | Synchronous (request/response) | Asynchronous (bus) |
|---|---|---|
| Discovery / conversation | Accept message; return ack + current Shared Understanding projection | `customer.message.submitted` → intent updates, tile refresh |
| Recommendation | Request generation; may return “in progress” quickly | `product.recommendations.requested` / `.ready` |
| Pricing / summary | Read current projected totals when available | `order.summary.updated` when pricing recomputes |
| Checkout / payment | Validate draft; return accept/reject of the command | `order.checkout.requested`, payment auth topics, `order.confirmed` |
| Tracking | Read authoritative status projection | `order.status.updated` |
| Support escalation | Accept Contact Florist request; return acknowledgement | `support.escalation.requested` |
| Situational support | Answer order status, delivery, or availability from session facts | `support.situation.answered` |

### Acknowledgement and timeouts

- Synchronous calls acknowledge command acceptance or validation failure within
  NFR-004 response targets whenever the edge can decide locally from
  experience-state projections and cached authoritative facts.
- Long-running domain work continues asynchronously; the UI reflects progress via
  projections (`workspace.state.updated` and related topics), not by holding the
  original HTTP/WebSocket call open for the full domain saga.
- On timeout of a synchronous edge call: surface a recoverable error; do not
  invent domain facts. Retry uses the same correlation ID where safe.
- Stale async results whose context version mismatches are rejected (FR-022).

### Correlation

- Every customer-initiated command receives a **correlation ID** at the edge.
- Bus messages for that work echo the correlation ID and context version
  (ADR-008 envelope).
- UI correlates progress and final outcomes without polling the broker.

## Rationale

Option 3 meets NFR-004, preserves FR-020 non-blocking regeneration, keeps
domain facts authoritative, and prevents the Adaptive UI from becoming a bus
publisher.

## Consequences

- Edge/BFF APIs are the only client entry points to commands and
  queries; broker credentials stay off the client.
- Orchestration translates accepted commands into outbox publications (ADR-008).
- Test plans cover ack latency, timeout behavior, correlation, and stale-result
  rejection for the flows in the table above.
- Broker product and endpoint shapes remain implementation details.
