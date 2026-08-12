# Coherence finding — Roadmap M4/M5 FR coverage vs GitLab milestones

tags: #aea #coherence
finding_id: CF-039
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-12-pre-m4-hygiene-reconciliation.md
supersedes:
issue: "#141"
branch: docs/cf-039-roadmap-milestone-coherence
merge_request: "!110"

## Claim

The canonical roadmap (`docs/07-roadmap/roadmap.md`) and live GitLab milestone
assignments disagree on milestone ownership for FR-013, FR-015, and FR-018, and
roadmap M5 double-lists NFR-014 (which the workbook governs as Future).

## Evidence

- Canonical source: `docs/07-roadmap/roadmap.md`
  - M4 coverage: FR-013, FR-014, FR-015
  - M5 coverage: FR-018, FR-019; NFR-013, NFR-014
- Conflicting tracker (GitLab, verified via `glab api projects/:id/issues/<n>`):
  - FR-013 (#32) -> M5 (roadmap M4)
  - FR-015 (#34) -> M6 (roadmap M4)
  - FR-018 (#37) -> M4 (roadmap M5)
  - FR-014 (#33) -> M4; FR-019 (#38) -> M5; NFR-013 (#55) -> M5 (all match)
  - NFR-014 (#56) -> Future Backlog; roadmap M5 also lists NFR-014 (double-listed)
- Workbook: NFR-014 is Future scope (`scope::future`), so GitLab #56 in Future
  Backlog is correct and the roadmap M5 listing is the error.
- Verification: `python scripts/check_coherence.py` (inventory unaffected; guard
  passes before and after — milestone coverage prose is not guard-validated).

## Intended fix

Roadmap is the canonical planning artifact; GitLab is the tracker. Reconcile the
tracker to the roadmap and correct the one roadmap error:

- Doc (this MR): remove NFR-014 from the roadmap M5 coverage column; it remains
  listed under Future Backlog.
- Tracker hygiene (GitLab, outside the MR): reassign FR-013 (#32) -> M4,
  FR-015 (#34) -> M4, FR-018 (#37) -> M5.

## Boundaries

- Included: roadmap M5 NFR-014 removal; GitLab milestone reassignment of #32,
  #34, #37; this finding note; queue row.
- Excluded: workbook; requirement/story scope; any BG/EP/US/FR/NFR ID change.
- ID impact: none / existing IDs only.

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-12 | queued | Pre-M4 hygiene reconciliation intake |
| 2026-08-12 | investigating | Reproduced live: #32->M5, #34->M6, #37->M4; NFR-014 double-listed |
| 2026-08-12 | in-mr | Issue #141; roadmap M5 NFR-014 removed; GitLab milestones reassigned |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-12-pre-m4-hygiene-reconciliation | first-seen | Queued as CF-039 |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created (#141)
- [x] Dedicated branch created from updated `main`
- [x] Focused fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan
- [ ] MR merged
- [ ] Post-merge verification passed on `main`
