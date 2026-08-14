# MVP Security Audit and NFR-015/016/017 Verification

Status: Accepted (M7 verification)

Scope: final verification and hardening review of the M1 governance, auditability,
and privacy baselines at MVP completion (M0-M6), per the M7 milestone. Deployment
hardening (production TLS/SASL, secret management) is applied in reference
deployment validation (#150).

Traceability: NFR-015 (maintainability/traceability, EP-001), NFR-016
(observability/auditability), NFR-017 (privacy/security). Builds on #55 (NFR-013
data protection).

## NFR-015 - Traceability and maintainability

- The canonical requirements workbook, the published docs, the traceability
  matrix, and the 21 governed topic schemas are held in lockstep by CI:
  `scripts/check_coherence.py` fails on any divergence in ID sets, scopes, or
  BG->EP->US->FR/NFR chains; `scripts/check_topic_schemas.py` validates the schemas
  against the reviewed payload manifest.
- Both guards pass at MVP completion. The single-source topic manifest
  (`write_mvp_topic_schemas.py`) keeps schema generation and validation aligned.

## NFR-016 - Auditability

- `orchestration.message_audit` records workflow metadata and outcomes only -
  message id, stage, actor, topic, source, correlation id, context version,
  publication time, outcome, and security context - and never payloads, card data,
  or tokens. The audit trail is therefore structurally payload-free.
- `PsycopgAuditReader.trace` returns that payload-free metadata for a correlation.
- Coverage spans every governed topic, including the M4-M6 events
  (`product.selected`, `delivery.details.updated`, `order.checkout.requested`,
  `order.confirmed`, `order.status.updated`, `support.faq.answered`): each is
  emitted through the same outbox/relay/consumer path whose publication and
  consumption stages write only metadata to `message_audit`.
- Verified by `test_payload_free_audit_trace_records_publication_and_consumption`.

## NFR-017 - Privacy and security (fail-closed)

- `PayloadPrivacyGuard` enforces the governed contract at both broker boundaries:
  publish (`PrivacyEnforcingPublisher`, and the relay's `SourceGuardedPublisher`
  which validates by the envelope's declared source) and consume
  (`GovernedConsumer`). It rejects raw sensitive fields, payload fields outside the
  minimum contract, unknown envelope/security-context fields, wrong sources, and
  wrong schema versions - fail-closed.
- **No governed topic can carry raw payment or PII.** Verified for **every** topic
  at publish and for **every** subscriber at delivery
  (`test_guard_is_fail_closed_for_every_governed_topic`).
- The forbidden-field set covers the payment and PII families (card number, CVV,
  cardholder name, recipient name/address/email, email, phone, address, and auth
  tokens/credentials) - verified by
  `test_forbidden_field_set_covers_payment_and_pii_families`.
- Sensitive data is reference-only: payment via an opaque `payment_reference`
  (#38), recipient details via `destination_reference` (#33). Raw card/PII never
  enters experience state, the order aggregate, events, or projections.
- Least-data projections: the BFF shapes every workspace facet and rejects raw
  card fields at `/api/v1/checkout`.

## Security review checklist

- **Authentication / session:** bearer authentication at the internal boundary;
  opaque `__Host-` session cookie (Secure, HttpOnly, SameSite=Lax) at the edge.
- **CSRF:** enforced on every state-changing edge request (session, commands,
  conversation, shared-understanding, selection, delivery, order, checkout,
  support).
- **No browser access to infrastructure:** the BFF owns no domain state and
  imports neither psycopg nor confluent_kafka; a boundary test asserts this. Nginx
  is the only published entry point; the BFF has no host port; internal identity
  headers are stripped before proxying.
- **Transport:** TLS termination at the gateway with security headers (CSP,
  HSTS, nosniff, frame-ancestors none). Production TLS/SASL for the broker is
  applied in #150.
- **Data protection:** reference-only payment/PII, fail-closed guard, payload-free
  audit, and least-data projections as above. Preference and delivery encryption
  posture (minimize stored sensitive fields; TLS in transit; production storage
  encryption at rest) is recorded in
  [nfr-007-012-encryption.md](nfr-007-012-encryption.md).

## Verification evidence

| Control | Requirement | Evidence |
|---------|-------------|----------|
| Docs == workbook == schemas | NFR-015 | check_coherence.py, check_topic_schemas.py |
| Payload-free audit trail | NFR-016 | test_payload_free_audit_trace_records_publication_and_consumption |
| Guard fail-closed for every topic, publish + consume | NFR-017 | test_guard_is_fail_closed_for_every_governed_topic |
| Forbidden field families complete | NFR-017 | test_forbidden_field_set_covers_payment_and_pii_families |
| Reference-only payment / PII | NFR-013/017 | test_checkout, test_delivery, nfr-013-data-protection.md |
| Preference / delivery encryption posture | NFR-007/012 | nfr-007-012-encryption.md; TLS edge; production disk encryption required |
| BFF imports no infra; boundary | NFR-017 | test_boundary_contains_no_domain_or_infrastructure_authority |

## Outcome

The M1 governance, auditability, and privacy baselines hold across the completed
MVP (M0-M6). No raw sensitive, payment, or PII data can reach experience state,
governed events, projections, or the audit trail. Remaining M7 hardening
(deployment TLS/SASL, availability, performance) is tracked in #150, #45, #152.
