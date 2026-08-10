# CF-012 — Stale open GitLab issues #79–#85

tags: #aea #coherence-finding
status: queued
finding_id: CF-012
severity: low

## Claim

Issues #79–#85 remain `opened` on GitLab though their claims are falsified or
intentional on `main` (largely superseded by CF-001–CF-005 remediations).

## Evidence

- GitLab issues #79–#85 state: opened
- Counter-evidence on main: CF-001/002/003/004/005 (#86–#93), topic contracts,
  CSV export, README links, intentional advisory lint

## Intended fix

Close each issue with a comment pointing at the verifying MR/issue (or
intentional design note for #84), without opening a docs change MR unless a
claim is still true.
