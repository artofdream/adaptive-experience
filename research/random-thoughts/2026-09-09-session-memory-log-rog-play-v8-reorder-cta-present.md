# Session Memory Log: ROG Play Internal v8 Need Reorder CTA PRESENT (receipt exists)

> **Tags**: #aea #session-memory #companion #play-honesty #rog #407 #408 #fr-008 #adr-020 #second-brain
> **Captured**: 2026-09-09 ~00:10 Europe/Berlin
> **Author**: `@aea-knowledge-guardian` with `@aea-coherence-guardian`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-05-session-memory-log-rog-play-v8-404-absent]] · [[2026-09-05-session-memory-log-a36-play-v8-honesty-401-402]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · [[ADR-020]] · [[FR-008]] · #404 · #407 · #408 · !459

---

## 1. Why this note exists

[#407](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/407) left Play-honest Need reorder **tap** **Unknown** after the 5 Sep 2026 ROG and A36 Play Internal v8 cold-start takes showed **no** CTA (empty / unread wallet). The sponsor then walked Need on the named ROG Play Internal v8 install with a wallet receipt already present.

This node records that walk so Pages do not keep the tap **Unknown** when a device-held receipt exists. It does **not** reopen [#404](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/404). Docs honesty for this prove is [#408](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/408).

This session did **not** open `C:\Users\claud\Temp\aea-rog-reorder-2026-09-09\` (sponsor machine only). Do not treat that path as inspected from this checkout. No Play Console. No `pm clear`. No Android version bump. No merge.

---

## 2. Install facts (sponsor probe — do not invent more)

On **2026-09-09 ~00:10 Europe/Berlin**, ASUS ROG (`ASUS_I001DC`, serial `K9AIKN07B088C89`) on cts-ai adb had companion from Play Internal:

| Fact | Value |
|---|---|
| Package | `link.artof.aea.companion` |
| `versionCode` | **8** |
| `versionName` | `0.1.0-alpha.8` |
| `installerPackageName` | `com.android.vending` |
| Debuggable | **non-`DEBUGGABLE`** |

---

## 3. Device prove (ROG Play v8 — wallet receipt already present)

| Step | Result | What the ROG showed |
|---|---|---|
| Cold Need (wallet already had a receipt) | **PRESENT** | "Reorder previous bouquet"; "1-tap repeat order from this phone's encrypted wallet"; button "Reorder →" |
| Force-stop cold relaunch | still **PRESENT** | Same returning-customer card |
| Tap Reorder → | **PASS** | Pick with Classic Rose Dozen recommended (`content-desc` Classic Rose Dozen); Continue to Checkout enabled |

Empty-wallet **ABSENT** was **not** re-tested on this take (no `pm clear`). Keep the 5 Sep 2026 A36 + ROG chips-only walk as the empty-wallet hide evidence. Do not claim that hide was re-probed today.

Sponsor-machine evidence (not seen in this session): `dumpsys-package.txt`, `need-with-reorder.png`, `ui-need-with-reorder.xml`, `cold-relaunch-need.png`, `after-reorder-tap.png`, `REPORT.txt` under `C:\Users\claud\Temp\aea-rog-reorder-2026-09-09\`.

---

## 4. What Pages must say

* Play-honest Need reorder **tap** on ROG Play Internal v8 is **Verified** when a wallet receipt exists (9 Sep 2026).
* Cold empty-wallet Need still shows **no** CTA. That hide was proved on 5 Sep 2026 (A36 and ROG). It was **not** re-probed on 9 Sep.
* Write vs tap stay two facts. The save on Confirm is not the same sentence as the Need card.
* Sideload ROG walk in [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] stays UX/code proof, not Play-install honesty.
* **This page's 30s demo clip** remains the !455 Need→Pick→Pay take and does not show the reorder card.
* `docs/framework/comparison.md` Honest Status Ledger has **no** matching reorder / Play tap Unknown row — do not invent one.

---

## 5. Covering (Knowledge First — not a DATE_RE rewrite)

Latest committed DATE_RE at write is [[2026-09-08]] (`research/daily-briefs/2026-09-08.md`). This prove is dated 2026-09-09. Prefer this vault note + `docs/framework/companion.md` over inventing a 2026-09-09 generator brief or a roadmap Completed claim.

Sibling pages (`docs/framework/crm.md`, `docs/framework/journal.md`, `docs/05-ux-design-guide/customer-edge-wallet-guide.md`) still carry 5 Sep **Unknown** tap language. This MR does not rewrite those pages.

---

## Wikilinks

[[2026-09-05-session-memory-log-rog-play-v8-404-absent]] · [[2026-09-05-session-memory-log-a36-play-v8-honesty-401-402]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · [[2026-09-08]] · [[ADR-020]] · [[FR-008]]
