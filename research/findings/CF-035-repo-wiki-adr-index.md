# Coherence finding — Repo wiki ADR index omits ADR-011/012

tags: #aea #coherence
finding_id: CF-035
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-12-pm-coherence-implementation.md
supersedes: CF-030 (live wiki only)
issue: #138
branch: docs/cf-035-wiki-adr-index
merge_request:

## Claim

`wiki/architecture-decision-records.md` in the repository still omits Accepted
ADR-011/012 and retains obsolete broker-deferred wording after CF-030 corrected
only the live GitLab wiki.

## Evidence

- Canonical source: `docs/06-adr/ADR-011-experience-state-datastore.md`,
  `docs/06-adr/ADR-012-external-message-broker.md` (Status: Accepted)
- Conflicting path: `wiki/architecture-decision-records.md` on `main` lists
  ADR-001…010 and says broker product selection remains deferred
- Live wiki (CF-030 / #132 / Wiki c8a1af4): already lists ADR-011/012 with
  Accepted PostgreSQL/Kafka wording
- Verification: compared repo file to
  `glab api projects/:id/wikis/architecture-decision-records`

## Intended fix

Replace the repo wiki ADR index content so it matches the live wiki index
(ADR-001…012; Accepted PostgreSQL/Kafka; no deferred/draft prose).

## Boundaries

- Included: `wiki/architecture-decision-records.md`; finding note; queue row
- Excluded: live wiki re-edit (already correct); ADR body files; CF-036/037
- ID impact: none

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-12 | queued | Assessment intake |
| 2026-08-12 | investigating | Reproduced against `origin/main` @ e267815 |
| 2026-08-12 | in-mr | Issue #138; sync repo wiki to live wiki content |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-12-pm-coherence-implementation | first-seen | Source lag after CF-030 live-wiki verify |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created
- [x] Dedicated branch created from updated `main`
- [ ] Focused fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan
- [ ] MR merged
- [ ] Post-merge verification passed on `main`
