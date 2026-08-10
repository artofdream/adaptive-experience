# Coherence finding — T-04 missing Colour and Ribbon fields

tags: #aea #coherence
finding_id: CF-008
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-10-wireframe-sample-fidelity.md
supersedes:
issue: "#98"
branch: docs/cf-008-t04-colour-ribbon
merge_request: "!47"

## Claim

The MVP wireframe's T-04 customization panel shows only Flower Type, Size and
Gift Card, dropping the Colour and Ribbon fields present in the source sample.

## Evidence

- Canonical source: `archive/sample-layout-3-with-notes.png` (Step 4: Flower Type, Colour, Size, Ribbon, Gift Card)
- Conflicting or incomplete path: `implementations/florist/wireframes/adaptive-workspace-mvp.svg` (T-04 group)
- Verification command: `python scripts/check_coherence.py`

## Intended fix

Restore Colour and Ribbon to the T-04 field list (five fields, compressed
spacing to fit the tile).

## Boundaries

- Included: two added fields + reflow of the T-04 field list.
- Excluded: other tiles, delivery date/time (relocated to T-05 by design).
- ID impact: none / existing IDs only

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-10 | queued | Intake from wireframe/sample validation |
| 2026-08-10 | in-mr | Colour + Ribbon restored to T-04; MR opened |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-10-wireframe-sample-fidelity | first-seen | Medium |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created
- [x] Dedicated branch created from updated `main`
- [x] Focused fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan
- [ ] MR merged
- [ ] Post-merge verification passed on `main`
