# Privacy-Preserving CRM & Least-Data Customer Intelligence

The Adaptive Experience Architecture (AEA) avoids centralized Personally Identifiable Information (PII) honeypots. Traditional CRMs store customer names, emails, phones, and addresses indefinitely. AEA satisfies operator order overview and customer relationship needs through a **3-Layer Privacy-Preserving CRM Pattern** (ADR-020).

---

## 1. The 3-Layer CRM Pattern

```
┌────────────────────────────────────────────────────────────────────────┐
│                      1. OPERATOR INSIGHTS TIER                         │
│   (Aggregated Intelligence · Behavior Buckets · Order Fulfillment)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Reads Pseudonymous Projections
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             2. PLATFORM PSEUDONYMOUS SUBJECT INTELLIGENCE              │
│       • Opaque Subject Tokens: `subject_reference = HMAC(client_id)`   │
│       • Transaction Aggregates: Order Count, Lifetime Spend Bands      │
│       • Occasion Vector: 70% Birthday (Mother), 30% Anniversary        │
│       • Preferred Channel: `Companion App` vs `Web Browser`            │
└─────────────────▲──────────────────────────────────▲───────────────────┘
                  │                                  │
    Presents Zero-PII Claim          Tokenized Destination Pointer
                  │                                  │
┌─────────────────┴─────────────┐    ┌───────────────┴───────────────────┐
│  3A. CLIENT-SIDE EDGE WALLET  │    │  3B. EPHEMERAL FULFILLMENT VAULT  │
│   (Companion On-Device DB)    │    │      (14-Day Auto-Shredding)      │
├───────────────────────────────┤    ├───────────────────────────────────┤
│ • Full local order receipts   │    │ • Raw delivery street address     │
│ • Favorite recipient records  │    │ • Unlocked ONLY during packing    │
│ • Custom occasion reminders   │    │ • KMS-encrypted, purged post-TTL  │
└───────────────────────────────┘    └───────────────────────────────────┘
```

---

## 2. Core Pillars

1. **Pseudonymous Subject Profiles:** Platform tables represent returning customers via deterministic salted hashes (`sub_9b179aea00e...`). Repeat orders, spend bands (`$50–$100`), and occasion types are tracked without storing names or emails.
2. **Client-Side Edge Wallet (Android Companion):** Detailed transaction history and recipient labels (e.g. "Mom") stay on the user's physical device in platform-backed encrypted storage. One-tap reorders (FR-008) present opaque claims directly.
3. **14-Day Ephemeral Address Shredding:** Physical street addresses and delivery phone numbers exist solely in an isolated KMS-encrypted table with an automated 14-day database-level TTL purge.

---

## 3. Related Decisions & Requirements

- [ADR-020 Privacy-Preserving CRM & Edge Wallet](../06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md)
- [ADR-013 Confirmation-Driven Experience](../06-adr/ADR-013-confirmation-driven-experience.md)
- [NFR-017 Zero-PII / Least-Data Perimeter](../02-business-analysis/requirements.md)
- [FR-008 Thin Reorder Hint](../02-business-analysis/requirements.md)
