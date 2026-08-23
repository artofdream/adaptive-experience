# Mother-birthday Path B rewalk after !226 T-02 session rebind — 17 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: none
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-17T23:30 Europe/Paris
assessed_by: aea-customer-journey
stack: Public ACM TLS. `GET /healthz` → **200** `{"status": "ok"}`. Claimed `origin/main` **b62ef96** (!226 RDS session rebind, !227 Track stepper). Session mint **201** on both viewports. Did not open `/florist`. Did not invent a warehouse seeder. Did not use Compose / `https://localhost:8443`.

## Scope

PM: Path B is on `origin/main` b62ef96. Rewalk **T-02 Review and correct** on live shop (desktop and phone-width). Confirm Shared Understanding PATCH succeeds — no toast **Correction failed (session_required)**. Mother-birthday through T-06. Default skip T-07 Place Order. Observe `Checkout failed (total_mismatch)` only; do not implement. Do not open `/florist` in the same session. Do not implement. Do not open an MR.

cursor-ide-browser: `browser_tabs` new created a tab, then `browser_navigate` to the public origin failed (`No browser tab available` / `Browser view not found`). Walk used Playwright (Edge channel) against `https://aea.artof.link/`. Two **separate** browser contexts (desktop 1440×1100, phone 390×844) so cookies never mixed. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit.

## Outcome

**T-02 PATCH succeeds on Path B.** Desktop and phone-width both saved a recipient correction to `Mum`. `PATCH /api/v1/shared-understanding` returned **202** `accepted` (context_version 5) on the first attempt. Toast was **Shared Understanding updated.** — not **Correction failed (session_required)**. No 401, no client retry, no `session_required` on any API in either session.

Shopper path completed through T-06 on both viewports. Picked Budget Mixed Bunch, Standard, card message. Delivery **2026-08-24** morning + destination reference `home`. Order summary itemized **Total $47.00**. Stopped before Place Order. `total_mismatch` was **not** seen.

!227 Track stepper is on the live shop (step 7 **Track**). T-08 still skipped with payment.

Wait tag **`none`**.

## Tile results

### Desktop (1440×1100)

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer. Session mint 201. Track stepper present. |
| T-01 thought completion | pass | `I need flowers…` posted. Chips: for Mom, for a birthday, under $75. Typing remained available. |
| T-01 Send + T-02 | pass | `Birthday flowers for Mum, under $75`. Facets: birthday / mother / 75. Review and correct visible. No `csrf_rejected`. |
| T-02 Review and correct | **pass** | Saved recipient to `Mum`. PATCH **202** `accepted`. Notice: `Shared Understanding updated.` Form error empty. `toast_session_required=false`. |
| T-03 Recommendations | pass | Two cards under $75: Budget Mixed Bunch $35 **Available**, Classic Rose Dozen $70 **Available**. Select enabled on both. |
| T-04 Select + customize | pass | Budget Mixed Bunch; size Standard; card “Happy Birthday Mum — love you”; colour pink, ribbon satin. |
| T-05 Delivery | pass | 2026-08-24 morning; destination `home`; no street-address fields. Banner: delivery confirmed. |
| T-06 Order Summary | pass | Product $35 + delivery $12 = **Total $47.00**. No checkout error. |
| T-07 Checkout | blocked | Scope skip. Chrome present: Create order / Place Order, no PAN. Did not Place Order. `total_mismatch` not seen. |
| T-08 Tracking | blocked | Scope skip with payment. Track stepper present (observe only). |
| ASO Help | pass | Overlay labeled “not a person”. Ask “When will delivery arrive?” used session delivery facts. |

### Phone (390×844)

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Same welcome + composer. Session mint 201 in a **new** context. innerWidth=390. |
| T-01 thought completion | pass | Same chips. Typing remained available. |
| T-01 Send + T-02 | pass | Same facets. Review and correct visible without opening `/florist`. |
| T-02 Review and correct | **pass** | Same PATCH **202** `accepted`. Notice: `Shared Understanding updated.` No `session_required` toast. Recipient `Mum`. |
| T-03 Recommendations | pass | Same two Available cards; Select enabled. |
| T-04 Select + customize | pass | Same Budget Mixed Bunch / Standard / card message. |
| T-05 Delivery | pass | Same 2026-08-24 morning + `home`. |
| T-06 Order Summary | pass | **Total $47.00**. |
| T-07 Checkout | blocked | Scope skip. Did not Place Order. `total_mismatch` not seen. |
| T-08 Tracking | blocked | Scope skip with payment. |

## Blockers vs friction

- **No shopper blocker.** T-02 correction holds after !226. Wait tag **`none`**.
- **Friction (known):** conversation AI stayed `fallback` (desktop workspace poll started `primary`, then fallback). Shopper path still completed.
- **Not this walk:** `csrf_rejected` not seen. `/florist` not opened. Did not Place Order. Did not see `Checkout failed (total_mismatch)` — that remains a separate Support intake if it appears later. Did not invent a seeder. Compose / localhost not used.

## Evidence

- Screenshots: `research/assessments/_walk_shots_t02_rebind/` (`d04-t02-correct.png`, `p04-t02-correct.png` show the success toast)
- Walker: `research/assessments/_walk_mother_birthday_t02_rebind.py`
- JSON (no session tokens): `research/assessments/2026-08-17-mother-birthday-t02-rebind.json`

## Highest-severity next step

None for T-02 / !226. Shared Understanding PATCH is live on Path B at desktop and phone width. Customer-journey will not implement. Do not open an MR from this assessment.
