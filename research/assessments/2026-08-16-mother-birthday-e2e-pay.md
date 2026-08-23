# Mother-birthday E2E walk with T-07 Pay — 16 Aug 2026

tags: #aea #customer-journey
status: assessment-only
walked_url: https://localhost:8443/
payment_included: yes
walked_at: 2026-08-16T01:40 Europe/Paris
assessed_by: aea-customer-journey
stack: Live Edge Compose after DevSecOps rebuild from `origin/main` (!188 on main). `https://localhost:8443/healthz` → `200 {"status": "ok"}`. Did not `down` the stack.

## Scope

- Default mother-birthday scenario from `implementations/florist/journeys/mother-birthday-journey.md`.
- Seven stages in `docs/03-functional-design/customer-journey.md`, **including T-07 Pay**.
- Used session payment reference `session_pay_ref`, confirmation checkbox, **Create order**.
- Did not invent card fields. No raw PAN/CVV inputs were present.
- Contact Florist on tracking only is intentional (CF-009) — not a finding.
- Assessment + canvas only. Did not implement the checkout fix. Did not open an MR. Did not commit.
- Did not refile known open frictions: T-01 chips vs “for Mom” (#185), USD vs €75 (#181).

## Bring-up

Polled `https://localhost:8443/healthz` (self-signed TLS). First probe returned `200 {"status": "ok"}`. Did not restart Compose. Did not unpark AWS.

cursor-ide-browser `browser_navigate` was classified/rejected (no tab created). Walk used Playwright against the live shop (Edge channel) with screenshots under `research/assessments/_walk_shots_pay/`.

## Outcome vs previous 404 `order_not_found`

**Pass.** Previous manual T-07 Create order returned 404 `order_not_found` (#189). After !188 on main, `POST /api/v1/checkout` returned **202** with `code: accepted`, `accepted: true`, `order_id: c59ac99b-9a88-455f-b2eb-64757ba8c9ec`, `status: submitted`. No `order_not_found`. No `csrf_rejected`. No new GitLab issue.

| Step | Tile | Result | Notes |
|------|------|--------|-------|
| 1 | T-01 Enter | pass | Welcome + free-text composer. Landing chips hidden until first send. |
| 2 | T-01 thought completion | fail vs sample “for Mom” | Live chips are API clarifying questions. Known #185. Typing still works. |
| 3 | T-01 Send + T-02 | pass | Occasion birthday, recipient mother then Mum, budget 75. Both conversation POSTs 202. |
| 4 | T-02 correct | pass | Recipient saved to Mum (202). `stale_context` did not fire. |
| 5 | T-03 | pass | Two Available cards: Budget Mixed Bunch $35.00, Classic Rose Dozen $70.00. Title-case names (prior slug #183 looks cleared). |
| 6 | T-04 | pass | Size Standard, colour pink, ribbon satin, card “Happy Birthday Mum — love you”. |
| 7 | T-05 + T-06 | pass | Destination `home`, morning window, delivery $12, total $47.00 USD. No street-address fields. |
| 8 | T-07 | **pass** | `session_pay_ref` + ack + Create order → **202 / order created**. Not 404. Notice: “Checkout accepted. Waiting for payment confirmation…”. `confirmed: false`, status `submitted` (FR-019 pending). No raw cards. |
| 9 | T-08 | pass | Tracking visible. Status `submitted` / “Order submitted”. Contact Florist on this tile only (CF-009). |
| — | ASO | pass | Help labeled not a person. Ask answered from session: delivery 2026-08-23 morning to `home`. |

## Blockers vs friction

- **Blockers:** none. The previous T-07 404 is gone.
- **Friction (known, not refiled):** sample “for Mom” chip never appears (#185); USD totals vs €75 example copy (#181); clock labels on named windows (mention only).
- **Observation (not a fail vs this assignment):** checkout stays `submitted` / pending confirmation after 202. Journey docs say the order is confirmed only after payment succeeds (FR-019). Tracking still opened. Did not file.

## Coherence

Assessment-only. No new CF row. CF-009 remains intentional. Do not invent BG/US/FR/NFR IDs.

## Evidence

- JSON: `research/assessments/2026-08-16-mother-birthday-e2e-pay.json`
- Screenshots: `research/assessments/_walk_shots_pay/`
- Canvas: `canvases/mother-birthday-e2e-pay-2026-08-16.canvas.tsx` (Cursor canvases dir)
