# Wireframe structure map

Source annotation: `archive/sample-layout-3-with-notes.png`.
Canonical tile catalog: `docs/03-functional-design/functional-design.md`.

## Adaptive Workspace MVP (`adaptive-workspace-mvp.svg`)

| Region | Tile / surface | Sample journey step | Reusable assets |
|---|---|---|---|
| Top bar | Header | All steps | `assets/chrome/header-bar.svg` |
| Left column | T-01 Conversation and Intent | 1 Open, 2 Share preferences | `icon-ai-concierge`, chat bubbles, `chat-input`, `icon-send` |
| Top-right band | T-02 Intent Summary | 2 Share preferences | `tile-frame` |
| Workspace grid | T-03 Curated Recommendations | 3 View recommendations | `product-card`, `status-badge-available`, `icon-bouquet` |
| Workspace grid | T-04 Product Selection and Customization | 4 Customize bouquet | `tile-frame`, form chrome |
| Workspace grid | T-05 Delivery and Recipient | 5 Select delivery | `icon-location`, `icon-clock`, `icon-truck`, badge |
| Workspace grid | T-06 Order Summary | 6 Confirm & pay | `order-summary` |
| Workspace grid | T-07 Checkout and Confirmation | 6 Confirm & pay | `icon-credit-card`, `icon-lock`, `button-primary` |
| Workspace grid | T-08 Order Tracking | 7 Track order | `tracking-timeline`, `icon-checkmark` |
| Floating control | ASO (FAQ overlay, not a journey tile) | Cross-cutting | `icon-help` |

## Journey step SVGs

Horizontal sample flow is preserved as seven importable frames under
`journey-steps/`. They are presentation slices of the same workspace regions
above, not alternate tile IDs.

## Layout rules applied

- Header is horizontal; Conversation stacks vertically.
- Frames mark major sections; grayscale low fidelity.
- Stable regions: conversation left, shared understanding top-right, adaptive
  tiles below (selective regeneration stays within those frames).
