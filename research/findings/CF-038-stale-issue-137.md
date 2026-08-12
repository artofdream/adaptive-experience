# Coherence finding — Stale open GitLab issue #137 (CF-035 duplicate)

tags: #aea #coherence
finding_id: CF-038
status: verified
severity: low
source_assessment: research/assessments/2026-08-12-late-coherence-implementation.md
supersedes:
issue: "#137 (closed as duplicate of #138)"
branch: docs/cf-038-close-duplicate-137
merge_request:

## Claim

GitLab issue #137 (CF-035) remained open though CF-035 was already closed via
#138 / !106.

## Evidence

- #138 / !106 merged; wiki ADR index on `main` lists ADR-011/012
- #137 open with identical CF-035 claim until 2026-08-12 close note

## Intended fix

Close #137 with a duplicate note pointing at #138 / !106; mark queue verified.

## Boundaries

- Included: GitLab issue close; finding note; queue row
- Excluded: wiki content (already fixed)
- ID impact: none

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-12 | queued | Late assessment intake |
| 2026-08-12 | verified | Closed #137; claim already on main via !106 |

## Completion

- [x] Finding reproduced against updated `main`
- [x] GitLab issue closed with verifying note
- [x] Queue updated
- [ ] Queue verify commit merged to `main`
