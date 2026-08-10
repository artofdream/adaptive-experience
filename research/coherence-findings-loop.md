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
| 7 | CF-007 | T-03 recommendation cards omit the Available badge (FR-011) | Medium | verified | 2026-08-10 | 2026-08-10 | #97 / !46 |
| 8 | CF-008 | T-04 customization panel drops Colour and Ribbon fields | Medium | verified | 2026-08-10 | 2026-08-10 | #98 / !47 |
| 9 | CF-009 | T-08 tracking omits Contact Florist and Future T-09 escalation (FR-006) | Medium | verified | 2026-08-10 | 2026-08-10 | #99 / !48 |
| 10 | CF-010 | GitLab wiki pages are title stubs with no body synced from canonical docs | Medium | in-mr | 2026-08-10 | 2026-08-10 | #101 |

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
