# CF-012 — Stale open GitLab issues #79–#85

tags: #aea #coherence-finding
status: verified
finding_id: CF-012
severity: low
issue: #103
mr: !52
branch: docs/cf-012-close-stale-issues
closed_issues: "#79 #80 #81 #82 #83 #84 #85"
verified_on_main: 8537084

## Claim

Issues #79–#85 remain `opened` on GitLab though their claims are falsified or
intentional on `main` (largely superseded by CF-001–CF-005 remediations).

## Evidence

- GitLab issues #79–#85 were open at intake
- Closed 2026-08-10 with verifying notes pointing at CF-001–CF-005 / CF-011

## Closure map

| Issue | Disposition |
|-------|-------------|
| #79 | Closed → CF-001 / #86 / !32 |
| #80 | Closed → CF-003 / #88 / !34 |
| #81 | Closed → payment outcomes on main |
| #82 | Closed → README + CF-011 / #102 / !51 |
| #83 | Closed → CF-002 / #87 / !33 |
| #84 | Closed → intentional CF-005 / #93 / !39 |
| #85 | Closed → CF-004 / #92 / !38 |

## Intended fix

Close each issue with a comment pointing at the verifying MR/issue (or
intentional design note for #84), without opening a docs change MR unless a
claim is still true. Queue update only.
