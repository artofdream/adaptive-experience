# Codex — Adaptive Experience Architecture

Architecture and executable reference-foundation repository for AEA, with
Lily's Florist as the reference design. Canonical requirements and design live
under `docs/` and `implementations/`; product-neutral runtime foundations live
under `platform/` and `edge/`.

## Session start & end protocol

Before acting in any session:
1. Read the most recent `research/daily-briefs/*.md` (sort by filename date) — it's the fastest way to pick up state from other tools/sessions working this repo concurrently.
2. Read `research/random-thoughts/*.md` (specifically the strategic architecture studies and session memory logs) to inherit the Second Brain project history, decisions, trade-offs, and lessons learned.
3. If reviewing transcript history or cross-agent context, feed prior session memory logs from `research/random-thoughts/` into context to build upon the continuous knowledge base.

Before concluding a session:
1. Extract session building memory, key decisions, trade-offs, and performance benchmarks to `research/random-thoughts/YYYY-MM-DD-session-memory-log-*.md` (`@aea-knowledge-guardian`).
2. Run `python scripts/generate_daily_brief.py` to regenerate `research/daily-briefs/YYYY-MM-DD.md` (`@aea-coherence-guardian`).
3. Run `python scripts/run_all_guards.py` to verify 14/14 pre-flight quality guards pass cleanly.
4. Commit and push knowledge notes to Git so all future sessions inherit the updated Second Brain memory.
Full SOP: `.cursor/rules/session-start-briefing.mdc`.


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
`.cursor/skills/aea-*/`. Discovery adapters for Codex live under
`.agents/skills/aea-*/` — each is a thin pointer back to the canonical role;
read the referenced canonical file completely before acting as that
stakeholder. Interpret `@aea-<role>` handoffs as the corresponding
`$aea-<role>` Codex skill.

Follow `.cursor/rules/stakeholder-skills-sync-sop.mdc` for every role change
so Cursor, Codex, Claude, Copilot, Gemini, and Grok stay semantically portable. Regenerate
adapters with `python scripts/generate_codex_stakeholder_skills.py`.

## Edit style

- Match existing markdown tone; keep diffs focused.
- Run `python scripts/run_verify_job.py` to verify 14/14 quality guards and coherence evidence.
- Before `git push` on edge/platform code, run local Docker integration tests (`.cursor/rules/docker-integration-before-mr.mdc`).
- Do not commit `.obsidian/` or secrets (enforced by `python scripts/check_secrets_posture.py`).
- Use `glab`, not GitHub CLI/PR tooling — this repository's tracker is GitLab, not GitHub.
