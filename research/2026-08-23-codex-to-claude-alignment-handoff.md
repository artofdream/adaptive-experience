# Codex → Claude alignment handoff — 2026-08-23

> **Tags**: #aea #handoff #codex #claude #second-brain
> **From**: Codex / `@aea-knowledge-guardian`
> **To**: Claude / `@aea-knowledge-guardian`
> **Repository ref at handoff**: `main` at `5da4db3`

## Requested Claude task

Perform an independent Claude-view repository progression and cross-session
alignment. Preserve genuine disagreements with Codex as evidence; do not merely
rewrite or endorse the Codex verdict.

## Mandatory reading order

1. `CLAUDE.md`
2. `.cursor/rules/session-start-briefing.mdc`
3. `research/daily-briefs/2026-08-23-daily-brief.md`
4. `research/random-thoughts/2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18.md`
5. `research/random-thoughts/2026-08-23-antigravity-assessment-reconciliation.md`
6. `research/assessments/2026-08-23-codex-independent-runtime-coherence-assessment.md`
7. `research/random-thoughts/2026-08-23-session-memory-log-cross-chat-knowledge-extraction.md`
8. `research/random-thoughts/2026-08-23-codex-view-repository-progression-study.md`
9. `research/coherence-findings-loop.md`

## Important warnings

- The latest daily brief is committed but its executive milestone section is
  not trustworthy. `scripts/generate_daily_brief.py` still hardcodes `15/16`
  completion and unsupported M15 pre-render/sub-100ms assertions (CF-048).
- Do **not** run `scripts/clean_repo_hygiene.py`; it calls that generator and
  can also delete root scratch files matching broad patterns.
- Do **not** run `scripts/generate_daily_brief.py` until CF-048 is remediated.
- Preserve `.claude/settings.local.json`; it is untracked local configuration.
  Do not commit, delete, quote, or summarize its contents.
- M14–M18 are reference extensions/paper-complete, not production-shipped.
- A 14/14 guard pass proves only the properties covered by those guards.

## Coherence boundary

CF-048 through CF-053 are already queued. Reuse those stable IDs for equivalent
claims and add Claude-specific evidence; do not create duplicate findings.

If the Claude assessment discovers genuinely new claims:

1. Normalize each to one falsifiable statement.
2. Search CF-001…053 and GitLab issues/MRs for equivalents.
3. Add only genuine new findings during assessment intake.
4. Stop after reconciliation. Do not remediate in the same pass.

Any later remediation must process only the first queued item and follow:

```text
one finding → one GitLab issue → one branch from updated main
→ one focused fix → one MR → verify merged main
```

Use `glab`, not GitHub tooling. Do not merge unless the MR Coordinator role is
explicitly invoked and its gates pass.

## Expected Claude deliverable

Write a new bidirectionally linked Second Brain node under
`research/random-thoughts/`, for example:

`2026-08-23-claude-view-repository-progression-and-alignment.md`

It should include:

- Claude's chronological view of repository evolution.
- Claims confirmed independently.
- Claims rejected or qualified, with exact evidence.
- Lessons not already captured by Codex.
- Historical beliefs that are now stale.
- Remaining unknowns and evidence limitations.
- A comparison table: Codex view / Claude view / reconciled conclusion.
- Links back to the Codex progression and cross-chat extraction nodes.

Do not copy raw private transcripts or secrets into the repository.

## Validation and closeout

Run:

```powershell
python scripts/run_all_guards.py
git diff --check
git status --short
```

Expected baseline: 14/14 guards pass. Commit and push the Claude knowledge note
so all other AI models can read it. Do not stage `.claude/settings.local.json`.

