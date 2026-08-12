# Roadmap NFR milestone coverage drift — 2026-08-13 (intake)

tags: #aea #coherence-assessment #intake
status: intake-complete
assessed_ref: fbdd39a
assessed_by: claude

## Scope

Discovered while remediating CF-040 (roadmap M4 NFR coverage). The roadmap NFR
milestone coverage disagrees with the live GitLab NFR milestone assignments on
M5, M6, M7, and Future - a broader class than the M4-scoped CF-040.

## Finding (new)

| ID | Claim | Sev | Decision |
|----|-------|-----|----------|
| CF-041 | Roadmap NFR coverage (M5/M6/M7/Future) disagrees with GitLab NFR milestone assignments; the roadmap lists Future-scope NFRs in MVP milestones | Medium | queued (intake) |

## Full NFR milestone map (GitLab, scope-consistent)

| NFR | Scope | GitLab milestone | Roadmap milestone | Agree? |
|-----|-------|------------------|-------------------|--------|
| 001 Usability | mvp | M2 | M2 | yes |
| 002 Compatibility | mvp | M2 | M2 | yes |
| 003 Availability | mvp | M7 | M7 | yes |
| 004 Performance | mvp | M2 | M2 | yes |
| 005 Transparency | mvp | M2 | M2 | yes |
| 006 Accuracy | mvp | M3 | M3 (+M4 via CF-040) | M3 yes |
| 007 Security | mvp | M5 | (absent from M5) | no |
| 008 Reliability | future | Future | M6 | no |
| 009 Data Integrity | mvp | M3 | M3 | yes |
| 010 Reliability | future | Future | M7 | no |
| 011 Performance | mvp | M6 | M7 | no |
| 012 Security | mvp | M5 | M7 | no |
| 013 Security | mvp | M5 | M5 | yes |
| 014 Scalability | future | Future | Future | yes |
| 015 Maintainability | mvp | M1 | M1 | yes |
| 016 Observability | mvp | M1 | M1 | yes |
| 017 Privacy Security | mvp | M1 | M1 | yes |

## Direction of reconciliation

Canonical scope (MVP/Future) from the workbook is authoritative. GitLab's NFR
milestone assignments respect scope (every Future-scope NFR is in the Future
milestone); the roadmap violates scope (Future NFR-008 in M6, Future NFR-010 in
M7). Therefore GitLab's NFR milestone mapping is correct and the **roadmap NFR
coverage is reconciled to GitLab**. (This does not contradict CF-039, which
reconciled the tracker to the roadmap for FRs where the roadmap was correct; the
principle is to reconcile toward the scope-consistent artifact, which here is
GitLab.)

The MVP-scope NFRs that move earlier than the roadmap implied - NFR-011 (M7 ->
M6) and NFR-012 (M7 -> M5) - are placed per their GitLab work items; M7 keeps
NFR-003 plus the M1-baseline hardening note.

## Intended fix (remediation)

Correct the roadmap coverage column:

- M5: `NFR-013` -> `NFR-007, NFR-012, NFR-013`
- M6: `NFR-008` -> `NFR-011`
- M7: `NFR-003, NFR-010, NFR-011, NFR-012; ...` -> `NFR-003; ...` (keep the
  M1-baseline hardening note)
- Future: `NFR-014` -> `NFR-008, NFR-010, NFR-014`

M4 is handled separately by CF-040 (#145 / !122). No GitLab reassignment and no
workbook/ID change; milestone-coverage prose is not guard-validated.

## Next

1. Remediate CF-041 (one issue/branch/MR editing the roadmap NFR rows).
2. Verify after CF-040 (!122) and CF-041 both merge; the two touch different
   roadmap rows and merge cleanly.
