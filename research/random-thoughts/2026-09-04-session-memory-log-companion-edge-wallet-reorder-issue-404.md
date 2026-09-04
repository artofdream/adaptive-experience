# Session Memory Log: FR-008 One-Tap Reorder Affordance from Edge Wallet on Android Companion (Issue #404)

> **Tags**: #aea #session-memory #companion #android #edge-wallet #fr-008 #adr-020 #nfr-009 #nfr-017 #second-brain
> **Captured**: 2026-09-04 ~23:30 Europe/Berlin (21:30 UTC)
> **Author**: @aea-knowledge-guardian & @aea-senior-software-engineer
> **Repository**: rtof-group/adaptive-experience-architecture
> **Related**: [[2026-09-04-session-memory-log-mrc-crm-companion-v5-play-honesty]] · [[2026-09-04-status-play-v5-gaps]] · docs/06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md · clients/mobile/android/app/src/main/java/link/artof/aea/companion/data/repository/SessionRepository.kt · clients/mobile/android/app/src/main/java/link/artof/aea/companion/ui/screens/Screens.kt · clients/mobile/android/app/src/main/java/link/artof/aea/companion/MainActivity.kt

---

## 1. Context & Problem Statement

Under **ADR-020 (Privacy-Preserving CRM & Edge Wallet)**, Lily's Florist Companion holds past order receipts locally inside encrypted on-device storage (EncryptedPrefsWalletStore), strictly preventing customer PII (recipient names, enclosure card drafts, delivery addresses) from persisting in the cloud CRM or platform databases (NFR-017).

While the underlying 
eorderFromWallet() BFF plumbing and EdgeWallet storage were implemented in previous sprints, the returning-customer affordance was missing from the UI:
- Returning shoppers opening the app or starting a new arrangement on NeedScreen saw only standard suggestion chips (Mom's Birthday, Anniversary).
- The device-held receipt from previous purchases was not exposed reactively, preventing users from benefiting from a **FR-008 One-Tap Reorder** flow.
- GitLab Issue [#404](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/404) was logged to connect the Edge Wallet state reactively to NeedScreen and prove the full flow on physical hardware.

---

## 2. Architectural & Implementation Decisions

### A. Reactive State Exposure in SessionRepository
- Added _latestWalletReceipt: MutableStateFlow<WalletReceipt?> = MutableStateFlow(wallet.latestReceipt()) and public al latestWalletReceipt: StateFlow<WalletReceipt?>.
- When an order completes successfully in completeCheckout(), _latestWalletReceipt.value = receipt is immediately published.
- When startOver() is tapped to begin a new arrangement, _latestWalletReceipt.value is synchronized with wallet.latestReceipt() to ensure fresh UI state.
- Provided explicit public helpers latestWalletReceipt(): WalletReceipt? and clearWallet() (supporting customer right-to-be-forgotten / reset).

### B. Returning Customer Card on NeedScreen
- In Screens.kt (NeedScreen), added parameters latestWalletReceipt: WalletReceipt? = null and onReorderFromWallet: () -> Unit = {}.
- Rendered an elevated Material 3 Card with secondaryContainer styling directly above the suggestion chips, gated on:
  `kotlin
  if (!hasUserMessages && !hasOccasion && latestWalletReceipt != null)
  `
- **Zero-PII Dynamic Personalization**:
  - Displays "Reorder for {recipientLabel}" (e.g. "Reorder for mother") if a recipient was saved locally, or fallback "Reorder previous bouquet".
  - Secondary caption: "1-tap repeat order from this phone's encrypted wallet".
  - Accessible 44dp action button: Button(onClick = onReorderFromWallet) { Text("Reorder →") }.

### C. Plumbing in MainActivity.kt
- Collected al latestWalletReceipt by repository.latestWalletReceipt.collectAsState().
- Passed latestWalletReceipt and onReorderFromWallet = { scope.launch { repository.reorderFromWallet() } } to NeedScreen.
- Tapping triggers 
eorderFromWallet():
  1. Ensures active anonymous session via BFF (POST /api/v1/session).
  2. Submits opaque SKU selection (POST /api/v1/selection) to re-validate catalog availability and pricing (NFR-009).
  3. Transitions stage directly to PICK with the arrangement pre-selected.

---

## 3. Verification & Physical Device Proof (ASUS ROG Phone K9AIKN07B088C89)

### Unit Tests
- Added latestWalletReceiptStateUpdatesOnCheckoutAndReset() in EdgeWalletReorderIntegrationTests.kt.
- Built and verified with JDK 21:
  - .\gradlew testDebugUnitTest: **BUILD SUCCESSFUL in 41s** (28/28 tasks passed, including Paparazzi screenshot regressions).

### Pre-Flight Quality Guards
- Ran python scripts/run_all_guards.py: **14/14 guards passed cleanly**.

### Physical Hardware Walkthrough on ASUS ROG Phone
1. **Device Identification**: Sideloaded only to the designated test device (K9AIKN07B088C89), leaving the sponsor's daily phone (SM-A366B) untouched.
2. **Initial Purchase Seed**:
   - Started fresh journey: Occasion "Mom's Birthday", selected $35.00 arrangement, entered card message "Happy Birthday mother! Love always.".
   - Reached PAY screen, tapped Confirm Order (,00).
   - Order confirmed (cee475e-37a6-48f2-a4b1-b93ff39f5c04), receipt saved to encrypted device storage.
3. **Returning Customer State**:
   - Tapped Start New Arrangement -> landed on NeedScreen.
   - Observed the newly surfaced Card:
     - Title: **"Reorder for mother"**
     - Subtitle: **"1-tap repeat order from this phone's encrypted wallet"**
     - Action: **"Reorder →"**
   - Screenshot recorded: clients/mobile/android/app/build/reorder-card-need-screen.png.
4. **1-Tap Reorder Action**:
   - Tapped Reorder →.
   - App immediately queried BFF selection endpoint and transitioned to PICK stage with the $35.00 bouquet selected, ready for checkout.
   - Screenshot recorded: clients/mobile/android/app/build/reordered-pick-screen.png.

---

## 4. Architectural Invariants & Security Boundaries

| Principle / Requirement | Implementation Guarantee |
|---|---|
| **ADR-020 Zero-PII Invariant** | Recipient names and card message drafts live exclusively in EncryptedSharedPreferences on the client device. They are NEVER sent to the backend CRM, Kafka, or PostgreSQL. |
| **NFR-009 Inventory Revalidation** | The reorder action does not blindly place an order; it passes the opaque productId through POST /api/v1/selection so the backend verifies availability and current pricing before landing on PICK. |
| **FR-008 One-Tap Ergonomics** | Returning shoppers bypass redundant chat / occasion intake and arrive directly at the selection stage with 1 tap. |
| **Right-to-be-Forgotten** | Added 
epository.clearWallet() to wipe local encrypted receipt stores on demand. |

---

## 5. Next Steps

1. Commit and push branch cursor/companion-wallet-reorder-404.
2. Open GitLab MR for Issue #404 with screen captures attached and hand off to @aea-mr-coordinator.
3. Regenerate daily brief via python scripts/generate_daily_brief.py.
