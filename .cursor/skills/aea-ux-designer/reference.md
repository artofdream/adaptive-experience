# AEA UX designer — surfaces and ADRs

Read this when assessing or implementing. Do not invent IDs; cite these.

## Journey stages → tiles

From `docs/03-functional-design/customer-journey.md`:

| Step | Stage | Active tile(s) |
|---|---|---|
| 1 | Enter / Discovery | T-01 Conversation and Intent |
| 2 | Describe need / Shared Understanding | T-01, T-02 Intent Summary |
| 3 | Review recommendations | T-03 Curated Recommendations |
| 4 | Customize | T-04 Product Selection and Customization |
| 5 | Confirm delivery | T-05 Delivery and Recipient, T-06 Order Summary |
| 6 | Review, pay, and order | T-06 Order Summary, T-07 Checkout and Confirmation |
| 7 | Track delivery | T-08 Order Tracking |

Mother-birthday script:
`implementations/florist/journeys/mother-birthday-journey.md`.

ASO is available on every stage; it is not a step. T-09 Contact Florist is a
separate overlay (thin FR-006 path).

## Tile catalog (functional-design.md)

- **T-01** — free-text conversation; optional suggestion chips (ADR-003).
- **T-02** — six facets: occasion, recipient, budget, style,
  flower_preference, timing. Review and correct (FR-021).
- **T-03** — curated cards from availability-aware **deterministic** ranking
  (FR-007 / `platform/aea_platform/recommendation.py`). Available badge
  (FR-011). Not an LLM product catalog.
- **T-04** — product selection, size, physical card message, thin FR-003 keys
  `flower_type` / `colour` / `ribbon` (ADR-006). No gift-card product.
- **T-05** — date, window, opaque `destination_reference` (NFR-017). Confirm
  saved session reference (`home`) rather than a street form (ADR-013).
- **T-06** — itemized summary, continuously updated (FR-018).
- **T-07** — confirmation-driven checkout: confirm destination, total, session
  payment reference; explicit ack. Order confirmed only after payment succeeds
  (FR-019). No card number fields.
- **T-08** — tracking timeline + Chat with Lily vs Contact Florist.
- **ASO** — `#help` dialog + `.aso` `?` button + header Help. Never blocks
  tiles (ADR-004 / FR-009). Disclose automated answers (NFR-005).
- **T-09** — `#escalation` dialog from `#contact-florist`. Allowlisted reasons
  only; least-data payload.

`/florist` is the operator sample, not a customer tile.

## ADR one-liners

| ADR | UX rule |
|---|---|
| ADR-001 | Shared Understanding is visible and correctable |
| ADR-002 | Experiences (tiles) enter/leave a stable workspace — not pages |
| ADR-003 | Progressive thought completion; chips optional; typing always allowed |
| ADR-004 | ASO ≠ T-09; Help is automated; Contact Florist is a person request |
| ADR-006 | T-04 MVP boundary (thin FR-003; card message ≠ gift card) |
| ADR-013 | T-05…T-07 confirm prior/session values; ask only for deltas |
| ADR-016 | AI interprets; domain services validate; disclose AI (NFR-005) |

## Implementation files

- `edge/gateway/ui/index.html` — structure, copy, tile eyebrows, dialogs
- `edge/gateway/ui/assets/styles.css` — layout, focus, reduced motion,
  desktop/tablet/mobile (`60rem` / `40rem`), 44px targets
- `edge/gateway/ui/assets/app.js` — `setJourneyStep`, `STEP_CAPTIONS`,
  `ERROR_COPY`, `SESSION_DESTINATION_REFERENCE`, `SESSION_PAYMENT_REFERENCE`,
  ASO vs escalation handlers
- `edge/tests/test_browser_ui.py` — copy and selector contracts; update when
  those change
- Figma mirror: `figma/README.md` + file `4PNLwici0GMwU824BpoZ38` (see skill
  Figma section). New journeys need mockups **and** a clickable prototype.

Do not treat CSRF `X-CSRF-Token` / `POST /api/v1/session` as a UX redesign.

## Assessment canvas (when assessment is the deliverable)

After reading `~/.cursor/skills-cursor/canvas/SKILL.md`, write one
`.canvas.tsx` under the workspace `canvases/` directory. Include:

1. Verdict (journey fit + highest-severity issue)
2. Findings table: tile/surface, severity, evidence, recommended tight change
3. Constraint check: ADR-002/003/004/006/013, NFR-005, NFR-017
4. Out of scope called out (wizard, LLM catalog, card fields, `/florist`, CSRF)

Link the canvas file with a markdown link in the chat reply. No empty
placeholder sections. Colors from `useHostTheme()` only.

## Accessibility bar (already in the UI)

Preserve or improve; do not regress:

- Skip links to `#conversation` and `#understanding`
- Landmarks: `header`, `main`, `section`, `aside`, `dialog`
- Labels for controls; `aria-live` on messages and adaptive region
- `:focus-visible`; `min-height: 44px`; `overflow-wrap: anywhere`
- `prefers-reduced-motion: reduce`; `forced-colors: active`
- `#disclosure` AI-generated interpretation copy (NFR-005)
