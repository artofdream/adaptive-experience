# Mother-birthday walk on Path B after live-test heartbeat — 17 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: none
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-17T13:21 Europe/Paris
assessed_by: aea-customer-journey
stack: Public ACM TLS. `GET /healthz` → `200 {"status": "ok"}`. Session mint **201**. DSO in-VPC `lily-reference-live-test` heartbeat (five SKUs, 30s) was already running. Did not open `/florist`. Did not invent a warehouse seeder.

## Scope

Mother-birthday / T-01 chips through T-03: **does Select enable?** Available vs Unknown badges. Continue to customize, delivery **reference**, T-06 if cheap. Skip Place Order unless natural. Payment / T-07 excluded.

cursor-ide-browser could not create a tab (`No browser tab available`). Walk used Playwright (Edge channel) against the public origin. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit.

## Outcome

**Select enabled.** T-03 ranked two arrangements under $75 with green **Available** badges. Both Select buttons were enabled on the first look (no 30s heartbeat wait needed).

Picked Budget Mixed Bunch, Standard, card message. Confirmed destination reference `home` (no street-address fields). Order summary itemized **Total $47.00**. Stopped before Place Order. Checkout chrome was visible (`session_pay_ref`, no PAN); payment was out of scope.

Session mint 201. `csrf_rejected` not seen. First workspace poll reported `mode: primary`; conversation messages then ran `mode: fallback`. Shopper path still completed.

Wait tag **`none`**.

## Tile results

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer. Session mint 201. |
| T-01 thought completion | pass | `I need flowers…` posted. Chips: for Mom, for a birthday, under $75. Typing remained available. |
| T-01 Send + T-02 | pass | `Birthday flowers for Mum, under $75`. Walker screenshot caught T-02 still on “Updating from your last message…”. Facets then showed birthday / mother / 75. Review and correct visible. Messages 202. **Friction:** pending banner lagged ~1s. |
| T-02 Review and correct | pass | Saved recipient to `Mum`. PATCH `/api/v1/shared-understanding` 202. |
| T-03 Recommendations | pass | Two cards: Budget Mixed Bunch $35 **Available**, Classic Rose Dozen $70 **Available**. Select enabled on both. No Unknown badges. Heartbeat SKUs not all ranked (under-$75 + occasion filter). |
| T-04 Select + customize | pass | Budget Mixed Bunch; size Standard; card “Happy Birthday Mum — love you”; colour pink, ribbon satin. |
| T-05 Delivery | pass | 2026-08-24 morning; destination `home`; no street-address fields. Banner: delivery confirmed. Windows also **Available**. |
| T-06 Order Summary | pass | Product $35 + delivery $12 = **Total $47.00**. |
| T-07 Checkout | blocked | Scope skip. Chrome present: session vault reference, Create order / Place Order, no PAN. Did not Place Order. |
| T-08 Tracking | blocked | Scope skip with payment. |
| ASO Help | pass | Overlay labeled “not a person”. Ask “When will delivery arrive?” used session delivery facts. |

## Blockers vs friction

- **No shopper blocker.** Select works. Wait tag **`none`**.
- **Friction:** T-02 pending copy before facets paint. Destination radio showed `( none )` until confirm, then `home`. Conversation AI stayed `fallback` after an initial workspace `primary`.
- **Not this walk:** `csrf_rejected` not seen. `/florist` not opened. Did not Place Order. Did not invent a seeder.

## Evidence

- Screenshots: `research/assessments/_walk_shots_heartbeat/`
- Walker: `research/assessments/_walk_mother_birthday_heartbeat.py`
- JSON (no session tokens): `research/assessments/2026-08-17-mother-birthday-heartbeat.json`

## Highest-severity next step

None for inventory wait. Optional observe-only: conversation `mode: fallback` vs claimed primary — AI engineer, not a product UX ticket from this walk. Customer-journey will not implement.
