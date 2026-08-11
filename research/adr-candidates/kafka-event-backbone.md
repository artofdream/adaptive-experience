# Draft — Kafka event backbone

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: ADR-011+ after an explicit **broker product** decision (CF-016).

## Intent

Use Kafka as the asynchronous messaging backbone for commands and domain events
between application components. Kafka transports messages; deterministic
application logic remains responsible for business-process orchestration and
state transitions.

Use domain-oriented topics, versioned schemas, correlation identifiers, and
stable business keys such as `order_id`.

## Notes

ADR-007 (CF-017 / !61) requires an **external message broker** for governed MVP
topics while keeping the **broker product** deferred. Technical architecture
stays product-neutral until a dedicated broker-selection ADR is Accepted.

This Kafka draft must remain **Draft** in `research/adr-candidates/` and must
not be promoted to `docs/06-adr/` or marked Accepted while product selection is
open. Promoting Kafka would prematurely commit the architecture to a vendor
and conflict with ADR-007’s deferred-product decision.
