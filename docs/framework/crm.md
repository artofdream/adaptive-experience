# Privacy-Preserving CRM & Least-Data Customer Intelligence

The Adaptive Experience Architecture (AEA) avoids centralized Personally Identifiable Information (PII) honeypots. Traditional CRMs store customer names, emails, phones, and addresses indefinitely. AEA satisfies operator order overview and customer relationship needs through a **3-Layer Privacy-Preserving CRM Pattern** (ADR-020).

> **In Plain English:** Traditional customer management systems (CRMs) collect and hoard customer names, phone numbers, home addresses, and credit card histories in a central database forever. When that database gets hacked, everyone's private life is exposed. AEA uses a **zero-PII, least-data** approach: the store tracks shopping patterns with anonymous tokens, customer favorites stay encrypted on their own phones, and physical delivery addresses are automatically shredded from the database 14 days after flowers arrive.

---

## 1. The 3-Layer CRM Pattern

Layers stack from operator view (top) down to where raw PII may briefly live (bottom). Each layer is a readable card on any screen width:

> **1. Operator Insights** — Aggregated intelligence · behavior buckets · order fulfillment. Reads pseudonymous projections from Layer 2 (never raw PII).

> **2. Platform Pseudonymous Subject Intelligence** — Opaque subject tokens (`subject_reference = HMAC(client_id)`); transaction aggregates (order count, lifetime spend bands); occasion vector (e.g. 70% Birthday / Mother, 30% Anniversary); preferred channel (`Companion App` vs `Web Browser`).

> **3A. Client-Side Edge Wallet** (Companion on-device DB) — Full local order receipts; favorite recipient records; custom occasion reminders. Presents a zero-PII claim up into Layer 2.

> **3B. Ephemeral Fulfillment Vault** (14-day auto-shred) — Raw delivery street address; unlocked only during packing; KMS-encrypted and purged after TTL. Tokenized destination pointer up into Layer 2.

---

## 2. Core Pillars

1. **Pseudonymous Subject Profiles:** Platform tables represent returning customers via deterministic salted hashes (`sub_9b179aea00e...`). Repeat orders, spend bands (`$50–$100`), and occasion types are tracked without storing names or emails.
2. **Client-Side Edge Wallet (Android Companion):** Detailed transaction history and recipient labels (e.g. "Mom") stay on the user's physical device in platform-backed encrypted storage. After a confirmed order, the phone can later send back only an opaque product/order token — not a name or address. **The save path is live.** A Need-screen “reorder last order” button is **not** shipped yet; do not read this page as if that tap already exists.
3. **14-Day Ephemeral Address Shredding:** Physical street addresses and delivery phone numbers exist solely in an isolated KMS-encrypted table with an automated 14-day database-level TTL purge.

---

## 3. Honest Implementation Status

Every capability is classified by its verified code and hardware probe status:

| Layer / Feature | Status | Implementation Evidence |
| :--- | :--- | :--- |
| **Layer 1: Occasion Memory & Pull Reminders** | **Live on `main` / Tested** | Migration `018_engagement_crm.sql`. Order-triggered occasion capture records categorical event month/day and relation. Workspace projection exposes deterministic `reminders` facet. |
| **Layer 1: Pseudonymous Subject Profiles** | **Live on `main` / Tested** | Migrations `024_operator_crm_subject_profile.sql` and `026_crm_lifetime_spend.sql`. Cumulative running spend bands (`band_50_100`, `band_250_plus`), order counter, preferred channel. 274 integration tests pass. |
| **Layer 1: Privacy Lifecycle & Retention Purge** | **Live on `main` / Tested** | Migration `025_crm_retention_indexes.sql`. Customer erasure (`DELETE /api/v1/crm/occasions` / `forget`), 400-day annual retention purge job (`purge_crm_retention.py`), and idempotent deletions. |
| **Layer 2: Client-Side Edge Wallet** | **Save live / Probed on Hardware; reorder tap Unknown** | Pure Kotlin on Android companion. Verified on physical ASUS ROG handset (`ASUS_I001DC`): Android Keystore Tink authenticated envelope encryption (`AesSivKey` + `AesGcmKey`). Receipt write on Confirm probed. Need-screen one-tap reorder control is **not** on the phone yet. |
| **Layer 3: Ephemeral Fulfillment Shredding** | **Live on `main` / Tested** | `orchestration.ephemeral_fulfillment` with 14-day `expires_at`. Automated database-level TTL purge via `PsycopgCrmStore.purge_expired_fulfillment`. |
| **Layer 3: KMS Address Encryption Write Path** | **Sponsor-Gated (Unbuilt)** | Database schema and retention shredder are in place. The live write path and AWS KMS Customer Managed Key (CMK) provisioning remain sponsor-gated for key lifecycle governance. |

---

## 4. Deterministic Pull Reminders (Not Creepy AI Push)

Reminders on the Adaptive Workspace are strictly **deterministic pull signals**:
- They trigger solely when a shopper initiates a session and the session's browser hash matches a previously recorded delivery anniversary.
- No unsolicited push notifications, marketing emails, SMS blasts, or third-party ad retargeting pixels.
- The reminder payload carries least-data fields only (`occasion_type`, `days_until_event`, `reminder_text`, `recipient_relation`) without customer names or delivery addresses.

---

## 5. Related Documentation & Architecture Decisions

- [Mobile Companion App](companion.html) — Client-side edge wallet and local encryption.
- [System Stack](stack.html) — How domain services and databases connect securely.
- [Architecture Blueprint](schema.html) — Core formula and the 6 outer harness layers.
- [Architecture Glossary](glossary.html) — Plain-English definitions of least-data terms.
- [Framework Home](index.html) — Return to the overview.
- Repository ADR references: `ADR-020` (Privacy CRM), `ADR-013` (Confirmation-Driven), `NFR-017` (Zero-PII Perimeter), and `FR-008` (Reorder Hint).

