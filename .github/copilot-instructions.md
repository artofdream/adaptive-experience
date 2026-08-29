# Copilot — Adaptive Experience Architecture

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

This repo runs a 14-role AEA stakeholder team (`aea-project-manager`,
`aea-product-owner`, `aea-ux-designer`, `aea-customer-journey`,
`aea-support-coordinator`, `aea-ai-engineer`, `aea-appsec-auditor`,
`aea-devsecops-platform`, `aea-senior-software-engineer`, `aea-mr-coordinator`,
`aea-coherence-guardian`, `aea-knowledge-guardian`, `aea-cost-guardian`, `aea-performance-guardian`). Canonical role definitions live under
`.cursor/skills/aea-*/`. Per-role instructions for Copilot live under
`.github/instructions/aea-*.instructions.md` — each is a thin pointer back to
the canonical role; read the referenced canonical file completely before
acting as that stakeholder. Copilot has no persona-switch mechanism, so act
under one of these roles only when the user explicitly asks for it or the
request clearly matches that role's owned surfaces.

Follow `.cursor/rules/stakeholder-skills-sync-sop.mdc` for every role change
so Cursor, Codex, Claude, and Copilot stay semantically portable. Regenerate
adapters with `python scripts/generate_codex_stakeholder_skills.py`.

## Edit style

- Match existing markdown tone; keep diffs focused.
- Run `python scripts/check_coherence.py` when ID inventories or counts move.
- Before opening or updating a merge request, run local Docker integration
  tests for every impacted component
  (`.cursor/rules/docker-integration-before-mr.mdc`). After create or
  push, notify MRC (`.cursor/rules/mr-handoff-to-mrc.mdc`).
- Do not commit `.obsidian/` or secrets.
- Use `glab`, not `gh` — this repository's tracker is GitLab, not GitHub.
