# Figma Workspace

Active file (Lily's Florist shop UI mirror + journey prototypes):

**[AEA Lily Florist](https://www.figma.com/design/4PNLwici0GMwU824BpoZ38)**
(`fileKey` `4PNLwici0GMwU824BpoZ38`)

**Runtime source of truth** is `edge/gateway/ui/` (CSS `:root` tokens, tiles,
ASO, florist chrome). Figma is the design **mirror** and the place to
**propose** new journeys. Do not invent a second CSS token system.

Sync and new-journey prototype rules:
`.cursor/skills/aea-ux-designer/SKILL.md` and
`.cursor/rules/figma-shop-ui-sync.mdc`.

## Pages (live inventory)

| Page | Status | Contents |
|---|---|---|
| Cover | Active | Shop UI library cover (15 Aug 2026) |
| Foundations | Active | `:root` color swatches + Inter type specimens |
| Components | Active | Color-matched atoms bound to AEA Shop CSS variables (includes `Journey stepper`) |
| Shop UI · current journey | Active | Mid-fidelity mockups of steps 1–7 + clickable prototype; mobile Discover chrome (`49:98`) |
| Shop UI · returning shopper (proposal) | Proposal | M8 reorder / modify-before-reorder mockups + clickable proto (#194). Not live shop. |
| Florist operator · T-09 inbox | Active | Operator console: honest empty inbox, labeled sample, staff orders (FR-013), today's prepare batching, 3-column mobile collapse, order/prepare detail dialogs, day-window filters, and ? Help routine (#213, #382, #398, #405). Mirrors `/florist`. |
| AEA Design System | Archive | Grayscale wireframe components + `adaptive-workspace-mvp` |
| Discovery v0.1 | Archive | Older composed workspace (component instances) |
| Recommendation Journey | Stub | Hidden / empty placeholder |
| Delivery Journey | Stub | Hidden / empty placeholder |
| Customer Support | Stub | Hidden / empty placeholder |
| Discovery v1.0 | Stub | Hidden / empty placeholder |
| Discovery v2 | Stub | Hidden / empty placeholder |
| Presentation | Stub | Hidden / empty placeholder |

## Frame → UI mapping

| Figma | Repo |
|---|---|
| Collection **AEA Shop CSS** (`purple`, `ink`, `page`, …) | `edge/gateway/ui/assets/styles.css` `:root` |
| Collection **AEA Wireframe Grayscale** | Archive only — not the live shop |
| Text styles `AEA/Brand` … `AEA/Button` | Inter sizes/weights in `styles.css` |
| Components `Button`, `Chip`, `Badge`, `Composer`, `Tile`, `Product Card` (`45:11`), `Header`, `ASO`, `Operator banner`, `Journey stepper` (`49:97`), `Operator nav` (`51:29`), `Operator filter buttons` (`51:40`), `Dialog sheet handle` (`51:43`), `Dialog card note` (`51:46`), `Circular scroll controls` (`51:53`) | Classes in `index.html` / `florist.html` + `styles.css`. Operator touch targets meet WCAG 2.1 ≥44×44px. |
| Shop UI · current journey `1 Discover` T-01 Chip | Live T-01 thought-completion copy (`for Mom` after a partial thought; API questions remapped in `app.js`) |
| Shop UI · current journey T-03 Product Card | Live T-03 card with vendored SKU still (`PRODUCT_ART` / `/assets/sku-*.jpg`); optional `Ordered earlier in this browser` hint uses existing `.hint` (thin FR-008, same browser, no login). Photos are category likenesses, not the shop cooler. |
| Shop UI · current journey T-04 selection thumb | Same vendored still as T-03 (`#selection-thumb`) |
| Prototype **Shop UI · current journey** | `index.html` journey steps 1–7 (`data-journey-mode="steps"`). Tablet (641–960px) keeps T-01 left of T-02; tiles span below (#215). Mobile `1 Discover · mobile` (`49:98`) shows Start–Track on one strip (#218). |
| Prototype **Shop UI · returning shopper (proposal)** | M8 FR-008 proposal only. Reorder + modify-before-reorder in the persistent workspace. Do not restyle live shop until approved. |
| Florist operator · T-09 inbox `1 Live empty` (`38:4`) | Live `/florist` empty inbox (no sample rows when operator APIs are on) |
| Florist operator · T-09 inbox `2 Sample layout` (`38:5`) | Fail-closed labeled sample; T-09 primary, session next, forecast secondary |
| Florist operator · `3 Phone · Staff orders` (`51:54`) | Phone 390: wrapped nav pills (incl. `? Help`), day-window filter pills, 3-column orders collapse, `Details ↗`, floating `↑`/`↓` (#382, #398) |
| Florist operator · `4 Phone · Order detail` (`51:289`) | Order-detail bottom sheet: handle, 44px close, facts, Jump to session / Close (#382, #398) |
| Florist operator · `5 Phone · Prepare` (`51:322`) | Phone prepare grouping: 3-column collapse + `Details ↗` (#382, #398) |
| Florist operator · `6 Phone · Prepare detail` (`51:371`) | Prepare-detail bottom sheet + `.dialog-card-note` enclosure cards (#398) |
| Florist operator · `7 Phone · Help routine` (`51:402`) | `? Help` Atelier Shift Routine dialog (#405) |
| Florist operator · `8 Tablet · Staff orders` (`51:429`) | Tablet 768: 3-column collapse, filters, `? Help`, scroll controls (#382, #398) |

Current-journey prototype (click Continue through steps 1→7):

**[Open prototype](https://www.figma.com/proto/4PNLwici0GMwU824BpoZ38?node-id=21-24&starting-point-node-id=21-24)**

Starting frame: `1 Discover` (`21:24`). Hyphens in the URL; MCP `nodeId` uses colons (`21:24`).

Returning-shopper proposal (recall → last order → reorder **or** modify → confirm delivery/pay → track):

**[Open prototype](https://www.figma.com/proto/4PNLwici0GMwU824BpoZ38?node-id=33-4&starting-point-node-id=33-4)**

Starting frame: `1 Recall` (`33:4`). Page `Shop UI · returning shopper (proposal)` (`33:3`). Branch at `3 Last order` (`33:26`): Reorder → `4 Reorder confirm` (`33:37`); Modify → `4b Modify` (`33:176`).

Florist operator T-09 (live empty ↔ fail-closed sample):

**[Open prototype](https://www.figma.com/proto/4PNLwici0GMwU824BpoZ38?node-id=38-4&starting-point-node-id=38-4)**

Starting frame: `1 Live empty` (`38:4`). Page `Florist operator · T-09 inbox` (`38:3`). Sample layout: `2 Sample layout` (`38:5`).

Florist operator phone chrome (wrapped nav, 3-col collapse, detail sheets, Help):

**[Open phone prototype](https://www.figma.com/proto/4PNLwici0GMwU824BpoZ38?node-id=51-54&starting-point-node-id=51-54)**

Starting frame: `3 Phone · Staff orders` (`51:54`). `Details ↗` → order sheet (`51:289`); Prepare `Details ↗` → prepare sheet (`51:371`); `? Help` → shift routine (`51:402`).

New journey proposals: add a page, mockup states, wire prototype connections,
then add a row here with the proto URL (file + `node-id`). After the journey
ships in `edge/gateway/ui/`, sync frames to the implemented UI.

## Cursor integration

This folder is the **page inventory** for AEA design work in Figma.
The live file URL is linked above; do not commit Figma tokens here.

Cursor is wired to the **official Figma MCP** via the Figma plugin
(`plugin-figma-figma` → `https://mcp.figma.com/mcp`):

- Authenticate once in **Cursor Settings → Tools & MCP** (Connect next to Figma)
  if tools fail or return “Not connected”.
- Skills: `/figma-use` (required before writes), `/figma-generate-library`
  (tokens/components), `/figma-generate-design` (screens + journey mockups).
- Never TalkToFigma.

Do not put Figma API tokens in this repo. Auth is OAuth via Cursor’s MCP
connection.
