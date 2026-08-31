# Stakeholder Handoff: Kocer 5-Layer Harness Gaps & Action Items

> **Tags**: #aea #second-brain #handoff #stakeholders #kocer #harness #knowledge-first
> **Captured**: 2026-08-31
> **Author**: @aea-project-manager, @aea-knowledge-guardian
> **Backlog Items**: #338 (Layer 02 Curator), #339 (Layer 05 Reviewer), #340 (Stack Diagnostic Sensor)

---

## 1. Specialist Assignments & Execution Scope

```
┌─────────────────────────────────────────────────────────────┬────────────────────────┬───────────────────────────────────────────┐
│ Issue Number & Scope                                        │ Primary Specialist     │ Next Actionable Implementation Step       │
├─────────────────────────────────────────────────────────────┼────────────────────────┼───────────────────────────────────────────┤
│ • #338 — Layer 02 Dynamic Context Curator                   │ @aea-ai-engineer       │ Author platform/aea_platform/context_     │
│   (Select, Compress, Prune)                                 │                        │ curator.py + unit tests under ADR-016.    │
├─────────────────────────────────────────────────────────────┼────────────────────────┼───────────────────────────────────────────┤
│ • #339 — Layer 05 Orthogonal Reviewer Node                  │ @aea-devsecops-plat    │ Implement scripts/run_orthogonal_review.py│
│   (Fresh Context CI Gate)                                   │                        │ & wire into GitLab CI verify stage.       │
├─────────────────────────────────────────────────────────────┼────────────────────────┼───────────────────────────────────────────┤
│ • #340 — Concentric Stack Layer Diagnostic Sensor           │ @aea-senior-software   │ Implement scripts/check_agent_stack_layers│
│   (Lower-Layer Health Check)                                │                        │ .py & add to run_all_guards.py suite.     │
└─────────────────────────────────────────────────────────────┴────────────────────────┴───────────────────────────────────────────┘
```

---

## 2. Technical Directives for Implementers

### A. `@aea-ai-engineer` (Issue #338 — Context Curator)
* Implement `ContextCurator` class in `platform/aea_platform/context_curator.py`.
* Hook into BFF/Agent prompt builder:
  1. Filter out repetitive intermediate tool outputs when final structured understanding exists.
  2. Inject active negative constraints from `AGENTS.md` and Second Brain memory.
  3. Enforce token budget caps to stay within NFR-003 latency envelopes ($\le 2.5\text{s}$).

### B. `@aea-devsecops-platform` (Issue #339 — Orthogonal Reviewer Gate)
* Implement `scripts/run_orthogonal_review.py` utilizing LiteLLM mock/live adapter.
* Reviewer input must be completely decoupled from previous author context: only receives git diff, issue description, and acceptance criteria.
* Add non-blocking advisory gate initially, promoting to blocking once false positive rate $< 5\%$.

### C. `@aea-senior-software-engineer` (Issue #340 — Stack Layer Diagnostic Sensor)
* Implement `scripts/check_agent_stack_layers.py`.
* Ensure each floor verifies prerequisites:
  - Floor 01: Prompt schema syntax & CTA invariants.
  - Floor 02: Context size & active constraints injection.
  - Floor 03: BFF/Gateway endpoint contract responses & 14/14 pre-flight guards.
  - Floor 04: Loop budget & iteration boundaries.
  - Floor 05: Stakeholder role authorization & MRC auto-merge prerequisites.
* Integrate as pre-flight guard #15 in `scripts/run_all_guards.py`.

Existing IDs: [[2026-08-31-aea-framework-harness-engineering]], [[2026-08-31-aea-vs-kocer-five-layers-agent-engineering]], [[2026-08-29-harness-memory-engineering-evaluation-synthesis]].
