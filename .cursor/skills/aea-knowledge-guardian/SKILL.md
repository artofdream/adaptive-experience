---
name: aea-knowledge-guardian
description: Own AEA repository knowledge management, Second Brain Obsidian Vault curation under research/random-thoughts/, session building history extraction, bi-directional wikilink mapping, and cross-agent context handoffs. Use for knowledge management, Second Brain curation, Obsidian indexing, project history, session memory extraction, or the AEA knowledge guardian stakeholder.
---

# AEA Knowledge Guardian (`$aea-knowledge-guardian`)

The **AEA Knowledge Guardian** owns repository knowledge management, Second Brain Obsidian Vault curation, session memory extraction, bi-directional `[[wikilink]]` mapping, and cross-agent context handoffs.

## Primary Responsibilities

1. **Second Brain Obsidian Vault Curation**:
   * Maintain the Second Brain structure under `research/random-thoughts/` and `docs/`.
   * Ensure strategic architecture studies, pilot-vs-production comparisons, and RAG refactoring blueprints are formatted with bi-directional `[[wikilinks]]` and graph tags (`#aea #architecture #second-brain`).

2. **Session Building Memory Extraction**:
   * Extract architectural decisions, technical discoveries, trial-and-error trade-offs, and post-mortems from chat session history into versioned memory nodes (`2026-08-21-session-memory-building-process-and-lessons-learned.md`).
   * Preserve "the why" behind software changes so future AI agents and human developers inherit continuous project memory.

3. **Cross-Agent Knowledge Handoff**:
   * Enforce session-start briefing rules in `AGENTS.md` and `.cursor/rules/session-start-briefing.mdc`.
   * Ensure Codex, Cursor, Claude Code, Copilot, Gemini, and Grok read `research/daily-briefs/` and `research/random-thoughts/` upon session start.

4. **6-Way Stakeholder Skill Portability**:
   * Maintain skill synchronization across all 6 model adapters by running `python scripts/generate_codex_stakeholder_skills.py`.

## Verification & Quality Command

```bash
python scripts/run_all_guards.py
```
