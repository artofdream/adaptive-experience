> **Tags**: #aea #second-brain #harness #kocer #architecture #knowledge-first
> **Captured**: 2026-08-31
> **Draft status**: vault note (not canonical `docs/`)
> **Related**: #337 (harness revision) · #288 · #289 · #290 · #291 · #292
> **Source**: kocer (@kocer_eth), *Five Layers of Agent Engineering: Each One Wraps the One Below It*, X post / article, 30 Aug 2026, https://x.com/kocer_eth/status/2094053231949177111. Independently compiled related work. Not endorsed. Not an AEA result.
> **AEA predecessor papers**: [[2026-08-28-aea-framework-harness-engineering]], [[2026-08-29-aea-framework-harness-engineering]]
> **Memory predecessor**: [[2026-08-29-aea-vs-wast3-memory-engineering]]

# AEA vs. Kocer Five Layers of Agent Engineering (31 Aug 2026)

#aea #second-brain

---

## 1. What Kocer Actually Postulates (The 5 Wrapping Floors)

In his 30 Aug 2026 analysis, Kocer resolves the industry debate between "harness vs. loop vs. graph" not as competing paradigms, but as **concentric hierarchical wrapping floors**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 05 | GRAPH ENGINEERING (The Topology)                                  │
│      Unit: The Graph Run (Goal + Nodes + Edges + Reviewer Node)        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 04 | LOOP ENGINEERING (The System)                               │  │
│  │      Unit: The Run (Goal + Criteria + Iterations + Budget)       │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ 03 | HARNESS ENGINEERING (The Machine / Operating Env)     │  │  │
│  │  │      Unit: The Execution (Context + Prompt -> LLM -> Tools)│  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │  │  │
│  │  │  │ 02 | CONTEXT ENGINEERING (The Memory)                │  │  │  │
│  │  │  │      Unit: Window Curator (Select, Compress, Prune)  │  │  │  │
│  │  │  │  ┌────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │ 01 | PROMPT ENGINEERING (The Message)          │  │  │  │  │
│  │  │  │  │      Unit: One Input (Role, Task, Rules)       │  │  │  │  │
│  │  │  │  └────────────────────────────────────────────────┘  │  │  │  │
│  │  │  └──────────────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Core Axioms from Kocer:
1. **The Wrapping Invariant**: Each layer assumes the one below it functions. If you skip Layer 02 (Context Engineering), Layer 03's verifier keeps failing for obscure reasons, and Layer 05 (Graph) looks broken when it is actually standing on nothing.
2. **Economic Moat**: Swapping the model is a 1-day task; swapping the 5-layer engineering stack takes a quarter. The model is a commodity; the five wrapping layers around it are the actual engineering.
3. **Orthogonal Reviewer Node**: In Layer 05, the final answer must be verified by an independent reviewer node operating with a **different model** and **fresh context** (zero contaminated history).

---

## 2. Side-by-Side Architectural Comparison

| Dimension | Kocer 5-Layer Stack (30 Aug 2026) | AEA Framework (`Shared Understanding + Domain Services + Outer Harness`) | Overlap & Contrast |
|---|---|---|---|
| **Paradigm** | Pure agentic cognitive hierarchy (Prompt $\to$ Context $\to$ Harness $\to$ Loop $\to$ Graph). | Socio-technical product architecture combining transactional services with agentic governance. | AEA's Outer Harness embeds Kocer's 5 floors but anchors them to deterministic domain services. |
| **Layer 01 (Prompt)** | Unit of work: One input (role, instructions, format). | Specialized stakeholder system prompts (14 canonical roles in `.cursor/skills/aea-*/`). | Identical unit: role + strict instruction boundaries. |
| **Layer 02 (Context)** | Dynamic Curator selects, compresses, and drops prior turns, tools, docs. | Second Brain Obsidian Vault (`research/random-thoughts/`) + `daily-briefs/` + Read-Before/Write-After SOP. | Partial overlap. AEA has durable files but lacks an active in-memory runtime curator. |
| **Layer 03 (Harness)** | Gather (context + prompt) $\to$ LLM $\to$ tools $\to$ verifier $\to$ response. | Edge BFF + Gateway + LiteLLM mock/live proxy (`ADR-016`) + 14 pre-flight quality guards. | Strong match: AEA's `scripts/run_all_guards.py` is the execution verifier. |
| **Layer 04 (Loop)** | Goal + success criteria + max iterations + budget + failure retry. | Coherence Finding (CF) loop: Intake $\to$ Assessment $\to$ 1-Finding/1-Issue/1-MR $\to$ MRC auto-merge. | Match: AEA enforces single-finding iterative cycles with strict budget caps. |
| **Layer 05 (Graph)** | Graph run: nodes, edges, state schema + independent fresh-context reviewer node. | 14-role stakeholder graph + Second Brain typed edges (`derived_from`, `constrains`, `verifies`) + MRC merge gate. | AEA uses human-in-the-loop / role-specialized hats rather than an arbitrary multi-agent swarm. |
| **Source of Truth** | In-memory graph state schema + context window. | PostgreSQL 16 + Kafka + Git `main` (uncommitted files are never shared memory). | **AEA Advantage**: Immutable persistent datastores prevent hallucinated state drift. |
| **Authoritative Logic** | Delegated to agent/tool nodes. | Deterministic Domain Services (pricing, inventory availability, zero-PII checkout). | **AEA Advantage**: Client/agent presents intent; domain services mutate state. |

---

## 3. Advantages of Kocer's Model (Ideas for AEA to Steal)

1. **Resolves Harness vs. Loop vs. Graph Debates**: Proves these are not competing architectural alternatives, but concentric floors of abstraction.
2. **Failure Diagnosis by Layer Root Cause**: Provides a clear diagnostic heuristic: when a complex agent fails, inspect the layer immediately below it (e.g., verifier failure $\to$ context curator deficiency).
3. **Orthogonal Reviewer Node with Fresh Context**: Prevents self-reinforcing LLM confirmation bias by requiring the final verification pass to run in an isolated environment with a different model family.
4. **Economic Clarity**: Articulates why investing in the harness/context stack creates durable intellectual property independent of underlying foundation model churn.

---

## 4. Drawbacks & Gaps of Kocer's Model (What AEA Must Not Copy)

1. **Absence of Transactional Domain Services**: Kocer models agent workflows as closed cognitive loops. In enterprise products (like Lily's Florist), agents cannot be allowed to hallucinate inventory, price calculations, or payment confirmations.
2. **Missing Deterministic Security & Role Ratchets**: Does not specify permission boundaries, ID freezes, or fail-closed state machines.
3. **No Presentation / Dual-Viewport Consumer Layer**: Focuses exclusively on backend developer agents, omitting multi-surface adaptive UI rendering.

---

## 5. Concrete Actionable Gaps Identified for AEA

To strengthen AEA's Outer Harness against Kocer's 5-floor hierarchy:
1. **Gap 1 (Layer 02 — Context Curator Component)**: Build a dedicated runtime context curator (`platform/agent/context_curator.py`) that systematically selects, compresses, and prunes context before LLM invocation.
2. **Gap 2 (Layer 05 — Isolated Reviewer Node with Fresh Context)**: Formalize an independent review gate in CI / MRC that evaluates PR diffs using an orthogonal model in an isolated context window.
3. **Gap 3 (Concentric Layer Invariant Sensor)**: Add a pre-flight guard that verifies lower-layer health before executing higher-layer loop ticks.

Existing IDs: [[2026-08-29-harness-memory-engineering-evaluation-synthesis]], [[2026-08-29-parallel-runner-claim-rule]], [[2026-08-29-core-principles-retrospective]].
