# Coherence finding — Future Backlog mislists FR-007 as CRM

tags: #aea #coherence
finding_id: CF-036
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-12-pm-coherence-implementation.md
supersedes:
issue: #139
branch: docs/cf-036-roadmap-fr-007
merge_request: !107

## Claim

Roadmap Future Backlog lists FR-007 under CRM analytics while FR-007 is MVP
Recommendations (M3).

## Evidence

- Canonical: `docs/02-business-analysis/requirements.md` — FR-007 MVP Recommendations;
  FR-008 Future history recommendations; FR-016/FR-017 Future CRM
- Conflicting: `docs/07-roadmap/roadmap.md` Future row
  `CRM analytics (FR-007, FR-008, FR-016, FR-017)` and coverage includes FR-007
- Correct M3 row already lists FR-007

## Intended fix

Remove FR-007 from Future Backlog description and coverage; cite FR-008 for
history-based recommendations and FR-016/FR-017 for CRM analytics.

## Boundaries

- Included: `docs/07-roadmap/roadmap.md`; finding note; queue row
- Excluded: workbook/archive IDs; wiki roadmap (no FR-007); CF-037
- ID impact: existing IDs only (no renumber)

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-12 | queued | Assessment intake |
| 2026-08-12 | investigating | Reproduced on `origin/main` @ 13b54a3 |
| 2026-08-12 | in-mr | Issue #139; roadmap Future row corrected |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-12-pm-coherence-implementation | first-seen | |

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
