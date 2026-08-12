# Coherence finding — Roadmap M4 NFR coverage lists non-M4 NFRs

tags: #aea #coherence
finding_id: CF-040
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-12-m4-nfr-coverage-intake.md
supersedes:
issue: "#145"
branch: docs/cf-040-roadmap-m4-nfr
merge_request:

## Claim

The roadmap M4 coverage row lists NFR-006 and NFR-007, but neither is an M4
deliverable: NFR-006 (Accuracy) is the M3 baseline (closed #48, already on the M3
row - double-listed), and NFR-007 (Security) is a GitLab M5 issue (#49). No NFR
issue is assigned to M4 in GitLab.

## Evidence

- `docs/07-roadmap/roadmap.md` M4 row: `FR-013, FR-014, FR-015; NFR-006, NFR-007`.
- GitLab NFR milestone assignments (via `glab issue view`): NFR-006 (#48) -> M3;
  NFR-007 (#49) -> M5; no NFR-US issue is in M4.
- Roadmap M3 row already lists NFR-006, so M4 double-lists it.
- `python scripts/check_coherence.py` passes before and after (milestone-coverage
  prose is not guard-validated).

## Intended fix

Correct the roadmap M4 coverage to its accurate requirement set:

- `FR-013, FR-014, FR-015; NFR-006, NFR-007` -> `FR-013, FR-014, FR-015`.

M4 delivers no new NFR; the M1-M3 NFR baselines continue to apply and are listed
on their own rows.

## Boundaries

- Included: the roadmap M4 coverage cell; issue #145; finding note; queue row.
- Excluded: workbook; requirement/story scope; any BG/EP/US/FR/NFR ID change;
  GitLab milestone reassignment.
- ID impact: none.

## Out of scope (separate finding)

A broader roadmap-vs-GitLab NFR milestone drift was observed on M5 (roadmap lists
NFR-013 only; GitLab has NFR-007/012/013), M6 (roadmap NFR-008, a Future
reliability NFR; GitLab NFR-011), M7, and Future. That is a distinct class needing
an authority decision (reconcile the tracker to the roadmap per CF-039, or the
roadmap to the tracker) and will be intaked separately (candidate CF-041). It is
deliberately not part of this focused fix.

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-12 | queued | M4 NFR coverage intake |
| 2026-08-13 | in-mr | Issue #145; roadmap M4 NFR clause removed; systemic drift flagged for CF-041 |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created (#145)
- [x] Dedicated branch created from updated `main`
- [x] Focused fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan
- [ ] MR merged
- [ ] Post-merge verification passed on `main`
