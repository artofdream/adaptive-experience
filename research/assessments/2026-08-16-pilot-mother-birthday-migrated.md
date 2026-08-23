# Mother-birthday walk on Path B pilot — post-migration replay — 16 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: none
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-16T18:54 Europe/Paris
assessed_by: aea-devsecops-platform (migrate) then aea-customer-journey (replay)
stack: Public ACM TLS. `GET /healthz` was already 200. RDS migrations applied this pass. `AEA_ENVIRONMENT=production` (no seeder, no florist). Did not open `/florist`. Did not `terraform apply`.

## Scope

Same script as the local mother-birthday walk: T-01 chips / “for Mom”, under $75, T-03 Select if inventory exists, customize, delivery reference, T-06 summary. Payment / T-07 Place Order excluded. Did not invent card fields.

cursor-ide-browser still could not create a tab (`No browser tab available`). Walk used Playwright (Edge channel) against the public origin. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit. Did not file a GitLab issue.

Pre-migration walk (session 500): `research/assessments/2026-08-16-pilot-mother-birthday.md`.

## Part 1 — migrate (DevSecOps)

**Method:** documented Path B bootstrap — ECS Fargate `RunTask` on cluster `aea-pilot`, task definition `aea-pilot-orchestration:1`, same private subnets and orchestration security group as the running service (`assignPublicIp=DISABLED`). Container command `python platform/scripts/apply_migrations.py`. `AEA_POSTGRES_DSN` injected from Secrets Manager `aea-pilot/app` (not read onto the laptop). Port 5432 was not opened to `0.0.0.0/0`. No `terraform apply`.

**Evidence:**

| Check | Result |
|------|--------|
| Migrator task | `2e6779fff9464ac19424da0b9e3fb1da` — container exit **0** |
| CloudWatch `/aea/aea-pilot/orchestration` | applied `001` … `014` (all 14 SQL files) |
| SQL check task | `6206c868b59a4f64bf2841c3df492a08` — exit **0**; `to_regclass('orchestration.experience_session')` → `orchestration.experience_session`; `schema_migration` versions `[1..14]` |
| `POST /api/v1/session` with UI bearer | **201** JSON `csrf_token`, `__Host-aea_session` Set-Cookie |
| Same POST without Authorization | **401** `authentication_required` (fail-closed, intended) |

## Outcome

**Session mint unblocked.** A first-time customer can send a message. Partial thought produced chips `for Mom`, `for a birthday`, `under $75`. Intent showed birthday / mother / 75; Review and correct saved recipient `Mum`. Help answered from approved copy and is labeled not a person. `csrf_rejected` was not seen. `authentication_required` was not seen on UI-authenticated calls.

**Remaining shopper stop:** T-03 ranked two arrangements (`Budget Mixed Bunch` $35, `Classic Rose Dozen` $70) but availability is **unknown**, so Select stays disabled. That is fail-closed production inventory (no operator feed into `inventory.product_availability`), not a missing-table / session-500 stack failure. **Friction, not wait-tag `shop`.** Did not invent a warehouse seeder.

T-05 / T-06 were not reached (no Select). T-07 / T-08 remain scope skips.

**Local Edge Compose remains the only full mother-birthday path through Select → customize → delivery → summary**, because Compose seeds availability. Path B now covers T-01 / T-02 / Help.

Wait tag **`none`** — assessment completed.

## Tile results

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer. Session mint 201. |
| T-01 thought completion | pass | `I need flowers…` posted. Chips: for Mom, for a birthday, under $75. Typing remained available. |
| T-01 Send + T-02 | pass | `Birthday flowers for Mum, under $75`. Intent: occasion birthday, recipient mother, budget 75. Review and correct visible. Messages 202. |
| T-02 Review and correct | pass | Saved recipient to `Mum`. PATCH `/api/v1/shared-understanding` 202. |
| T-03 Recommendations | fail | Two cards under $75. Availability **unknown**. Select disabled. Friction (no live availability feed), not empty-warehouse and not session bootstrap. |
| T-04 Select + customize | fail | No enabled Select. Could not set size / card message. |
| T-05 Delivery | blocked | Prior: no selection. |
| T-06 Order Summary | blocked | Prior: no selection. |
| T-07 Checkout | blocked | Scope skip (payment not included). Chrome present; no PAN fields. Did not Place Order. |
| T-08 Tracking | blocked | Scope skip with payment. |
| ASO Help | pass | Overlay labeled “not a person”. Ask “When will delivery arrive?” answered same-day / next-day copy. POST `/api/v1/support` 200 `answered`. |

## Blockers vs friction

- **No stack blocker remaining for session mint.** Wait tag **`none`**.
- **Friction:** ranked cards with `unknown` availability; customer cannot Select. Expected under `AEA_ENVIRONMENT=production` without an operator inventory feed. Do not treat as a product UX ticket. Do not invent a seeder.
- **Not this walk:** `csrf_rejected` not seen. Fail-closed 401 without bearer still holds. Did not open `/florist`. Kafka/MSK not on this public shop path.

## Evidence

- Screenshots: `research/assessments/_walk_shots_pilot_migrated/`
- Walker: `research/assessments/_walk_mother_birthday_pilot_migrated.py`
- JSON (no session tokens): `research/assessments/2026-08-16-pilot-mother-birthday-migrated.json`
- Migrator logs: ECS task `2e6779fff9464ac19424da0b9e3fb1da` in `/aea/aea-pilot/orchestration`

## Highest-severity next step

Operator inventory feed into `inventory.product_availability` so T-03 can show Available and Select can enable. DevSecOps / ops — not a new GitLab product bug from this walk. Customer-journey will not invent a warehouse seeder.
