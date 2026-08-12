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

## Next

1. ~~Land CF-038 queue verify MR~~ done (#137 closed; queue verified)
2. ~~Remediate CF-039~~ done (!110 merged; roadmap M5 corrected; #32/#34→M4, #37→M5;
   queue row + finding note verified post-merge on `6184c22`)
3. ~~Decide M3 close vs open Edge T-03 follow-on~~ opened #142 for the Edge
   recommendations/availability/`product.selected` wiring; M3 closes on #142
4. **Next build item:** implement #142 (M3 Edge wiring) before M4, since T-04
   Product Selection depends on a `product.selected` path at the edge
5. Then M4 build: #122 → #33 → #32 → #34
