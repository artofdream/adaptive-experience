# NFR-007 / NFR-012 Encryption Posture

Status: Accepted (MVP controls)

Requirements:

- **NFR-007** — Customer preference data shall be encrypted and securely stored.
- **NFR-012** — Customer delivery information shall be encrypted during storage
  and transmission.

Traceability: EP-003 → NFR-US-007 → NFR-007; EP-006 → NFR-US-012 → NFR-012.

This note records how the MVP reference foundation satisfies those requirements
without claiming application-level field encryption that the platform does not
implement. It complements
[nfr-013-data-protection.md](nfr-013-data-protection.md) (least-data and
reference-only controls).

## Decision

Satisfy NFR-007 and NFR-012 with **three complementary controls**:

1. **Minimize what is stored** in experience state and domain aggregates
   (opaque references / tokens; no raw preference PII or delivery PII).
2. **Encrypt in transit** on the customer path (TLS at the Adaptive Edge
   gateway).
3. **Encrypt at rest in production** via the PostgreSQL hosting environment
   (volume / disk / provider storage encryption), not via application-managed
   column ciphers in the MVP codebase.

Local Compose and CI may use unencrypted developer volumes. They are not
production evidence for NFR-007 / NFR-012 storage encryption.

## Controls

### 1. Application minimization (what is stored)

| Data class | MVP handling | Evidence |
|---|---|---|
| Preferences / Shared Understanding | Session experience state holds intent facets (occasion, budget, style, …), not raw contact PII | ADR-009; experience-state store |
| Delivery / recipient | Opaque `destination_reference` only; raw name/address rejected | `#33`; `delivery.py`; `test_delivery.py` |
| Payment | Opaque `payment_reference` vault token; raw PAN rejected | `#38`; `nfr-013-data-protection.md` |

Reducing stored sensitive material does **not** replace encryption at rest for
remaining session and reference data; it limits the blast radius if storage is
compromised and keeps broker/audit payloads clean (NFR-017).

### 2. Encryption in transit (NFR-012 transmission)

- Browser traffic terminates TLS at the Edge gateway (`https://…`).
- The BFF is not published on a host port; internal hops stay on the Compose /
  deployment network behind the gateway.
- Production broker paths require authenticated TLS/SASL (ADR-012); local
  plaintext Kafka listeners are non-production only.

Evidence: `edge/README.md`, `edge/docker-compose.yml`, perimeter tests,
`mvp-security-audit.md` transport row.

### 3. Encryption at rest (NFR-007 storage; NFR-012 storage)

- Authoritative persistence for experience state (and module outboxes beside it)
  is PostgreSQL ([ADR-011](../06-adr/ADR-011-experience-state-datastore.md)).
- **Production deployments must enable storage encryption** for the PostgreSQL
  data volume (or equivalent provider disk / TDE offering). Secrets and DB
  credentials are supplied outside the repository.
- The MVP platform does **not** implement application-level envelope encryption
  or column ciphers. Claiming otherwise would be false evidence.

Deployment validation for production profiles (encrypted volumes, TLS/SASL,
secret management) remains part of M7 hardening / reference deploy checks
(e.g. closed `#150` acceptance themes).

## What this ADR/docs set does **not** claim

- No app-managed AES field encryption of preference or delivery columns.
- No assertion that local `platform/docker-compose.yml` Postgres volumes are
  encrypted.
- No substitution of “we only store references” for production disk encryption.

## Verification

| Control | How verified |
|---|---|
| No raw delivery PII in platform | `platform/tests/test_delivery.py`; postgres delivery tests; privacy guard |
| No raw payment PII | `nfr-013-data-protection.md` evidence table |
| TLS on customer path | Edge gateway HTTPS; `edge/tests/test_perimeter.py` |
| At-rest encryption required for production | This note + ADR-011 production access language; deploy checklist / `#150` themes |
| Docs do not overclaim app ciphers | ADR-009 / ADR-011 link here; CF-045 |

## Related

- [ADR-009 Experience-State Ownership](../06-adr/ADR-009-experience-state-ownership.md)
- [ADR-011 Experience-State Datastore](../06-adr/ADR-011-experience-state-datastore.md)
- [NFR-013 Data Protection](nfr-013-data-protection.md)
- [MVP Security Audit](mvp-security-audit.md)
