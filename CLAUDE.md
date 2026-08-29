# Claude — Adaptive Experience Architecture

Architecture and executable reference-foundation repository for AEA, with
Lily's Florist as the reference design. Canonical requirements and design live
under `docs/` and `implementations/`; product-neutral runtime foundations live
under `platform/` and `edge/`.

## Session start

Before acting, read the most recent `research/daily-briefs/*.md` (sort by
filename date) if one exists — it's the fastest way to pick up state from
other tools/sessions working this repo concurrently. If it's more than a day
or two old, say so; don't treat it as current. Full SOP:
`.cursor/rules/session-start-briefing.mdc`.

## Source of truth

- Requirements counts and mapping: `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`
- Published architecture: `docs/`, `implementations/`
- Working notes (pre-canonical): `research/`

Do not invent BG/US/FR/NFR IDs. Prefer citing existing IDs; archive changes are rare and explicit.

## Stakeholder skills

Discover AEA stakeholder roles under `.claude/skills/`. Their canonical role
definitions live under `.cursor/skills/`; read the referenced canonical skill
completely whenever a stakeholder skill triggers. Follow
`.cursor/rules/stakeholder-skills-sync-sop.mdc` for every role change so Cursor,
Codex, Claude, Copilot, Gemini, and Grok remain semantically portable.

## Claude ↔ Obsidian loop

Full SOP: `research/claude-obsidian-loop.md`

1. Capture in Obsidian → `research/inbox/` (or private vault notes).
2. Triage/synthesize here → promotion candidates under `research/`.
3. Promote tightly into `docs/` / `implementations/` when asked.
4. Coherence inconsistencies/gaps → `.cursor/rules/coherence-findings-sop.mdc`
   (one finding → one issue → one branch → one MR).

## Edit style

- Match existing markdown tone; keep diffs focused.
- Run `python scripts/check_coherence.py` when ID inventories or counts move.
- Before `git push` and opening or updating an MR, run local Docker
  integration tests for every impacted component
  (`.cursor/rules/docker-integration-before-mr.mdc`). After create or
  push, notify MRC (`.cursor/rules/mr-handoff-to-mrc.mdc`). If blocked,
  request the owning specialist, or PM and/or sponsor
  (`.cursor/rules/blocked-reach-out.mdc`).
- Do not commit `.obsidian/` or secrets.
