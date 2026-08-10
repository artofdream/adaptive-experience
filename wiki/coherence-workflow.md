# Coherence workflow

Inconsistencies and gaps from a coherence assessment or review canvas follow the
always-apply SOP:

1. Intake stable `CF-NNN` in the findings queue
2. One GitLab issue
3. One feature branch from `main`
4. One focused fix
5. One MR (`Closes #N`) — humans merge

Hourly tick: remediate one queued finding **or** intake-only if the queue is
empty. Do not auto-merge.

## Canonical docs

- [coherence-findings-loop.md](https://gitlab.com/artof-group/adaptive-experience-architecture/-/blob/main/research/coherence-findings-loop.md)
- [coherence-findings-sop.mdc](https://gitlab.com/artof-group/adaptive-experience-architecture/-/blob/main/.cursor/rules/coherence-findings-sop.mdc)
- [claude-obsidian-loop.md](https://gitlab.com/artof-group/adaptive-experience-architecture/-/blob/main/research/claude-obsidian-loop.md)
- Guard: `python scripts/check_coherence.py`
