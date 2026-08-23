# Mother-birthday E2E rewalk — 15 Aug 2026 23:42

tags: #aea #customer-journey
status: assessment-only
walked_url: https://localhost:8443/
payment_included: no
walked_at: 2026-08-15T23:42 Europe/Paris
assessed_by: aea-customer-journey
stack: Edge Compose + LiteLLM overlay already up (`edge-gateway` healthy on :8443; `edge-litellm` healthy; orchestration `/internal/v1/ai/health` `available: true`, `mode: primary`, `circuit: closed`)
local_git_at_walk: `1d0f8e8` on `docs/aea-senior-software-engineer-skill` (this skill did not switch branches; live shop is the running Compose stack)

## Scope

- Default mother-birthday scenario from `implementations/florist/journeys/mother-birthday-journey.md`.
- Seven stages in `docs/03-functional-design/customer-journey.md`.
- Payment / T-07 and T-08 tracking excluded. Did not Place Order. Did not invent card fields.
- Contact Florist on tracking only is intentional (CF-009) — not a finding.
- Assessment + canvas only. Did not implement. Did not open an MR. Did not commit.
- Did not refile the four known frictions Support is filing: T-01 chips vs “for Mom” (#185), T-03 slug names (#183), USD vs €75 (#181), T-02 `stale_context` (#184).

## Bring-up

`https://localhost:8443/healthz` returned `{"status": "ok"}`. Did not restart Compose. Did not unpark AWS. Did not terraform apply. Stack left running.

cursor-ide-browser MCP would not hold a tab (`navigate` / `lock` reported no tab). Walk used Playwright against the live shop (Edge channel) with screenshots under `research/assessments/_walk_shots_rewalk/`.

## Outcome

**Pass, with friction.** T-01–T-06 reached a coherent pre-checkout state on the successful attempt. No `csrf_rejected` (!165 holds). No new GitLab issue from this walk.

| Step | Tile | Result | Notes |
|------|------|--------|-------|
| 1 | T-01 Enter | pass | Welcome + free-text composer. Landing chips hidden until first send. |
| 2 | T-01 thought completion | fail vs sample “for Mom” | Live chips are API clarifying questions. Known #185. Typing still works. |
| 3 | T-01 Send + T-02 | pass | Occasion birthday, recipient mother then Mum, budget 75, Edit available. Both conversation POSTs 202 on the successful attempt. |
| 4 | T-02 correct | pass | Recipient saved to Mum (202). `stale_context` did **not** fire when we waited for Updating to settle. Still reproducible if you save during update (#184). |
| 5 | T-03 | pass | Two Available cards under budget: `budget mixed bunch` $35.00, `classic rose dozen` $70.00. Slug names (#183). |
| 6 | T-04 | pass | Size Standard, colour pink, ribbon satin, card “Happy Birthday Mum — love you”. |
| 7 | T-05 + T-06 | pass | Destination `home`, morning window with clock labels 10:00–12:00 / 12:00–14:00 / 14:00–16:00, delivery $12, total $47.00 USD. No street-address fields. |
| 8 | T-07 | blocked | Payment excluded. Checkout tile visible (session payment reference, Place Order) — not used. |
| 9 | T-08 | blocked | No order; Contact Florist stays on tracking (CF-009). |
| — | ASO | pass | Help labeled not a person. Ask answered from session: delivery 2026-08-23 morning to `home`. |

## Attempt 1 (not the scored walk)

First send returned **503 `orchestration_unavailable`** to the shopper while orchestration logged **202** on the same conversation POST. Immediate retry then hit **409 `stale_context`**. Intent never populated; T-03/T-04 were empty as a cascade, not an empty catalog. Second attempt (wait after send; do not race a second message) both conversation POSTs were 202 and the journey completed.

Not filed: did not reproduce on the scored walk; not one of the four Support tickets; closest open chore is #152 (availability hardening). Mention only.

## Blockers vs friction

- **Blockers:** none on the scored no-payment path.
- **Friction (known, not refiled):** sample “for Mom” chip never appears (#185); slug product names (#183); USD totals vs €75 example copy (#181); `stale_context` if you correct during “Updating…” (#184); clock labels on named windows (not a new blocker).
- **Friction (observed, not filed):** intermittent first-send 503 when BFF’s 3s orchestration timeout loses a still-accepted write.

Shopper-visible intent still looks like the bounded facet extractor (birthday / mother / 75 plus clarifying questions) even with LiteLLM healthy in `primary`. That matches the interpreter contract; it is not a new journey fail.

## Coherence

Assessment-only. No new CF row. CF-009 remains intentional. Do not invent BG/US/FR/NFR IDs.

## Evidence

- JSON: `research/assessments/2026-08-15-2342-mother-birthday-e2e-rewalk.json`
- Screenshots: `research/assessments/_walk_shots_rewalk/`
- Canvas: `canvases/mother-birthday-e2e-rewalk-2026-08-15.canvas.tsx` (Cursor canvases dir)
