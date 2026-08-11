# Coherence assessment — 2026-08-11 (repo + GitLab ecosystem)

tags: #aea #coherence-assessment
status: intake-complete
assessed_ref: cf9f8945e427470147dd7bcc778ae0ae4b74e1e2
assessed_by: cursor-agent

## Scope

- Paths reviewed: `docs/`, `implementations/florist/`, `wiki/`, `figma/`,
  `research/coherence-findings-loop.md`, `.gitlab-ci.yml`
- Checks executed: `python scripts/check_coherence.py` (pass);
  `glab mr list` / `glab issue list`; live wiki bodies; Figma page list via MCP
- Exclusions: advisory lint allow_failure (CF-005); intentional journey-step
  presentation slices (`STRUCTURE.md`)

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-013 | MVP T-04 wireframe/Figma surfaces Flower Type/Colour/Ribbon while FR-003 advanced customization is Future and functional design says MVP is basic options + card message | Medium | `adaptive-workspace-mvp.svg`; `figma/README.md`; `docs/03-functional-design/functional-design.md` T-04; `docs/02-business-analysis/requirements.md` FR-003; `docs/07-roadmap/roadmap.md` | #104 (ADR-006) |
| CF-001–012 | Prior remediations | — | Queue all verified | !32–!52 |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-013 | new | queued | Wireframe fidelity vs published MVP/Future scope; ADR-006 (#104) already open |
| Journey-step SVG fidelity | rejected | — | Documented as presentation slices in `STRUCTURE.md` |
| Empty Figma planned pages | rejected | — | Named stub/planned pages with zero children still match inventory intent |
| CF-005 lint allow_failure | rejected (as new) | — | Already accepted |
| CF-010–012 | still resolved | verified | Wiki populated; naming fixed; #79–#85 closed; !55 Figma docs merged |

## GitLab ecosystem snapshot

- Open MRs: **0**
- Open issues: requirement/epic backlog + ADR gate **#104–#108**
- Wiki: **11** populated pages
- Main pipeline: coherence-guard green; advisory lint may fail with allow_failure

## Assessment conclusion

- New findings added: CF-013
- Regressions reopened: none
- Duplicates linked: none
- Queue reordered: yes (CF-013 medium first among queued)
- Next queued finding: CF-013
