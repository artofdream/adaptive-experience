# Coherence assessment — 2026-08-11 (full repo)

tags: #aea #coherence-assessment
status: intake-complete
assessed_ref: 623be219472d04ac03866ecf6748b8972003e475
assessed_by: cursor-agent

## Scope

- Paths reviewed: `docs/` (requirements, functional design, TA, topic contracts,
  schemas README, ADR-001…010), `wiki/`, `implementations/florist/wireframes/`,
  `research/adr-candidates/`, `research/coherence-findings-loop.md`,
  `.gitlab-ci.yml`, root README
- Checks executed: `git pull origin/main` @ `623be21`;
  `python scripts/check_coherence.py` (**pass**);
  local SVG/README/ADR/topic-contract cross-read;
  open MR list (none)
- Exclusions: live Figma pixel audit (MCP not run this pass); advisory
  markdownlint; inventing/changing archive FR IDs

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-007 | T-03 recommendation cards in composed MVP SVG omit Available badges (FR-011); README still claims them | Medium | `implementations/florist/wireframes/adaptive-workspace-mvp.svg` T-03; `wireframes/README.md`; drop in `f9e5981` | #97 / !46 |
| CF-009 | T-08 omits Contact Florist and Escalate (Future); README still claims them | Medium | same SVG T-08; `wireframes/README.md`; drop in `f9e5981` | #99 / !48 |
| CF-018 | FR-003 table lists size/personal messages as Future while T-04 MVP includes size + card message | Medium | `requirements.md` FR-003 + Interpretation (ADR-006) note | #104 / !60 |
| CF-013 | MVP T-04 wireframe shows advanced customization fields while FR-003 Future | Medium | SVG T-04 = Arrangement/Size/Card message only | #104 / !60 |
| CF-015 | Gate #106–#108 lack matching ADR files | High | `docs/06-adr/ADR-008`…`010` Accepted on main | #106–#108 / !57–!59 |
| CF-016 | Kafka stub Accepted while broker product-neutral | Medium | `research/adr-candidates/kafka-event-backbone.md` Draft; ADR-007 Accepted | #111 / !62 |
| CF-017 | ADR-007 BFF missing from technical-architecture.md | Medium | TA Core elements + Initial deployment topology | #105 / !61 |
| CF-019 | Wiki ADR index lists only ADR-001…005 | Low | `wiki/architecture-decision-records.md` lists 001–010 | #112 / !63 |
| CF-020 | Topic contracts name Workspace as bus Owner/publisher for six UI-originated topics while ADR-007/009/010 forbid client→broker publish and treat Workspace as projection | Medium | `topic-contracts.md` vs ADR-007, ADR-009, ADR-010 | — |
| CF-021 | Accepted ADR-008 requires machine-readable schemas under `schemas/` (and CI contract checks) before publishers ship; tree has only README that defers files; CI has no schema job | Medium | ADR-008; `schemas/README.md`; `.gitlab-ci.yml` | — |
| CF-022 | `adaptive-workspace-mvp.png` still shows Colour/Ribbon/Gift Card as MVP T-04 (pre–ADR-006 raster) while composed SVG and ADR-006 do not | Medium | `wireframes/adaptive-workspace-mvp.png` vs `.svg` / ADR-006 | residual of CF-013 |
| CF-023 | `research/adr-candidates/README.md` still says candidates must not occupy ADR-006…010 until gates #104–#108; those ADR slots are Accepted | Low | `research/adr-candidates/README.md` vs `docs/06-adr/` | — |
| CF-024 | ADR-009 still says BFF “if introduced by deployment ADRs” though ADR-007 Accepted a separate BFF | Low | ADR-009 Consequences vs ADR-007 Decision | — |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-007 | regression | regressed | Fixed in !46; collateral drop in ADR-006 SVG rewrite `f9e5981` |
| CF-009 | regression | regressed | Fixed in !48; same SVG rewrite |
| CF-013 | resolved | verified | Local SVG T-04 aligned with ADR-006; original claim not reproducible on SVG |
| CF-015 | resolved | verified | Gate ADR-008…010 Accepted on main |
| CF-016 | resolved | verified | Kafka remains Draft; broker product deferred by design under ADR-007 |
| CF-017 | resolved | verified | BFF + topology documented in TA; ADR-007 Accepted |
| CF-018 | resolved (intentional) | verified | Archive FR-003 wording retained; ADR-006 interpretation note documents MVP carve-out |
| CF-019 | resolved | verified | Wiki ADR index lists 001–010; !63 merged |
| CF-020 | new | queued | Publisher/ownership conflict between topic contracts and Accepted ADRs |
| CF-021 | new | queued | ADR-008 Accepted contract vs empty schemas/ + no CI contract job |
| CF-022 | new | queued | Stale PNG contradicts Accepted ADR-006 / current SVG |
| CF-023 | new | queued | Stale research README gate wording |
| CF-024 | new | queued | Stale ADR-009 BFF conditional wording |

## Assessment conclusion

- Coherence guard (ID inventories / chains / CSV): **pass**
- Verdict on published architecture docs (ADR-001…010 + TA after !61–!63):
  **mostly coherent**, with medium publisher/schema/wireframe residuals
- New findings added: **CF-020…CF-024**
- Regressions reopened: **CF-007**, **CF-009**
- Duplicates linked: README Available/Contact claims → evidence under CF-007/CF-009
- Queue reordered: yes (regressed mediums first among active work)
- Next queued/regressed finding: **CF-007**
- Intake only — no issues, branches, or MRs created in this pass
