# T-04 Card Message and Size Contract

Status: Accepted implementation contract

Related: ADR-006 (MVP customization boundary), ADR-008 (contract-first messaging),
FR-013 (MVP selection), FR-018 (order summary), FR-020 (selective regeneration),
T-04 (Product Selection and Customization), `product.selected` topic.

This contract makes T-04 selection options explicit without reopening ADR-006. It
governs the `product.selected` payload `options` object, the BFF
`POST /api/v1/selection` request, and the `orchestration.experience_session`
`decisions.product` facet.

## Explicit option fields

MVP T-04 carries exactly two optional customization fields, kept distinct:

| Field | Type | Bounds | Meaning |
|-------|------|--------|---------|
| `size` | string | 1–40 chars, control-free | an eligible catalog size token |
| `card_message` | string | 1–280 chars, plain text | the personal message on the physical card |

No other option key is accepted. Flower type, colour, ribbon, free-form
composition, and stored-value gift cards are FR-003 Future and are rejected, so
Future customization cannot enter the MVP contract (`additionalProperties: false`
on the `options` object; unknown keys rejected in code).

Authoritative catalog and inventory own size eligibility; this contract validates
only the field shape. Enforcing that `size` is an eligible catalog variant is
FR-013 (#32).

## Card message rules

- **Optional.** An absent, `null`, empty, or whitespace-only `card_message` means
  *no card message*: it is normalized away and omitted from the stored decision
  and the emitted event. An order may proceed with no card message.
- **Length.** At most 280 characters after trimming; longer is rejected (422).
- **Characters.** Plain text. Leading and trailing whitespace is trimmed; internal
  text is preserved. Control characters other than newline and tab are rejected.
- **Sanitization.** The message is stored and rendered as plain text; it is never
  interpreted as markup. It is fulfillment content, not a command.
- **Errors.** Validation failures return a stable `validation_failed` /
  `invalid_selection_shape` outcome without mutating experience state.

## Pricing treatment

The standard physical message card is **included in the selected product price**;
it is **not** a separate charge and carries no stored value. The authoritative
order summary (FR-018, #37) must therefore reflect a zero card-message charge and
must represent the card and its message as order content fulfilled with the
product — never as payment data or a gift-card balance. This contract fixes the
rule; the order-summary tile enforces it when M5 lands.

## State, event, and regeneration

- Selection writes `decisions.product = {product_id, options}` through
  `apply_experience_patch` and emits `product.selected` exactly once at the new
  context version (ADR-008 outbox).
- `product.selected.payload.options` uses the same two explicit fields.
- Under FR-020, a later intent change deep-merges unaffected facets, so a recorded
  product selection (including its size and card message) is preserved when
  unrelated workspace state regenerates.

## Exclusions

- No flower type, colour, ribbon, or free-form composition control (FR-003).
- No stored-value gift-card product, balance, purchase, or redemption.
- No card-design selection.
