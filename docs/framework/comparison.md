# Comparison

This page is a short public comparison: Adaptive Experience Architecture next to a six-layer harness taxonomy used for coding agents. It exists so a reader can see the sources and the limits in one place.

[What this is](#what-this-is) · [Core principles](#core-principles) · [Sources](#sources) · [Six layers compared](#same-layers-different-product) · [Agreements & differences](#where-they-agree)

## What this is

An independent Art of Group note. It maps AEA onto six harness layers (guides, sensors, loop, memory, permissions, observability) that public writing on coding agents already uses. The AEA formula stays: Shared Understanding + Domain Services + Outer Harness. [Path B](glossary.html#path-b) at [aea.artof.link](https://aea.artof.link) is the case study, not a trophy.

## What this is not

- Not an official Google paper, not an OpenAI paper, not an Anthropic paper, not a HashiCorp paper.
- Not affiliated with those organizations, and not endorsed by them.
- Not a reprint of the internal vault working paper.
- Not a leaderboard. Related-work benches (GAIA swings, Terminal Bench ranks, a million generated lines) are **not** AEA results. They were not run on Lily's Florist.
- Not AGENTS.md, not DATE_RE, not a pitch deck, not 3DX Lab.
- Not proof that Path B dual-viewport is done. That clip after the CSS is **Unknown**. **[CF-054](glossary.html#cf-nnn-coherence-finding-codes)** is **regressed**.

## Core principles

The six layers are the map. These four do not drop out of the layer names, and they are what this page is actually comparing.

1. **The formula** — Adaptive Experience = Shared Understanding + Domain Services + Outer Harness. Domain services stay authoritative. The model may interpret; it does not invent stock, price, delivery, or payment.
2. **Honesty** — a status word is a claim. Probe it on the same journey and viewport, or write **Unknown**. Merging CSS, closing a ticket, or publishing Pages is not a clip. **CF-054** stays **regressed**. The post-CSS dual-viewport clip stays **Unknown**.
3. **Knowledge First** — read committed shared memory before doing new work. Shared memory is GitLab `main`. Chat is not shared memory. An uncommitted file is not shared memory. A fluent recap is not a probe.
4. **Antifragility** — when the same miss repeats, change the strongest layer (a sensor, a gate, a permission), not another paragraph of motivation. Related work calls this a ratchet. This is the goal we pursue, end to end: the framework site, the live florist, and how the work is run. AEA is **not** there yet. Dual-viewport is still a counter-example. A check that shipped as a build is another.

These are principles, not operator SOPs. DATE_RE, AGENTS.md, and CI job catalogs stay off this site.

## Sources

Related work (cited, not inherited as AEA evidence):

1. Mitchell Hashimoto, “My AI Adoption Journey,” mitchellh.com, 5 Feb 2026. Agent mistakes get a ratchet so they do not recur.
2. Ryan Lopopolo, “Harness Engineering: Leveraging Codex in an Agent-First World,” OpenAI, 11 Feb 2026. Coding-agent field report. The million-line figure is not an AEA result.
3. Birgitta Böckeler, “Harness Engineering for Coding Agent Users,” martinfowler.com, Apr 2026. Guides and sensors vocabulary.
4. Vinay Trivedy, “The Anatomy of an Agent Harness,” LangChain Blog, 10 Mar 2026.
5. Adnan Masood, “Agentic Harness Engineering,” Google Cloud / Medium, Jun 2026. GAIA deltas are not AEA results. Not an official Google research paper.
6. LangChain Engineering, “Improving Deep Agents with Harness Engineering,” 17 Feb 2026. Terminal Bench ranks are not AEA results.
7. Lauren Tan, “How Cursor Turned AI Agents Into Better Engineers,” Aug 2026.
8. Anthropic, “Building Effective AI Agents,” anthropic.com, Dec 2024.
9. Independent compilation, “Production Agent Engineering Practice 2026” (`harness_final.pdf`). Independently compiled. Not affiliated with Google, OpenAI, or Anthropic. Used as a **document-design template** only, not as an official source of AEA evidence.
10. 0xWast3 (wast3), “Memory Engineering for Kimi,” Aug 2026. Context window is a workspace, not memory; splits procedure, correction, and relationship memory.
11. Kocer (@kocer_eth), “Five Layers of Agent Engineering: Each One Wraps the One Below It,” Aug 2026. Resolves harness vs loop vs graph as five concentric floors (prompt, context, harness, loop, graph).
12. rvaniaaa (@rvaniaaaa), “The Second Brain That Acts. The Agent Team That Remembers,” Aug 2026. Six non-overlapping roles around a compiled second brain; guardian blocks irreversible acts before executor.

Primary AEA sources (probed on GitLab `main`, not chat):

- GitLab project [artof-group/adaptive-experience-architecture](https://gitlab.com/artof-group/adaptive-experience-architecture)
- Live Path B shop [aea.artof.link](https://aea.artof.link)
- This public site, allowlisted from `docs/framework/`

## Same layers, different product

Related work often writes Agent = Model + Harness. AEA restates that for an experience: the model may interpret; domain services decide; the outer harness keeps those two honest.

### The Three Eras of Building with AI

| Era | Focus | Optimizes | Limitation |
|---|---|---|---|
| **Era 1 (2023–24)** | Single turn | Prompts, tone, magic keywords | Forgets everything when chat ends |
| **Era 2 (2025)** | What the model sees | RAG, MCP, document stuffing | Info overload; knows facts, no real actions |
| **Era 3 (2026)** | The entire system | Harness, databases, test guards | Bounded, honest, verified outcomes |

### The Five Concentric Floors

Kocer nests agent engineering into five concentric wrapping floors: Prompt (message) $\to$ Context (curator) $\to$ Harness (machine) $\to$ Loop (run) $\to$ Graph (topology). Each floor rests on the one below it. AEA maps its six outer harness layers onto this hierarchy and anchors the entire stack to deterministic domain services:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🏢 FLOOR 05: THE AGENT TEAM & GOVERNANCE (Graph Engineering)           │
│    Specialized stakeholder roles + Independent Reviewer Gate.          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 🔄 FLOOR 04: THE GOAL RUN & RETRIES (Loop Engineering)           │  │
│  │    1 Finding -> 1 Issue -> 1 Branch -> 1 MR with FinOps caps.    │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ ⚙️ FLOOR 03: THE MACHINE & TESTS (Harness Engineering)     │  │  │
│  │  │    Edge BFF + Gateway + 14 Automated Quality Guards.       │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │  │  │
│  │  │  │ 🧠 FLOOR 02: THE MEMORY CURATOR (Context Engineering)│  │  │  │
│  │  │  │    Second Brain Vault, Daily Briefs, Active Constraints│  │  │
│  │  │  │  ┌────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │ 💬 FLOOR 01: THE MESSAGE (Prompt Engineering)  │  │  │  │  │
│  │  │  │  │    14 Canonical Role Prompts, Single Primary CTA│  │  │  │  │
│  │  │  │  └────────────────────────────────────────────────┘  │  │  │  │
│  │  │  └──────────────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Built On Real Infrastructure
┌────────────────────────────────────────────────────────────────────────┐
│ 🏛️ SOLID FOUNDATION: REAL DATABASES & INVENTORY (PostgreSQL & Kafka)   │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Guides** — feedforward. Related work: AGENTS.md, negative constraints, role system prompts (Layer 01 Prompt Engineering). AEA: session-start rules, [fourteen roles](glossary.html#fourteen-hats-roles), Path B dual-viewport contract.
2. **Sensors** — feedback. Related work: tests and computational checks first (Layer 03 Harness Verifier). AEA: the same idea, plus fail-closed inventory and journey×viewport clips.
3. **Loop** — related work: goal, iterations, budget, retry on failure (Layer 04 Loop Engineering). AEA: one finding, one issue, one branch, one merge request. Only the MR coordinator merges.
4. **Memory** — related work: context window curator and typed relationship graphs (Layer 02 Context Engineering). AEA: Second Brain vault with 4 distinct memory vaults (Procedures, Corrections, Relationships, Daily Briefs). Chat is not shared memory.
5. **Permissions** — the model cannot restrict itself (Layer 05 Graph & Reviewer Governance). AEA: fourteen hats, no fifteenth implementer, [ID freeze](glossary.html#id-freeze), human confirmation for secrets and spend.
6. **Observability** — status words need a probe. Grafana is not a vibe check. Unknown is required when the probe was not run.

## Where they agree

- A fluent demo is not a production system.
- Prompt patches do not survive the next session. Environment changes do.
- Computational sensors beat asking a model whether it “feels” done.
- When the same failure repeats, fix the strongest layer (a sensor or a gate), not another paragraph.

## Where they differ

- The product. Related work is mostly coding agents. AEA is a customer-facing florist experience. Domain services stay authoritative for stock, price, delivery, and payment.
- The evidence. This page does not copy third-party bench deltas as if Path B had run them.
- The merge gate. AEA treats merge as an independent job. The hat that produced the change is not the judge of “verified.”
- Honesty as a sensor. Closing a ticket, merging CSS, or publishing Pages is not a journey clip.

## Honest Status Ledger

To avoid confusing architecture mental models with live production software, every concept on this site is explicitly flagged:

| Item / Concept | Status Flag | Operational Reality |
|---|---|---|
| **Domain Services & Backend** | **Live / Production** | PostgreSQL, Kafka, Nginx, and Edge BFF running on AWS ECS Fargate (`aea.artof.link`). |
| **Fail-Closed Availability** | **Live / Verified** | Select button automatically disables when inventory or delivery probes are stale or missing. |
| **14 Pre-Flight Quality Guards** | **Live / Verified** | Automated Python guards blocking secret leaks, skill drift, and broken traceability in CI. |
| **14 Stakeholder Hats & MRC Gate** | **Live / Operational** | Role separation and independent MR coordinator gate enforced before merging code. |
| **Second Brain Memory Vaults** | **Live / Operational** | 4-vault curated Obsidian structure (Skills, Constraints, Graph, Daily Briefs) in Git. |
| **5 Concentric Wrapping Floors** | **Taxonomy Map Only** | Conceptual framing (Kocer) adapted to explain how AEA layers nest; not a separate library. |
| **rvaniaaaa 6-Role Second Brain** | **Taxonomy Map Only** | Pattern evaluated for pre-irreversible gates; 6 generic role collapse is rejected. |
| **CF-054 Dual-Viewport Live Re-record** | **Unknown / Regressed** | CSS merged to repo, but dual-viewport side-by-side video clip re-recording remains unprobed. |
| **Live Stripe Card Gateway** | **Simulated Extension** | Runs deterministic payment simulation engine under ADR-016; live Stripe is not active. |
| **Third-Party Benchmark Scores** | **Not AEA Evidence** | GAIA, Terminal Bench, and 1M-line metrics belong strictly to cited papers [2], [6], [7]. |

## What AEA claims here

Only what has a probe, or Unknown:

- The formula and six layers are the public map.
- Path B exists as a live shop. Dual-viewport is the **intended** presentation.
- Daily-brief honesty (unprobed status words; same incident as [Claim vs probe](journal.html#claim-vs-probe) in the journal) was a real finding and was corrected in GitLab.
- Dual-viewport CSS merged. A journey on phone and desktop **after** that CSS is still **Unknown**. Do not round that up to verified.

## What AEA does not claim here

- Live Stripe, a finished dual-viewport, a 14/14 skill score, GAIA, Terminal Bench, or a million generated lines.
- Endorsement by any organization named in related work.

Back to the [framework](index.html), the [schema](schema.html), the [glossary](glossary.html), the [Path B case study](path-b.html), or the [journal](journal.html).
