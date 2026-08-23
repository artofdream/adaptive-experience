# Mother-birthday T-01 chip + T-07 smoke — 16 Aug 2026

tags: #aea #customer-journey
status: assessment-only
walked_url: https://localhost:8443/
payment_included: yes
walked_at: 2026-08-16T02:12 Europe/Paris
assessed_by: aea-customer-journey
stack: Live Edge Compose after DevSecOps rebuild from `origin/main` (`4521f6d`, !189 T-01 chips). BFF/gateway/orchestration recreated 2026-08-16 02:05 CEST. `https://localhost:8443/healthz` → `200 {"status": "ok"}`. Did not `down` the stack. Did not rebuild.

## Scope

- Short check only: first chip after `I need flowers...` (mother-birthday step 2) + T-07 Create order smoke.
- Session payment reference `session_pay_ref`, confirmation checkbox, **Create order**.
- Did not invent card fields. No raw PAN/CVV inputs were present.
- Assessment files only. Did not implement. Did not open an MR. Did not commit.
- Did not refile #181 (USD vs €75). Did not refile #185 — first chip now matches.

## Bring-up

Polled `https://localhost:8443/healthz` (self-signed TLS). Probe returned `200 {"status": "ok"}` after the 02:05 recreate. Served `/assets/app.js` includes `THOUGHT_COMPLETION_COPY` (`"Who are the flowers for?": "for Mom"`) and `list.unshift("for Mom")`.

cursor-ide-browser `browser_navigate` was classified/rejected (no tab created). Walk used Playwright against the live shop (Edge channel) with screenshots under `research/assessments/_walk_shots_chip_t07/`. Nothing to unlock.

## Outcome

**T-01 first chip: pass.** After `I need flowers...`, chips were `for Mom`, `for a birthday`, `under €75`. First chip is exactly `for Mom`. !189 is on the live images; #185 did not regress.

**T-07 smoke: pass.** `POST /api/v1/checkout` returned **202** with `code: accepted`, `accepted: true`, `order_id: 9740f995-6454-46af-897c-9e10edda2607`, `status: submitted`. No `order_not_found`. No `csrf_rejected`. No new GitLab issue.

| Step | Tile | Result | Notes |
|------|------|--------|-------|
| 1 | T-01 Enter | pass | Welcome + free-text composer. Landing chips hidden until first send. |
| 2 | T-01 first chip | **pass** | First chip `for Mom`. Then `for a birthday`, `under €75`. |
| 3 | T-01 Send + T-02 | pass | Occasion birthday, recipient mother, budget 75. Conversation POST 202. |
| 4 | T-03 | pass | Budget Mixed Bunch $35.00, Classic Rose Dozen $70.00. Both Available. |
| 5 | T-04 | pass | Size Standard, colour pink, ribbon satin, card “Happy Birthday Mum — love you”. |
| 6 | T-05 + T-06 | pass | Destination `home`, morning window, delivery $12, total $47.00. No street-address fields. |
| 7 | T-07 | **pass** | `session_pay_ref` + ack + Create order → **202 / order created**. Not 404. Notice: “Checkout accepted. Waiting for payment confirmation…”. `confirmed: false`, status `submitted`. No raw cards. |

## Blockers vs friction

- **Blockers:** none.
- **Friction (known, not refiled):** USD totals vs €75 example copy (#181). UX is implementing it.
- **New issues filed:** none.

## Coherence

Assessment-only. No new CF row. Do not invent BG/US/FR/NFR IDs.

## Evidence

- JSON: `research/assessments/2026-08-16-mother-birthday-chip-t07.json`
- Screenshots: `research/assessments/_walk_shots_chip_t07/`
- Walker: `research/assessments/_walk_mother_birthday_chip_t07.py`
