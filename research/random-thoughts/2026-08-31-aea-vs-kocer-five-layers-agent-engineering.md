> **Tags**: #aea #second-brain #harness #kocer #architecture #knowledge-first
> **Captured**: 2026-08-31
> **Draft status**: vault note (not canonical `docs/`)
> **Related**: #341 (honesty) · #337 (PO decisions) · #288 · #289 · #290 · #291 · #292 · #338 parked · #339 rejected · #340 deferred
> **Source**: kocer (@kocer_eth), *Five Layers of Agent Engineering: Each One Wraps the One Below It*, X post / article, 30 Aug 2026, https://x.com/kocer_eth/status/2094053231949177111. Independently compiled related work. Not endorsed. Not an AEA result.
> **AEA predecessor papers**: [[2026-08-28-aea-framework-harness-engineering]], [[2026-08-29-aea-framework-harness-engineering]], [[2026-08-30-aea-framework-harness-engineering]]
> **Memory predecessor**: [[2026-08-29-aea-vs-wast3-memory-engineering]], `research/2026-08-31-aea-harness-30aug-vs-31aug.md`

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
| **Layer 02 (Context)** | Dynamic Curator selects, compresses, and drops prior turns, tools, docs. | DATE_RE + Second Brain vault + session SOP. Runtime curator is K4 **parked** (#338). | Files exist. A curator process does not. |
| **Layer 03 (Harness)** | Gather (context + prompt) $\to$ LLM $\to$ tools $\to$ verifier $\to$ response. | Edge BFF + Gateway + LiteLLM mock/live proxy (`ADR-016`) + 14 pre-flight quality guards. | Strong match: AEA's `scripts/run_all_guards.py` is the execution verifier. |
| **Layer 04 (Loop)** | Goal + success criteria + max iterations + budget + failure retry. | Coherence Finding (CF) loop: Intake $\to$ Assessment $\to$ 1-Finding/1-Issue/1-MR $\to$ MRC auto-merge. | Match: AEA enforces single-finding iterative cycles with strict budget caps. |
| **Layer 05 (Graph)** | Graph run: nodes, edges, state schema + independent fresh-context reviewer node. | 14-role hats + MRC merge gate. Vault typed edges (`derived_from`, `constrains`, `verifies`) are I7 **deferred**, not inventory. | AEA uses human-in-the-loop hats. Orthogonal LLM reviewer is **rejected** (K6). |
| **Source of Truth** | In-memory graph state schema + context window. | PostgreSQL 16 + Kafka + Git `main` (uncommitted files are never shared memory). | **AEA Advantage**: Immutable persistent datastores prevent hallucinated state drift. |
| **Authoritative Logic** | Delegated to agent/tool nodes. | Deterministic Domain Services (pricing, inventory availability, zero-PII checkout). | **AEA Advantage**: Client/agent presents intent; domain services mutate state. |

---

## 3. Advantages of Kocer's Model (Ideas for AEA to Steal)

1. **Resolves Harness vs. Loop vs. Graph Debates**: Proves these are not competing architectural alternatives, but concentric floors of abstraction.
2. **Failure Diagnosis by Layer Root Cause**: Provides a clear diagnostic heuristic: when a complex agent fails, inspect the layer immediately below it (e.g., verifier failure $\to$ context curator deficiency).
3. **Independent fresh-context review**: Steal the *independence* (already MRC + CI). Do **not** steal a different model family as the merger (K6 **reject**).
4. **Economic Clarity**: Articulates why investing in the harness/context stack creates durable intellectual property independent of underlying foundation model churn.

---

## 4. Drawbacks & Gaps of Kocer's Model (What AEA Must Not Copy)

1. **Absence of Transactional Domain Services**: Kocer models agent workflows as closed cognitive loops. In enterprise products (like Lily's Florist), agents cannot be allowed to hallucinate inventory, price calculations, or payment confirmations.
2. **Missing Deterministic Security & Role Ratchets**: Does not specify permission boundaries, ID freezes, or fail-closed state machines.
3. **No Presentation / Dual-Viewport Consumer Layer**: Focuses exclusively on backend developer agents, omitting multi-surface adaptive UI rendering.

---

## 5. Gaps — flagged, not a build list

PO (31 Aug 2026) on #337 / #338–#340. Do not treat this section as implement-now.

1. **Gap 1 — runtime context curator**: **park** (K4). #338 closed. Easy to become I11 CONSTRAINTS injection.
2. **Gap 2 — orthogonal LLM reviewer**: **reject** (K6). Fresh-window **MRC + required CI** is already true (K5). #339 closed.
3. **Gap 3 — new stack-layer sensor**: **defer** (K7). #340 closed. Must not weaken the 14-guard ratchet or assume a curator that does not exist.

Existing IDs: [[2026-08-29-harness-memory-engineering-evaluation-synthesis]], [[2026-08-29-parallel-runner-claim-rule]], [[2026-08-29-core-principles-retrospective]].
