# Draft — Kafka event backbone (historical)

Status: Historical Draft — **Kafka is Accepted in
[ADR-012](../../docs/06-adr/ADR-012-external-message-broker.md)**

Quarantined from a misnumbered `docs/06-adr/` stub (CF-014). The broker product
decision later landed as ADR-012; Kafka remains the correct MVP choice.

## Intent

Use Kafka as the asynchronous messaging backbone for commands and domain events
between application components. Kafka transports messages; deterministic
application logic remains responsible for business-process orchestration and
state transitions.

Use domain-oriented topics, versioned schemas, correlation identifiers, and
stable business keys such as `order_id`.

## Notes

Do **not** promote this file as a second broker ADR. Canonical decision,
operating baseline, and consequences live in ADR-012. Keep this Draft only as
quarantine history from CF-014.
