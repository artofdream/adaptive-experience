# UX and Figma Design Guide

## Sections
- Header
- Conversation (tile T-01 Conversation and Intent)
- Shared Understanding (tile T-02 Intent Summary)
- Adaptive Workspace (tiles T-03..T-08)

## Tile mapping
The design surfaces map to the canonical tile catalog (see
`docs/03-functional-design/functional-design.md`):

| UX surface | Tile |
|---|---|
| Conversation | T-01 Conversation and Intent |
| Shared Understanding | T-02 Intent Summary |
| Recommendations | T-03 Curated Recommendations |
| Customization | T-04 Product Selection and Customization |
| Delivery | T-05 Delivery and Recipient |
| Order Summary | T-06 Order Summary |
| Checkout | T-07 Checkout and Confirmation |
| Tracking | T-08 Order Tracking |
| Automated Support Overlay (MVP) | ASO — FR-009 FAQ overlay (not a journey tile) |
| Support Escalation (T-09) | T-09 Support Escalation (FR-006) — Contact Florist |

## Typography
- AEA / H1
- AEA / H2
- AEA / H3
- AEA / Body
- AEA / Secondary
- AEA / Caption

## Layout rules
- Use Frames for major sections.
- Use Auto Layout for reusable containers.
- Keep Discovery vertical.
- Header is horizontal.
- Conversation stacks vertically.
- Avoid tabs and spaces for positioning.
- Preserve stable regions during updates.
- Use grayscale for low-fidelity wireframe SVGs.
- The runnable Adaptive Workspace (`edge/gateway/ui/`) is mid-fidelity color
  matching `archive/sample-layout-3.png` (purple primary, lavender surfaces,
  green availability/success). Journey steps 1–7 are presentations of T-01…T-08,
  not a separate wizard. ADR-006 still limits T-04 to Arrangement, Size, and
  Card message.
