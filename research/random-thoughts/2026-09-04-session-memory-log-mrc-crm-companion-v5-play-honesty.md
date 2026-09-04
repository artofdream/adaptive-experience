# Session Memory Log: MRC Processing, CRM Completion, Companion v5 Play Honesty & Operator Console Review (2026-09-04)

> **Tags**: #aea #session-memory #mrc #crm #edge-wallet #companion #play-honesty #rog #381 #390 #375 #434 #knowledge-first
> **Captured**: 2026-09-04 ~11:30 Europe/Berlin (09:30 UTC)
> **Author**: `@aea-knowledge-guardian` and `@aea-mr-coordinator`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-03-session-memory-log-crm-edge-wallet-merge-validation]] · [[2026-09-03-asus-rog-live-e2e-order-edge-wallet-proof]] · [[2026-09-03-session-memory-log-381-rog-cts-ai]] · [[2026-09-04]] (`research/daily-briefs/2026-09-04.md`) · [!441](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/441) · [!442](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/442) · [!443](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/443) · [!444](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/444) · [!432](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/432) · [!434](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/434)

---

## 1. Executive Milestone & Merge Queue Completion

All open candidate MRs on the queue have been reviewed, gated, and merged by `@aea-mr-coordinator`:

1. **MR !444 (`fix/companion-versioncode-5`) — MERGED**:
   - Bumped Android companion `versionCode` 4 → 5 (`0.1.0-alpha.5`).
   - Triggered release pipeline `#2818539184` on `main`, executing `android-bundle-release` and `android-play-internal-upload` to Google Play Console Internal Track and Firebase App Distribution.
2. **MR !441 (`feat/381-companion-t09-real-t05`) — MERGED (Closes #381)**:
   - Added Ktor `ContentNegotiation` and JSON serializer to `BffClientHeaderTests.kt` (`0b977e3`) to resolve unit test failure under JDK 21.
   - Verified clean locally with `--no-daemon` and on CI pipeline `#2818538806`.
   - Adds T-09 "Contact Florist" (`POST /api/v1/support/escalation`) and choosable delivery window (morning/afternoon/evening) / destination reference (`home`/`work`).
3. **MR !442 (`cursor/crm-privacy-lifecycle-941a`) — MERGED**:
   - Closes privacy lifecycle under ADR-020: customer erasure (`DELETE /api/v1/crm/occasions` / `forget`), 400-day annual retention purge job (`platform/scripts/purge_crm_retention.py`), and 14-day ephemeral vault shredding.
   - Introduced Migration 025 (`025_crm_retention_indexes.sql`). Pipeline `#2818424246` green.
4. **MR !443 (`cursor/crm-capture-read-5d6b`) — MERGED**:
   - Wires zero-PII CRM from order capture → workspace pull reminders read.
   - Implemented pseudonymous subject profile (`orchestration.subject_profile`) with cumulative running lifetime spend bands (`band_50_100`, `band_250_plus`), order counter, and preferred channel.
   - Cleanly stacked on top of !442 as Migration 026 (`026_crm_lifetime_spend.sql`). 274 integration tests pass.
5. **MR !432 (`cursor/setup-dev-environment-941a`) — MERGED**:
   - Standardized dev environment configuration in `.cursor/environment.json`.

---

## 2. Hardware Verification & Live Production Proofs

### A. Google Play Store Honesty Gate Verified on Physical ASUS ROG (Issue #390)
* **Handset**: ASUS ROG (`ASUS_I001DC`, serial `K9AIKN07B088C89`).
* **Evidence**: Inspected package via ADB after updating from Google Play Internal Track:
  ```text
  versionCode=5 minSdk=26 targetSdk=36
  installerPackageName=com.android.vending
  pkgFlags=[ HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP ]
  ```
* **Significance**: Confirms non-debuggable, signed release AAB delivered directly by `com.android.vending`. Closing evidence posted to GitLab Issue #390 Note #3785752118. Both test phones (Samsung Galaxy A36 on v4 and ASUS ROG on v5) now have verified Play Store installations.

### B. Channel Observability Dual-Probe Verified (Issue #375)
* **Execution**: Physical shopping walk on ASUS ROG:
  - Tapped `[Mom's Birthday (Same-Day)]` → budget `[$50–100]` → `classic-rose-dozen` ($70.00 + $12.00 delivery = $82.00).
  - Confirmed Order UUID: `34091114-cb91-44de-a5a3-6be78c503912`.
* **Backend Proof**: Queried AWS ECS Fargate live endpoint `GET https://aea.artof.link/api/v1/operator/orders`.
  - Order `34091114-cb91-44de-a5a3-6be78c503912` appeared at the top of the feed with `client: companion-android` via `X-AEA-Client` telemetry.
  - Closed GitLab Issue #375 Note #3785753427.

### C. ADR-020 Layer 2 Edge Wallet Cryptographic Proof
* Device sandbox dump at `/data/data/link.artof.aea.companion/shared_prefs/aea_edge_wallet.xml` proved `EncryptedPrefsWalletStore` wrote encrypted receipt using Android Keystore Tink keysets (`AesSivKey` + `AesGcmKey`). Zero customer PII or card message plain text at rest on the device.

---

## 3. CRM Architecture Completion (ADR-020)

With MRs !442 and !443 merged, ADR-020 status is:

| Layer | Component | Status | Production / Code Reality |
| :--- | :--- | :--- | :--- |
| **Layer 1** | Occasion Memory & Reminders | **Merged & Live** | `crm.customer_occasion_memory` (Migration 018). Order path capture records categorical month/day/relation. Workspace projection surfaces deterministic `reminders` facet. Customer opt-out `DELETE /api/v1/crm/occasions` (`forget`) + 400-day retention purge (Migration 025). |
| **Layer 1** | Pseudonymous Subject Profile | **Merged & Live** | `orchestration.subject_profile` (Migrations 024 & 026). Cumulative running spend bands (`band_50_100`, `band_250_plus`), order counter, preferred channel, and operator subject insights endpoint. |
| **Layer 2** | Client-Side Edge Wallet | **Merged & Probed** | Pure Kotlin in Android companion (`clients/mobile/android/`). Android Keystore Tink encrypted storage on physical device. Proved on ASUS ROG. |
| **Layer 3** | Ephemeral Fulfillment Vault | **Merged (Storage & Shredder)** | `orchestration.ephemeral_fulfillment` with 14-day `expires_at`. Automated TTL database shredding via `purge_crm_retention.py`. |
| **Layer 3** | KMS Address Encryption Write Path | **Sponsor-Gated** | The write path and AWS KMS Customer Managed Key (CMK) provisioning remain sponsor-gated for key governance and cloud spend. |

---

## 4. Architectural Review of Draft MR !434 (Operator Console Efficiency)

MR !434 (`cursor/operator-efficiency-improvements-df7e`) was reviewed across engineering, product, and process boundaries:
1. **Parallel Boot (`florist.js`)**: Replaced sequential `await`s with `Promise.allSettled([inbox, orders, forecasts])`. Reduces console TTFR to the slowest single fetch without compromising fail-closed fallback to sample data if inbox fails.
2. **Keyset Cursor Pagination**: Parameterized `after_cursor` across DB stores, internal API, BFF, and UI `Load more…` button. Increases item cap from 50 to 200, resolving the issue where older orders were unreachable.
3. **Bounded GET Retry**: Implements max 2 retries (0.3s base exponential backoff) in BFF `orchestration.py` strictly for safe `GET` calls on network timeouts or 500s. Non-GET mutations (`POST`, `PUT`, `PATCH`, `DELETE`) fail-fast immediately with no retry.
4. **Mergeability**: 0 git conflicts against updated `main`. 80 edge tests, 275 platform tests, and 14/14 quality guards pass cleanly.
5. **Process Note**: The MR was held in Draft due to the "mixed scope" policy (3 changes in 1 MR). The PO/PM recommendation is to accept it as a single unified "Operator Resilience & Scaling" package rather than splitting it into 3 separate churn-heavy branches.

---

## 5. Public Framework Surface Synchronization (`architecture.artof.link`)

To maintain empirical honesty on the public documentation site:
1. **`docs/framework/README.md`**: Added `crm.md` to the allowlist table.
2. **`docs/framework/companion.md`**:
   - Updated Honesty Gates table to reflect **Play Internal versionCode 5** on ASUS ROG (`ASUS_I001DC`).
   - Recorded live channel observability proof on ECS Fargate (Order `34091114-cb91-44de-a5a3-6be78c503912` showing `client: companion-android`).
   - Added entry for T-09 Contact Florist escalation and choosable delivery windows (MR !441).
3. **`docs/framework/crm.md`**:
   - Added comprehensive **Honest Implementation Status** table detailing Layers 1, 2, and 3.
   - Explicitly clarified that reminders are **deterministic pull signals** based on delivery dates, rejecting unsolicited AI push notifications or tracking pixels.
4. **Site Builder Verification**: `python scripts/build_framework_site.py` and `python scripts/test_build_framework_site.py` executed cleanly (6/6 tests passed). Pushed to `main` (`4a1a86c`) so GitLab Pages rebuilds `architecture.artof.link`.

---

## 6. Sponsor Governance & FinOps Notice

1. **ADR-020 Layer 3 KMS Write Path**: Sponsor gate required before provisioning AWS KMS Customer Managed Key and enabling live ephemeral address encryption.
2. **GitLab Duo AI Review Credits**: GitLab Duo automated review reported `No GitLab Credits remain for this billing period (DCR4002)`. Standard CI/CD runner execution remains unaffected.
3. **External Commercial CRM (M12 Scope)**: The repository has delivered the zero-PII, zero-external-vendor in-house solution (Layers 1 and 2), keeping external SaaS subscription costs at **$0**.

---

## 7. Mobile Viewport Refinement (`architecture.artof.link/companion.html`)

- **Root Cause Analysis**:
  - The site generator stylesheet in `scripts/build_framework_site.py` used `th, td { word-break: break-word; overflow-wrap: anywhere; }`. In CSS, `overflow-wrap: anywhere` allows breaking between arbitrary graphemes/syllables inside common words when table column widths shrink.
  - On narrow mobile viewports (<360px), the 2-column Honesty Gates table (`Claim | Gate`) had no column min-width. Because the "Gate" column had full paragraphs, table auto-layout compressed the "Claim" column to ~60px, causing severe word-breaking artifacts (e.g. `Install / s from / Play`, `comp / anion / chann / el`).
- **Remediation**:
  1. **Site CSS Fix (`scripts/build_framework_site.py`)**:
     - Reset `th, td` to `overflow-wrap: break-word; word-break: normal;` preventing English prose from being hyphen-less sliced mid-word.
     - Added `td code, th code { word-break: break-all; }` so long code symbols, URLs, and hashes still wrap safely.
     - Added `@media(max-width:640px) { .table-wrap table { min-width: 28rem; } th,td { padding: .35rem .5rem; font-size: .78rem; } blockquote.callout { padding: .75rem .9rem; margin: 1rem 0; } }` ensuring any table that remains a table scrolls horizontally via its `.table-wrap` wrapper instead of crushing columns.
  2. **Responsive Card Architecture (`docs/framework/companion.md`)**:
     - Converted the cramped 2-column table under `## Honesty gates` into stacked executive callout cards (`blockquote.callout` with gold accent left border), matching the pattern established in `crm.md`.
     - Output renders at full 100% viewport width with zero word splitting and full readability on small phone screens.
  3. **Plain English Editorial Reformulation (`docs/framework/companion.md`)**:
     - Reformulated dense engineer-facing jargon ("thin live-BFF client for the Path B Need → Pick → Pay slice") into clear, approachable, human explanations with an explicit "In Plain English" blockquote callout.
     - Explained the core value: an app that shows real bouquets actually in stock, protects customer privacy, and checks out in seconds without duplicating shop databases.
     - Upgraded `scripts/build_framework_site.py` with standard `<hr class="rule">` parsing for `---` / `***` thematic break dividers, adding CSS border styling (`var(--rule)`).
  4. **Verification**:
     - `scripts/build_framework_site.py` rebuilt all framework pages cleanly.
     - `python scripts/test_build_framework_site.py` passed (6/6 tests, including new `<hr class="rule">` assertion).
     - `python scripts/run_all_guards.py` passed (14/14 quality guards).

---

## 8. Site-Wide Plain English Reformulation (`architecture.artof.link`)

Following the successful reformulation of `companion.html`, the entire public framework documentation surface across all 9 allowlisted pages in `docs/framework/` was reviewed and elevated to accessible, human-first plain English without sacrificing empirical precision:

1. **`index.md` (Framework Home)**:
   - Added `crm.html` to framework exploration links.
   - Refined the core formula summary with everyday metaphors (live digital notepad, warehouse and cash register).
   - Added `<hr class="rule">` section dividers.
2. **`schema.md` (Architecture Blueprint)**:
   - Added an executive "In Plain English" blueprint callout.
   - Fixed broken TOC navigation link (`#fourteen-hats-three-jobs` -> `#team-roles-and-responsibilities`).
   - Clarified the 14 stakeholder hats as review lenses rather than headcount, and reinforced the 3 executable jobs (implement, verify, merge) with MRC gatekeeping.
3. **`stack.md` (System Architecture & Stack)**:
   - Added plain English summary explaining the "Two Hostnames, Two Jobs" separation.
   - Synchronized honesty ledger with today's empirical probes: Google Play internal track v5 release and ECS Fargate write-through (`34091114-cb91-44de-a5a3-6be78c503912`).
   - Clarified cloud infrastructure vs local developer paths.
4. **`comparison.md` (Visual Guide & 5 Floors)**:
   - Polished transitions between the 3 AI eras, 5 concentric floors, and 4 memory vaults.
   - Added clean section dividers throughout.
   - Preserved all cross-linked integrity assertions (`Daily-brief honesty`, `#what-aea-claims-here`, etc.).
5. **`path-b.md` (Florist Case Study)**:
   - Clearly introduced Path B as the live reference store at `aea.artof.link`.
   - Re-framed the 4 customer scenarios (Urgent Sam, Planner Sarah, Loyal Alex, Tracker Chris) with engaging persona descriptions highlighting the architectural capability proven by each 30s video.
6. **`glossary.md` (Architecture Glossary)**:
   - Expanded from 5 internal codes to a comprehensive dictionary with clear definitions for *Shared Understanding*, *Domain Services*, *Outer Harness*, *Fail-Closed Availability*, *Thin Client*, *BFF*, and *Least-Data / Ephemeral Shredding*.
7. **`journal.md` (Project Journal & Lessons Learned)**:
   - Transformed staccato notes into engaging narrative case studies (Why This Project Started, Claim vs Probe, Two Hostnames, Four Lines One Day).
   - Preserved all required test assertions and diagram assets.
8. **`crm.md` (Privacy CRM)**:
   - Added "In Plain English" callout on the perils of indefinite PII hoarding vs 14-day address shredding.
   - Polished framework navigation links.

**Verification Results**:
- `test_build_framework_site.py`: 6/6 tests PASS.
- Pre-flight Quality Guards: 14/14 PASS.
