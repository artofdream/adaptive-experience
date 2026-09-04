# Privacy-Preserving CRM & Least-Data Customer Intelligence

The Adaptive Experience Architecture (AEA) avoids centralized Personally Identifiable Information (PII) honeypots. Traditional CRMs store customer names, emails, phones, and addresses indefinitely. AEA satisfies operator order overview and customer relationship needs through a **3-Layer Privacy-Preserving CRM Pattern** (ADR-020).

---

## 1. The 3-Layer CRM Pattern

Layers stack from operator view (top) down to where raw PII may briefly live (bottom). Each layer is a readable card on any screen width.

> **1. Operator Insights** — Aggregated intelligence · behavior buckets · order fulfillment. Reads pseudonymous projections from Layer 2 (never raw PII).

> **2. Platform Pseudonymous Subject Intelligence** — Opaque subject tokens (`subject_reference = HMAC(client_id)`); transaction aggregates (order count, lifetime spend bands); occasion vector (e.g. 70% Birthday / Mother, 30% Anniversary); preferred channel (`Companion App` vs `Web Browser`).

> **3A. Client-side Edge Wallet** (Companion on-device DB) — Full local order receipts; favorite recipient records; custom occasion reminders. Presents a zero-PII claim up into Layer 2.

> **3B. Ephemeral Fulfillment Vault** (14-day auto-shred) — Raw delivery street address; unlocked only during packing; KMS-encrypted and purged after TTL. Tokenized destination pointer up into Layer 2.

---

## 2. Core Pillars

1. **Pseudonymous Subject Profiles:** Platform tables represent returning customers via deterministic salted hashes (`sub_9b179aea00e...`). Repeat orders, spend bands (`$50–$100`), and occasion types are tracked without storing names or emails.
2. **Client-Side Edge Wallet (Android Companion):** Detailed transaction history and recipient labels (e.g. "Mom") stay on the user's physical device in platform-backed encrypted storage. One-tap reorders (FR-008) present opaque claims directly.
3. **14-Day Ephemeral Address Shredding:** Physical street addresses and delivery phone numbers exist solely in an isolated KMS-encrypted table with an automated 14-day database-level TTL purge.

---

## 3. Honest Implementation Status

Every capability is classified by its verified code and hardware probe status:

| Layer / Feature | Status | Implementation Evidence |
| :--- | :--- | :--- |
| **Layer 1: Occasion Memory & Pull Reminders** | **Live on `main` / Tested** | Migration `018_engagement_crm.sql`. Order-triggered occasion capture records categorical event month/day and relation. Workspace projection exposes deterministic `reminders` facet. |
| **Layer 1: Pseudonymous Subject Profiles** | **Live on `main` / Tested** | Migrations `024_operator_crm_subject_profile.sql` and `026_crm_lifetime_spend.sql`. Cumulative running spend bands (`band_50_100`, `band_250_plus`), order counter, preferred channel. 274 integration tests pass. |
| **Layer 1: Privacy Lifecycle & Retention Purge** | **Live on `main` / Tested** | Migration `025_crm_retention_indexes.sql`. Customer erasure (`DELETE /api/v1/crm/occasions` / `forget`), 400-day annual retention purge job (`purge_crm_retention.py`), and idempotent deletions. |
| **Layer 2: Client-Side Edge Wallet** | **Live on `main` / Probed on Hardware** | Pure Kotlin on Android companion. Verified on physical ASUS ROG handset (`ASUS_I001DC`): Android Keystore Tink authenticated envelope encryption (`AesSivKey` + `AesGcmKey`). Zero raw PII or card message plain text at rest. |
| **Layer 3: Ephemeral Fulfillment Shredding** | **Live on `main` / Tested** | `orchestration.ephemeral_fulfillment` with 14-day `expires_at`. Automated database-level TTL purge via `PsycopgCrmStore.purge_expired_fulfillment`. |
| **Layer 3: KMS Address Encryption Write Path** | **Sponsor-Gated (Unbuilt)** | Database schema and retention shredder are in place. The live write path and AWS KMS Customer Managed Key (CMK) provisioning remain sponsor-gated for key lifecycle governance. |

---

## 4. Deterministic Pull Reminders (Not Creepy AI Push)

Reminders on the Adaptive Workspace are strictly **deterministic pull signals**:
- They trigger solely when a shopper initiates a session and the session's browser hash matches a previously recorded delivery anniversary.
- No unsolicited push notifications, marketing emails, SMS blasts, or third-party ad retargeting pixels.
- The reminder payload carries least-data fields only (`occasion_type`, `days_until_event`, `reminder_text`, `recipient_relation`) without customer names or delivery addresses.

---

## 5. Related Decisions & Requirements

- [ADR-020 Privacy-Preserving CRM & Edge Wallet](../06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md)
- [ADR-013 Confirmation-Driven Experience](../06-adr/ADR-013-confirmation-driven-experience.md)
- [NFR-017 Zero-PII / Least-Data Perimeter](../02-business-analysis/requirements.md)
- [FR-008 Thin Reorder Hint](../02-business-analysis/requirements.md)
