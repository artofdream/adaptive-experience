# CF-045 — NFR-007/012 encryption-at-rest without evidenced posture

finding_id: CF-045
status: in-mr
issue: "#160"

## Claim

NFR-007 and NFR-012 require encryption of preference / delivery data. ADR-009
and ADR-011 cited those NFRs beside reference/token storage, but the platform
had no documented encryption-at-rest evidence (no app ciphers; local Postgres
volumes unencrypted), leaving the requirements under-specified.

## Fix

Document the Accepted MVP posture in
`docs/04-technical-architecture/nfr-007-012-encryption.md`:

1. Minimize stored sensitive fields (opaque references).
2. TLS in transit (Edge gateway).
3. Production PostgreSQL storage encryption at rest (deployment control).

Clarify that application-level field encryption is out of MVP scope, and that
local/CI volumes are not production evidence. Cross-link from ADR-009,
ADR-011, `mvp-security-audit.md`, and `platform/README.md`.

## Verification

- New note exists and states the three controls + non-claims.
- ADR-009 / ADR-011 no longer imply unimplemented app ciphers.
- Platform README states local Compose volumes are unencrypted.
