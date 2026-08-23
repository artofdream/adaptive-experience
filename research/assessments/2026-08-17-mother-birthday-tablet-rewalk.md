# Mother-birthday tablet rewalk after !224 on Path B — 17 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: none
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-17T22:00 Europe/Paris
assessed_by: aea-customer-journey
stack: Public ACM TLS. Session mint **201**. Live `/assets/styles.css` is the !224 sibling-grid tablet rule (no `.understanding { order: -1 }` at 60rem). Did not open `/florist`. Did not invent a warehouse seeder. Did not use Compose / `https://localhost:8443`.

## Scope

PM assignment: tablet-only rewalk after Path B UI deployed from `origin/main` **c9c5c0b** (**!224**). Confirm Conversation (T-01) is **left of** Intent Summary (T-02) in the first viewport at **768** and **900**, not stacked above. Brief T-01…T-03. Full mother-birthday through T-06 optional — skipped. Payment / T-07 excluded. If tablet is still one column T-01 above T-02, score **product fail** (image is current), not deploy lag. Do not implement. Do not open an MR.

cursor-ide-browser: `browser_tabs` listed none; `browser_navigate` to the public origin failed (`No browser tab available`). Walk used Playwright (Edge channel) against `https://aea.artof.link/`. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit.

## Outcome

**Tablet !224 holds on the live image.** At 768×1024 and 900×1024, Conversation sits **left of** Intent Summary in the first viewport. Same top (133). Two equal columns. Grid areas `"conversation understanding" / "main main"`. Both tiles visible without scrolling. Not stacked.

Brief shopper path T-01…T-03 **pass**. Select stayed enabled. Stopped before customize / delivery / payment.

Picked-path evidence only as far as recommendations: Budget Mixed Bunch $35 **Available** and Classic Rose Dozen $70 **Available**.

Wait tag **`none`**. Earlier wait tag `path-b-deploy` from the same-day pre-deploy walk is cleared.

## Tile results

| Tile | Result | Notes |
|------|--------|-------|
| Tablet 768 T-01 left of T-02 | pass | Viewport 768×1024: T-01 left 16 / width 359 vs T-02 left 393 / width 359; same top 133. Both in first viewport. `order` 0 / 0. Two columns. |
| Tablet 900 T-01 left of T-02 | pass | Viewport 900×1024: T-01 left 16 / width 425 vs T-02 left 459 / width 425; same top 133. Both in first viewport. |
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer. Session mint 201. |
| T-01 thought completion | pass | `I need flowers…` posted. Chips: for Mom, for a birthday, under $75. Typing remained available. |
| T-01 Send + T-02 | pass | `Birthday flowers for Mum, under $75`. Facets: birthday / mother / 75. Review and correct visible. Messages 202. No `csrf_rejected`. |
| Tablet 768 after intent | pass | Two-column layout still holds after Shared Understanding fills. |
| T-03 Recommendations | pass | Two cards under $75: Budget Mixed Bunch $35 **Available**, Classic Rose Dozen $70 **Available**. Select enabled on both. |
| T-04…T-06 | blocked | Scope skip (optional on this rewalk). |
| T-07 Checkout | blocked | Scope skip. Did not Place Order. |
| T-08 Tracking | blocked | Scope skip with payment. |

## Blockers vs friction

- **No shopper blocker.** Tablet layout matches !224. T-01…T-03 work.
- **No product fail** on the assigned tablet check. Live CSS matches c9c5c0b (sibling comment, two-col areas, no `order: -1`).
- **Friction (known):** conversation / workspace AI stayed `fallback`. Shopper path still completed through T-03.
- **Not this walk:** `csrf_rejected` not seen. `/florist` not opened. Did not Place Order. Did not invent a seeder. Compose / localhost not used. Mobile 390 not re-checked (tablet-only assignment).

## Evidence

- Screenshots: `research/assessments/_walk_shots_tablet_rewalk/`
- Walker: `research/assessments/_walk_mother_birthday_tablet_rewalk.py`
- JSON (no session tokens): `research/assessments/2026-08-17-mother-birthday-tablet-rewalk.json`
- Prior same-day walk (not-yet-deployed): `research/assessments/2026-08-17-mother-birthday-tablet-t01-t02.md`

## Highest-severity next step

None for tablet T-01 / T-02. !224 is on Path B and the first viewport is two columns. Customer-journey will not implement. Do not open an MR from this assessment.
