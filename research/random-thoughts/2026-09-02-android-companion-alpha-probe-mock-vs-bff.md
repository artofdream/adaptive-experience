# Android companion alpha probe (Play internal testing, 2026-09-02)

> **Tags**: #aea #second-brain #mobile #companion #path-b #honesty #j1 #knowledge-first
> **Captured**: 2026-09-02
> **Sponsor**: Tsarafidy (internal tester only)

## Context

Play internal-testing install of **Lily's Florist Companion** (`link.artof.aea.companion`), versionCode **2**, targetSdk **36**, after launcher-icon + API-36 + versionCode bumps (!372 / !373 / !374). Package and signing are real; **journey logic on this build is a local UI mock**, not live Path B.

Related runbook: [[2026-09-01-native-app-setup-and-link-runbook]].

## What the sponsor walked

Need → Pick → Pay → Order Confirmed (e.g. LF-6613) via **Mom's Birthday (Same-Day)** chip only. Sold-out SKU blocked; available SKUs selectable. Pay card message editable; Confirm works; **Start New Arrangement** returns to Need.

Operator dual-check: Lily's Florist Operator (T-09 sample inbox) showed **Aug 18 / Aug 27** Contact Florist rows only — **no** companion LF-####. Banner: local florist operator sample, not live billing CRM.

## Findings (one issue each)

| ID | Finding |
|----|---------|
| [#357](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/357) | Need Continue stays disabled unless Mom's Birthday chip; free text / Anniversary do not unlock |
| [#358](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/358) | Pick: no back to Need; forced to select |
| [#359](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/359) | Never asked for budget |
| [#360](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/360) | Checkout is local mock; does not hit website / BFF / operator |

Positive (not bugs): sold-out fail-closed on Pick; Pay confirm UI; Play internal install works for the single internal tester.

## Code honesty (main at probe time)

`SessionRepository` (companion):

- Welcome + chips + `postUserMessage` — **local keyword** (`Mom` / `birthday` / `same`) sets occasion; not `BffClient`.
- Arrangements — **hardcoded** in-memory (incl. sold-out peony).
- `completeCheckout` — invents random `LF-####` locally; advances to TRACKING.
- `BffClient` exists (`https://aea.artof.link`) but **MainActivity happy path does not call it**.

Live Edge BFF contract (for the real-agent wire — do not re-invent):

- Auth: **cookie session + `X-CSRF-Token`**, not Bearer.
- `POST /api/v1/session` → `csrf_token` + Set-Cookie.
- `POST /api/v1/conversation/messages` body: `{message_text, observed_context_version}` only.
- `POST /api/v1/selection` — `product_id` / items / options + `observed_context_version`.
- `POST /api/v1/checkout` — `{payment_reference, observed_total}` only (no raw card fields).

Companion `BffClient.kt` / `Models.kt` on main **do not match** those shapes; rewrite required for live agent path.

## Product decision in flight

Sponsor asked to **proceed with the real agent path** while the app remains **internal-testing only** (safe to iterate). Wire Need/Pick/Pay to live BFF; then dual-probe website/operator before claiming write-through. Until then: Confirmation screen is a **UI probe**, not proof of atelier/website orders.

## Agent rules

- Do not tell other agents the companion is “live Path B” or that LF-#### appears on operator/website.
- Do not reopen Firebase/Play setup issues closed by prior Slice D work unless sponsor asks.
- Prefer knowledge-first: read this note + [[2026-09-01-native-app-setup-and-link-runbook]] before rediscovering mock vs BFF.
- Journeys [[J1]] [[J2]] [[J3]] [[J4]] still apply as probe scripts once live wire lands.

## Out of scope here

- Implementing the BFF wire (separate SSE MR).
- Play Developer API auto-upload (#354).
