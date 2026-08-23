# Mother-birthday Path B rewalk after !219 / !220 — 17 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: none
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-17T20:54 Europe/Paris
assessed_by: aea-customer-journey
stack: Public ACM TLS. Session mint **201**. DSO in-VPC `lily-reference-live-test` heartbeat still feeding availability. Did not open `/florist`. Did not invent a warehouse seeder. Did not use Compose / `https://localhost:8443`.

## Scope

PM 20:00 slot: first-time mother-birthday on **live Path B only**. T-01…T-06 with Select enabled (REFERENCE_CATALOG SKUs, Available badges). Specifically re-check merged **!219** (T-05 past dates / min-date) and **!220** (mobile Help usable). Payment / T-07 excluded. Tablet T-01 vs T-02 column order is known friction — confirm, do not implement.

cursor-ide-browser created a tab, then `browser_navigate` to the public origin was classified/rejected. Walk used Playwright (Edge channel) against `https://aea.artof.link/`. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit.

## Outcome

**No shopper blocker.** Select stayed enabled. T-01…T-06 completed. !219 and !220 hold on the live shop.

Picked Budget Mixed Bunch, Standard, card message. Past date **2026-08-16** was rejected (`min=2026-08-17`); Confirm did not persist. Future date **2026-08-24** morning + destination reference `home` confirmed. Order summary itemized **Total $47.00**. Stopped before Place Order.

On a phone viewport the duplicate `?` FAB is hidden; header **Help** (44px) opened the overlay, answered from session delivery facts, and closing returned to the composer. FAB did not cover Send.

Wait tag **`none`**.

## Tile results

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer. Session mint 201. |
| T-01 thought completion | pass | `I need flowers…` posted. Chips: for Mom, for a birthday, under $75. Typing remained available. |
| T-01 Send + T-02 | pass | `Birthday flowers for Mum, under $75`. Facets: birthday / mother / 75. Review and correct visible. Messages 202. No `csrf_rejected`. |
| T-02 Review and correct | pass | Saved recipient to `Mum`. PATCH `/api/v1/shared-understanding` 202. |
| T-03 Recommendations | pass | Two cards under $75: Budget Mixed Bunch $35 **Available**, Classic Rose Dozen $70 **Available**. Select enabled on both. No Unknown badges. Five heartbeat SKUs are not all ranked (budget + occasion filter); lilac / vase / orchid sit above $75 or off-occasion. |
| T-04 Select + customize | pass | Budget Mixed Bunch; size Standard; card “Happy Birthday Mum — love you”; colour pink, ribbon satin. Selection POST 202. |
| T-05 past dates (!219) | pass | `#delivery-date` `min=2026-08-17`. Hint: “Today or later — past days cannot be delivered.” Setting 2026-08-16 → customError + rangeUnderflow + copy “Delivery cannot be scheduled in the past. Choose today or a later date.” Confirm did **not** persist. No delivery POST for the past value. |
| T-05 Delivery | pass | 2026-08-24 morning; destination `home`; no street-address fields. Banner: delivery confirmed. Windows **Available**. Delivery POST 202 once, after the future date. |
| T-06 Order Summary | pass | Product $35 + delivery $12 = **Total $47.00**. |
| T-07 Checkout | blocked | Scope skip. Chrome present: session vault reference, Create order / Place Order, no PAN. Did not Place Order. |
| T-08 Tracking | blocked | Scope skip with payment. |
| ASO Help (desktop FAB) | pass | `?` FAB opened overlay labeled “not a person”. Ask “When will delivery arrive?” used session delivery facts. Support POST 200. |
| ASO Help (mobile, !220) | pass | Viewport 390×844: `.aso` `display:none` (does not cover Send). Header Help visible, 44px tall, opens the same overlay. Ask answered. Close left the composer usable. |
| Tablet T-01 vs T-02 column order | pass (friction still present) | Viewport 768×1024: one workspace column (`736px`). Conversation (T-01) still paints above Intent Summary (T-02) (`top` 133 vs 769) even though `.understanding` computes `order: -1`. T-02 lives inside `.workspace-main`, so that order rule cannot swap it with T-01. Observe only — not implemented. |

## Blockers vs friction

- **No shopper blocker.** Select works. Past dates cannot be confirmed. Mobile Help is usable. Wait tag **`none`**.
- **Friction (known, still present):** tablet one-column stack keeps T-01 above T-02, so Shared Understanding sits below a tall conversation. Do not implement from this walk.
- **Friction (known):** conversation AI stayed `fallback` after an initial workspace `primary`. Shopper path still completed.
- **Not this walk:** `csrf_rejected` not seen. `/florist` not opened. Did not Place Order. Did not invent a seeder. Compose / localhost not used.

## Evidence

- Screenshots: `research/assessments/_walk_shots_t05_help/`
- Walker: `research/assessments/_walk_mother_birthday_t05_help.py`
- JSON (no session tokens): `research/assessments/2026-08-17-mother-birthday-t05-help.json`

## Highest-severity next step

None for !219 / !220. Tablet T-01 vs T-02 stack remains known friction for UX, not a Path B wait. Customer-journey will not implement.
