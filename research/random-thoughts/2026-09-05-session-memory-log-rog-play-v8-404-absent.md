# Session Memory Log: ROG Play Internal v8 #404 Reorder CTA ABSENT

> **Tags**: #aea #session-memory #companion #play-honesty #rog #404 #407 #fr-008 #adr-020 #second-brain
> **Captured**: 2026-09-05
> **Author**: `@aea-project-manager` with `@aea-knowledge-guardian` and `@aea-coherence-guardian`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-05-session-memory-log-a36-play-v8-honesty-401-402]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · [[2026-09-04-session-memory-log-evening-mrc-rog-wallet-honesty]] · [[ADR-020]] · [[FR-008]] · #404 · #407 · !459

---

## 1. Why this note exists

[#404](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/404) closed when [!459](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/459) merged the Need **Reorder →** card. The A36 Play v8 take earlier today left #404 tap **Unknown** and still named ROG as the preferred hardware gap. The sponsor then probed the named ROG on Play Internal v8. Same **ABSENT**. This node records that so Pages do not keep ROG as an open prove, and so #404 is not reopened.

This session did **not** open `C:\Users\claud\Temp\aea-rog-404\` (sponsor machine only). Do not treat that path as inspected from this checkout. No Play Console. No `cts-ai` clone. No merge.

---

## 2. Install facts (sponsor probe — do not invent more)

On **2026-09-05**, ASUS ROG (`ASUS_I001DC`, serial `K9AIKN07B088C89`) installed companion from Play Internal:

| Fact | Value |
|---|---|
| `versionCode` | **8** |
| `versionName` | `0.1.0-alpha.8` |
| `installerPackageName` | `com.android.vending` |
| Debuggable | **non-`DEBUGGABLE`** |

Cold-start Need showed suggestion chips only (Mom's Birthday / Anniversary, etc.). Reorder / wallet one-tap CTA **ABSENT** — same as A36 earlier today.

---

## 3. Root-cause hypothesis (code, not device dump)

No feature flag, no min-version, no remote FR-008 gate.

`NeedScreen` shows the returning-customer card only when:

```
!hasUserMessages && !hasOccasion && latestWalletReceipt != null
```

Suggestion chips use the same freshness pair **without** the receipt check (`clients/mobile/android/app/src/main/java/link/artof/aea/companion/ui/screens/Screens.kt`). Chips visible + CTA absent ⇒ `latestWalletReceipt == null` on that cold start.

Why the receipt StateFlow is null (ranked, not proven from a wallet dump):

1. **Empty Play wallet (primary).** `EdgeWallet.latestReceipt()` is null when EncryptedPrefs has no receipts. Play signing does not inherit debug / App Dist Keystore data. A first Play session that has not Confirm'd writes nothing. Empty-wallet hide is current FR-008 / ADR-020 product — not an empty-state CTA.
2. **Keystore init fallback.** `MainActivity` catches `EncryptedPrefsWalletStore` failures and uses `SessionRepository()` → `InMemoryWalletStore()` (empty every process).
3. **Corrupt/missing blob.** `EncryptedPrefsWalletStore.load()` returns `emptyList()` on decode failure.
4. **Possible v8 AAB without !459 (secondary, not proven).** `versionCode = 8` was bumped on #402 commit `01fe2e7` (not an ancestor of `1a1ffea`). That commit merged to `main` at `887305e` after !459. A main-based v8 AAB should include the card. A #402-branch-only AAB would not. A36 v8 **PASS** on #401 and #402 makes a main-based upload more likely. `main` is still `versionCode` 8, so `dumpsys` cannot distinguish.

Session leftover occasion / user messages are **ruled out** for this take: those would also hide the chips.

---

## 4. Tracker

* Do **not** reopen #404.
* New issue: [#407](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/407) — Play-honest prove / wallet-contents walk. Owner `@aea-senior-software-engineer`. `@aea-product-owner` only if product asks for an empty-wallet CTA.
* Sideload ROG walk in [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] stays UX/code proof, not Play-install honesty.

---

## 5. What Pages must say

* Play-honest #404 on **both** named handsets is **ABSENT** on fresh / cold-start Need (A36 and ROG, Play Internal v8).
* Do not leave ROG as the preferred remaining #404 tap prove.
* Write vs tap stay two facts. Need reorder tap on Play stays **Unknown**.
* Do not claim the customer guide card appears on every cold start. It appears when a **device-held receipt** exists.
* **This page's 30s demo clip** remains the !455 Need→Pick→Pay take and does not show the reorder card.

---

## Wikilinks

[[2026-09-05-session-memory-log-a36-play-v8-honesty-401-402]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · [[2026-09-04-session-memory-log-evening-mrc-rog-wallet-honesty]] · [[ADR-020]] · [[FR-008]]
