# Coherence finding — Roadmap NFR coverage disagrees with GitLab (M5/M6/M7/Future)

tags: #aea #coherence
finding_id: CF-041
status: verified
severity: medium
source_assessment: research/assessments/2026-08-13-nfr-milestone-coverage-intake.md
supersedes:
issue: "#146"
branch: docs/cf-041-roadmap-nfr-coverage
merge_request: "!123"

## Claim

The roadmap NFR milestone coverage disagrees with the live GitLab NFR milestone
assignments on M5, M6, M7, and Future. The roadmap lists Future-scope NFRs inside
MVP milestones (NFR-008 in M6, NFR-010 in M7) and misplaces MVP NFRs (M5 omits
NFR-007/012; NFR-011 in M7 though tracked in M6).

## Evidence

- `docs/07-roadmap/roadmap.md` rows vs `glab issue view` milestones:
  - M5 roadmap `NFR-013`; GitLab M5 = NFR-007 (#49), NFR-012 (#54), NFR-013 (#55).
  - M6 roadmap `NFR-008`; GitLab: NFR-008 (#50) is Future, M6 = NFR-011 (#53).
  - M7 roadmap `NFR-003, NFR-010, NFR-011, NFR-012`; GitLab: 003 (#45) M7, 010
    (#52) Future, 011 (#53) M6, 012 (#54) M5.
  - Future roadmap `NFR-014`; GitLab Future = NFR-008, NFR-010, NFR-014.
- `python scripts/check_coherence.py` passes before and after (milestone-coverage
  prose is not guard-validated).

## Direction

Canonical scope (MVP/Future) is authoritative. GitLab NFR assignments respect
scope (all Future-scope NFRs are in Future); the roadmap violates it. So the
roadmap NFR coverage is reconciled to GitLab.

## Fix

- M5: `NFR-013` -> `NFR-007, NFR-012, NFR-013`.
- M6: `NFR-008` -> `NFR-011`.
- M7: `NFR-003, NFR-010, NFR-011, NFR-012; ...` -> `NFR-003; ...` (M1-baseline
  hardening note kept).
- Future: `NFR-014` -> `NFR-008, NFR-010, NFR-014`.

## Boundaries

- Included: roadmap M5/M6/M7/Future NFR coverage cells; issue #146; finding note;
  queue row; source assessment.
- Excluded: roadmap M4 (CF-040 / #145 / !122); workbook; GitLab reassignment; any
  ID change.
- ID impact: none.

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-13 | queued | Intake (2026-08-13-nfr-milestone-coverage-intake) |
| 2026-08-13 | in-mr | Issue #146; roadmap M5/M6/M7/Future NFR rows reconciled to GitLab |
| 2026-08-13 | verified | !123 merged (main d6f3767); M5/M6/M7/Future NFR rows correct on `main`; `check_coherence.py` passes |

## Completion

- [x] Finding reproduced against updated `main`
- [x] GitLab issue created (#146)
- [x] Dedicated branch created from updated `main`
- [x] Focused fix committed and pushed
- [x] Relevant checks passed
- [x] MR includes `Closes #N`, summary, and test plan
- [x] MR merged
- [x] Post-merge verification passed on `main`
