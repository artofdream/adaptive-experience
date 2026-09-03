# ADR-020 — Privacy-Preserving Pseudonymous CRM & Edge Wallet

Status: Accepted — Layer 1 shipped (M12 `crm.py`) with a zero-PII privacy lifecycle (erasure + retention); **Layer 2 (Edge Wallet) implemented** in the Android companion; Layer 3 ephemeral-fulfillment **14-day shredding lifecycle implemented** (KMS-encrypted write path sponsor-gated).

Date: 2026-09-02 (Layer 2 accepted 2026-09-03; privacy lifecycle 2026-09-03)

Related requirements: NFR-017 (zero-PII / least-data perimeter), FR-008 (thin reorder hint), FR-013 (least-data staff orders), ADR-013 (confirmation-driven experience / tokenized references), ADR-018 (mobile session auth)

Related decisions: [ADR-013 Confirmation-Driven Experience](ADR-013-confirmation-driven-experience.md), [ADR-018 Mobile Session & Auth Model](ADR-018-mobile-session-auth.md)

Related roadmap: M12 (CRM Stance / Least-Data Resolution), M19 (Native Mobile Companion), [roadmap.md](../07-roadmap/roadmap.md)

## Context

Canonical AEA architecture strictly enforces the Zero-PII and Least-Data principles (ADR-013 / NFR-017): customer names, raw street addresses, phone numbers, and payment details are never stored in operational platform databases, Kafka event streams, or application loggers. Consequently, M12 (traditional centralized marketing CRM) was parked to prevent constructing a high-liability PII honeypot.

However, business operators and returning customers require:
1. Operational order history overview (volumes, repeat fulfillment rates, delayed status triage).
2. Frictionless repeat purchases under FR-008 (one-tap reorder for Mom's birthday).
3. Customer relationship insights (preferred occasions, gift frequency, and budget bands) to assist customer care without tracking individuals across the web.

## Alternatives Considered

1. **Traditional Centralized CRM Database (Salesforce / PostgreSQL PII store):** Store persistent customer tables with email, phone, and full address history.
   - *Rejected:* Violates ADR-013 and NFR-017; introduces GDPR/CCPA compliance liability and security exposure.
2. **Strict Ephemeral Statelessness (Zero History Retention):** Discard all session and order associations immediately after checkout.
   - *Rejected:* Disables FR-008 reordering, prevents operator fulfillment troubleshooting, and degrades returning customer experience.
3. **3-Layer Privacy-Preserving CRM & Edge Wallet Architecture (Proposed):**
   - **Layer 1 (Platform):** Pseudonymous `subject_reference` hashing and categorical behavior vectors (e.g. occasion distributions, budget bands, frequency tiers).
   - **Layer 2 (Edge Client):** Device-owned local receipt storage in Android Keystore / EncryptedSharedPreferences (Edge Wallet).
   - **Layer 3 (Fulfillment):** Ephemeral 14-day TTL auto-shredding vault for physical courier addresses.

## Decision

Adopt **Alternative 3 (3-Layer Privacy-Preserving CRM & Edge Wallet Architecture)**:

1. **Pseudonymous Subject Identification:** The platform represents returning clients via salted, one-way cryptographic tokens (`subject_reference`). Operational dashboards aggregate lifetime value bands and occasion distributions without recording personal identifiers.
2. **Client-Side Edge Wallet:** The native mobile companion app stores historical transaction receipts, recipient labels (e.g. "Mom"), and card message drafts locally on-device in platform-backed encrypted storage. During FR-008 reorders, the client presents the opaque reference directly.
3. **14-Day Ephemeral Address Shredding:** Plaintext delivery coordinates and phone numbers used for physical fulfillment are locked with KMS encryption and automatically purged after a 14-day post-delivery retention window.

## Implementation status

- **Layer 1 (Platform):** shipped as the M12 zero-PII Engagement CRM
  (`platform/aea_platform/crm.py`, `crm.customer_occasion_memory`, migration
  018) with occasion memory + reminder endpoints. Reminders are **deterministic
  pull signals** computed on read (`GET .../crm/reminders`); proactive push
  delivery (FCM/APNs) is not shipped (see ADR-019). **Capture→read wiring:** the
  platform order path (`_create_order` / checkout in
  `platform/aea_platform/internal_api.py`) now records a zero-PII occasion
  memory (`browser_hash` derived from the durable `recall_id`, `occasion_type`,
  `event_month/day`, `recipient_relation`) whenever a confirmed order carries
  `shared_understanding.occasion` and a delivery date. Capture is best-effort
  and fail-closed — a CRM failure or incomplete intent never blocks order
  creation and only categorical, non-PII fields are stored (NFR-017). The
  workspace projection surfaces a least-data `reminders` facet (occasion,
  `days_until_event`, reminder text, recipient relation) computed from the
  session's own browser hash. Privacy lifecycle (NFR-017): customer erasure via
  `EngagementCrmService.forget` / `DELETE /internal/v1/crm/occasions` (BFF
  `DELETE /api/v1/crm/occasions` opt-out forwards to it), and time-based
  retention via `purge_expired` (default ~13 months since last update);
  operational job `platform/scripts/purge_crm_retention.py`. The previously dark
  pseudonymous **subject profile** (`orchestration.subject_profile`, migrations
  024/026) is now implemented in `PsycopgCrmStore` (`record_crm_order` /
  `get_crm_profile`): a completed order increments `total_orders`, accumulates
  `lifetime_spend_cents`, and recomputes the `lifetime_spend_band` from the
  cumulative running total. Operator insights are exposed least-data at
  `GET /internal/v1/operator/subjects/{ref}` (BFF
  `GET /api/v1/operator/subjects/{ref}`), and subject-profile erasure + retention
  purge (by `last_seen_at`) provide right-to-be-forgotten parity. `FR-016`/
  `FR-017` remain **Future** in the source-of-truth workbook (reference-extension
  delivery).
- **Layer 2 (Edge Wallet):** **sponsor-accepted (2026-09-03) and implemented**
  in the Android companion (`clients/mobile/android`). Device-owned receipts
  are stored in `EncryptedSharedPreferences` under an Android Keystore AES-256
  master key (`EncryptedPrefsWalletStore`). The pure-Kotlin `EdgeWallet` domain
  keeps device-only convenience fields (recipient label, card-message draft,
  occasion month/day) on-device and exposes only an opaque `ReorderReference`
  (`product_id`, `order_reference`) to the platform for FR-008 reorder. Wired
  through `SessionRepository` (write on confirmed checkout; `reorderFromWallet`
  re-selects the opaque product with authoritative NFR-009 inventory
  revalidation). See
  [`research/design-notes/adr-020-layer2-edge-wallet.md`](../../research/design-notes/adr-020-layer2-edge-wallet.md).
- **Layer 3 (Fulfillment):** the ephemeral fulfillment table
  (`orchestration.ephemeral_fulfillment`, migration 024) and the **14-day
  auto-shredding lifecycle** are implemented —
  `PsycopgCrmStore.purge_expired_fulfillment` deletes rows past `expires_at`,
  run by `platform/scripts/purge_crm_retention.py`. The KMS-encrypted write
  path for `encrypted_address` (populating the vault at fulfillment time)
  remains **sponsor-gated** (cloud KMS + budget) and unbuilt.

## Consequences

- **Positive:** Operators gain full visibility into order frequency, volume trends, and fulfillment status without holding PII.
- **Positive:** Customers enjoy 1-tap reordering and local history on their mobile companion without creating server accounts.
- **Positive:** Satisfies ADR-013, NFR-017, and Safe Harbor privacy compliance by design.
- **Trade-off:** Marketing cannot execute traditional spam email blasts or cross-site surveillance tracking, aligning with Lily's Florist brand trust mission.
