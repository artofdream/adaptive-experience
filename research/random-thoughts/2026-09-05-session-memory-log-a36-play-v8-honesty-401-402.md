# Session Memory Log: A36 Play Internal v8 device prove (#401 #402; #404 Unknown)

> **Tags**: #aea #session-memory #companion #play-honesty #a36 #401 #402 #404 #second-brain
> **Captured**: 2026-09-05
> **Author**: `@aea-knowledge-guardian` with `@aea-coherence-guardian`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-04-session-memory-log-evening-mrc-rog-wallet-honesty]] · [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · [[ADR-020]] · [[FR-008]] · #401 · #402 · #404

---

## 1. Why this note exists

`docs/framework/companion.md` still treated a **device re-walk** of #401 / #402 as **Unknown** after those issues closed on `main` (!457, !460). Play Internal install honesty on the page still stopped at `versionCode` **7**. This node records the 2026-09-05 Samsung A36 Play Internal **v8** prove so the next session does not leave those two rows Unknown, and does not credit ROG for a walk it did not do.

This session did **not** open `C:\Users\claud\Temp\aea-v8\evidence\` (sponsor machine only). Do not treat that path as inspected from this checkout.

---

## 2. Install facts (sponsor probe — do not invent more)

On **2026-09-05**, Samsung A36 (`SM_A366B`, adb `RZCY60W1EZW`) installed companion from Play Internal:

| Fact | Value |
|---|---|
| `versionCode` | **8** |
| `versionName` | `0.1.0-alpha.8` |
| `installerPackageName` | `com.android.vending` |
| Debuggable | **non-`DEBUGGABLE`** |

This is the sponsor daily phone already named in [[2026-09-04-session-handover-afk-cts-ai]]. Do not `adb uninstall` / sideload debug over it.

---

## 3. Device prove (A36 Play v8 — not ROG)

| Issue | Result | What the A36 showed |
|---|---|---|
| [#401](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/401) | **PASS** | Free-text Need then `$100+` → chat `Budget: $100+`; no BFF `422`; **View Arrangements** shown |
| [#402](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/402) | **PASS** | **No limit** chip → Need/Pick/Pay honest **No limit** copy (not Skip budget / Budget not set) |
| [#404](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/404) | **ABSENT** on this take | Fresh Need: no Reorder / wallet one-tap CTA visible |

#404 reorder **tap** on A36 stays **Unknown**. A missing CTA on a fresh Need is not a tap prove. ROG remains the preferred hardware gap for #404 (do not sideload debug over the A36).

Sponsor-machine evidence directory (not seen in this session): `C:\Users\claud\Temp\aea-v8\evidence\`

---

## 4. What Pages must say

* Play-install honesty for **v8** is the A36 Play Internal take (`com.android.vending`, non-`DEBUGGABLE`). Do not attribute that dumpsys / install to ROG.
* #401 and #402 are closed on `main` **and** device-proved on A36 Play v8. Do not leave those two rows **Unknown**.
* #404 write vs tap stay two facts. A36 fresh Need did not show the Reorder CTA; leave A36 tap **Unknown**. The !455 30s clip is still the ROG App Dist / packageinstaller Need→Pick→Pay take, not this v8 Play walk.

---

## Wikilinks

[[2026-09-04-session-memory-log-evening-mrc-rog-wallet-honesty]] · [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · [[ADR-020]] · [[FR-008]]
