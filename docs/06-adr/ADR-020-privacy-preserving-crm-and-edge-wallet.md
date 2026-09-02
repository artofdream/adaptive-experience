# ADR-020 — Privacy-Preserving Pseudonymous CRM & Edge Wallet

Status: Proposed

Date: 2026-09-02

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

## Consequences

- **Positive:** Operators gain full visibility into order frequency, volume trends, and fulfillment status without holding PII.
- **Positive:** Customers enjoy 1-tap reordering and local history on their mobile companion without creating server accounts.
- **Positive:** Satisfies ADR-013, NFR-017, and Safe Harbor privacy compliance by design.
- **Trade-off:** Marketing cannot execute traditional spam email blasts or cross-site surveillance tracking, aligning with Lily's Florist brand trust mission.
