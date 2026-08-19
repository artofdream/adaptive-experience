# Codex — Adaptive Experience Architecture

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

This repo runs a 10-role AEA stakeholder team (`aea-project-manager`,
`aea-product-owner`, `aea-ux-designer`, `aea-customer-journey`,
`aea-support-coordinator`, `aea-ai-engineer`, `aea-devsecops-platform`,
`aea-senior-software-engineer`, `aea-mr-coordinator`,
`aea-coherence-guardian`). Canonical role definitions live under
`.cursor/skills/aea-*/`. Discovery adapters for Codex live under
`.agents/skills/aea-*/` — each is a thin pointer back to the canonical role;
read the referenced canonical file completely before acting as that
stakeholder. Interpret `@aea-<role>` handoffs as the corresponding
`$aea-<role>` Codex skill.

Follow `.cursor/rules/stakeholder-skills-sync-sop.mdc` for every role change
so Cursor, Codex, Claude, Copilot, and Gemini stay semantically portable. Regenerate
adapters with `python scripts/generate_codex_stakeholder_skills.py`.

## Edit style

- Match existing markdown tone; keep diffs focused.
- Run `python scripts/check_coherence.py` when ID inventories or counts move.
- Before `git push` and opening or updating an MR, run local Docker
  integration tests for every impacted component
  (`.cursor/rules/docker-integration-before-mr.mdc`).
- Do not commit `.obsidian/` or secrets.
- Use `glab`, not GitHub CLI/PR tooling — this repository's tracker is
  GitLab, not GitHub.
