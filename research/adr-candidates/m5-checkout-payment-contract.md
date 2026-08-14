# Design note — M5 checkout, payment, and confirmation (#38 / #55)

status: accepted (2026-08-13)
for_issues: "#38 (FR-019 Payment & Checkout), #55 (NFR-013 Security)"
affects: "M5; builds on #32 order aggregate, #37 order summary, #34 status lifecycle"
author: claude
date: 2026-08-13

> **Decisions (endorsed 2026-08-13):**
> 1. Lifecycle: insert `confirmed` -> `created, submitted, confirmed, preparing,
>    dispatched, delivered` (`confirmed` is already permitted by the migration-008
>    CHECK, so this is a code-only sequence change - no migration).
> 2. Authorization is **synchronous** against a `payment_reference`, behind a
>    small `PaymentAuthority.authorize(payment_reference, total)` seam so moving to
>    an async payment-service consumer later only relocates the call site, not the
>    contract. The governed events are emitted in sync, keeping the contract
>    async-ready.
> 3. `payment_reference` is an opaque client-supplied token (real minting is a
>    vault concern).

## Decision to settle before code

M5 checkout introduces the first payment handling. This note fixes the
payment-data boundary (reference/token only), the checkout -> confirmation flow
and events, where confirmation sits in the order lifecycle, and the NFR-013
security scope, so #38 and #55 land consistently on the existing substrate.

## Grounding (already in place)

- **Governed events keep payment data out by contract:**
  - `order.checkout.requested` (orchestration -> order/payment/workspace, key
    `draft_order_id`): payload `{draft_order_id, total}` - no card fields.
  - `order.confirmed` (order -> orchestration/workspace/inventory/delivery, key
    `order_id`): payload `{order_id, confirmation_state}`.
  - `order.summary.updated` (pricing): `{itemized_charges, total}` - delivered as
    the #37 `order_summary` read projection.
- **`PayloadPrivacyGuard` forbids raw payment/card fields** in envelopes:
  `card_number`, `cardholder_name`, `cvv`, `access_token`, `authorization`,
  `password`, ... ("use references or tokens").
- Order aggregate `orchestration.customer_order` (#32) with status lifecycle
  `created -> submitted -> preparing -> dispatched -> delivered` (#34); the CHECK
  constraint also permits `confirmed` and `cancelled`.

## Payment data boundary (settled by contract + guard)

- The customer supplies a **`payment_reference`** - an opaque token for a payment
  method held in a PCI-scoped vault/provider. Raw card number, CVV, and
  cardholder name **never** enter experience state, the order aggregate, events,
  or projections; the guard rejects them.
- Authorization runs against the `payment_reference`, not raw card data. For the
  MVP reference path this is a deterministic reference payment authority (like the
  reference inventory/recommendation implementations), not a real gateway.
- No payment total, card, or token appears in any least-data projection; the
  workspace only ever shows order status and the (non-payment) order summary.

## Checkout -> confirmation flow (FR-014 #38)

1. From an assembled, priced order (#32 + #37), the customer initiates checkout
   with a `payment_reference` and the observed `total`.
2. Orchestration marks the order `submitted` and emits `order.checkout.requested`
   `{draft_order_id, total}`.
3. The reference payment authority authorizes against `payment_reference`.
4. On success the order service sets status `confirmed` and emits `order.confirmed`
   `{order_id, confirmation_state}`; the workspace `order` facet reflects
   `confirmed`. On failure the order stays `submitted` and the response carries a
   stable decline code (no card data).
5. BFF `POST /api/v1/checkout` (CSRF-guarded) accepts `{payment_reference,
   observed_total}` only; raw card fields are rejected at the edge.

## Order lifecycle placement of `confirmed`

Confirmation sits between submission and fulfillment. Extend the status sequence
to `created -> submitted -> confirmed -> preparing -> dispatched -> delivered`
(small migration in #38); the #34 forward-only advance then continues from
`confirmed`. Checkout confirmation is its own operation (emits `order.confirmed`),
distinct from the fulfillment `order.status.updated` advances.

## NFR-013 security scope (#55)

NFR-013 ("customer data shall comply with privacy and protection requirements")
largely rides on the reference-only design plus the existing guard and audit:

- Assert the guard rejects payment/card fields in checkout events and requests.
- Confirm the payment-free audit trail (correlation only, no card/token) covers
  checkout and confirmation.
- Confirm least-data projections never surface payment data.
- Add regression tests for each of the above; this is verification/hardening, not
  a new subsystem.

## Future evolution: async payment authorization

Delivered by #148 / PaymentCheckoutHandler:

- Checkout HTTP submits only: stores a private `checkout_intent`, emits
  `order.checkout.requested`, returns `202 accepted` + `pending: true`.
- The **payment** consumer authorizes against the private `payment_reference`
  (never on the bus), emits `payment.authorization.succeeded|failed`, and on
  success the order path emits `order.confirmed`.
- The reference orchestration path dispatches that consumer in-process after
  submit (same handler Kafka workers use). Browser observes confirmation via
  workspace/stream refresh, not an inline confirm code on the HTTP response.

## Build order

`#38 (checkout + payment reference + confirmation)` -> `#55 (NFR-013 security
verification)`. #55 rides on #38's reference-only design. Async payment is a
post-MVP evolution (#148), not required for the MVP reference path.

## Open questions

1. **`payment_reference` minting** - where the token originates (payment
   vault/provider); for the reference path, an opaque client-supplied token.
2. **Checkout idempotency** - one confirmation per order; re-checkout on an
   already-`confirmed` order returns 409.
3. **Sync vs async authorization** - the reference path authorizes synchronously
   and still emits the governed events for audit/other services; a real deployment
   would consume `order.checkout.requested` in a payment service and emit
   `order.confirmed` asynchronously. (Lean: synchronous reference now.)
4. **`confirmed` migration** - insert into the advance sequence at index 2; verify
   the #34 forward-only rule still holds.
