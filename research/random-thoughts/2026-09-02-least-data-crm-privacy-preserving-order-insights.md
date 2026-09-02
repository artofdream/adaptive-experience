# Strategic Architecture Study: Least-Data Privacy-Preserving CRM & Order Intelligence

#aea #aea/crm #aea/privacy #aea/architecture #aea/adr

**Date:** 2026-09-02  
**Author:** `@aea-product-owner`, `@aea-appsec-auditor` & `@aea-senior-software-engineer`  
**Repository:** `artof-group/adaptive-experience-architecture`  
**Target Scope:** Customer Relationship Intelligence, Operator Order Overview, Zero-PII Compliance (ADR-013 / NFR-017), and Edge Wallet Patterns  
**Related Documents:** [[2026-09-02-devops-architecture-efficiency-report]] · [[2026-09-02-session-memory-log-devops-companion-budget-florist-operator]] · [[2026-09-02-framework-prove-value-kpis-checklist]]

---

## 1. Executive Context & The Problem

Traditional e-commerce Customer Relationship Management (CRM) platforms operate on high-risk, centralized honeypots of Personally Identifiable Information (PII): permanent storage of customer names, email addresses, phone numbers, full physical street addresses, and un-expunged communication logs.

In the **Adaptive Experience Architecture (AEA)** and the Lily's Florist reference design, canonical principles (ADR-013, NFR-017, and M12 Backlog Stance) forbid storing customer PII in application databases or event brokers.

However, business operators and marketing coordinators still require:
1. An **Overview of Historical Orders** (volumes, fulfillment status, repeat purchase rates).
2. **Customer Relationship Intelligence** (recognizing a returning customer, understanding gift occasion preferences, predicting reorder timing).
3. **Frictionless Reorder Experiences** (one-tap repurchase for Mom's birthday under FR-008).

This document details the **3-Layer Privacy-Preserving CRM & Order Intelligence Architecture** that fulfills 100% of these business requirements without compromising the Least-Data perimeter.

---

## 2. The 3-Layer Privacy-Preserving CRM Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      1. OPERATOR INSIGHTS TIER                          │
│     (Aggregated Intelligence · Behavior Buckets · Fulfillment KPIs)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Reads Pseudonymous Projections
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              2. PLATFORM PSEUDONYMOUS SUBJECT INTELLIGENCE              │
│       • Opaque Subject Tokens: `subject_reference = HMAC(client_id)`    │
│       • Transaction Aggregates: Order Count, Lifetime Value Bands       │
│       • Occasion Vector: 70% Birthday (Mother), 30% Anniversary         │
│       • Preferred Channel: `Companion App` vs `Web Browser`             │
└──────────────────▲─────────────────────────────────▲────────────────────┘
                   │                                 │
     Presents Zero-PII Claim         Tokenized Destination Pointer
                   │                                 │
┌──────────────────┴──────────────┐   ┌──────────────┴────────────────────┐
│   3A. CLIENT-SIDE EDGE WALLET   │   │  3B. EPHEMERAL FULFILLMENT VAULT  │
│    (Companion On-Device DB)     │   │      (14-Day Auto-Shredding)      │
├─────────────────────────────────┤   ├───────────────────────────────────┤
│ • Full local order receipts     │   │ • Raw delivery street address     │
│ • Favorite recipient addresses  │   │ • Unlocked ONLY during packing    │
│ • Custom occasion reminders     │   │ • KMS-encrypted, purged post-TTL  │
└─────────────────────────────────┘   └───────────────────────────────────┘
```

---

## 3. Detailed Component Specifications

### 3.1. Layer 1: Pseudonymous Subject Tokenization
- **Mechanism:** Customers are represented internally via salted, deterministic cryptographic hashes (`subject_reference`).
- **Data Model:**
  ```json
  {
    "subject_reference": "sub_9b179aea00e24505853b9ccfa0c57ae0",
    "customer_segment": "repeat_buyer",
    "total_completed_orders": 3,
    "lifetime_value_band": "band_100_250",
    "primary_occasion": "birthday_mother",
    "average_budget_tier": "50_100",
    "last_order_timestamp": "2026-09-02T19:28:40Z"
  }
  ```
- **Operator Benefit:** Staff and management can analyze customer cohorts, retention curves, and average order values without any personal data stored on the platform.

### 3.2. Layer 2: Client-Side Edge Wallet (Self-Sovereign History)
- **Mechanism:** The mobile companion (`link.artof.aea.companion`) stores full transaction receipts, recipient names, and delivery notes in **EncryptedSharedPreferences** / Jetpack Security.
- **FR-008 Reorder Flow:** When the user taps *"Reorder for Mom"*, the mobile app passes the previous order's `order_id` and tokenized payload to the BFF. The server validates the arrangement availability and pricing without needing to store the user's permanent address book.

### 3.3. Layer 3: Ephemeral Fulfillment Vault (14-Day TTL)
- **Mechanism:** Physical delivery addresses and recipient contact numbers are stored in an isolated, KMS-encrypted fulfillment table with a database-level TTL:
  ```sql
  CREATE TABLE orchestration.ephemeral_fulfillment (
      destination_reference UUID PRIMARY KEY,
      encrypted_payload BYTEA NOT NULL,
      expires_at TIMESTAMPTZ NOT NULL DEFAULT (clock_timestamp() + interval '14 days')
  );
  ```
- **Automatic Purging:** A scheduled pg_cron or AWS Lambda job automatically executes `DELETE FROM orchestration.ephemeral_fulfillment WHERE expires_at < clock_timestamp()`. After 14 days, the address data is permanently erased.

---

## 4. Comparison: Traditional CRM vs Privacy-Preserving CRM

| Dimension | Legacy Centralized CRM | AEA Privacy-Preserving CRM |
|:---|:---|:---|
| **Storage Location** | Cloud CRM database (Salesforce, HubSpot, custom) | Edge Wallet (on-device) + Ephemeral KMS Vault |
| **Identity Model** | Plaintext Email, Phone, Full Name | Opaque Salted `subject_reference` |
| **Data Retention** | Indefinite (High liability & GDPR audit surface) | 14-Day Ephemeral TTL for physical delivery data |
| **Breach Impact** | Catastrophic PII and customer identity leaks | Safe Harbor: Zero PII stored in operational database |
| **Personalization** | Server-side tracking cookies and cross-site scraping | Intent-driven dynamic adaptation via Adaptive Workspace |

---

## 5. Architectural Recommendations & Next Steps

1. **Adopt as ADR-018 (Proposed):** Formalize this pattern as `ADR-018: Privacy-Preserving Pseudonymous CRM and Edge Wallet History`.
2. **Implement Edge Wallet in Android Companion:** Add local encrypted SQLite/Room or Jetpack Datastore storage for `OrderReceiptEntity` in `clients/mobile/android/`.
3. **Add Database TTL Purge Task:** Schedule `apply_migrations.py` migration `024_ephemeral_fulfillment_ttl.sql` for automated fulfillment address expiration.
