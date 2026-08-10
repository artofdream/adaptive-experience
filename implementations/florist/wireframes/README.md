# Florist wireframes

Low-fidelity grayscale wireframes for Lily's Florist, derived from
`archive/sample-layout-3-with-notes.png` and mapped to UX surfaces in
`docs/05-ux-design-guide/ux-design-guide.md`.

## Figma

Live file (drafts on Claude tsarafidy's team):

**[AEA Lily Florist Wireframes](https://www.figma.com/design/4PNLwici0GMwU824BpoZ38)**

Page inventory (see `figma/README.md`):

- **AEA Design System** — components + `adaptive-workspace-mvp`
- **Discovery v0.1** — composed MVP shell (T-01…T-08, ASO)
- **Recommendation / Delivery / Customer Support** — stubs
- **Discovery v1.0 / v2 / Presentation** — planned stubs

MVP fidelity matches local SVGs (Available badges, Colour/Ribbon, Contact Florist
+ Future escalate).
## Local artifacts

| Path | Description |
|---|---|
| `adaptive-workspace-mvp.svg` | Desktop shell: Header + T-01 Conversation + T-02 Shared Understanding + Adaptive Workspace tiles T-03…T-08 + ASO affordance |
| `adaptive-workspace-mvp.png` | Raster export of the Figma Adaptive Workspace MVP frame |
| `journey-steps/01-open-conversation.svg` | Sample step 1 → opens T-01 |
| `journey-steps/02-share-preferences.svg` | Sample step 2 → intent capture → T-02 |
| `journey-steps/03-recommendations.svg` | Sample step 3 → T-03 |
| `journey-steps/04-customize.svg` | Sample step 4 → T-04 |
| `journey-steps/05-delivery.svg` | Sample step 5 → T-05 |
| `journey-steps/06-checkout.svg` | Sample step 6 → T-06 / T-07 |
| `journey-steps/07-tracking.svg` | Sample step 7 → T-08 |
| `STRUCTURE.md` | Region → tile → asset mapping |

Reusable chrome/icons/tile pieces: `assets/` (see `assets/README.md`).

Regenerate SVGs:

```bash
python scripts/generate_florist_wireframe_assets.py
```

## Fidelity

Wireframes stay **grayscale** per the UX layout rules. The annotated sample
uses purple product chrome for presentation; that colour is not carried into
these MVP wireframes.
