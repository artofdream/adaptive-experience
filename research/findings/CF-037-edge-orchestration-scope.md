# Coherence finding — Edge vs Internal Orchestration route scope

tags: #aea #coherence
finding_id: CF-037
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-12-pm-coherence-implementation.md
supersedes:
issue: #140
branch: docs/cf-037-edge-orchestration-scope
merge_request: !108

## Claim

Edge documents and routes commands, workspace, and stream while Internal
Orchestration only implements conversation and Shared Understanding.

## Evidence

- `edge/README.md` listed commands/workspace/stream without distinguishing
  unimplemented Internal resources
- `edge/bff/aea_bff/orchestration.py` called `/internal/.../commands` and
  `/workspace` though `platform/aea_platform/internal_api.py` returns 404 for them
- Stream adapter already returned an empty iterator

## Intended fix

Document wired M2 paths vs perimeter placeholders; fail closed in
`HttpOrchestration` without calling missing internal endpoints; note the same
boundary in `platform/README.md`.

## Boundaries

- Included: edge README, HttpOrchestration stubs, adapter test, platform README note,
  finding note, queue
- Excluded: implementing Internal command/workspace/stream surfaces (delivery work)
- ID impact: none

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-12 | queued | Assessment intake |
| 2026-08-12 | investigating | Reproduced on `origin/main` @ 49d0af6 |
| 2026-08-12 | in-mr | Issue #140; docs + fail-closed adapter |

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
