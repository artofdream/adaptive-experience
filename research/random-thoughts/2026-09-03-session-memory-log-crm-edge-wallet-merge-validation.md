# Session Memory Log: CRM & Edge Wallet Merge Completion & System Validation (2026-09-03)

> **Tags**: #aea #session-memory #crm #edge-wallet #android #migration-024 #handover #knowledge-first
> **Captured**: 2026-09-03 ~22:35 Europe/Berlin (20:35 UTC)
> **Author**: @aea-knowledge-guardian & @aea-senior-software-engineer
> **Repository**: rtof-group/adaptive-experience-architecture
> **Related**: [[2026-09-02-least-data-crm-privacy-preserving-order-insights]] · [[2026-09-03-session-handover-afk-cloud-runners]] · [[2026-09-03-play-internal-v4-upload-390]] · [[2026-09-03-path-b-florist-384-migration-023-channel-live]] · [!431](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/431) · [!438](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/438) · [!439](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/439) · [!440](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/440)

---

## 1. Executive Milestone Progress

Four major merge requests impacting the Privacy-Preserving CRM, Native Android Companion, Public Framework Site, and System Documentation have been successfully merged into main:

1. **MR !431 (eat/least-data-operator-crm)**:
   - Implemented CrmService in platform/aea_platform/crm.py under ADR-020, ADR-013, and NFR-017.
   - Added migration platform/migrations/024_operator_crm_subject_profile.sql creating orchestration.subject_profile (pseudonymous HMAC-SHA256 tokens, spend bands, occasion vectors, channel distribution) and orchestration.ephemeral_fulfillment (14-day auto-shredding vault).
   - Preserved backward compatibility for EngagementCrmService (occasion memory for FR-016/FR-017).
   - Created public framework reference page docs/framework/crm.md.
2. **MR !438 (cursor/crm-layer2-edge-wallet-941a)**:
   - Implemented ADR-020 Layer 2 Edge Wallet in clients/mobile/android/.
   - Pure-Kotlin domain (EdgeWallet, WalletReceipt, ReorderReference, InMemoryWalletStore) ensuring zero-PII invariant: device-only fields (ecipientLabel, cardMessageDraft, occasionType) are encrypted via Android Keystore AES-256 (EncryptedSharedPreferences) and never leave the handset.
   - Enables FR-008 one-tap reorders presenting purely opaque {productId, orderReference} tokens with authoritative NFR-009 inventory re-validation.
3. **MR !439 (docs/framework-companion-play-honesty-jump-nav)**:
   - Captured physical device validation for Issue #390 on Samsung Galaxy A36 (installerPackageName=com.android.vending, ersionCode 4, non-DEBUGGABLE).
   - Documented florist channel gate #384 (channel=web on Path B).
   - Added responsive smooth-scroll mobile Top/Bottom jump navigation controls.
4. **MR !440 (docs/framework-crm-layers-readable-mobile)**:
   - Reformatted the 3-Layer CRM architecture Mermaid diagram for readability on narrow mobile viewports.

---

## 2. Technical Decisions & Incident Remediation

During the integration and merge process, four key technical defects were diagnosed and remediated:

1. **UTF-8 Byte Order Mark (BOM) in SQL Migration**:
   - *Symptom*: Migration 024 failed during CI platform-foundation-integration with: syntax error at or near "﻿" LINE 1: ﻿-- 024_operator_crm_subject_profile.sql.
   - *Fix*: Stripped '\xef\xbb\xbf' from the file header, restoring pure UTF-8 formatting.
2. **orchestration.schema_migration Column Parity**:
   - *Symptom*: Migration 024 attempted to insert into (version, description), but the table schema only defines ersion.
   - *Fix*: Normalized insert to INSERT INTO orchestration.schema_migration (version) VALUES (24) ON CONFLICT (version) DO NOTHING;.
3. **Database Migration Count Invariant (23 → 24)**:
   - *Symptom*: FoundationTests.test_all_24_database_migrations_are_discoverable_and_ordered and PostgreSQLIntegrationTests.test_migrations_are_at_latest_version both asserted hardcoded len(expected) == 23.
   - *Fix*: Synchronized both discovery assertions to 24 migrations.
4. **Canonical System Documentation Enhancement**:
   - Updated docs/aea-system-documentation.md adding **Section 10** (Privacy-Preserving CRM & Ephemeral Fulfillment) and **Section 11** (Native Mobile Companion Architecture), and reconciled the 14-role stakeholder roster.

---

## 3. Handover Matrix for Autonomous Cloud Runners

When local workstation (cts-ai) is offline, autonomous Cloud Runners (AWS ECS Fargate 24/7 Agent Runner, Cursor Cloud Agents, GitLab CI scheduled jobs) can execute the following tasks:

| Priority | Task Description | Target Component | Ownership & Command |
| :--- | :--- | :--- | :--- |
| **P1** | **Apply Migration 024 on Production RDS** | AWS ECS Fargate ea-pilot | Once uild-ecr deploys to ECR, run ECS RunTask executing python platform/scripts/apply_migrations.py on cluster ea-pilot. |
| **P2** | **Review & Auto-Merge Operator Efficiency MR !434** | edge/gateway/ui/assets/florist.js | Cursor Agent c-e4875f0e... is authoring boot parallelization & pagination. Once ready (glab mr update 434 --ready), MRC can review and merge. |
| **P3** | **Close Resolved Issues #375 & #377** | GitLab Issue Tracker | Verify live https://aea.artof.link/florist operator orders exhibit channel=web and full product titles/prices, then close #375 and #377. |
| **P4** | **Monitor Cursor Cloud Dev Container MR !432** | .cursor/ | Review .cursor/environment.json Docker Compose nested VM boot scripts for dev agent reproducibility. |
| **P5** | **Verify GitLab Pages Deployment** | https://architecture.artof.link | Verify Pages job builds and publishes the mobile-optimized CRM diagram (crm.html) and companion honesty table (companion.html). |

---

## 4. Operational Posture

- **Pre-Flight Quality Guards**: **14/14 Passed Cleanly**.
- **Platform Unit Tests**: **259 Passed** (0 errors, 0 failures).
- **Edge Unit Tests**: **72 Passed** (0 errors, 0 failures).
- **Knowledge Graph**: **148 notes, 792+ wikilinks validated**.
- **Working Tree**: Clean on main.
