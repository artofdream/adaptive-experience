# Draft — Kafka event backbone

Status: Draft (research promotion candidate; not an Accepted ADR)

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). Tentative future
slot: ADR-011+ after broker selection (see CF-016).

## Intent

Use Kafka as the asynchronous messaging backbone for commands and domain events
between application components. Kafka transports messages; deterministic
application logic remains responsible for business-process orchestration and
state transitions.

Use domain-oriented topics, versioned schemas, correlation identifiers, and
stable business keys such as `order_id`.

## Notes

Conflicts with Proposed ADR-007 leaving the broker product-neutral until
explicitly decided. Do not Accept while topology ADR still says “broker TBD”.
