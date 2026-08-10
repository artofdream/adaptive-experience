# Coherence assessment — 2026-08-10

tags: #aea #coherence-assessment
status: intake
assessed_ref: ef98c1d
assessed_by: Claude (wireframe vs sample validation)

## Scope

- Paths reviewed:
  - `implementations/florist/wireframes/adaptive-workspace-mvp.svg`
  - `implementations/florist/wireframes/STRUCTURE.md`, `README.md`
  - `archive/sample-layout-3-with-notes.png` (annotated source with FR/NFR tags)
- Checks executed: visual field-by-field comparison of the MVP wireframe tiles
  (T-01…T-08) against the seven-step sample journey and its requirement notes.
- Exclusions or limitations: non-visual NFRs (e.g. NFR-012 encryption) are not
  representable in a wireframe and are out of scope. The 7-screen → single
  adaptive-workspace consolidation is intentional (documented in `STRUCTURE.md`)
  and is not a finding.

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-007 | T-03 recommendation cards omit the "Available" badge the sample shows (FR-011 inventory availability). | Medium | sample-layout-3-with-notes.png (Step 3); adaptive-workspace-mvp.svg (T-03) | #97 |
| CF-008 | T-04 customization panel drops the Colour and Ribbon fields present in the sample. | Medium | sample-layout-3-with-notes.png (Step 4); adaptive-workspace-mvp.svg (T-04) | #98 |
| CF-009 | T-08 tracking omits Contact Florist and any Future T-09 escalation (FR-006) affordance. | Medium | sample-layout-3-with-notes.png (Step 7); adaptive-workspace-mvp.svg (T-08) | #99 |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-007 | new | in-mr | No equivalent prior CF/issue; distinct T-03 fidelity gap. |
| CF-008 | new | in-mr | No equivalent prior CF/issue; distinct T-04 fidelity gap. |
| CF-009 | new | in-mr | No equivalent prior CF/issue; distinct T-08/T-09 gap. |

## Assessment conclusion

- New findings added: CF-007, CF-008, CF-009
- Regressions reopened: none
- Duplicates linked: none
- Queue reordered: no (all Medium; appended in discovery order)
- Next queued finding: CF-007

## Not findings (documented / intentional)

- Generic vs dated delivery slots and substituted currency line items in T-05/T-06
  are low-severity presentation choices; the sample itself is internally
  inconsistent (`sample-layout-3.png` shows Total $1337.50 vs $137.50 annotated),
  so no authoritative value exists to reconcile against. Left out of the queue.
