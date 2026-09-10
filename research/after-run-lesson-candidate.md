# After-run lesson-candidate SOP

> **Captured**: 2026-09-10
> **Owner**: `@aea-knowledge-guardian` with `@aea-coherence-guardian`
> **Traceability**: Issue #412 (X1 adapt from the 10 Sep compare)
> **Cite, do not duplicate**: [[2026-09-10-aea-vs-x-scan-gipp-beam-avid]] · #411 · !489

After a meaningful agent or CI run, write a small lesson *candidate* under
`research/inbox/`. That is the mechanical extract AEA was missing: session-end
memory and DATE_RE already exist, but they are optional or human-gated. This
SOP makes the candidate step expected. It does **not** promote, and it does
**not** rewrite skills or canonical docs.

#413 (cost playbook) is a separate ticket. Do not implement it here.

## Dual loop

Two roles, even when one session plays both:

| Loop | Job | Writes |
|------|-----|--------|
| **Task** | Do the work (issue, MR, CI, probe). | Product / docs / research as scoped. |
| **Reviewer** | Extract what failed, what changed, what worked. | One inbox candidate only. |

The reviewer pass stores a reusable correction as a **small file**. Prefer that
over growing a prompt or appending to a giant session log.

Same session may run both loops. The reviewer extract still must not
self-promote.

## When to write a candidate

Write one when the run produced a reusable correction, failure mode, or working
recipe — for example a red CI job and the fix that cleared it, a wrong branch
base, a guard miss, or a Path B probe that changed the next command.

Skip when nothing reusable happened: read-only Q&A, a no-op cadence tick, or
"looked at the brief and stopped." Do not write empty candidates.

One candidate per meaningful run. Do not batch unrelated runs into one note.

## How to draft

1. Copy [`templates/lesson-candidate.md`](templates/lesson-candidate.md).
2. Save as `research/inbox/YYYY-MM-DD-lesson-<short-slug>.md`.
3. Fill **What failed**, **What changed**, and **What worked**. Link the issue,
   MR, job, or SHA. Cite existing BG/US/FR/NFR IDs only; do not invent IDs.
4. Tag `#aea #inbox #lesson-candidate`. Leave `status: candidate`.
5. Stop. Do not move the file to `research/random-thoughts/`. Do not edit
   `.cursor/skills/` or canonical `docs/` / `implementations/` from this pass.

A candidate is not DATE_RE. Do not write it onto
`research/daily-briefs/YYYY-MM-DD.md`.

## Promote (Knowledge Guardian only)

`@aea-knowledge-guardian` triages `#lesson-candidate` inbox notes and, when
durable, promotes them to `research/random-thoughts/` (usually a short memory
node or a section on that day's session-memory log). Session-end extraction
in `.cursor/rules/session-start-briefing.mdc` remains the KG-owned path for
full session memory.

Until that promote, the inbox file is a candidate. `#promote` on an ordinary
inbox note is a different queue (`claude-obsidian-loop.md`); a lesson
candidate does not become canonical `docs/` by being tagged.

Canonical `docs/` / `implementations/` still use the existing promote +
coherence-findings path. Skill text still uses
`.cursor/rules/stakeholder-skills-sync-sop.mdc`. Neither is this SOP.

## Hard no (reviewer loop)

- Do not auto-edit `.cursor/skills/` or generated adapters.
- Do not auto-edit canonical `docs/` or `implementations/`.
- Do not merge skill or prompt changes from the extract.
- Do not install a third-party memory product or a second vault tree.
- Do not invent FR/NFR IDs or edit the Future workbook.
- Do not treat related commentary (including the 10 Sep X posts) as AEA
  evidence. The compare already maps X1; this SOP implements that flag only.

## Relation to session-end

| Artifact | Who | When | Where |
|----------|-----|------|-------|
| Lesson candidate | Task+reviewer (any role) | After a meaningful run | `research/inbox/` |
| Session-memory log | `@aea-knowledge-guardian` | Session end | `research/random-thoughts/` |
| DATE_RE brief | generator + honest hand-review | Cadence / session end | `research/daily-briefs/YYYY-MM-DD.md` |

Writing a candidate does not replace session-end. Skipping a candidate when
nothing reusable happened is correct.

## Pointers

- Capture boundaries: [`claude-obsidian-loop.md`](claude-obsidian-loop.md)
- Session start/end: `.cursor/rules/session-start-briefing.mdc`
- 10 Sep taxonomy (X1 adapt / X6 reject):
  `research/random-thoughts/2026-09-10-aea-vs-x-scan-gipp-beam-avid.md`
