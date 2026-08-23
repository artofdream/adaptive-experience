# Mother-birthday E2E walk — 15 Aug 2026

tags: #aea #customer-journey
status: assessment-only
walked_url: https://localhost:8443/
payment_included: no
assessed_ref: 0656c78 (local checkout `ux/t01-api-thought-completion-chips`; `origin/main` was e9d509c)
assessed_by: aea-customer-journey

## Scope

- Default mother-birthday scenario from `implementations/florist/journeys/mother-birthday-journey.md`.
- Seven stages in `docs/03-functional-design/customer-journey.md`.
- Payment / T-07 and T-08 tracking excluded.
- Contact Florist on tracking only is intentional (CF-009) — not a finding.
- Did not implement T-01 chips, CSRF, or LiteLLM.

## Bring-up

Edge Compose was down at start. Brought up with `docker compose -f edge/docker-compose.yml up --build --wait -d` (detached so the stack survives the agent shell). Customer URL hard-refreshed. During the walk the Compose project also had `docker-compose.litellm.yml` attached by another session; this skill did not start LiteLLM. Intent still looked like the reference extractor (birthday / mother / 75 plus clarifying questions).

## Outcome

**Pass, with friction.** T-01–T-06 reached a coherent pre-checkout state. No `csrf_rejected` (!165 holds). No new coherence finding. No GitLab issue or MR from this walk.

| Step | Tile | Result | Notes |
|------|------|--------|-------|
| 1 | T-01 Enter | pass | Welcome + free-text composer |
| 2 | T-01 thought completion | fail vs sample “for Mom” | Live chips are API clarifying questions after the first message. Not static Birthday / Wedding / Sympathy. Known UX #175 (closed on this checkout), not a new CF |
| 3 | T-01 Send + T-02 | pass | Occasion birthday, recipient mother, budget 75, Edit available |
| 4 | T-02 correct | pass | 409 `stale_context` if saving while “Updating…”; facets already correct |
| 5 | T-03 | pass | Two Available cards under budget |
| 6 | T-04 | pass | Size, colour, ribbon, physical card message |
| 7 | T-05 + T-06 | pass | Destination `home`, morning window, delivery $12, total $47.00 |
| 8 | T-07 | blocked | Payment excluded |
| 9 | T-08 | blocked | No order; Contact Florist stays on tracking (CF-009) |
| — | ASO | pass | Help labeled not a person; Ask answer not captured this run |

## Blockers vs friction

- **Blockers:** none on the no-payment path.
- **Friction:** sample “for Mom” chip never appears; slug product names; USD vs €75 example copy; clock labels on named windows; leaked `stale_context` if you correct during an in-flight update.

## Coherence

This is assessment-only. It does **not** invent a CF row. #175 (wire T-01 chips to API suggestions) is the known UX item and is closed on this checkout; remaining “for Mom” wording is the sample journey script, not a docs/live contradiction that needs a new CF. CF-009 remains verified / intentional.

## Evidence

- JSON: `research/assessments/2026-08-15-mother-birthday-e2e-walk.json`
- Canvas: `canvases/mother-birthday-e2e-2026-08-15.canvas.tsx` (Cursor canvases dir)
