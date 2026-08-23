# Mother-birthday Path B rewalk after !224 — 17 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: path-b-deploy (!224 / c9c5c0b)
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-17T21:52 Europe/Paris
assessed_by: aea-customer-journey
stack: Public ACM TLS. Session mint **201**. Live `/assets/styles.css` is still the pre-!224 tablet rule. Did not open `/florist`. Did not invent a warehouse seeder. Did not use Compose / `https://localhost:8443`.

## Scope

PM assignment: Path B rewalk after **!224** merged (`ux/tablet-t01-above-t02` → `origin/main` **c9c5c0b**). First-time mother-birthday on **live shop only**. Confirm tablet **T-01 left of T-02** (641–960px) and mobile **T-01 above T-02** (through 640px). Payment / T-07 excluded. If tablet layout is unchanged, report **not-yet-deployed** vs product fail. Do not implement. Do not open an MR.

cursor-ide-browser created a tab, then navigate to the public origin failed (`No browser tab available` / `Browser view not found`). Walk used Playwright (Edge channel) against `https://aea.artof.link/`. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit.

## Outcome

**Shopper path completed.** T-01…T-06 passed. Select stayed enabled. Stopped before Place Order.

**Tablet !224 is not on this Path B image.** At 768×1024 and 900×1024, Conversation (T-01) still stacks **above** Intent Summary (T-02) in one column. Live CSS still has `.understanding { order: -1 }` and `grid-template-columns: 1fr` inside `@media (max-width: 60rem)`. That is the pre-!224 rule. `origin/main` c9c5c0b / `1a9fd24` is **not-yet-deployed** — not scored as a product fail.

**Mobile T-01 above T-02 already holds** at 390×844 (one column, conversation top 160 vs understanding 1048).

Picked Budget Mixed Bunch, Standard, card message. Delivery **2026-08-24** morning + destination reference `home`. Order summary itemized **Total $47.00**.

Wait tag **`path-b-deploy`** for the tablet layout only. Shopper journey itself has no blocker.

## Tile results

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer. Session mint 201. |
| T-01 thought completion | pass | `I need flowers…` posted. Chips: for Mom, for a birthday, under $75. Typing remained available. |
| T-01 Send + T-02 | pass | `Birthday flowers for Mum, under $75`. Facets: birthday / mother / 75. Review and correct visible. Messages 202. No `csrf_rejected`. |
| T-02 Review and correct | pass | Saved recipient to `Mum`. PATCH `/api/v1/shared-understanding` 202. |
| T-03 Recommendations | pass | Two cards under $75: Budget Mixed Bunch $35 **Available**, Classic Rose Dozen $70 **Available**. Select enabled on both. |
| T-04 Select + customize | pass | Budget Mixed Bunch; size Standard; card “Happy Birthday Mum — love you”; colour pink, ribbon satin. |
| T-05 Delivery | pass | 2026-08-24 morning; destination `home`; no street-address fields. Banner: delivery confirmed. |
| T-06 Order Summary | pass | Product $35 + delivery $12 = **Total $47.00**. |
| T-07 Checkout | blocked | Scope skip. Chrome present: Create order / Place Order, no PAN. Did not Place Order. |
| T-08 Tracking | blocked | Scope skip with payment. |
| ASO Help | pass | Overlay labeled “not a person”. Ask “When will delivery arrive?” used session delivery facts. |
| Tablet T-01 left of T-02 (!224) | blocked (not-yet-deployed) | Viewport 768×1024: T-01 top 133 / left 16 vs T-02 top 769 / left 16; one column `736px`. Same stack at 900×1024 (`868px`). Live CSS ≠ c9c5c0b sibling-grid rule. Not a product fail. |
| Mobile T-01 above T-02 | pass | Viewport 390×844: T-01 top 160 above T-02 top 1048; same left 16; one column. |

## Blockers vs friction

- **No shopper blocker.** Select works. Delivery confirms. Wait tag is **deploy**, not UX.
- **Not-yet-deployed (tablet):** Path B ECS is still serving the old 60rem rule. `order: -1` on `.understanding` does not put T-02 beside T-01. After the new image lands, tablet should show two columns with T-01 left of T-02 and tiles spanning below.
- **Friction (known):** conversation / workspace AI stayed `fallback`. Shopper path still completed.
- **Not this walk:** `csrf_rejected` not seen. `/florist` not opened. Did not Place Order. Did not invent a seeder. Compose / localhost not used.

## Evidence

- Screenshots: `research/assessments/_walk_shots_tablet_224/`
- Walker: `research/assessments/_walk_mother_birthday_tablet_224.py`
- JSON (no session tokens): `research/assessments/2026-08-17-mother-birthday-tablet-t01-t02.json`

## Highest-severity next step

Redeploy Path B UI from `origin/main` c9c5c0b, then rewalk tablet 768 and 900 only. Customer-journey will not implement. Do not open an MR from this assessment.
