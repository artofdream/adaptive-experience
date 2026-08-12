# Design note — M4 order and delivery domain contract (#33 / #32 / #34)

status: accepted (2026-08-12)
for_issues: "#33 (FR-014 delivery), #32 (FR-013 order), #34 (FR-015 status)"
affects: "M4; builds on #144 workspace substrate, #142 selection, #122 T-04 contract"
author: claude
date: 2026-08-12

> **Decision:** endorsed 2026-08-12. Open question #1 resolved: M4 stops at a
> created pre-checkout order aggregate; checkout, payment, and confirmation are
> M5. Recipient PII is reference-only (`destination_reference`). Build order
> #33 -> #32 -> #34.

## Decision to settle before code

The three M4 tiles are net-new authoritative domain services, unlike the M3 work
which wired existing services. This note fixes the domain model, the state facets
and events each tile uses, the recipient-PII handling, and the build order, so the
three land consistently on the existing substrate.

## Grounding (already in place)

- **Governed topics + schemas exist** (contracts ready; services do not):
  - `delivery.details.updated` (orchestration -> delivery/order/workspace):
    payload `destination_reference` (required) + `timing`.
  - `delivery.slots.ready` (delivery -> orchestration/workspace): `eligible_slot_ids`.
  - `delivery.slot.selected` (orchestration -> pricing/order/workspace): `slot_id`.
  - `order.confirmed` (order, key `order_id`); `order.status.updated` (order ->
    orchestration/workspace): `order_id`, `authoritative_status`.
  - `order.checkout.requested` (orchestration -> order/payment, key
    `draft_order_id`) and `order.summary.updated` (pricing) are **M5** (checkout /
    FR-018), not M4.
- **`decisions.delivery` is already a `projection_dependency` state facet** (like
  `decisions.product`), invalidating `order_summary`.
- **PII is already reference-based.** `PayloadPrivacyGuard.RAW_SENSITIVE_FIELDS`
  forbids `recipient_name`, `recipient_address`, `recipient_email`, `address`,
  `phone`, ... in envelopes ("use references or tokens"), and
  `delivery.details.updated` carries `destination_reference`, not a raw address.

## Domain model

### FR-014 delivery scheduling (#33) — first

- Orchestration accepts delivery details: a `timing` selection and a
  `destination_reference` (an opaque token for the recipient/address held behind a
  reference, never raw PII in state or events).
- Writes the **`decisions.delivery`** facet via `apply_experience_patch` (mirrors
  #142 selection writing `decisions.product`); emits `delivery.details.updated`.
- Slot selection writes the chosen `slot_id` and emits `delivery.slot.selected`.
  Authoritative eligible-slot computation is the `delivery` service (owner of
  `delivery.slots.ready`); for the MVP reference path this may be a deterministic
  local slot source, as inventory/recommendation are today.
- Workspace gains a **`delivery` facet** (timing, chosen slot, and a
  reference-only recipient descriptor — no raw PII), shaped least-data at the edge.

### FR-013 order creation (#32) — second

- An **order aggregate** (new persistence, keyed by `order_id`) is assembled from
  the completed decisions: `decisions.product` (+ its size/card_message options,
  #122) and `decisions.delivery`. Creation records the order and links it to the
  session/context version.
- Workspace gains an **`order` facet** (order_id + current status), least-data.
- **Boundary with M5:** FR-013 in M4 is order *creation* (a draft/created order
  from assembled decisions). Payment, `order.checkout.requested`, pricing
  `order.summary.updated`, and `order.confirmed` are **M5** (#37/#38). This note
  scopes M4 order creation to the pre-checkout aggregate; see Open questions.

### FR-015 order status (#34) — last

- Requires an order to exist (#32). The `order` service publishes
  `order.status.updated` (`order_id`, `authoritative_status`); orchestration
  consumes it and reflects status in the workspace `order` facet, so the browser
  sees preparation/dispatch/delivery status via the existing SSE stream.

## Recipient PII handling (settled by existing convention)

- Raw recipient name/address/email/phone are **never** placed in envelopes,
  experience state, or least-data projections. They flow only as a
  `destination_reference` (guard-permitted reference), consistent with
  `delivery.details.updated` and `PayloadPrivacyGuard`.
- The workspace `delivery` facet exposes only the reference and non-PII fields
  (timing, slot); the edge least-data shaper drops anything else.
- If raw recipient capture is needed for fulfillment, it lives behind the
  reference in an authoritative store, not in the experience document.

## Build order

`#33 (FR-014 delivery decision)` -> `#32 (FR-013 order from assembled decisions)`
-> `#34 (FR-015 status)`. Status is last (needs an order); order needs the delivery
decision plus the selection already delivered by #142/#122.

## Open questions

1. **FR-013 order-create vs M5 checkout boundary** - confirm M4 stops at a created
   pre-checkout order aggregate and M5 owns checkout/payment/confirmation. (Lean:
   yes; `order.checkout.requested`/`order.confirmed` are M5.)
2. **Delivery slot source** - full `delivery` service vs a deterministic reference
   slot source for the MVP path. (Lean: reference source now, mirroring the
   recommendation/inventory reference implementations.)
3. **Catalog size authority** - #122 deferred authoritative size eligibility here;
   order creation can validate assembled decisions against the reference catalog
   until a catalog authority exists.
4. **`destination_reference` minting** - where the reference is created and how it
   maps to fulfillment PII (authoritative store vs BFF-held). Settle before #33.
