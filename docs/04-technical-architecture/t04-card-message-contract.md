# T-04 Selection Options Contract

Status: Accepted implementation contract

Related: ADR-006 (customization boundary, thin FR-003 amendment), ADR-008
(contract-first messaging), FR-003 (thin compositional options), FR-013 (MVP
selection), FR-018 (order summary), FR-020 (selective regeneration), T-04
(Product Selection and Customization), `product.selected` topic.

This contract makes T-04 selection options explicit. It governs the
`product.selected` payload `options` object, the BFF `POST /api/v1/selection`
request, and the `orchestration.experience_session` `decisions.product` facet.

## Explicit option fields

T-04 carries these optional customization fields:

| Field | Type | Bounds | Meaning |
|-------|------|--------|---------|
| `size` | string | 1–40 chars, control-free | an eligible catalog size token |
| `card_message` | string | 1–280 chars, plain text | the personal message on the physical card |
| `flower_type` | string | 1–40 chars, token | a flower tag eligible for the selected product |
| `colour` | string | 1–40 chars, token | reference colour vocabulary |
| `ribbon` | string | 1–40 chars, token | reference ribbon vocabulary |

No other option key is accepted (`additionalProperties: false` on the `options`
object; unknown keys rejected in code). Stored-value gift cards and free-form
bouquet composition remain excluded.

Authoritative catalog and inventory own size eligibility; this contract validates
only the field shape for `size`. Enforcing that `size` is an eligible catalog
variant is FR-013 (#32).

`flower_type` must match a flower tag on the selected product in the reference
catalog. `colour` and `ribbon` use fixed reference allowlists until a Catalog SoT
exists; they are not priced or reserved as separate SKUs in this thin slice.

### Reference vocabularies

- **Colours:** `red`, `pink`, `white`, `yellow`, `purple`, `mixed`
- **Ribbons:** `none`, `satin`, `organza`, `kraft`

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
it is **not** a separate charge and carries no stored value. Thin FR-003 option
keys (`flower_type`, `colour`, `ribbon`) likewise introduce **no compositional
surcharge** in this contract; the authoritative order summary (FR-018) continues
to price the selected catalog product. Component-level inventory and
compositional pricing remain deferred.

## State, event, and regeneration

- Selection writes `decisions.product = {product_id, options}` through
  `apply_experience_patch` and emits `product.selected` exactly once at the new
  context version (ADR-008 outbox).
- `product.selected.payload.options` uses the same explicit fields.
- Under FR-020, a later intent change deep-merges unaffected facets, so a recorded
  product selection (including size, card message, and thin FR-003 options) is
  preserved when unrelated workspace state regenerates.

## Exclusions

- No free-form bouquet composition builder.
- No stored-value gift-card product, balance, purchase, or redemption.
- No card-design selection.
- No component-level inventory reservation or compositional price lines.
