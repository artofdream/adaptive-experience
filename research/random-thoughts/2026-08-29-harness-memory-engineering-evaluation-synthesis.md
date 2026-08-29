# Harness & Memory Engineering Evaluation Synthesis (Issues #289–#292)

> **Tags**: #aea #second-brain #harness-engineering #memory-engineering #governance #architecture #knowledge-first
> **Captured**: 2026-08-29
> **Author**: @aea-ai-engineer, @aea-product-owner, @aea-project-manager, @aea-knowledge-guardian
> **GitLab**: Evaluates #289, #290, #291, #292
> **Owners to inherit**: @aea-project-manager, @aea-ai-engineer, @aea-knowledge-guardian, @aea-mr-coordinator

---

## 1. Executive Summary

In response to recent 2026 memory engineering literature (*0xWast3, Kimi Context Graphs*), the AEA stakeholder team evaluated four architectural mechanisms to strengthen the repository's harness and long-term session memory:
1. **#289**: `CONSTRAINTS.md` as correction memory.
2. **#290**: Typed relationship graphs for vault and Shared Understanding.
3. **#291**: Formal read-before / write-after session memory protocol.
4. **#292**: Contradiction surfacing (no silent resolution).

---

## 2. Evaluation Results & Decisions

### A. Issue #289: Correction Memory (`CONSTRAINTS.md`)
* **Finding**: Introducing a 15th separate guide file (`CONSTRAINTS.md`) risks guide bloat, cognitive load fragmentation, and fights issue #275 (pruning guides that CI sensors already enforce).
* **Decision**: **Fold into AGENTS.md & specialized skill rules**. Negative constraints (what *not* to do, e.g., no base64 in `.jpg` files, no invented IDs, no unprobed status claims) belong directly in `AGENTS.md` and role definitions where all 6 AI model adapters already load them automatically.
* **Status**: **Resolved via `AGENTS.md` / Skill integration**.

### B. Issue #290: Typed Relationship Graphs
* **Finding**: Full 300-agent swarm property graphs introduce excessive graph database overhead. However, flat un-typed `[[wikilinks]]` lose semantic intent (*does note A constrain note B, or is it derived from note B?*).
* **Decision**: **Adopt lightweight typed edge relationships in Second Brain frontmatter**:
  - `derived_from`: Source paper / customer brief
  - `constrains`: Architectural invariant or negative rule
  - `verifies`: Sensor or empirical test probe
* **Status**: **Adopted as lightweight frontmatter metadata pattern**.

### C. Issue #291: Read-Before / Write-After Protocol
* **Finding**: AEA already runs this implicitly via `AGENTS.md` Session Start & End SOP, but lacked formal protocol naming.
* **Decision**: **Adopt as canonical 2-phase protocol**:
  - **Phase 1 (Read-Before)**: Ingest latest `research/daily-briefs/YYYY-MM-DD.md` + active Second Brain notes before tool invocation.
  - **Phase 2 (Write-After)**: Extract session building memory $\to$ regenerate daily brief $\to$ execute 14/14 quality guards $\to$ push to Git.
* **Status**: **Adopted into repository SOP**.

### D. Issue #292: Contradiction Surfacing (No Silent Resolve)
* **Finding**: LLMs have a known failure mode of "hallucinated harmony" (silently picking one conflicting fact or smoothing over contradictory requirements).
* **Decision**: **Adopt as a core honesty sensor rule**: When two notes, status fields, or specs conflict, the agent **must explicitly surface the contradiction** (`[CONTRADICTION: X vs Y]`), mark the status as **Unknown**, and escalate to `@aea-product-owner` or the project sponsor.
* **Status**: **Adopted as foundational honesty sensor**.

---

Existing IDs: [[2026-08-29-parallel-runner-claim-rule]], [[2026-08-29-core-principles-retrospective]], [[2026-08-29-sprint-coordination-finops-and-ux]], [[2026-08-29-public-voice-pass]].
