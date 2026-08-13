# NFR-013 Data Protection Compliance

Status: Accepted (MVP controls)

Requirement NFR-013: Customer data shall comply with privacy and protection
requirements. Traceability: EP-007 -> NFR-US-013 -> NFR-013.

This note maps the implemented controls that satisfy NFR-013 for the MVP
reference path. The controls are defense in depth: raw sensitive customer data
never enters the platform, and the broker boundary fails closed if it ever tries
to.

## Controls

1. **Reference/token-only sensitive data.** Customer payment and recipient data
   are handled as opaque references, never raw values:
   - Payment is a `payment_reference` vault token (#38); a card-number-shaped
     reference is rejected, and authorization runs against the token.
   - Delivery recipient details are a `destination_reference` (#33), never a raw
     name/address.
   Raw card numbers, CVV, cardholder names, and recipient PII therefore never
   reach experience state, the order aggregate, events, or projections.

2. **Fail-closed broker guard.** `PayloadPrivacyGuard` (NFR-017) validates every
   publication and delivery: it rejects raw sensitive fields (`card_number`,
   `cvv`, `cardholder_name`, `recipient_name`, `recipient_address`, `email`,
   `phone`, tokens, ...), enforces each topic's minimum-payload contract (extra
   fields are rejected), the governed envelope and `security_context` shape, and
   publisher/subscriber authorization. The M5 checkout events
   (`order.checkout.requested`, `order.confirmed`) are covered like every other
   topic.

3. **Least-data projections.** The BFF shapes every workspace facet to
   non-sensitive fields, and `POST /api/v1/checkout` accepts only a
   `payment_reference` and `observed_total`, rejecting raw card fields at the
   edge. No payment total, card, or token appears in any browser-facing
   projection.

4. **Payload-free audit trail.** `orchestration.message_audit` records workflow
   metadata and outcomes only (correlation, topic, stage, context version) - never
   payloads, card data, or tokens - so tracing a checkout exposes no customer data.

5. **Perimeter controls (M1).** TLS termination at the gateway, opaque session +
   CSRF, no browser access to the broker or datastore, and stripped internal
   identity headers bound the data that can enter or leave.

## Verification

- `platform/tests/test_privacy.py` - the guard rejects raw card data in
  `order.checkout.requested`/`order.confirmed` and authorizes their clean forms.
- `platform/tests/test_checkout.py` - a card-number-shaped `payment_reference` is
  rejected; declines carry no card data.
- `platform/tests/test_postgres_integration.py` - the actual emitted checkout
  events are re-validated through `PayloadPrivacyGuard` (end-to-end broker-clean),
  and the audit trace is payload-free.
- `edge/tests/test_perimeter.py` - `/api/v1/checkout` rejects raw card fields.

## Scope

These are the MVP data-protection controls. M7 audits, exercises, and hardens
them (deployment TLS/SASL, key management, and operational verification); it does
not defer their first implementation.
