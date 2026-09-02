# Session memory — dual-probe, staff list, florist queue, ROG

> **Captured**: 2026-09-02
> **Owner**: `@aea-knowledge-guardian`
> **Tags**: #aea #second-brain #companion #florist #dual-probe #rog #afk
> **Companion**: [[2026-09-02-session-memory-log-florist-queue-rog-handoff]] · [[2026-09-02-companion-native-web-gap-closing-loop]]

Sponsor standing rules this session: **be proactive**; **knowledge capture remains a must**; prefer work that does **not** need sponsor secrets/budget or local Auto-review script cards. cts-ai may go AFK; cloud runners + GitLab are the bus.

## What shipped (do not rediscover)

| Item | Evidence |
|---|---|
| Companion Need→Pick→Pay is live BFF, not the old local mock | !376 / !379 / !380 already on `main` before this session |
| #360 reopened then closed as **staff order list**, not “checkout is still a mock” | Sponsor/PO: companion checkouts belong on `/florist`. !401 `9e406dfe` merged 16:55Z. Live `/florist` has Staff orders |
| 30s Need tape on the public Companion page | !399 / #373. [architecture.artof.link/companion.html](https://architecture.artof.link/companion.html) |
| Dual-probe (Samsung A36, serial `RZCY60W1EZW`) | Confirm UUID `b2cdd537-cd20-478e-8320-08f320249be0` was phone-only. Shop Track = session-scoped “No order yet.” Florist T-09 was not an order list (two old inbox rows). Clips under companion-dual-probe-2026-09-02 |
| Auto Blocker | USB debug reverts after ~30 min time or inactivity. Windows then shows MTP only (`Claude sin A36`) |

Do **not** reopen #360 for customer Track write-through. That is a different claim. Do **not** treat T-09 sample inbox as CRM.

## Device split (do not mix)

| Device | Role |
|---|---|
| ASUS ROG `ASUS_I001DC` serial `K9AIKN07B088C89` | Dedicated validation phone. Grok-bot / grob-ai holds ADB (#381) |
| Samsung A36 `RZCY60W1EZW` | Sponsor daily phone. Use only when plugged and USB debug allowed |

Never open `/florist` in the same browser as customer `/` (CSRF / !165).

## Florist efficiency (after !401)

Staff list exists. It is not yet a work queue.

| Gap | Ticket | Native needed? |
|---|---|---|
| Card, catalog title, channel, paid/declined on the row | #376 | Channel prove = ROG checkout |
| Today / delayed filter; “order or inbox” copy | #378 | No |
| T-09 badge when that session also has an order | #379 | No |
| Fake Claim/Resolve (local JS only) | #380 — **remove buttons** (persist parked) | No |
| Destination handle without street | #382 — parked (PO) | T-05 collection is #381 |
| Companion has no T-09; checkout hard-codes today/afternoon/home | #381 grok-bot | Yes — ROG |

Cloud SSE opened stacked MRs (do not re-open the same slices): !409 #376, !412 #378, !415 #379, !417 #380-remove. Merge **!409 first** (targets `main`); then retarget. Do not persist Claim unless PO names it. Channel persist is in !409; live `companion-android` still needs a ROG checkout (#381).

## Native ↔ web (operator-relevant only)

Same BFF spine. Native-behind that **lies to the florist**: no escalation POST; delivery defaults look chosen. Full workspace / SSE / tiles stay **different-by-design** (`docs/framework/companion.md`). Start Over is native-ahead.

## Process lessons

- Primary tree mid-rebase + “checkpoint before checkout” commits (LFS mipmap pointers) collided with #360. Worktree isolation is only written on coherence-guardian / findings loop — **AGY / Grok / always-on files did not get that memo**. Push clean WIP (`wip/360-operator-orders` `b0192dc`) rather than dirty checkpoints.
- Windows Auto-review cannot sandbox this machine; `adb` / `glab` / git often become approval cards. AFK path = **cloud agents + GitLab MWPS**, or Cursor **Run Everything** (no sandbox). Auto-review is not AFK.
- Knowledge that exists only in chat or an uncommitted brief is not shared memory (CF-048 class). Commit `research/random-thoughts/` and DATE_RE.

## Out

CRM #35/#36. Shop CSS. Street/PII. Play upload. Sharing ADB with grok-bot. Closing florist honesty from unit tests or UUID-on-phone-only.

[[ADR-013]] · [[ADR-016]] · [[2026-09-02-session-handover-cloud-agents-local-cts-ai]]
