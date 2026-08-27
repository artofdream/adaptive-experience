# Trust but verify: written must match implemented

> **Tags**: #aea #second-brain #honesty #verify #knowledge-first #coherence #antifragility
> **Captured**: 2026-08-25
> **GitLab**: #257
> **Owners to inherit**: @aea-knowledge-guardian, @aea-coherence-guardian, @aea-senior-software-engineer, @aea-mr-coordinator
> **This node is knowledge, not a merge of product work.**

This note is the committed bus for a 2026-08-25 sponsor correction: do **not** solo-rewrite stakeholder skills. Capture the principle so the team can implement one finding at a time.

---

## 1. Principle

**What is written must match what is implemented.** Trust but verify.

Status surfaces (daily briefs, roadmap Completed tags, always-loaded role counts, embedded "14/14 guards" blocks) are claims. A claim of Completed / shipped / installed is only honest when a mechanical check can point at evidence: tests, probes, or an evidence manifest whose paths exist.

Hardcoded narrative is not evidence. Regeneration that overwrites an honest sentence with a static `15/16` is a regression of this principle. See queued **CF-048** in `research/coherence-findings-loop.md` and [[2026-08-23-claude-view-repository-progression-and-alignment]].

Anti-fragility depends on this: a guard network that believes its own press release cannot grow stronger from stress. Cornerstone SOP (markdown, not a vault wikilink; `.cursor/` is outside the graph resolver): [antifragility-cornerstone-sop.mdc](../../.cursor/rules/antifragility-cornerstone-sop.mdc). Coherence loop SOP: [coherence-findings-sop.mdc](../../.cursor/rules/coherence-findings-sop.mdc). Fail-closed AI honesty path: [[ADR-016]].

---

## 2. Knowledge First (inherit before act)

Session-start is not optional colour. Before any write:

1. Read the latest **committed** file in `research/daily-briefs/` (SOP: [session-start-briefing.mdc](../../.cursor/rules/session-start-briefing.mdc)). Today this session read `research/daily-briefs/2026-08-24-daily-brief.md` at `0a2c68c`. The 2026-08-25 brief did not exist. Treat post-brief commits as unknown until verified.
2. Read `research/random-thoughts/` studies and session memory, especially the 2026-08-23 review / CF-048 through CF-053 intake and the 24-hour lessons: [[2026-08-24-24-hour-lessons-learned-retrospective]], [[2026-08-23-session-memory-log-cross-chat-knowledge-extraction]], [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]], [[2026-08-21-kb-project-building-lessons]].
3. An uncommitted brief is not shared memory.

Knowledge First is how later agents inherit this node. Shared committed memory is the bus. Chat is not.

---

## 3. Missing verify job (do not add a 15th hat)

The missing capability is a **job**, not another isolated stakeholder skill.

A verify job must instruct, in order:

1. **Search the vault first** for a prior failure of this class (coherence queue, assessments, session memory, GitLab issues/MRs) before writing code. Reuse the stable CF id when the claim is equivalent. Do not invent BG/US/FR/NFR IDs.
2. **Walk the chain** requirement -> ADR -> schema -> code -> test -> probe. Stop and report at the first break. Do not claim the chain is closed because a later document says Completed.
3. **Fail closed** if a brief or roadmap says Completed / shipped without evidence (tests, probes, or an evidence manifest). Do not rewrite history in old briefs; stop producing the lie going forward.

Related live evidence on `origin/main` @ `0a2c68c` (2026-08-25):

- `scripts/generate_daily_brief.py` still hardcodes `15/16 Milestones Completed (93.75%)`, active M15 "Edge SSR & Sub-100ms LCP", and process text that *guarantees* sub-100ms LCP. The only live-derived field is the guard transcript. That is CF-048. No GitLab issue existed for CF-048 when this node was written; do not silently retitle #257 as CF-048 unless `@aea-coherence-guardian` intake says the claims are the same.
- `docs/07-roadmap/roadmap.md` marks M8-M13 `(Completed)` and M14-M18 `(Reference Extension)`. M0-M7 have no Completed tag. A brief that prints 15/16 is not a parse of that table.
- Metric-label honesty already had a round: [[2026-08-24-24-hour-lessons-learned-retrospective]] (TTFB is not LCP). Do not re-implement CF-049 inside a verify-job MR.

Canonical knowledge-guardian skill (markdown link; skill files are outside the graph resolver): [aea-knowledge-guardian/SKILL.md](../../.cursor/skills/aea-knowledge-guardian/SKILL.md).

---

## 4. Fourteen hats are lenses; three jobs are executable

Keep the **14** stakeholder hats as domain lenses. Do **not** collapse or delete them. Do **not** add a 15th isolated stakeholder (`aea-verifier`) as a peer hat.

Three executable jobs:

| Job | Who runs it | Rule |
|-----|-------------|------|
| implement | `@aea-senior-software-engineer` (and the domain hat that owns the surface) | One finding, one branch, one MR |
| verify | a **shared job** invoked by implementers and reviewers; vault search + chain walk + Completed-without-evidence fail | Not a new role count |
| merge | `@aea-mr-coordinator` only | `disable-model-invocation: true`; `glab mr merge <n> --yes --auto-merge` after gates; loop ticks must not merge |

Merge skill: [aea-mr-coordinator/SKILL.md](../../.cursor/skills/aea-mr-coordinator/SKILL.md).

---

## 5. One role list, six adapters (fix 14 vs 11 vs 10 drift)

`scripts/generate_codex_stakeholder_skills.py` copies Cursor skills into Codex, Claude, Copilot, Gemini, and Grok. That is the right shape. The drift is **multiple source lists**:

| Surface (2026-08-25 `origin/main`) | Count claimed or stored |
|------------------------------------|-------------------------|
| `.cursor/skills/aea-*` directories | **14** |
| generator `SKILLS` dict | **14** (second list; can drift from the filesystem) |
| `AGENTS.md` | **14-role** text |
| `.github/copilot-instructions.md` | **10-role** text |
| `docs/aea-system-documentation.md` | **11-role** team |
| `.cursor/rules/stakeholder-skills-sync-sop.mdc` | **14 roles** (was 11; see [[2026-08-23-codex-and-claude-feedback-reconciliation-study]]) |
| `scripts/generate_daily_brief.py` section 4 | hardcoded **14-Role** matrix |

Prior vault hits of this class: [[2026-08-21-kb-project-building-lessons]] (SOP 11 vs generator 13), REV-10 in the 2026-08-23 repository review.

**Fix (team, later, one CF):** generate all six adapters from **one** role list (prefer the Cursor skill directory as source of truth, or a single manifest the generator and always-loaded files both read). Do not keep a parallel hardcoded `SKILLS` dict plus prose counts in AGENTS/Copilot/system docs/daily-brief. Do not add verifier as a 15th name on that list.

---

## 6. What this session did not do (boundaries)

- Did **not** implement `aea-verifier/SKILL.md`.
- Did **not** push a skill-rewrite branch.
- Did **not** open a CF-048 honesty/code MR (issue+branch+MR for that brick had not been created; this node is the correction's preferred bus). CF-048 remains `queued` in the loop file.
- Did **not** invent BG/US/FR/NFR IDs or a new CF number. Intake is `@aea-coherence-guardian`.
- Did **not** merge anything.
- Did **not** implement Stripe / WebSocket / WebRTC, drop `allow_failure` flags, or rewrite 14 sibling skills.

GitLab tracker for this node: **#257**.

---

## 7. Next team action

1. `@aea-knowledge-guardian` curates this node (tags, wikilinks, vault index). This file is the draft they inherit.
2. `@aea-coherence-guardian` runs **assessment intake only**: one CF, reuse CF-048 if equivalent, otherwise next unused CF from `research/coherence-findings-loop.md`. Do not batch CF-048 through CF-053.
3. `@aea-senior-software-engineer` implements that one ingested finding (verify job wiring and/or single role-list generator, as intake states).
4. `@aea-mr-coordinator` merges after scope / boundary / validation gates. Not this session.

---

## 8. Graph and SOP links

Vault notes (wikilinks; graph guard resolves `research/random-thoughts/`):

- [[2026-08-24-24-hour-lessons-learned-retrospective]]
- [[2026-08-24-session-memory-log-milestone-shipped-status-assessment]]
- [[2026-08-23-claude-view-repository-progression-and-alignment]]
- [[2026-08-23-session-memory-log-cross-chat-knowledge-extraction]]
- [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]]
- [[2026-08-23-codex-and-claude-feedback-reconciliation-study]]
- [[2026-08-21-kb-project-building-lessons]]

- [[2026-08-26-date-re-bus-and-agent-runner-image-roll]]
- [[2026-08-27-honesty-crisis-lessons-and-path-b-chain]]

ADRs (prefix allowed by `scripts/check_knowledge_graph.py`): [[ADR-016]]

SOPs and skills (markdown links; `.cursor/` is not in the wikilink resolver, so a `[[wikilink]]` here would be a broken graph edge and would violate this note's own principle):

- [antifragility-cornerstone-sop.mdc](../../.cursor/rules/antifragility-cornerstone-sop.mdc)
- [coherence-findings-sop.mdc](../../.cursor/rules/coherence-findings-sop.mdc)
- [session-start-briefing.mdc](../../.cursor/rules/session-start-briefing.mdc)
- [aea-knowledge-guardian/SKILL.md](../../.cursor/skills/aea-knowledge-guardian/SKILL.md)
- [aea-mr-coordinator/SKILL.md](../../.cursor/skills/aea-mr-coordinator/SKILL.md) (`disable-model-invocation: true`)