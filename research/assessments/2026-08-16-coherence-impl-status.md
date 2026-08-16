# Coherence + implementation status — 2026-08-16

tags: #aea #coherence-assessment #implementation-status
status: intake
assessed_ref: origin/main d1debab
assessed_by: aea-project-manager
walked_at: 2026-08-16T08:06 Europe/Paris

## Scope

- Paths reviewed: workbook + `docs/02-business-analysis/requirements.md`,
  `docs/07-roadmap/roadmap.md` on `origin/main`,
  `implementations/florist/requirements/traceability-matrix.md`,
  `research/coherence-findings-loop.md`, GitLab issues/MRs/group milestones
- Checks executed: `git fetch origin`; `python scripts/check_coherence.py`
  (pass); `glab issue list` / `glab mr list`; group milestones API
- Exclusions: production SLO evidence; AWS (parked); live wiki body sync;
  remediating CF-047 in this pass (intake only; do not mix into !194)

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-047 | Group milestone *descriptions* still list pre-CF-041 coverage (M5 NFR-014, M6 NFR-008, M7 NFR-010; Future still names FR-003 type/colour/ribbon as undelivered) and UX alignment still says current #154 / #148 | Medium | GitLab group milestones M4–M7, Future Backlog, UX alignment vs `docs/07-roadmap/roadmap.md` @ d1debab; CF-041 explicitly excluded GitLab description edits | — (new) |

Not a regression of CF-041 (that fix was roadmap-only) or CF-029 (verbatim M2 copy). Issue *assignments* already match the published roadmap.

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-047 | new | queued | Distinct from CF-041 (descriptions vs issue assignments) |
| CF-001…046 | still verified | verified | No reproduced regression on `origin/main` |

## Assessment conclusion

- New findings added: CF-047
- Regressions reopened: none
- Duplicates linked: none
- Queue reordered: no (only one queued row)
- Next queued finding: **CF-047**
- Do not remediate on `feat/fr-008-session-prior-order-hint`

## Implementation coverage (origin/main d1debab)

M0–M7 group milestones are **closed**. Open `scope::mvp` issues: **0**.

Open Future *stories*: #27 FR-008, #35 FR-016, #36 FR-017. Epics #13–#19 remain
open as containers. In-flight child: #190 / !194 (session prior-order hint;
not on `main` yet).

Thin Future already delivered (issues closed, scope stays Future): FR-006 #25,
FR-010 #29, FR-012 #31, NFR-014 pin #56. NFR-008 #50 is closed with no
quality-monitoring path; NFR-010 #52 is closed and used by the FR-012 thin
path. Neither is claimed as fully delivered in the workbook.

Live shop smoke 16 Aug (d1debab): T-01–T-07 pass, including checkout 202.
