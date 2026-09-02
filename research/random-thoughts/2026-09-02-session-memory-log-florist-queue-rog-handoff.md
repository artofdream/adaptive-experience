# Session memory — florist queue and ROG handoff

> **Captured**: 2026-09-02
> **Owner**: `@aea-knowledge-guardian` with `@aea-support-coordinator`
> **Tags**: #aea #florist #companion #rog #gap-loop

Sponsor rule: **be proactive**. cts-ai is back; grok-bot holds ADB on the dedicated **ROG** (`ASUS_I001DC`, `K9AIKN07B088C89`). The A36 is the sponsor daily phone only.

## Split (do not steal lanes)

| Lane | Owns | Do not |
|---|---|---|
| Grok-bot / grob-ai | [#381](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/381) companion T-09 + real T-05; ROG dual-probe | florist.js / BFF list MRs |
| Cloud SSE | [#376](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/376) → [#378](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/378) → [#379](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/379) → [#380](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/380) → [#382](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/382) | ADB, companion UI |
| MRC | merge after gates | rebase / invent product |

`/florist` and customer `/` stay in **separate browsers**.

## Already on main

- !401 staff order list (FR-013). #360 closed. Live `/florist` has Staff orders.
- Companion Need tape on [architecture.artof.link/companion.html](https://architecture.artof.link/companion.html) (!399 / #373).
- Need→Pick→Pay BFF contracts shipped (!376/!379/!380). Write-through to **customer** Track is still session-scoped; do not reopen #360 for that.

## Florist slices opened (not yet on `main`)

[Florist no-sponsor slices](bc-f1e61c7c-9e90-4841-9692-11baa7dc2065) shipped four stacked MRs. MRC merge order: **!409 → !412 → !415 → !417**. Do not merge the later three into the parent feature branch (that would mix !409). After !409 is on `main`, retarget !412 to `main`.

| Issue | MR | HEAD | In |
|---|---|---|---|
| #376 | [!409](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/409) → `main` | `6e88a364` | card, catalog title, allowlisted channel (`web` / `companion-android` / `unknown`, migration 023), paid/declined/unpaid |
| #378 | [!412](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/412) → !409 branch | `08ec183d` | Today (live default) / Delayed / All; “order or inbox” copy |
| #379 | [!415](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/415) → !412 branch | `dc0758e1` | read-only Has order / Inbox session badge |
| #380 | [!417](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/417) → !415 branch | `61a18af3` | **remove** fake Claim/Resolve only |

**Parked:** #382 destination handle (PO). Persist Claim (not in !417).

CI Docker integration already passed on !409 (`platform-foundation-integration` + `edge-docker-integration`). Local Docker was not available in the cloud worktree.

## Native proof grok-bot must run

Companion checkout hard-codes today / afternoon / `home`. No T-09 POST. After #376 merges: ROG Confirm → order id on `/florist` Staff orders; comment UUID on #381. Channel `companion-android` vs `web` is the join.

## Out

CRM #35/#36. Shop CSS restyle. Street/PII. Sharing ADB while grok-bot has the ROG.

[[2026-09-02-session-memory-log-dual-probe-florist-rog]] · [[2026-09-02-companion-native-web-gap-closing-loop]]
