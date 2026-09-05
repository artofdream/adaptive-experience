# ADR-006 — MVP Customization Boundary

Status: Accepted

Date: 2026-08-11

Related requirements: FR-003 (MVP thin options), FR-013 (MVP), FR-018 (MVP), FR-020 (MVP)

Related design element: T-04 — Product Selection and Customization

## Context
The canonical functional design defines MVP tile T-04 as product selection,
basic arrangement and size options, and a card message. FR-003 originally
covered advanced customization in Future scope; a later thin promotion brings
discrete flower-type, colour, and ribbon option keys into MVP without
authorizing free-form bouquet composition.

Some supporting design artifacts describe or display T-04 controls for Flower
Type, Colour, Size, Ribbon, and Gift Card. Without a firm implementation
boundary, those controls can be mistaken for free-form composition or
gift-card products, widening scope and making requirements, design,
implementation, and acceptance tests disagree.

This ADR resolves that discrepancy and records the thin FR-003 amendment.

## Decision drivers
- Preserve the canonical MVP and Future requirement scopes.
- Keep the first implementation small enough to validate the adaptive journey.
- Preserve completed selections when unrelated workspace state regenerates
  under FR-020.
- Avoid presenting controls that imply unsupported or non-authoritative choices.
- Give design, engineering, and testing one unambiguous T-04 boundary.
- Permit future customization to be added without redesigning the tile's role.

## Alternatives

### Include every control shown in the current wireframe
Implement Flower Type, Colour, Size, Ribbon, and Gift Card in the MVP.

This maximizes visual fidelity but silently promotes Future functionality into
the MVP and creates requirements and validation work not authorized by the
canonical scope.

### Remove all Future controls from MVP artifacts and interfaces
Show only the controls that are functional in the MVP.

This produces the clearest customer experience and is preferred for the
production interface, but reference artifacts may still need to communicate
the longer-term product direction.

### Retain Future controls as explicit, non-interactive previews
Allow advanced controls to remain in exploratory or roadmap-oriented artifacts
only when they are clearly marked Future and cannot be mistaken for available
MVP functionality.

This preserves design intent but introduces a risk that disabled controls are
treated as incomplete MVP work.

## Decision
MVP T-04 supports:

- selection of an eligible product or arrangement;
- selection of a basic size option when the selected product offers one;
- entry of a personal card message; and
- thin FR-003 compositional option keys (`flower_type`, `colour`, `ribbon`) as
  accepted and persisted selection options (see Amendment — Thin FR-003 options).

Free-form bouquet composition, stored-value gift-card products, component-level
inventory reservation, and compositional price lines remain out of scope.

The wireframe label **Gift Card** is interpreted for MVP purposes as a physical
message card delivered with the ordered product. The customer supplies its
personal message through T-04. It does not authorize a stored-value gift-card
product, balance, purchase, or redemption capability.

Production MVP interfaces may expose interactive controls for the thin FR-003
keys. Exploratory design artifacts that show free-form composition or gift-card
products must mark those controls **Future** or **Non-functional preview** and
keep them non-interactive. Acceptance criteria and implementation decisions
follow the canonical requirements and this ADR (including the thin-FR-003
amendment), not incidental visual fidelity to a reference artifact.

> **Historical note:** The 2026-08-11 Decision deferred flower type, colour, and
> ribbon entirely to Future FR-003. The 2026-08-14 amendment promotes those three
> keys as a thin MVP slice without authorizing free-form composition.

## Rationale
The selected boundary preserves traceability while delivering the smallest
useful customization step in the end-to-end journey. Size and a personal
message let a customer meaningfully complete a florist order without requiring
the catalog modeling, inventory validation, pricing rules, and fulfillment
constraints needed for compositional customization.

Explicit treatment of Future controls also prevents a visual sample from
becoming an accidental source of scope.

## Consequences

### Positive
- MVP scope remains aligned with the canonical functional design and roadmap,
  including the thin FR-003 option keys.
- Catalog, inventory, pricing, and fulfillment contracts need only support
  product eligibility, basic size variants, and reference vocabularies for the
  thin option keys — not free-form composition SKUs.
- Acceptance tests can distinguish thin option keys from free-form composition
  previews.
- T-04 remains extensible when free-form composition is promoted later.

### Negative
- The production MVP will not reproduce every control in older free-form
  wireframes (gift-card products, open composition builders).
- Supporting Figma inventories, wireframes, and their documentation require
  clarification or revision when they still depict Future-only controls.
- Customers cannot free-form compose a bouquet; thin option keys are discrete
  selects, not a compositional builder.

### Risks
- Free-form composition may be reintroduced as functional behavior through
  design or implementation drift.
- “Arrangement” may be misread as free-form composition rather than selection
  of an eligible catalog product or predefined arrangement.
- “Gift Card” may be misread as a stored-value product rather than the physical
  message card delivered with the order.

## Implementation constraints
- T-04 may accept and persist thin FR-003 option keys (`flower_type`, `colour`,
  `ribbon`) per the amendment; it must not accept free-form composition controls,
  gift-card value fields, or other unknown option keys.
- Arrangement selection must reference an authoritative eligible catalog item;
  it is not a free-form bouquet composition command.
- Available sizes must come from authoritative catalog and inventory data and
  be reflected in pricing before confirmation.
- The physical message card and its personal message must be represented as
  order content fulfilled with the selected product, not payment data or a
  stored-value gift-card product.
- Free-form composition previews, where retained outside the production
  interface, must be non-interactive and explicitly labelled Future.
- Thin FR-003 keys introduce no compositional inventory reservation or
  compositional price lines in this boundary.

## Verification
- T-04 MVP acceptance tests cover product or arrangement selection, eligible
  size selection, a personal card message, and thin FR-003 option keys.
- Tests confirm that changing size recalculates the authoritative order summary
  when price is affected.
- Production UI inspection finds interactive flower-type, colour, and ribbon
  selects for the thin slice, and finds no free-form composition builder or
  gift-card product controls.
- Contract and persistence reviews authorize only the explicit option keys
  (size, card_message, flower_type, colour, ribbon).
- Any retained free-form Future control is visibly labelled and cannot receive
  input.
- Requirements traceability reports FR-003 as MVP for the thin option keys;
  free-form composition remains Future.

## Revisit conditions
Revisit this decision when free-form bouquet composition (beyond the thin option
keys) is promoted into a dated delivery scope, or when validated customer and
operational evidence justifies compositional inventory/pricing. Further
promotion requires coordinated updates to catalog and inventory models, pricing
and fulfillment rules, design artifacts, contracts, and acceptance tests.

## Amendment — Thin FR-003 options (2026-08-14)

FR-003 is promoted into MVP as a **thin** compositional options slice on T-04.

Accepted option keys in addition to size and card message:

- `flower_type` — must match a flower tag on the selected product in the
  reference catalog;
- `colour` — fixed reference vocabulary;
- `ribbon` — fixed reference vocabulary.

Still out of scope (unchanged exclusions):

- free-form bouquet composition builder;
- stored-value gift-card products;
- component-level inventory reservation;
- compositional price lines / surcharges.

Production UI may expose interactive selects for the thin keys. Contracts,
BFF allowlists, persistence, and acceptance tests accept these keys and continue
to reject unknown keys and gift-card value fields.
