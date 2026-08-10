# Coherence finding — T-08 omits Contact Florist + Future T-09 escalation

tags: #aea #coherence
finding_id: CF-009
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-10-wireframe-sample-fidelity.md
supersedes:
issue: "#99"
branch: docs/cf-009-t09-escalation
merge_request:

## Claim

The MVP wireframe's T-08 Order Tracking tile provides no direct support action
and no representation of the Future human-escalation affordance, though the
sample shows Chat with Lily / Contact Florist plus an FR-006 "Escalate to Staff"
future item.

## Evidence

- Canonical source: `archive/sample-layout-3-with-notes.png` (Step 7)
- Conflicting or incomplete path: `implementations/florist/wireframes/adaptive-workspace-mvp.svg` (T-08 group)
- Tile / requirement: FR-006 maps to T-09 Support Escalation (Future) — `docs/03-functional-design/functional-design.md`, `docs/02-business-analysis/requirements.md`
- Verification command: `python scripts/check_coherence.py`

## Intended fix

Add a "Contact Florist" action and a dashed, clearly-Future "Escalate (Future)"
affordance (= T-09) to the T-08 tile, placed to avoid overlapping the ASO
overlay. Tile height extended within the 900px canvas.

## Boundaries

- Included: two actions in the T-08 group; T-08 tile height 304 -> 324.
- Excluded: building out the T-09 overlay itself (remains Future); ASO overlay.
- ID impact: none / existing IDs only (references FR-006 / T-09, does not create IDs)

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-10 | queued | Intake from wireframe/sample validation |
| 2026-08-10 | in-mr | Contact Florist + Future T-09 escalate added to T-08; MR opened |

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
