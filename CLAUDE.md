# Claude — Adaptive Experience Architecture

Architecture and executable reference-foundation repository for AEA, with
Lily's Florist as the reference design. Canonical requirements and design live
under `docs/` and `implementations/`; product-neutral runtime foundations live
under `platform/` and `edge/`.

## Source of truth

- Requirements counts and mapping: `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`
- Published architecture: `docs/`, `implementations/`
- Working notes (pre-canonical): `research/`

Do not invent BG/US/FR/NFR IDs. Prefer citing existing IDs; archive changes are rare and explicit.

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
  (`.cursor/rules/docker-integration-before-mr.mdc`).
- Do not commit `.obsidian/` or secrets.
