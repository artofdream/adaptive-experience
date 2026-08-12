# Pre-M4 reconciliation gaps — 2026-08-12

tags: #aea #coherence-assessment #pre-m4
status: intake-complete
assessed_ref: a13388c
assessed_by: cursor-agent

## Hygiene completed

- Closed duplicate GitLab issue **#137** (CF-038) with note → #138 / !106
- Dropped obsolete stash `wip: evening coherence intake`
- CF-037 marked verified after !108 merge

## Reconciliation gaps before M4

| ID | Gap | Sev | Decision |
|----|-----|-----|----------|
| CF-039 | Roadmap M4/M5 FR placement disagrees with GitLab milestones | Medium | verified (!110 merged; queue + finding note closed) |
| #142 | M3 group milestone still **active** with 0 open M3 issues while Edge T-03/recommendations/selection remain unwired | Medium | ticketed 2026-08-12 as #142 (`scope::mvp`, `type::chore`, M3); implementation open |
| #144 | Edge advertises `workspace`/`stream`/`commands` routes returning `orchestration_unavailable` (CF-037 gray zone); no reactive substrate for cross-tile async progression | Medium | ticketed 2026-08-12 as #144 (`scope::mvp`, `type::chore`, **M4 entry point**); `/commands` deferred by decision; implementation open |
| #143 | Orphaned `orchestration.apply_experience_mutation` SQL superseded by `apply_experience_patch` (mig 004), never dropped; a legacy test still pins it | Low | ticketed 2026-08-12 as #143 (`scope::mvp`, `type::chore`, **M7**); implementation open |
| — | Untracked local assessments / activity report / artifacts not on `main` | Low | promote via hygiene MR or leave local |

### CF-039 detail

Canonical roadmap (`docs/07-roadmap/roadmap.md`):

| Milestone | Roadmap coverage |
|-----------|------------------|
| M4 | FR-013, FR-014, FR-015; NFR-006, NFR-007 |
| M5 | FR-018, FR-019; NFR-013, NFR-014 |

GitLab open assignments:

| Issue | Title | GitLab milestone |
|-------|-------|------------------|
| #122 | T-04 card-message contract | M4 |
| #33 | FR-014 | M4 |
| #37 | FR-018 | **M4** (roadmap: M5) |
| #32 | FR-013 | **M5** (roadmap: M4) |
| #34 | FR-015 | **M6** (roadmap: M4) |
| #38 | FR-019 | M5 |
| #55 | NFR-013 | M5 |

Also: roadmap M5 lists **NFR-014** while Future Backlog also lists NFR-014
(NFR-014 is Future Scalability in requirements).

### External assessment cross-check (source of #143 / #144)

`artifacts/AEA-repo-assessment.pdf` (Rev 2, 2026-08-12) independently confirmed
the coherence model as strong and CI-enforced, and flagged **two open gaps**,
cross-checked against current code and reconciled here:

- **Platform/edge capability gap** — `inventory.py`/`recommendation.py` built and
  unit-tested but not exposed via `internal_api.py` or the BFF. Already owned by
  **#142** (M3). The same paragraph notes the BFF `workspace`/`stream`/`commands`
  stubs (CF-037); split into **#144** (workspace + SSE stream → M4 entry point)
  with `/commands` deferred (dedicated endpoints suffice; de-advertise until a
  command-envelope standard is chosen).
- **Orphaned SQL** — `apply_experience_mutation` (mig 001) superseded by
  `apply_experience_patch` (mig 004), never dropped, no application caller, but
  `platform/tests/test_postgres_integration.py:57` still pins it. Now **#143**
  (M7); scope includes migrating the pinning test.

Neither gap touches the requirements model, so `check_coherence.py` is
unaffected; both are implementation-hygiene / delivery items, not CF findings.

## Next

1. ~~Land CF-038 queue verify MR~~ done (#137 closed; queue verified)
2. ~~Remediate CF-039~~ done (!110 merged; roadmap M5 corrected; #32/#34→M4, #37→M5;
   queue row + finding note verified post-merge on `6184c22`)
3. ~~Decide M3 close vs open Edge T-03 follow-on~~ opened #142 for the Edge
   recommendations/availability/`product.selected` wiring; M3 closes on #142
4. **Next build item:** #144 (M4 reactive edge substrate — workspace projection
   plus SSE stream) as the M4 entry point, then #142 (M3 Edge recs/selection).
   Rationale: M4 is the first cross-tile async fan-out (select → pricing/delivery
   react), so the reactive substrate precedes the FR tiles; `/commands` deferred.
5. Then M4 build: #122 → #33 → #32 → #34
6. M7 hardening backlog now includes #143 (drop orphaned SQL + migrate its test)
