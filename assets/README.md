# Assets

Shared static assets for AEA / Lily's Florist docs and wireframes.
Extracted from `archive/sample-layout-3-with-notes.png` and aligned to the UX
guide (`docs/05-ux-design-guide/ux-design-guide.md`) as **grayscale**
low-fidelity pieces.

Regenerate with:

```bash
python scripts/generate_florist_wireframe_assets.py
```

## Icons (`assets/icons/`)

| File | Use |
|---|---|
| `icon-ai-concierge.svg` | AI Floral Concierge avatar in Conversation (T-01) |
| `icon-bouquet.svg` | Product / arrangement placeholder |
| `icon-truck.svg` | Delivery affordance (T-05 / tracking) |
| `icon-location.svg` | Recipient address pin (T-05) |
| `icon-credit-card.svg` | Payment method (T-07) |
| `icon-lock.svg` | Secure checkout cue (T-07) |
| `icon-checkmark.svg` | Completed timeline / confirmation |
| `icon-clock.svg` | Delivery slot / refresh cue |
| `icon-send.svg` | Chat compose send control |
| `icon-help.svg` | Automated Support Overlay (ASO) entry |

## Chrome (`assets/chrome/`)

| File | Use |
|---|---|
| `header-bar.svg` | Global Header (logo + Orders + Help) |
| `chat-bubble-user.svg` | User message bubble (T-01) |
| `chat-bubble-assistant.svg` | Assistant message bubble (T-01) |
| `chat-input.svg` | Conversation compose field |
| `status-badge-available.svg` | Inventory / slot availability badge |
| `button-primary.svg` | Primary CTA chrome |

## Tiles (`assets/tiles/`)

| File | Use |
|---|---|
| `tile-frame.svg` | Generic Adaptive Workspace tile shell |
| `product-card.svg` | Recommendation card (T-03) |
| `order-summary.svg` | Itemized totals (T-06) |
| `tracking-timeline.svg` | Status timeline (T-08) |

Composed wireframes that assemble these pieces live under
`implementations/florist/wireframes/`.
