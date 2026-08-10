# Coherence finding — T-03 recommendations missing Available badge

tags: #aea #coherence
finding_id: CF-007
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-10-wireframe-sample-fidelity.md
supersedes:
issue: "#97"
branch: docs/cf-007-t03-availability-badge
merge_request:

## Claim

The MVP wireframe's T-03 Curated Recommendations cards render no availability
status, though the source sample shows an "Available" badge on both products.

## Evidence

- Canonical source: `archive/sample-layout-3-with-notes.png` (Step 3, both cards)
- Conflicting or incomplete path: `implementations/florist/wireframes/adaptive-workspace-mvp.svg` (T-03 group)
- Requirement: FR-011 real-time inventory availability (`docs/02-business-analysis/requirements.md`)
- Verification command: `python scripts/check_coherence.py`

## Intended fix

Add a grayscale "Available" pill to each T-03 product card.

## Boundaries

- Included: two status badges in the T-03 group.
- Excluded: colour, other tiles, currency values.
- ID impact: none / existing IDs only

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-10 | queued | Intake from wireframe/sample validation |
| 2026-08-10 | in-mr | Badges added to T-03 cards; MR opened |

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
