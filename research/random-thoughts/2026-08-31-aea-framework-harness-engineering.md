> **Tags**: #aea #second-brain #harness #path-b #knowledge-first #kocer
> **Captured**: 2026-08-31
> **Draft status**: in progress (not canonical `docs/`)
> **Successor of**: [[2026-08-29-aea-framework-harness-engineering]] (do not overwrite)
> **Comparisons**: [[2026-08-31-aea-vs-kocer-five-layers-agent-engineering]], [[2026-08-29-aea-vs-wast3-memory-engineering]]
> **Related**: #337 (this paper revision) · #289 · #290 · #291 · #292 · #307 · #308
> **Honesty on this revision**: Kocer 5-layer nesting is **integrated as an architectural taxonomy**. Proposed runtime components (Context Curator, Orthogonal Reviewer Node) are **identified and proposed**. They are not in production.

# Production Experience Engineering Practice 2026

# Adaptive Experience Architecture

## Adaptive Experience = Shared Understanding + Domain Services + Outer Harness

### Revision of 31 August 2026 (Europe/Berlin) — Five Concentric Floors of Agent Engineering

*Instantiated on Lily's Florist Path B (Art of Group). Canonical remote: GitLab https://gitlab.com/artof-group/adaptive-experience-architecture. Live shop: https://aea.artof.link. Live documentation: https://architecture.artof.link. Tracker is GitLab (`glab`), not GitHub.*

*Independently compiled — Art of Group / AEA knowledge guardian — not affiliated with Google, OpenAI, Anthropic, HashiCorp, or Moonshot AI. This revision synthesizes related work from Hashimoto [1], 0xWast3 (Memory Engineering, 13 Aug 2026) [19], and Kocer (Five Layers of Agent Engineering, 30 Aug 2026) [21].*

*Vault: #aea. Existing IDs only: [[FR-001]] [[FR-003]] [[FR-007]] [[FR-008]] [[FR-009]] [[FR-011]] [[NFR-005]] [[NFR-009]] [[NFR-017]] [[J1]] [[J2]] [[J3]] [[J4]] [[CF-048]] [[CF-054]] [[CF-055]]. Do not invent fake IDs. Do not paste this into DATE_RE.*

---

## Abstract

The 28 Aug edition stated the core formula and mapped AEA onto six harness layers. The 29 Aug revision integrated memory engineering primitives (context is not memory; procedure vs. correction vs. relationship). This **31 Aug 2026 revision** incorporates Kocer's unifying insight [21]: **harness, loop, and graph are not competing choices; they are five concentric wrapping floors**. 

Each layer wraps and assumes the stability of the floor beneath it:
1. **01 | Prompt Engineering** (The Message) wraps the raw model.
2. **02 | Context Engineering** (The Memory / Curator) wraps the prompt.
3. **03 | Harness Engineering** (The Machine / Execution Environment) wraps context.
4. **04 | Loop Engineering** (The System / Goal + Iterations + Budget) wraps the harness.
5. **05 | Graph Engineering** (The Topology / Multi-Node Orchestration + Reviewer) wraps the loop.

AEA adopts this 5-floor wrapping hierarchy within its **Outer Harness**, while maintaining its fundamental architectural differentiator: **the cognitive stack is anchored to deterministic Domain Services (PostgreSQL, Kafka, pricing, fail-closed inventory)** rather than operating in an ungrounded hallucination loop.

---

## I. WHAT THIS REVISION CHANGES

| Kept from 28 & 29 Aug | Added 31 Aug (Kocer Pass) | Proposed Extensions |
|---|---|---|
| Core Formula: `SU + Domain Services + Outer Harness` | Concentric 5-Floor Hierarchy (Prompt $\to$ Context $\to$ Harness $\to$ Loop $\to$ Graph) [21] | Layer 02 Dynamic Context Curator component |
| 6 Outer Harness Layers (Guides, Sensors, Loop, Memory, Permissions, Observability) | Resolves "Harness vs Loop vs Graph" as nested wrapping floors | Layer 05 Orthogonal Reviewer Node with fresh context |
| 14 Stakeholder Roles & MRC Auto-Merge Gate | Layer Failure Root-Cause Principle ("Skip Layer 2 $\to$ Layer 3/5 fails") | Concentric Stack Diagnostic Sensor |
| Deterministic Domain Services (PostgreSQL 16, Kafka, Fail-Closed) | Economic Moat Law: Model is commodity (1-day swap); Stack is IP (1-quarter swap) | Formalized in GitLab Backlog |

---

## II. THE UNIFIED FIVE-FLOOR WRAPPING STACK IN AEA

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 05 | GRAPH ENGINEERING (Stakeholder Topology & Orthogonal Review)                      │
│      • 14 Specialized Roles (@aea-*) + Typed Edges (derived_from, constrains, verifies)│
│      • Independent Reviewer Gate (MRC / GitLab Duo / CI Quality Ratchet)               │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 04 | LOOP ENGINEERING (The System Run & Coherence Finding Cycles)                │  │
│  │      • Single-Finding Invariant: 1 Finding -> 1 Issue -> 1 Branch -> 1 MR        │  │
│  │      • Execution Budgets, Cadence Ticks, & Max Iteration Bounds                  │  │
│  │  ┌────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ 03 | HARNESS ENGINEERING (The Execution Machine & Pre-Flight Verifiers)    │  │  │
│  │  │      • Edge BFF + Gateway + LiteLLM Mock/Live Proxy (ADR-016)              │  │  │
│  │  │      • 14/14 Pre-Flight Quality Guards (scripts/run_all_guards.py)         │  │  │
│  │  │  ┌──────────────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │ 02 | CONTEXT ENGINEERING (The Memory & Curator Layer)                │  │  │  │
│  │  │  │      • Read-Before / Write-After Session Memory Protocol             │  │  │  │
│  │  │  │      • Second Brain Vault (research/random-thoughts/) + Daily Briefs │  │  │  │
│  │  │  │      • Dynamic Pruning, Compression, & Negative Constraints Memory   │  │  │  │
│  │  │  │  ┌────────────────────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │ 01 | PROMPT ENGINEERING (The Role & Message Boundary)          │  │  │  │  │
│  │  │  │  │      • Canonical System Prompts (.cursor/skills/aea-*/SKILL.md)   │  │  │  │  │
│  │  │  │  │      • Single Primary CTA, Zero-PII, & Anti-Hallucination Rules   │  │  │  │  │
│  │  │  │  └────────────────────────────────────────────────────────────────┘  │  │  │  │
│  │  │  └──────────────────────────────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Anchored via Type-Safe Contracts to
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ DETERMINISTIC DOMAIN SERVICES (The Source of Truth)                                    │
│ • PostgreSQL 16 Datastore (Unified Session State & pgvector semantic embeddings)       │
│ • Amazon MSK / Kafka Event Streaming & Transactional Outbox (ADR-008)                  │
│ • Fail-Closed Inventory Availability (NFR-009) & Zero-PII Payment Simulation (NFR-017) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## III. THE CONCENTRIC LAYER INVARIANTS

Kocer's analysis provides three architectural laws that govern this revision:

### Law 1: The Dependency of Higher Floors
Layer 5 assumes Layer 4 works. Layer 4 assumes Layer 3 works. Layer 3 assumes Layer 2 works. Layer 2 assumes Layer 1 works.
* If a multi-agent graph or reviewer node produces erratic outputs, the root cause is almost never the graph topology — it is a context curator failure in Layer 02 (contaminated window, stale state, unpruned tool chatter).

### Law 2: The Independent Fresh-Context Reviewer
In Layer 05, the agent that created an implementation must never be the sole entity that verifies it. Verification requires:
1. An **orthogonal model instance** (preventing symmetric model-family blindspots).
2. A **fresh, unpolluted context window** containing only the diff, the requirements, and the verification sensor criteria.

### Law 3: The Economic Asymmetry
* Foundation models are interchangeable commodities (swappable in 1 day via LiteLLM abstraction under `ADR-016`).
* The **5-layer wrapping stack, deterministic domain contracts, and Second Brain institutional memory** constitute the durable proprietary asset (swapping takes a quarter).

---

## IV. PROPOSED HARNESS EXTENSIONS (HONESTY AUDIT)

The following enhancements are **identified and proposed** for evaluation by the stakeholder team:

1. **Layer 02 Runtime Context Curator (`platform/agent/context_curator.py`)**:
   * Programmatic pre-prompt pipeline that compresses prior conversational turns, prunes voluminous tool logs, and injects only relevant negative constraints before LLM calls.
2. **Layer 05 Orthogonal Reviewer Gate**:
   * Automated CI/MRC gate invoking an isolated reviewer agent with fresh context to audit MR diffs against canonical requirements before auto-merge.
3. **Concentric Stack Diagnostic Sensor (`scripts/check_agent_stack_layers.py`)**:
   * Pre-flight diagnostic tool checking lower-layer invariants before allowing loop/graph ticks.

---

## V. REFERENCES

[1] Hashimoto, M., *Agent Harness Design & The Ratchet Principle*, 2026.  
[2]–[18] Canonical architectural references as in [[2026-08-28-aea-framework-harness-engineering]].  
[19] 0xWast3 (wast3), *Memory Engineering for Kimi*, X article, 13 Aug 2026.  
[20] GitLab Issues #288–#292 (Memory Engineering evaluations).  
[21] Kocer (@kocer_eth), *Five Layers of Agent Engineering: Each One Wraps the One Below It*, X post/article, 30 Aug 2026, https://x.com/kocer_eth/status/2094053231949177111.
