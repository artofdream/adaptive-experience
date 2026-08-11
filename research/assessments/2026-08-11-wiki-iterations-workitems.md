# Coherence assessment — 2026-08-11 (wiki · iterations · work items)

tags: #aea #coherence-assessment
status: intake-complete
assessed_ref: 843ed310210e91aa0023d928aa172afd85b5b4df
assessed_by: cursor-agent

## Scope

- Paths: `docs/` (ADRs, TA, topic contracts, schemas), `wiki/`,
  `implementations/florist/wireframes/`, `research/coherence-findings-loop.md`,
  `research/adr-candidates/`
- Checks: `python scripts/check_coherence.py` (**pass**);
  `python scripts/check_topic_schemas.py` (**pass**, 21 schemas);
  GitLab wiki API (11 pages); open/closed issues; group milestones + iterations;
  PNG visual check vs SVG
- Exclusions: live Figma MCP re-audit; advisory markdownlint; inventing FR IDs

Assessed SHA: `843ed31` on `origin/main`.

## Ecosystem snapshot

| Area | State |
|------|--------|
| Coherence / topic-schema guards | Pass |
| CF queue CF-001…024 | All **verified**; no open MRs |
| Wiki pages | 11 published (home … source-of-truth) |
| Issues | 107 total · 41 open · 66 closed |
| Open CF work items | **#109** only (stale vs closed #110) |
| Open MRs | None |
| Active milestones | M0–M7 + Future Backlog (9) |
| Iterations | 8 (seq 1 current/closed-ish state=2: 2026-08-09–08-22; seq 2–8 upcoming) |
| Backlog open | ~40 requirement/story/NFR/epic issues (intentional delivery backlog) |

## Findings

| Finding ID | Claim | Severity | Evidence | Existing issue / MR |
|------------|-------|----------|----------|---------------------|
| CF-025 | `adaptive-workspace-mvp.png` omits T-03 Available badges and T-08 Contact Florist / Escalate (Future) present in SVG after CF-007/009 | Medium | SVG L63–72, L146–149 vs PNG; README fidelity claim | residual of #117 / !68 |
| CF-026 | ADR-010 still says Edge/BFF APIs “if present” though ADR-007 Accepted a separate BFF | Low | `ADR-010-command-event-boundaries.md` ~L75 vs ADR-007; ADR-009 already fixed (CF-024) | — |
| CF-027 | Wiki ADR page still says “ADR-007 lands with CF-017 / !61” though ADR-007 is Accepted on main | Low | `wiki/architecture-decision-records.md` + live wiki API content | related CF-019 |
| CF-028 | GitLab issue #109 (CF-014 quarantine) remains **open** while CF-014 was closed via #110 / !56 | Low | `glab issue view 109` open vs #110 closed; queue CF-014 verified | #109 vs #110 |
| CF-029 | Group milestones M3–M7 and Future Backlog reuse the M2 description verbatim; M1 description empty | Medium | `groups/artof-group/milestones` — MILESTONE_DESC_CLONES_OF_M2 | — |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-001…024 | resolved | verified | Prior remediations on main; !73 queue verify merged |
| CF-025 | new | queued | PNG not re-rendered after SVG CF-007/009 |
| CF-026 | new | queued | Sister wording gap to CF-024 on ADR-010 |
| CF-027 | new | queued | Wiki prose lag after CF-019 table fix |
| CF-028 | new | queued | Duplicate CF-014 issue left open (work-item hygiene) |
| CF-029 | new | queued | Milestone copy-paste undermines iteration/milestone planning clarity |

## Assessment conclusion

- Verdict: **architecture docs coherent** (guards green; ADR-001…010 Accepted;
  schemas present; topic publishers aligned). Residuals are **artifact fidelity**,
  **wiki prose**, and **GitLab planning metadata**.
- New findings added: **CF-025…CF-029**
- Next queued finding: **CF-025** (then CF-029, then CF-026…028)
- Intake only — no issues/branches/MRs created in this pass
