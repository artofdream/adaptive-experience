# ADR-018 — Mobile Session & Auth Model

Status: Accepted

Date: 2026-08-29

Related requirements: NFR-017 (zero-PII / least-data), ADR-013 (destination
reference, not raw address)

Related decisions: [ADR-017 Native Client Architecture](ADR-017-native-client-architecture.md),
[ADR-013 Confirmation-Driven Experience](ADR-013-confirmation-driven-experience.md)

Related roadmap: M19 — Native Mobile Companion, Android (Reference
Extension), [roadmap.md](../07-roadmap/roadmap.md)

## Context

The web client's session model is already decided and shipped: a
session-based reference, no password, no account required. ADR-013 already
requires a destination *reference* rather than a raw street address, and
NFR-017 already requires least-data / zero-PII handling. ADR-017 (native
client architecture) states the native client is a third presentation of
the same session, but does not say *where* or *how* that session reference
is stored on a device that has no browser cookie jar. Without this ADR, an
implementer could reach for the easiest local storage available
(unencrypted SharedPreferences, plain files) and silently weaken a
guarantee the web client already meets.

## Alternatives

1. **Plain local storage** (unencrypted `SharedPreferences` / a flat file) —
   simplest to implement; fails NFR-017's least-data intent the moment the
   device is compromised or backed up unencrypted.
2. **Require login / account creation for native** — would be a new product
   requirement (no such FR exists) and directly contradicts the web
   client's "session, not password" pattern the CF-054 evidence explicitly
   called out as a thing to *keep*, not replace.
3. **Store the same opaque session reference the web client already uses,
   in platform-backed encrypted storage** (Android Keystore-backed
   EncryptedSharedPreferences or DataStore; iOS Keychain Services, later
   phase) — no new server-side session model, no login, matches NFR-017 and
   ADR-013's own reference-not-raw-value pattern applied to client storage.
4. **Biometric-gated unlock of the stored reference** — an enhancement on
   top of Option 3, not a replacement; deferred as a later, optional
   hardening step, not required for Phase 0/1.

## Decision

Adopt **Option 3**. The native client stores the **same opaque session
reference** the BFF already issues to web clients, using **platform-backed
encrypted storage** — Android Keystore-backed `EncryptedSharedPreferences`
or `DataStore` for the Android phase; iOS Keychain Services when that phase
starts. No password, no account, no login screen — consistent with what
the web client already does and what the 2026-08-27 J1–J4 evidence note
explicitly flagged as worth keeping.

The stored value is a **reference**, never a raw credential, raw address,
or payment detail — the same reference-not-raw-value pattern ADR-013
already establishes for delivery destinations extends here to session
storage generally.

**Option 4 (biometric gate)** is left available as a future enhancement,
not required for the native client to ship. It is out of scope for Phase 0
and Phase 1.

## Rationale

Option 3 is the only alternative that requires zero new server-side
session infrastructure (the BFF's existing session issuance is unchanged),
introduces no new product requirement (no login FR is created or implied),
and satisfies NFR-017 using platform-native primitives that already exist
for exactly this purpose (Android Keystore, iOS Keychain) rather than
inventing custom encryption. Option 1 is rejected as a regression from the
web client's existing guarantee. Option 2 is rejected as unscoped product
change with no requirement backing it.

## Consequences

- No BFF/session-issuance code changes — the native client is simply a new
  consumer of the session reference the web client already receives.
- `SessionStore` (Android) becomes a Phase 0 implementation dependency —
  see the M19 Phase 0 scaffold issue. This ADR does not implement it.
- Session reference rotation/expiry policy is whatever the BFF already
  enforces today — this ADR does not change server-side session lifetime.
- If a future ADR introduces biometric unlock or a native-only
  authentication enhancement, it must not weaken the "no password required"
  guarantee for a customer who declines biometrics — a fallback path is
  required, not specified here.
- Crash reports (Firebase Crashlytics, per the M19 CI/Firebase issue) must
  not capture the session reference value itself — device/stack traces
  only, consistent with NFR-017. Flagged here as a constraint on that
  separate implementation, not implemented by this ADR.
