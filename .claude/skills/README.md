# AEA stakeholder skills — Claude Code adapters

`.claude/skills/aea-*/SKILL.md` are **generated discovery adapters**, one per
canonical role in `.cursor/skills/aea-*/`. Each adapter is a thin pointer:
read the canonical `.cursor/skills/aea-<role>/SKILL.md` completely before
acting, then apply the Claude-specific translations in this file's "Claude
Code mechanic differences" section (below) and in the adapter's own "Claude
adaptations" list.

**Do not hand-edit a generated adapter as the final change.** Change the
canonical role in `.cursor/skills/`, update
`scripts/generate_codex_stakeholder_skills.py` if the role's trigger,
adaptation, or linked-reference note changed, then regenerate:

```bash
python scripts/generate_codex_stakeholder_skills.py
python scripts/generate_codex_stakeholder_skills.py --check   # verify no drift
```

Full SOP (source/target relationship, mandatory same-change workflow,
equivalence boundary): `.cursor/rules/stakeholder-skills-sync-sop.mdc`.

## Claude Code mechanic differences

The canonical skills are written for Cursor. These mechanics don't exist in
Claude Code and are translated by every generated adapter's "Claude
adaptations" section plus the notes below:

| Cursor mechanic | Claude Code translation |
|---|---|
| `@aea-<role>` mention routing | `Skill({skill: "aea-<role>"})` to continue as that persona in the current turn, or `Agent({subagent_type: "general-purpose", prompt: "..."})` briefed with the role's canonical `.cursor/skills/aea-<role>/SKILL.md` path for independent/parallel work |
| `~/.cursor/skills-cursor/canvas/SKILL.md` → `.canvas.tsx` | Load the `artifact-design` skill and publish with the `Artifact` tool (HTML) |
| `cursor-ide-browser` MCP (`browser_tabs`, `browser_navigate`, `browser_lock`, `browser_snapshot`) | `mcp__Claude_Browser__*` tools: `tabs_context`, `navigate`, `computer`, `read_page` (no `browser_lock` equivalent — nothing else shares this session's browser pane) |
| Cursor Cloud Agents | Claude Code background `Agent` execution, optionally `isolation: "worktree"` or `"remote"` |
| `disable-model-invocation: true` (on Scrum-Master-only roles like `aea-project-manager`, `aea-mr-coordinator`) | No platform equivalent — the canonical role's own text states when it should only be explicitly invoked; honor it by convention |
| `.cursor/rules/*.mdc` with `alwaysApply: true` | Not auto-injected in Claude Code — `Read` the referenced `.mdc` file at the point of use instead of assuming prior injection |

## Team

Canonical roster and ownership: `.cursor/skills/` (source of truth). Do not
duplicate the roster here — it drifts. Run
`python scripts/generate_codex_stakeholder_skills.py --check` to confirm
this directory's inventory matches canonical.
