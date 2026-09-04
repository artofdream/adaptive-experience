# Session Memory Log: Evening MRC, ROG wallet clip, and Pages honesty (2026-09-04)

> **Tags**: #aea #session-memory #mrc #companion #edge-wallet #rog #florist-operator #pages-honesty #401 #402 #403 #399 #400
> **Captured**: 2026-09-04 ~23:20 Europe/Berlin
> **Author**: `@aea-knowledge-guardian` with `@aea-mr-coordinator` / `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-04-session-memory-log-mrc-crm-companion-v5-play-honesty]] · [[2026-09-04-future-native-florist-operator-app-gates]] · [[2026-09-04-florist-operator-multi-device-responsive-architecture]] · [[ADR-020]] · [[FR-008]] · [!434](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/434) · [!453](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/453) · [!450](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/450) · [!455](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/455) · #403

---

## 1. Why this note exists

The afternoon AFK handover and the morning MRC/CRM note are still true, but they stop before the evening merge wave and the ROG Confirm→Track recut. Public Pages (`companion.md` / `crm.md`) also over-claimed **one-tap reorder** as if the Need button already existed. This node is the evening handoff so the next session does not re-derive GitLab from scratch or repeat that honesty miss.

Do **not** treat inbox `*.mp4` files as git memory. They stay local.

---

## 2. What merged on `main` this evening

| MR | What it actually is | Status |
|---|---|---|
| [!451](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/451) | Companion Need Continue unlocks on free-text / any usable intent facet (#400) | Merged earlier |
| [!452](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/452) | Pick/Pay quantity 1–10 as `options.quantity` (web customize parity); `versionCode` **7** / `0.1.0-alpha.7` | Merged earlier |
| [!455](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/455) | Pages 30s Need→Pick→Pay clip + poster (ROG; App Dist / packageinstaller take) | Merged |
| [!454](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/454) | Vault: native **operator** Android is future-only; four gates | Merged |
| [!450](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/450) | Florist `/florist` CSS polish; ≥44px targets; wrap nav on phone | Merged |
| [!453](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/453) | Staff orders / inbox **day-window** filters + counts (#398) | Merged |
| [!434](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/434) | Operator boot `Promise.allSettled`, keyset pagination, GET-only bounded retry | Merged after SSE rebase |

---

## 3. Lesson: two `florist.js` MRs need an SSE rebase

MRC gated all five open MRs. Docs and CSS merged first. After !453 landed, !434 went `cannot_be_merged` on `edge/gateway/ui/assets/florist.js` (and tests). **MRC must not rebase.** SSE keep-both: inbox day-filter listeners **and** `loadMoreOrders` / `loadMoreInbox`. Force-with-lease on the feature branch only. Then MRC MWPS.

Do not open a second operator efficiency MR to “also fix filters.”

---

## 4. Companion / ROG honesty (cts-ai)

* **Probe phone:** ASUS ROG `K9AIKN07B088C89` (`ASUS_I001DC`). **Daily phone:** Samsung A36 `RZCY60W1EZW` — Play install; do not sideload debug over it.
* **On ROG after reboot:** debug `0.1.0-alpha.7` (`DEBUGGABLE`, packageinstaller). Play Internal **upload** of v7 is claimed on Pages; that take’s clip is **not** Play-install honesty.
* **Wallet write:** `completeCheckout` → `EdgeWallet.saveReceipt` (Keystore envelope). Track shows the order. There is **no** Need “Reorder previous arrangement” button. `reorderFromWallet()` exists; UI is not wired. That is the AGY option-3 slice (own issue/MR), not this note.
* **ROG recut (local only):** `research/inbox/2026-09-04-edge-wallet-demo-rog.mp4` — Pay Confirm → Track. Order `04088a5a-715d-4dfe-8015-2bd4787c5070`, morning → work, $47. **Do not commit.**
* **Pages clip (!455):** order `f3583908-b2ca-4b5e-a4e8-aa0c6c040177`, afternoon → home, $47. Same SKU path; different take.
* **A36 afternoon clip** never reached Confirm. Superseded for demo; still do not commit.

---

## 5. Open product lanes (do not steal)

| Owner | Issue | Surface |
|---|---|---|
| grok-bot | #401 | Free-text Need then `$100+` → BFF `422 validation_failed` |
| grok-bot | #402 | **No limit** chip still behaves like skip-budget |
| AGY | FR-008 Need CTA | Wire `reorderFromWallet()`; sideload ROG; 30s clip |
| this MR | #403 | Pages + vault honesty only |

Do not edit budget-chip / `setBudgetChoice` in a reorder MR. Do not restyle `/florist` from a companion or docs MR.

---

## 6. Local machine notes (cts-ai)

* JDK 21 for companion assemble: Temurin `C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot`.
* Host `:5432` may be held by `cafe-pg` (not AEA). Local `platform/scripts/run_integration_tests.py` then fails bind. Edge Compose postgres is internal and still runs. Say CI-only for platform if that happens; do not kill `cafe-pg` without asking.
* Leftover `adaptive-experience-foundation` kafka can remain after a failed platform up — not a product defect.

---

## 7. What Pages must say (plain language)

* Companion is a thin phone shop: Need → Pick → Pay. Quantity and free-text Continue are on `main`.
* Edge Wallet **saves** the last confirmed order on the phone. A one-tap reorder **button** is not on Need yet.
* Florist staff stay on **mobile web** `/florist` (day filters, load-more, phone-sized targets). A native staff app is a **future** with four gates — [[2026-09-04-future-native-florist-operator-app-gates]].
* “Verified” still means a probe. A merged MR is not a phone control.

---

## Wikilinks

[[2026-09-04]] · [[ADR-020]] · [[FR-008]] · [[NFR-017]] · [[ADR-013]] · [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-04-future-native-florist-operator-app-gates]]
