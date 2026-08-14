# CF-043 — ADR candidates mixed with issue design notes

finding_id: CF-043
status: verified
verified_on: origin/main @ 5eec495

## Claim

`research/adr-candidates/` mixed issue design notes with ADR Drafts, inviting
CF-014-style renumber confusion.

## Fix (landed)

Commit `4caa69f` (merged via ADR-013 branch follow-up / main history):

- Moved five issue contracts to `research/design-notes/`
- Split `adr-candidates/README.md` into Active Drafts / Historical / Design notes
- Updated edge README + BFF comment paths
- Retargeted remaining Drafts to ADR-014+

## Verification (2026-08-14)

On `origin/main` @ `5eec495`:

- `research/adr-candidates/` contains only README + 5 Draft/historical files
  (no `edge-` / `m5-` / `m6-` / `order-delivery` contracts)
- `research/design-notes/` holds the five contracts + README
- Edge README points at `research/design-notes/edge-workspace-projection-contract.md`

## Hygiene in this verify MR

- Remove stale “ADR-013 pending merge” wording from candidates README
- Mark CF-043 and CF-044 `verified` in the coherence queue
