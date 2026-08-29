> **Tags**: #aea #second-brain #harness #knowledge-first
> **Captured**: 2026-08-29
> **Draft status**: vault note (not canonical `docs/`)
> **Related**: #288 (this note + successor paper) · #289 · #290 · #291 · #292
> **Source**: 0xWast3, *Memory Engineering for Kimi: Why a 1M-Token Window Isn't Memory, and What Actually Is*, X article 13 Aug 2026, https://x.com/0xWast3/status/2087872696109449303 (article 2087776707063271424). Independently compiled related work. Not Moonshot. Not an AEA result.
> **AEA paper (28 Aug)**: [[2026-08-28-aea-framework-harness-engineering]]
> **Successor paper (29 Aug)**: [[2026-08-29-aea-framework-harness-engineering]]
> **CF-054**: **regressed**. Live J1 after !300 Unknown. Do not invent CF-055.

# AEA vs 0xWast3 memory engineering (29 Aug 2026)

#aea

Read the X article via fxtwitter API (plain `x.com` fetch 403). No X login used. Hari Kishan's LinkedIn rewrite of a similar Kimi-memory thesis is a **different document** and is not treated as the tweet.

## What the article actually says

The tweet is a link to an X article. Thesis: Kimi K3's 1,048,576-token window is a bigger room for one sitting. It is not memory. Moonshot's own write-ups (as the author cites them) do not claim a retrieval architecture under the window. Every new session opens empty.

Memory engineering, as named there, is four moves plus a loop:

1. Stop making context do memory's job. Keep a separate layer that decides what is kept, small enough to reload cheaply.
2. Skills persist **procedure**, not output. After a run you will repeat, capture the workflow (input shape, steps, output, validation) as a Skill folder (`SKILL.md` + scripts + references).
3. Constraints files persist **corrections**. A Skill without constraints gets faster. A Skill with constraints gets faster **and** more correct. Highest leverage: when a verification pass catches a real flaw, write the lesson into a file the next run reads automatically.
4. A context graph persists **relationships**, not only facts. Flat stores throw connections away. The article's vendor shape is Kimi Agent Swarm (up to 300 agents) plus an Obsidian export of nodes and typed edges as `[[wikilinks]]`.
5. The loop: Skill + constraints + graph are read before the next run and written after it. Weights are not retrained. The system around the model accumulates memory.

Honest closer: "The window got bigger. The memory still has to be engineered."

## What AEA already is (from the 28 Aug paper, not from this article)

Adaptive Experience = Shared Understanding + Domain Services + Outer Harness. Six layers: guides, sensors, CF loop, memory (DATE_RE one file), permissions (14 hats), observability (honesty). Status words need a probe. [[CF-048]] verified (#259 / !280). [[CF-054]] **regressed** after !304. Live [[J1]] clip after !300 Unknown. Uncommitted files are not shared memory. MRC hat merges. No 15th implementer.

The article is a memory-layer essay for a coding/research swarm. AEA is an experience harness around a florist shop. They overlap on "the model forgets; the system remembers." They do not share a product.

## Side by side

| Topic | 0xWast3 / Kimi | AEA 28 Aug paper | Overlap |
|---|---|---|---|
| Context window | 1M tokens is a room, not memory | LiteLLM under NFR-003; window is not the product | Yes: empty session |
| Procedure memory | Skill folder after a repeatable run | 14 hat skills + AGENTS.md + ADRs | Partial: AEA skills are role SOPs, not captured customer-journey procedures |
| Correction memory | CONSTRAINTS.md auto-loaded | Corrections spread across rules, skills, CF notes, DATE_RE | Gap: no single correction file. #289 |
| Relationship memory | Swarm context graph to Obsidian edges | Wikilinks + graph-guard (ID drift sensor) | Gap: graph-guard is not typed relationship memory. #290 |
| Read/write loop | Read Skill+constraints+graph; write after | Recovery test + session-start SOP; write DATE_RE / random-thoughts | Partial. #291 |
| Contradictions | Surface; no silent resolve | Honesty is unprobed **status words**; fail-closed is stale stock | Gap: two facts that cannot both be true. #292 |
| Domain services | Absent | Inventory, price, delivery, payment (FR-007 / FR-011 / NFR-009) | AEA advantage |
| Merge / hats | Swarm of agents | 14 hats, one CF, MRC only | AEA advantage |
| Customer honesty | Cite sources; flag unverified figures | Status words need a probe; CF-054 false verified is the exhibit | Related, different object |
| Vendor lock | Kimi Skills, Agent Swarm, context graph | GitLab + vault + Path B runtime | Drawback of the article |

## Advantages of the article (for AEA to steal as **ideas**)

- Names the silent failure of "just keep the window." AEA already says the model starts empty; the article is sharper about **cost and weight**: a throwaway comment treated like a hard constraint.
- Splits procedure vs correction. AEA mixes both into "guides." A Skill that only gets faster is not memory that matters.
- Treats edges as first-class. AEA wikilinks are human and sparse. graph-guard checks IDs, not occasion-to-recipient or SKU-to-observation.
- Makes write-after as mandatory as read-before. AEA recovery test is read-only.
- Forbids silent conflict resolution. AEA honesty does not yet cover that class.

## Drawbacks of the article (do not copy)

- Vendor-shaped: Kimi Skills, Agent Swarm, 300 parallel agents, Moonshot context graph. AEA does not run that stack.
- No domain-services layer. A florist Available badge cannot be a graph node the model drew.
- No independent merge verifier. A swarm that writes its own constraints can ratify its own mistakes.
- No customer-facing shop, dual viewport, fail-closed inventory, or MRC.
- Research-swarm example (100 companies) is not Path B. Using it as a shop design would teach the wrong product.
- Moonshot citations inside the article were not re-probed here. Treat those benches and "300 agents" as the author's claims. Unknown to AEA.

## What could improve AEA (proposed, not adopted)

Team evaluates. Do not implement from this note.

1. **#289** — First-class correction-memory file, written only after a probe, auto-read at session start. Must not become a 15th skill. Must not fight #275 (prune guides that sensors already enforce).
2. **#290** — Typed relationship graph for vault and/or Shared Understanding. Nodes + edge types. Not a Kimi swarm. Not auto-edges from untrusted shop speech.
3. **#291** — Named read-before / write-after protocol. Must not let cadence write DATE_RE.
4. **#292** — Surface contradictions. Do not invent CF-055. Prefer a rule or computational sensor, not an LLM judge.

Procedure-capture ("save this workflow as a Skill") is **not** a fifth ticket. It folds into existing 14 skills and #275: update a skill after a verified CF; do not add a hat.

## What we are not doing

- Not pasting this onto architecture.artof.link.
- Not pasting into DATE_RE.
- Not treating the article as an official Moonshot paper.
- Not claiming AEA is now "memory engineered."
- Not restyling the shop. Not merging from implementer.
