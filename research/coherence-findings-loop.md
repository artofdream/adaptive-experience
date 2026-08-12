# Coherence Findings Loop

This is the durable queue for ingesting assessments and iterating coherence
findings through the Claude–Obsidian workflow. Intake may reconcile every
finding in one assessment; remediation processes exactly one `queued` or
`regressed` finding per iteration.
Canonical changes still follow the coherence findings SOP: one issue, one
branch, one focused fix, and one linked merge request.

## Queue

Order is severity first, then dependency. Update status in place; do not remove
completed rows because the queue is also the audit trail.

| Order | ID | Finding | Severity | Status | First seen | Last seen | Issue / MR |
|-------|----|---------|----------|--------|------------|-----------|------------|
| 1 | CF-001 | Validate complete BG→EP→US→FR/NFR mappings and scope, not only ID inventories | Medium | verified | 2026-08-10 | 2026-08-10 | #86 / !32 |
| 2 | CF-002 | Generate and verify the canonical CSV export against the workbook | Medium | verified | 2026-08-10 | 2026-08-10 | #87 / !33 |
| 3 | CF-003 | Add explicit topic schema versions and machine-readable contracts | Medium | verified | 2026-08-10 | 2026-08-10 | #88 / !34 |
| 4 | CF-004 | Restore root README repository-area links lost during merge resolution | Low | verified | 2026-08-10 | 2026-08-10 | #92 / !38 |
| 5 | CF-005 | Correct stale CI and coherence-guard descriptions | Low | verified | 2026-08-10 | 2026-08-10 | #93 / !39 |
| 6 | CF-006 | Add a full post-merge documentation verification path | Low | verified | 2026-08-10 | 2026-08-10 | #95 / !41 |
| 7 | CF-007 | T-03 recommendation cards omit the Available badge (FR-011) | Medium | verified | 2026-08-10 | 2026-08-11 | #97 / !46 · #113 / !64 |
| 8 | CF-008 | T-04 customization panel drops Colour and Ribbon fields | Medium | verified | 2026-08-10 | 2026-08-10 | #98 / !47 |
| 9 | CF-009 | T-08 tracking omits Contact Florist and Future T-09 escalation (FR-006) | Medium | verified | 2026-08-10 | 2026-08-11 | #99 / !48 · #114 / !65 |
| 10 | CF-010 | GitLab wiki pages are title stubs with no body synced from canonical docs | Medium | verified | 2026-08-10 | 2026-08-10 | #101 / !50 |
| 11 | CF-011 | Wiki florist page says “reference implementation” while repo naming uses “reference design” | Low | verified | 2026-08-10 | 2026-08-10 | #102 / !51 |
| 12 | CF-012 | GitLab issues #79–#85 remain open though claims are fixed or intentional on main | Low | verified | 2026-08-10 | 2026-08-10 | #103 / !52 |
| 13 | CF-014 | Misnumbered Accepted ADR stubs (files ADR-008…012 titled ADR-006…010) collide with Proposed ADR-006/007 and gate issues | High | verified | 2026-08-11 | 2026-08-11 | #110 / !56 |
| 14 | CF-015 | Gate issues #106–#108 lack matching ADR files; slots hold unrelated tech stubs | High | verified | 2026-08-11 | 2026-08-11 | #106 / !57 · #107 / !58 · #108 / !59 |
| 15 | CF-013 | MVP T-04 wireframe/Figma shows advanced customization fields while FR-003 remains Future | Medium | verified | 2026-08-11 | 2026-08-11 | #104 / !60 |
| 16 | CF-016 | Kafka stub Accepted while Proposed ADR-007 / TA leave broker product-neutral | Medium | verified | 2026-08-11 | 2026-08-11 | #111 / !62 |
| 17 | CF-017 | Proposed ADR-007 introduces a BFF not listed in technical-architecture.md | Medium | verified | 2026-08-11 | 2026-08-11 | #105 / !61 |
| 18 | CF-018 | FR-003/roadmap Future text lists size and personal messages as Future while T-04 MVP treats catalog size + card message as MVP | Medium | verified | 2026-08-11 | 2026-08-11 | #104 / !60 |
| 19 | CF-019 | Wiki ADR index still lists only ADR-001…005 | Low | verified | 2026-08-11 | 2026-08-11 | #112 / !63 |
| 20 | CF-020 | Topic contracts name Workspace as bus publisher for UI-originated topics while ADR-007/009/010 require BFF/Orchestration edges and forbid client→broker publish | Medium | verified | 2026-08-11 | 2026-08-11 | #115 / !66 |
| 21 | CF-021 | ADR-008 requires schemas under schemas/ plus CI contract checks before publishers ship; only schemas/README exists and CI has no schema job | Medium | verified | 2026-08-11 | 2026-08-11 | #116 / !67 |
| 22 | CF-022 | adaptive-workspace-mvp.png still shows Colour/Ribbon/Gift Card as MVP T-04 after ADR-006 aligned the SVG | Medium | verified | 2026-08-11 | 2026-08-11 | #117 / !68 |
| 23 | CF-023 | research/adr-candidates/README still says ADR-006…010 gate slots are open though those ADRs are Accepted | Low | verified | 2026-08-11 | 2026-08-11 | #118 / !69 |
| 24 | CF-024 | ADR-009 still says BFF “if introduced by deployment ADRs” though ADR-007 Accepted a separate BFF | Low | verified | 2026-08-11 | 2026-08-11 | #119 / !72 |
| 25 | CF-025 | adaptive-workspace-mvp.png omits T-03 Available badges and T-08 Contact Florist / Escalate present in SVG | Medium | verified | 2026-08-11 | 2026-08-11 | #123 / !74 |
| 26 | CF-029 | Group milestones M3–M7 and Future Backlog reuse M2 description verbatim; M1 description empty | Medium | verified | 2026-08-11 | 2026-08-11 | #124 / !75 |
| 27 | CF-026 | ADR-010 still says Edge/BFF APIs “if present” though ADR-007 Accepted a separate BFF | Low | verified | 2026-08-11 | 2026-08-11 | #125 / !76 |
| 28 | CF-027 | Wiki ADR page still says “ADR-007 lands with CF-017 / !61” though ADR-007 is Accepted on main | Low | verified | 2026-08-11 | 2026-08-11 | #126 / !77 |
| 29 | CF-028 | GitLab issue #109 (CF-014) remains open while CF-014 was closed via #110 / !56 | Low | verified | 2026-08-11 | 2026-08-11 | #109 / !56 |
| 30 | CF-030 | Wiki ADR index omitted Accepted ADR-011/012 and retained obsolete broker-deferred wording | Medium | verified | 2026-08-12 | 2026-08-12 | #132 / Wiki c8a1af4 |
| 31 | CF-034 | Edge BFF used UnavailableOrchestration; Shared Understanding lacked browser-facing runtime routes | Medium | verified | 2026-08-12 | 2026-08-12 | #130 / !93 |
| 32 | CF-031 | `CLAUDE.md` described the repository as docs-only despite executable `platform/` and `edge/` areas | Medium | verified | 2026-08-12 | 2026-08-12 | #133 / !100 |
| 33 | CF-033 | `platform/README.md` said M2 behavior was not implemented despite merged M2 services | Medium | verified | 2026-08-12 | 2026-08-12 | #134 / !101 |
| 34 | CF-032 | Root README repository navigation omitted `platform/` and `edge/` | Low | verified | 2026-08-12 | 2026-08-12 | #135 / !102 |
| 35 | CF-035 | Repo wiki/architecture-decision-records.md still omits ADR-011/012 and retains broker-deferred wording after CF-030 live-wiki verify | Medium | verified | 2026-08-12 | 2026-08-12 | #138 / !106 |
| 36 | CF-036 | Roadmap Future Backlog lists FR-007 under CRM analytics while FR-007 is MVP Recommendations (M3) | Medium | verified | 2026-08-12 | 2026-08-12 | #139 / !107 |
| 37 | CF-037 | Edge documents/routes commands, workspace, and stream while Internal orchestration only implements conversation + Shared Understanding | Medium | verified | 2026-08-12 | 2026-08-12 | #140 / !108 |
| 38 | CF-038 | GitLab issue #137 (CF-035) remains open though CF-035 was closed via #138 / !106 | Low | verified | 2026-08-12 | 2026-08-12 | #137 closed (dup #138 / !106) |
| 39 | CF-039 | Roadmap M4/M5 FR coverage disagrees with GitLab milestone assignments (FR-013/015/018; NFR-014) | Medium | verified | 2026-08-12 | 2026-08-12 | #141 / !110 |
| 40 | CF-040 | Roadmap M4 coverage lists NFR-006 (M3, double-listed) and NFR-007 (M5, closed) though both are delivered in other milestones | Medium | queued | 2026-08-12 | 2026-08-12 | (intake 2026-08-12-m4-nfr-coverage-intake) |

Allowed statuses: `queued`, `investigating`, `ready`, `in-progress`, `in-mr`,
`verified`, `regressed`, `duplicate`, `not-reproducible`, and `blocked`.

## Assessment intake

Run intake whenever a new coherence assessment is produced. Intake updates the
queue but does not start remediation in the same iteration.

1. Save the assessment under `research/assessments/YYYY-MM-DD-<short-name>.md`
   using [`templates/coherence-assessment.md`](templates/coherence-assessment.md).
   Record the assessed `main` commit so later results are reproducible.
2. Normalize each finding to one falsifiable claim. Search this queue, prior
   assessments, and open/closed GitLab issues and MRs for equivalent claims.
3. Reuse the existing `CF-NNN` when the underlying claim is equivalent, even
   if wording or evidence paths changed. Add the assessment to that finding's
   history and update `Last seen`.
4. Classify each result:

   - **new** — assign the next unused `CF-NNN` and append it as `queued`;
   - **duplicate** — link it to the existing ID; do not add another active row;
   - **regression** — change a previously `verified` finding to `regressed` and
     preserve its old issue/MR links;
   - **still open** — retain its active status and update evidence/history;
   - **resolved or rejected** — record evidence, but do not silently mark an
     active item `verified`; verification still requires the completion rules.

5. Reorder only `queued` and `regressed` rows by severity and dependency.
   Never renumber stable IDs or reorder active work (`investigating` through
   `in-mr`). A regression takes priority within its severity.
6. Complete the assessment's intake-reconciliation table and stop. Start the
   one-finding remediation loop as a separate run.

## One iteration

1. Fetch and inspect updated `main`; never assess from a stale feature branch.
2. Select the first `regressed` or `queued` row in queue order. Mark it
   `investigating` before changing canonical files.
3. Reproduce the claim using the workbook, published docs, CI, and current
   GitLab issues/MRs. Record exact paths and commands in a note created from
   [`templates/coherence-finding.md`](templates/coherence-finding.md).
4. If the finding is already fixed, duplicated, or not reproducible, record
   the evidence, set the terminal status, and stop this iteration.
5. If confirmed, set it `ready` and follow
   `.cursor/rules/coherence-findings-sop.mdc`. Never reuse another finding's
   issue, branch, or MR.
6. After merge, verify the resulting `main`, not merely the source branch.
   Record the main pipeline and any cross-MR regression before setting
   `verified`. Use the post-merge path in
   [`claude-obsidian-loop.md`](claude-obsidian-loop.md)
   (`python scripts/check_coherence.py` + main `coherence-guard`).
7. Stop. The next scheduled or human-triggered pass starts with the next
   `queued` row.

## Safety and stop conditions

- Do not invent or renumber BG/EP/US/FR/NFR IDs.
- An archive/workbook change requires explicit human confirmation.
- Do not overwrite a dirty worktree. Use an isolated worktree for finding
  branches.
- Do not merge automatically. A human owns merge approval.
- Stop on authentication, permission, unresolved conflict, failed required CI,
  or evidence that changes the intended scope.
- Never process two findings in one branch or MR, even when they touch the same
  file.
- Never reuse a merged MR for a regression. Keep the stable finding ID, link
  the previous remediation, and create a new issue/branch/MR cycle.

## Loop prompt

```text
Run one iteration of research/coherence-findings-loop.md. Work only on the
first queued finding. Reproduce it against updated main, create or update its
finding note, and—only if confirmed—follow the coherence findings SOP through
one issue, one isolated branch, one focused fix, and one MR. Do not merge.
After a human merges it, verify main and mark the row verified. Stop after this
single finding and report the next queued item.
```

## Assessment intake prompt

```text
Ingest the newest coherence assessment using
research/coherence-findings-loop.md. Save a dated assessment record, reconcile
every finding against stable CF IDs plus GitLab issues/MRs, append only genuine
new findings, reopen regressions, and reprioritize unstarted work. Do not create
issues, branches, or MRs during intake. Stop after reporting the reconciled
queue and next finding.
```

## Hourly automatic cadence

Default recurring mode for this repository:

1. **Session loop** — `/loop 1h` (or an armed `AGENT_LOOP_TICK_coherence` shell) runs
   the **Hourly tick prompt** below in this Agents chat until stopped.
2. **Cursor Automation** (optional, persists outside the chat) — schedule
   `0 * * * *` against this repo with the same tick prompt.

### Hourly tick prompt

```text
Hourly coherence tick for this repo. Follow research/coherence-findings-loop.md,
.cursor/rules/coherence-findings-sop.mdc, and .cursor/rules/claude-obsidian-loop.mdc.

1. Fetch/pull origin/main. Refresh glab PATH on Windows if needed.
2. Reconcile research/coherence-findings-loop.md Status and Issue/MR columns
   against GitLab (open/merged). Do not invent CF IDs.
3. If any row is queued or regressed: run ONE remediation iteration on the first
   such row (severity then dependency). Reproduce; if confirmed, one issue → one
   isolated branch → one focused fix → one MR. Do not merge.
4. If none queued/regressed: run python scripts/check_coherence.py plus a light
   inconsistency/gap scan. If new findings appear, run assessment INTAKE only
   (dated assessment + queue update). Do not remediate in the same tick.
5. Update the coherence canvas if the verdict changed.
6. Report: mode (intake|remediation|idle), finding ID, MR URL if any, next
   queued item, and any stop condition hit.
```

For a lower-volume reminder, use `/loop 1d` with the single-finding Loop prompt
above. Manual runs from Obsidian or Claude remain valid.
