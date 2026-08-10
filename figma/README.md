# Figma Workspace

Active file (Lily's Florist MVP wireframes):

**[AEA Lily Florist Wireframes](https://www.figma.com/design/4PNLwici0GMwU824BpoZ38)**

## Pages (live inventory)

| Page | Status | Contents |
|---|---|---|
| AEA Design System | Active | Grayscale components + `adaptive-workspace-mvp` frame (Header, T-01…T-08, ASO) |
| Discovery v0.1 | Active | Composed Adaptive Workspace MVP (component instances) |
| Recommendation Journey | Stub | Placeholder for journey step frames |
| Delivery Journey | Stub | Placeholder |
| Customer Support | Stub | ASO / Future T-09 escalation placeholder |
| Discovery v1.0 | Planned stub | Not yet designed |
| Discovery v2 | Planned stub | Not yet designed |
| Presentation | Planned stub | Not yet designed |

MVP fidelity (aligned with local SVGs / CF-007–CF-009):

- T-03 — Available badges on recommendation cards
- T-04 — Flower Type, Colour, Size, Ribbon, Gift Card
- T-08 — Contact Florist + Escalate (Future)

Local SVG exports and structure notes:
`implementations/florist/wireframes/` (see that README).
Reusable split assets: `assets/`.

## Cursor integration

This folder is the **page inventory** for AEA design work in Figma.
The live file URL is linked above; do not commit Figma tokens here.

Cursor is wired to the **official Figma MCP** via the Figma plugin
(`plugin-figma-figma` → `https://mcp.figma.com/mcp`):

- Authenticate once in **Cursor Settings → Tools & MCP** (Connect next to Figma)
  if tools fail or return “Not connected”.
- Paste a `figma.com` URL or ask the agent to create/update pages from the list
  above.
- Useful agent skills: `/figma-use`, `/figma-generate-design`,
  `/figma-design-to-code`, `/figma-generate-library`.

Do not put Figma API tokens in this repo. Auth is OAuth via Cursor’s MCP
connection.
