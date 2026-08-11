# ADR-006 — MVP Customization Boundary

Status: Accepted

Date: 2026-08-11

Related requirements: FR-003 (Future), FR-013 (MVP), FR-018 (MVP), FR-020 (MVP)

Related design element: T-04 — Product Selection and Customization

## Context
The canonical functional design defines MVP tile T-04 as product selection,
basic arrangement and size options, and a card message. It explicitly places
advanced customization under FR-003 in the Future scope.

Some supporting design artifacts describe or display T-04 controls for Flower
Type, Colour, Size, Ribbon, and Gift Card. Without a firm implementation
boundary, those controls can be mistaken for committed MVP behavior, widening
scope and making requirements, design, implementation, and acceptance tests
disagree.

This ADR resolves that discrepancy without changing the canonical scope of
FR-003.

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
- selection of a basic size option when the selected product offers one; and
- entry of a personal card message.

Flower type, colour, ribbon, and other advanced composition choices remain
Future functionality governed by FR-003. They must not be implemented as
functional MVP controls.

The wireframe label **Gift Card** is interpreted for MVP purposes as a physical
message card delivered with the ordered product. The customer supplies its
personal message through T-04. It does not authorize a stored-value gift-card
product, balance, purchase, or redemption capability.

Production MVP interfaces omit Future controls. Exploratory design artifacts
may retain them only when each control is visibly marked **Future** or
**Non-functional preview** and is non-interactive. Acceptance criteria and
implementation decisions follow the canonical requirements and this ADR, not
incidental visual fidelity to a reference artifact.

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
- MVP scope remains aligned with the canonical functional design and roadmap.
- Catalog, inventory, pricing, and fulfillment contracts need only support
  product eligibility and basic size variants for the MVP.
- Acceptance tests can distinguish committed behavior from roadmap previews.
- T-04 remains extensible when FR-003 is promoted in a future release.

### Negative
- The production MVP will not reproduce every control in the current wireframe.
- Supporting Figma inventories, wireframes, and their documentation require
  clarification or revision before they can be used as implementation guides.
- Customers cannot compose a bouquet by flower type, colour, or ribbon in the
  MVP.

### Risks
- A Future control may be reintroduced as functional behavior through design or
  implementation drift.
- “Arrangement” may be misread as free-form composition rather than selection
  of an eligible catalog product or predefined arrangement.
- “Gift Card” may be misread as a stored-value product rather than the physical
  message card delivered with the order.

## Implementation constraints
- T-04 must not accept, persist, price, reserve, or publish flower-type, colour,
  ribbon, or other FR-003 customization selections in the MVP.
- Arrangement selection must reference an authoritative eligible catalog item;
  it is not a free-form bouquet composition command.
- Available sizes must come from authoritative catalog and inventory data and
  be reflected in pricing before confirmation.
- The physical message card and its personal message must be represented as
  order content fulfilled with the selected product, not payment data or a
  stored-value gift-card product.
- Future preview controls, where retained outside the production interface,
  must be non-interactive and explicitly labelled.
- Schemas, APIs, persistence models, analytics events, and tests must not imply
  that Future customization is part of the MVP contract.

## Verification
- T-04 MVP acceptance tests cover product or arrangement selection, eligible
  size selection, and a personal card message.
- Tests confirm that changing size recalculates the authoritative order summary
  when price is affected.
- Production UI inspection finds no functional flower-type, colour, or ribbon
  controls.
- Contract and persistence reviews find no MVP fields that authorize FR-003
  customization.
- Any retained Future control is visibly labelled and cannot receive input.
- Requirements traceability continues to report FR-003 as Future.

## Revisit conditions
Revisit this decision when FR-003 is formally promoted into a dated delivery
scope, or when validated customer and operational evidence justifies a
different customization model. Promotion requires coordinated updates to the
canonical requirements, catalog and inventory models, pricing and fulfillment
rules, design artifacts, contracts, and acceptance tests before controls become
functional.
