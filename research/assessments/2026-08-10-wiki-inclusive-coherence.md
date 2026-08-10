# Coherence assessment — 2026-08-10 (wiki-inclusive)

tags: #aea #coherence-assessment
status: intake-complete
assessed_ref: 660db1e1090cc4d3dcc2ba787c63982e9e80eb5f
assessed_by: cursor-agent

## Scope

- Paths reviewed: `docs/`, `implementations/florist/`, `wiki/`, `README.md`,
  `research/coherence-findings-loop.md`, `.gitlab-ci.yml`, live GitLab wiki
- Checks executed: `python scripts/check_coherence.py` (pass);
  `glab api projects/:id/wikis` + per-slug bodies; MR !50 / issue #101 state
- Exclusions: pure advisory lint risk unless asked (CF-005 accepted)

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-010 | GitLab wiki pages are title stubs with no body synced from canonical docs | Medium | Live wiki bodies 449–1399 chars; `wiki/` on main; !50 merged | #101 / !50 |
| CF-011 | Wiki florist page says “reference implementation” while repo naming uses “reference design” | Low | `wiki/florist-reference-design.md` L3; `README.md` naming | — |
| CF-012 | GitLab issues #79–#85 remain open though claims are fixed or intentional on main | Low | GitLab issues API; CF-001–005 / #86–#93 | #79–#85 |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-010 | resolved | verified | !50 merged @ 660db1e; #101 closed; live wiki populated; `wiki/` on main |
| CF-011 | new | queued | Fresh wording slip on wiki florist page vs README “reference design” |
| CF-012 | new | queued | Process hygiene; superseded/intentional issues still open |
| CF-005 lint allow_failure | rejected (as new) | — | Already accepted under CF-005; risk only |
| Architecture FR 8/23 | rejected (as new) | — | Intentional criteria already documented |
| FR-015/023 overlap | rejected (as new) | — | Disambiguation already in requirements.md |

## Assessment conclusion

- New findings added: CF-011, CF-012
- Regressions reopened: none
- Duplicates linked: none
- Queue reordered: yes (queued lows after verified trail)
- Next queued finding: CF-011
