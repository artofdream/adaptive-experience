> **Tags**: #aea #second-brain #harness #path-b #knowledge-first #kocer
> **Captured**: 2026-08-31
> **Draft status**: vault taxonomy pass (not canonical `docs/`, not adopted runtime)
> **Successor of**: [[2026-08-30-aea-framework-harness-engineering]] (do not overwrite 28 / 29 / 30 Aug)
> **Comparisons**: [[2026-08-31-aea-vs-kocer-five-layers-agent-engineering]], [[2026-08-29-aea-vs-wast3-memory-engineering]], `research/2026-08-31-aea-harness-30aug-vs-31aug.md`
> **Related**: #341 (honesty of this file) · #337 (PO decisions recorded; paper close ≠ implement) · #289 · #290 · #291 · #292 · #308 · #338 parked · #339 rejected · #340 deferred
> **Honesty on this revision**: Kocer 5-floor nesting is a **map**. Typed edges, negative-constraints memory, context curator, and an orthogonal LLM reviewer are **not** inventory. I1–I15 and K1–K10 are flagged. [[CF-054]] remains **regressed**.

# Production Experience Engineering Practice 2026

# Adaptive Experience Architecture

## Adaptive Experience = Shared Understanding + Domain Services + Outer Harness

### Revision of 31 August 2026 (Europe/Berlin) — Five Concentric Floors of Agent Engineering

*Instantiated on Lily's Florist Path B (Art of Group). Canonical remote: GitLab https://gitlab.com/artof-group/adaptive-experience-architecture. Live shop: https://aea.artof.link. Live documentation: https://architecture.artof.link. Tracker is GitLab (`glab`), not GitHub.*

*Independently compiled — Art of Group / AEA knowledge guardian — not affiliated with Google, OpenAI, Anthropic, HashiCorp, or Moonshot AI. This revision synthesizes related work from Hashimoto [1], 0xWast3 (Memory Engineering, 13 Aug 2026) [19], and Kocer (Five Layers of Agent Engineering, 30 Aug 2026) [21].*

*Vault: #aea. Existing IDs only: [[FR-001]] [[FR-003]] [[FR-007]] [[FR-008]] [[FR-009]] [[FR-011]] [[NFR-005]] [[NFR-009]] [[NFR-017]] [[J1]] [[J2]] [[J3]] [[J4]] [[CF-048]] [[CF-054]] [[ADR-016]] [[ADR-005]]. [[CF-055]] is the public-glossary finding (#300 / !331), not a contradiction CF. Do not invent a second CF-055. Do not paste this into DATE_RE.*

---

## Abstract

The 28 Aug edition stated the core formula and mapped AEA onto six harness layers. The 29 Aug revision added [19]. The 30 Aug successor **flagged** I1–I15 and recorded that #289–#292 closed ≠ shipped. This **31 Aug 2026 revision** adds Kocer's unifying insight [21]: **harness, loop, and graph are not competing choices; they are five concentric wrapping floors**. It does **not** absorb the 30 Aug flags by being newer. PO comments on #337 (31 Aug) are the decision record. 

Each layer wraps and assumes the stability of the floor beneath it:
1. **01 | Prompt Engineering** (The Message) wraps the raw model.
2. **02 | Context Engineering** (The Memory / Curator) wraps the prompt.
3. **03 | Harness Engineering** (The Machine / Execution Environment) wraps context.
4. **04 | Loop Engineering** (The System / Goal + Iterations + Budget) wraps the harness.
5. **05 | Graph Engineering** (The Topology / Multi-Node Orchestration + Reviewer) wraps the loop.

AEA **maps** this 5-floor wrapping hierarchy onto its **Outer Harness**. That is a taxonomy, not a shipped curator or reviewer. The differentiator stays: **the cognitive stack is anchored to deterministic Domain Services (PostgreSQL, Kafka, pricing, fail-closed inventory)**.

---

## I. WHAT THIS REVISION CHANGES

| Kept | Added 31 Aug (map only) | Still proposed / parked / rejected |
|---|---|---|
| Formula `SU + Domain Services + Outer Harness` | Five-floor wrapping map [21] (K1 **adapt**) | K4 **park** — runtime context curator (#338 closed) |
| Six outer-harness layers; 14 hats; MRC only | Diagnose downward (K2 **adopt**); model commodity / stack IP (K3 **adopt**) | K6 **reject** — orthogonal LLM merge gate (#339 closed) |
| I1–I3 language (30 Aug); I5 fold; I6 naming; I8 guide | Independent review = MRC + required CI (K5 **adopt**) | K7 **defer** — new stack sensor (#340 closed) |
| [[CF-048]] verified; [[CF-054]] **regressed** | Domain services drawn under the floors | I7 typed edges **defer**; I11 CONSTRAINTS.md **reject** |

---

## II. THE UNIFIED FIVE-FLOOR WRAPPING STACK IN AEA

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 05 | GRAPH ENGINEERING (Stakeholder Topology & Independent Review)                     │
│      • 14 Specialized Roles (@aea-*) — typed vault edges are I7 **deferred**, not inventory │
│      • Independent review = MRC hat + required CI (K5). Duo is not the merger.         │
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
│  │  │  │      • DATE_RE + vault. Negative constraints = I5 fold, not a new file │  │  │  │
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
* If a higher floor looks broken, probe the floor below (K2). Today that means DATE_RE / vault / guides / guards — not a runtime curator (#338 parked).

### Law 2: The Independent Fresh-Context Reviewer
In Layer 05, the hat that created an implementation must never be the sole entity that verifies it. **Already true (K5):** MRC merges; required CI jobs are computational. **Rejected (K6 / I8):** an orthogonal **LLM** as auto-merge judge. A fresh window for the MRC hat is a process rule, not a second model family.

### Law 3: The Economic Asymmetry
* Foundation models are interchangeable commodities (swappable in 1 day via LiteLLM abstraction under `ADR-016`).
* The **5-layer wrapping stack, deterministic domain contracts, and Second Brain institutional memory** constitute the durable proprietary asset (swapping takes a quarter).

---

## IV. FLAGS AND PATH B HONESTY

PO recorded on #337 / #289–#292 / #338–#340 (31 Aug 2026). Do not implement from this paper.

| ID | Flag | Item |
|---|---|---|
| I1–I3, K2, K3, K5 | **accept** (language) | Context ≠ memory; diagnose downward; model commodity; MRC+CI review |
| I5, I6, I8 | **accept** as fold / naming / guide | Existing guides and SOP. No new file. No judge model. |
| I4, I7, K7 | **defer** | Skill-after-verified-CF; vault frontmatter triple; new stack sensor |
| I9–I10, K4 | **park** | Shop graph; swarm importer; `context_curator.py` |
| I11–I15, K6 | **reject** | CONSTRAINTS.md; swarm; speech-edges; borrowed benches; weight training; LLM merge gate |

[[CF-048]] verified: #259 / !280.

[[CF-054]] **regressed**: CSS !300; live [[J1]] phone+desktop after !300 **Unknown**. Merge is not clip-verify.

[[CF-055]] is the glossary finding (#300 / !331). It is not a contradiction-sensor CF.

---

## V. REFERENCES

[1] Hashimoto, M., *Agent Harness Design & The Ratchet Principle*, 2026.  
[2]–[18] Canonical architectural references as in [[2026-08-28-aea-framework-harness-engineering]].  
[19] 0xWast3 (wast3), *Memory Engineering for Kimi*, X article, 13 Aug 2026.  
[20] GitLab Issues #288–#292 (evaluate). PO Done-when comments 31 Aug 2026. Synthesis `2026-08-29-harness-memory-engineering-evaluation-synthesis.md` is a proposal, not a ship probe.
[21] Kocer (@kocer_eth), *Five Layers of Agent Engineering: Each One Wraps the One Below It*, X post/article, 30 Aug 2026, https://x.com/kocer_eth/status/2094053231949177111.
[22] PO/PM honesty #341. Comparison `research/2026-08-31-aea-harness-30aug-vs-31aug.md`.
