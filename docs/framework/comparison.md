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

Primary AEA sources (probed on GitLab `main`, not chat):

- GitLab project [artof-group/adaptive-experience-architecture](https://gitlab.com/artof-group/adaptive-experience-architecture)
- Live Path B shop [aea.artof.link](https://aea.artof.link)
- This public site, allowlisted from `docs/framework/`

## Same layers, different product

Related work often writes Agent = Model + Harness. AEA restates that for an experience: the model may interpret; domain services decide; the outer harness keeps those two honest.

Kocer nests agent engineering into five concentric wrapping floors: Prompt (message) $\to$ Context (curator) $\to$ Harness (machine) $\to$ Loop (run) $\to$ Graph (topology). AEA maps its six outer harness layers onto this hierarchy and anchors the entire stack to deterministic domain services:

1. **Guides** — feedforward. Related work: AGENTS.md, negative constraints, role system prompts (Layer 01 Prompt Engineering). AEA: session-start rules, [fourteen roles](glossary.html#fourteen-hats-roles), Path B dual-viewport contract.
2. **Sensors** — feedback. Related work: tests and computational checks first (Layer 03 Harness Verifier). AEA: the same idea, plus fail-closed inventory and journey×viewport clips.
3. **Loop** — related work: goal, iterations, budget, retry on failure (Layer 04 Loop Engineering). AEA: one finding, one issue, one branch, one merge request. Only the MR coordinator merges.
4. **Memory** — related work: context window curator and typed relationship graphs (Layer 02 Context Engineering). AEA: Second Brain vault, one daily handoff filename. Chat is not shared memory.
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
