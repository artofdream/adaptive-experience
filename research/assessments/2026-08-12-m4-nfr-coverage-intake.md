# M4 NFR coverage discrepancy — 2026-08-12 (intake)

tags: #aea #coherence-assessment #intake
status: intake-complete
assessed_ref: e3b8442
assessed_by: claude

## Scope

Pre-M4 coherence check of `docs/07-roadmap/roadmap.md` milestone coverage against
canonical scope and live GitLab milestones. Guards pass (`check_coherence.py`,
`check_topic_schemas.py`); CF ledger otherwise all `verified`.

## Finding (new)

| ID | Claim | Sev | Decision |
|----|-------|-----|----------|
| CF-040 | Roadmap M4 coverage lists NFR-006 and NFR-007, but both are delivered in other milestones per canonical/GitLab | Medium | queued (intake only) |

### CF-040 detail

`docs/07-roadmap/roadmap.md` M4 row: `FR-013, FR-014, FR-015; NFR-006, NFR-007`.

- **NFR-006 (Accuracy)** is an M3 deliverable (roadmap M3 row also lists it) and is
  closed as GitLab #48 under M3. It is **double-listed** on M3 and M4.
- **NFR-007 (Security)** is GitLab milestone **M5** and is **closed**. The roadmap
  places it in M4.

So the roadmap M4 NFR coverage disagrees with the canonical/tracker milestone
placement. Same class as CF-039 (milestone-coverage prose is not guard-validated),
so `check_coherence.py` does not catch it.

## Intended fix (for a later remediation iteration — not this intake)

Reconcile the roadmap M4 NFR coverage to canonical:

- remove NFR-007 from M4 (it is M5 security);
- de-duplicate NFR-006 (it is the M3 accuracy baseline, not an M4 deliverable);
- determine M4's actual NFR coverage from the canonical mapping (may be none, or a
  different NFR) rather than assuming; do not invent NFR IDs.

One finding -> one issue -> one branch -> one MR, per the coherence findings SOP.

## Boundaries

- Included: roadmap M4 NFR coverage prose; this assessment; the CF-040 queue row.
- Excluded: workbook; requirement/story scope; FR/NFR ID changes; M4 build.
- ID impact: none.

## Next

1. Remediate CF-040 (one issue/branch/MR correcting the roadmap M4 NFR coverage).
2. Order/delivery domain design note (separate, M4 build prep).
3. Then M4 build: #33 (FR-014 delivery) -> #32 (FR-013 order) -> #34 (FR-015 status).
