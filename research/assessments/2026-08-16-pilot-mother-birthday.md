# Mother-birthday walk on Path B pilot — 16 Aug 2026

> **Superseded for wait-tag purposes.** RDS migrations were applied later the same evening. Post-migration replay: `research/assessments/2026-08-16-pilot-mother-birthday-migrated.md` (`wait_tag: none`). This file is the pre-migration session-500 evidence.

tags: #aea #customer-journey
status: assessment-only
wait_tag: shop
walked_url: https://aea.artof.link/
payment_included: no
walked_at: 2026-08-16T18:22 Europe/Paris
assessed_by: aea-customer-journey
stack: Public ACM TLS (`CN=*.artof.link`, issuer Amazon RSA 2048 M01). `GET /healthz` → `200 {"status": "ok"}`. Did not apply RDS migrations. Did not seed inventory. Did not open `/florist`.

## Scope

Same script as the local mother-birthday walk: T-01 chips / “for Mom”, under $75, T-03 Select, customize, delivery reference, T-06 summary. Payment / T-07 Place Order excluded unless Path B checkout was clearly usable without inventing card fields. Default skip Place Order.

cursor-ide-browser could not create a tab (`No browser tab available`). Walk used Playwright (Edge channel) against the public origin. Did **not** use `--ignore-certificate-errors`. Assessment files only. Did not implement. Did not open an MR. Did not commit. Did not file a GitLab issue.

## Outcome

**Blocked by stack at session mint.** The static shop loads. A first-time customer cannot send a message.

`POST /api/v1/session` returned **500** `text/plain` body `Internal Server Error` (repeated on boot and on each later API retry). Conversation then **401** `session_required` (`correlation_id` `c056e332-498f-4151-a165-16dbda06009f` on first Send). Shopper copy: “Something went wrong on our side. Try again in a moment.”

This matches the known Path B gap: RDS may never have run `python platform/scripts/apply_migrations.py` (`orchestration.experience_session` missing). **Stopped.** Did not apply migrations. DevSecOps owns bootstrap.

`authentication_required` was **not** seen on UI-authenticated calls. UI bearer `local-browser-token` appears still aligned (!201). A curl without Authorization still 401 `authentication_required`, which is expected.

T-03 empty state is **not** an independent inventory finding. Intent never posted, so warehouse emptiness was not verified.

**Local Edge Compose remains the only full mother-birthday path.**

## Tile results

| Tile | Result | Notes |
|------|--------|-------|
| T-01 Enter / Discovery | pass | Welcome, assistant hello, free-text composer, `$75` placeholder. Toast already showing session 500. |
| T-01 thought completion | fail | Send of `I need flowers...` did not post. No chips. 401 `session_required` after mint 500. |
| T-01 Send + T-02 | fail | `Birthday flowers for Mum, under $75` stayed in the composer. Intent panel empty. |
| T-02 Review and correct | blocked | Prior blocker. PATCH `/api/v1/shared-understanding` → 401 `session_required`. |
| T-03 Recommendations | blocked | Prior blocker. Empty copy asks for occasion/budget first — not a verified empty warehouse. |
| T-04 Select + customize | blocked | No enabled Select. |
| T-05 Delivery | blocked | Not reached. |
| T-06 Order Summary | blocked | Not reached. |
| T-07 Checkout | blocked | Scope skip (payment not included) and prior blocker. No PAN fields on the loaded chrome. Did not Place Order. |
| T-08 Tracking | blocked | Scope skip with payment. |
| ASO Help | blocked | Overlay chrome labeled “not a person”. Ask → same 401 `session_required`. |

## Blockers vs friction

- **Blocker:** `POST /api/v1/session` **500 Internal Server Error**. Shopper cannot start. Wait tag **`shop`**.
- **Friction:** generic “something went wrong” toast instead of a session/bootstrap explanation. T-03 empty copy is a consequence, not a second finding.
- **Not this walk:** `csrf_rejected` not seen. `authentication_required` not seen on the UI bearer path. Inventory seeder not independently tested.
- **New issues filed:** none. Report to PM / DevSecOps rather than a product UX ticket.

## Evidence

- Screenshots: `research/assessments/_walk_shots_pilot/`
- Walker: `research/assessments/_walk_mother_birthday_pilot.py`
- JSON (no session tokens): `research/assessments/2026-08-16-pilot-mother-birthday.json`

## Highest-severity next step

DevSecOps: apply RDS migrations on the pilot (`python platform/scripts/apply_migrations.py`) so `POST /api/v1/session` can mint. Then re-walk. Do not invent a warehouse seeder from this assessment. Customer-journey will not implement the bootstrap.
