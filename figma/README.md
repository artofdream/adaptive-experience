# Figma Workspace

Active file (Lily's Florist MVP wireframes):

**[AEA Lily Florist Wireframes](https://www.figma.com/design/4PNLwici0GMwU824BpoZ38)**

Recommended pages (present in the file above unless noted):

1. AEA Design System — grayscale components + imported SVG assets
2. Discovery v0.1 — Adaptive Workspace MVP (Header, T-01, T-02, T-03…T-08, ASO)
3. Discovery v1.0 — planned
4. Discovery v2 — planned
5. Recommendation Journey — sample journey step frames
6. Delivery Journey — page stub
7. Customer Support — page stub (ASO / future escalation)
8. Presentation — planned

Local SVG exports and structure notes:
`implementations/florist/wireframes/` (see that README).
Reusable split assets: `assets/`.

## Cursor integration

This folder is the **planned page inventory** for AEA design work in Figma.
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
