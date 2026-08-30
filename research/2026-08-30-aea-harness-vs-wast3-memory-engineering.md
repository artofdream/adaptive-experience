> **Tags**: #aea #second-brain #harness #knowledge-first
> **Captured**: 2026-08-30
> **Draft status**: vault note (not canonical `docs/`)
> **Related**: [[2026-08-28-aea-framework-harness-engineering]] [[2026-08-29-aea-framework-harness-engineering]] [[2026-08-29-aea-vs-wast3-memory-engineering]] [[2026-08-28-where-harness-playbook-lives]] [[ADR-016]] [[ADR-005]] [[CF-048]] [[CF-054]]
> **GitLab**: #337 (implementation backlog; paper MR is Related, not Closes)
> **This revision**: independent 30 Aug re-read of the same X article already treated on 29 Aug. New work is the adopt/adapt/defer/reject flag set and the honesty check on #288–#292.

# AEA harness vs 0xWast3 memory engineering (30 Aug 2026)

#aea

This note compares one X article to the AEA outer-harness playbook. It is research scratch, not published architecture. It does not restyle the shop. It does not invent BG/US/FR/NFR IDs. It does not weaken guards.

## Sources

| Artifact | Bibliographic data | How probed this session |
|---|---|---|
| Tweet | 0xWast3 (display name wast3), https://x.com/0xWast3/status/2087872696109449303, posted 13 Aug 2026 12:03 UTC. Tweet body is only the article URL. | `x.com` HTML **403**. `nitter.net` **403**. Retrieved 30 Aug 2026 via `https://api.fxtwitter.com/0xWast3/status/2087872696109449303` (HTTP 200). No X login. |
| Article | 0xWast3, *Memory Engineering for Kimi: Why a 1M-Token Window Isn't Memory, and What Actually Is*, X article id `2087776707063271424`, created 13 Aug 2026. URL in the tweet: `https://x.com/i/article/2087776707063271424`. Preview: “Kimi K3 ships with a million-token context window. That's not memory.” | Full article text extracted from the fxtwitter `tweet.article.content.blocks` payload. Cover and inline images were **not** re-interpreted. Moonshot pages cited *inside* the article were **not** re-fetched. |
| Not a PDF | There is no arXiv / PDF for this artifact. It is an X long-form article, not a conference paper. | Do not cite arXiv `2608.02276` (Harness-R1) as this tweet. That is a different document. |
| AEA 28 Aug playbook | `research/random-thoughts/2026-08-28-aea-framework-harness-engineering.md` — *Adaptive Experience = Shared Understanding + Domain Services + Outer Harness*. Independently compiled. Not affiliated with Google / OpenAI / Anthropic / HashiCorp. | On `origin/main` as of this branch tip. |
| AEA 29 Aug successor | `research/random-thoughts/2026-08-29-aea-framework-harness-engineering.md` plus sibling `research/random-thoughts/2026-08-29-aea-vs-wast3-memory-engineering.md`. | Same tweet, already extracted 29 Aug. Issues #288–#292. |
| Placement index | `research/random-thoughts/2026-08-28-where-harness-playbook-lives.md` | Research index. Not DATE_RE. |
| Public framework site | `docs/framework/` (allowlisted Pages). `docs/framework/comparison.md` compares AEA to the coding-agent six-layer taxonomy, not to this article. | Do not paste this vault paper onto Pages. |
| Prior evaluate tickets | #288 (closed, vault-place 29 Aug paper). #289–#292 (closed, evaluate-only). Synthesis on main: `research/random-thoughts/2026-08-29-harness-memory-engineering-evaluation-synthesis.md` (`0aa0e60`). | See honesty contradiction below. |

HEAD used for this branch: `origin/main` at worktree create. Shared memory remains committed GitLab `main` only.

## What each artifact is

### The tweet / article (0xWast3)

**Scope.** A memory-layer essay for people building around Kimi K3 and Kimi Agent Swarm. Audience: coding / research swarm operators. Claim: a 1,048,576-token window is a bigger room for one sitting, not memory. Moonshot’s own write-ups (as the author cites them) describe the window as room to reason, not a retrieval architecture. Every new session opens empty.

**What it actually proposes** (from the article text, not from a paraphrase of the 29 Aug note):

1. Stop making context do memory’s job. Keep a separate layer that decides what is kept, small enough to reload cheaply.
2. Skills persist **procedure** (`SKILL.md` + scripts + references), not output. After a run you will repeat, capture the workflow.
3. A constraints file persists **corrections**. A Skill without constraints gets faster. A Skill with constraints gets faster **and** more correct. Highest leverage: when a verification pass catches a real flaw, write the lesson into a file the next run reads automatically. Example rule in the article: “no silent conflict resolution — surface contradictions.”
4. A context graph persists **relationships**, not only facts. Vendor shape: Kimi Agent Swarm (author: up to 300 agents) plus an Obsidian export of nodes and typed edges as `[[wikilinks]]`.
5. Loop: Skill + constraints + graph are read before the next run and written after it. Weights are not retrained. The system around the model accumulates memory.

Honest closer, quoted from the article: “The window got bigger. The memory still has to be engineered.”

The article’s own footer says it describes Kimi K3 and Kimi Agent Swarm features as documented by Moonshot AI as of July 2026, and that the Obsidian export pattern is an independent integration, not an official Moonshot feature. Verify at kimi.com. Those Moonshot pages were **not** re-probed here.

### AEA harness-framework-engineering

**Scope.** Working playbook for Adaptive Experience Architecture as an **outer harness** around a florist product (Lily’s Florist Path B). Audience: the 14 AEA hats. Formula: Adaptive Experience = Shared Understanding + Domain Services + Outer Harness. Six layers: guides, sensors, agentic loop, memory, permissions, observability.

**What it is not.** Not a Kimi skill pack. Not a coding-agent swarm. Not canonical `docs/` until `@aea-product-owner` promotes it. Not DATE_RE. Not the public `docs/framework/` site (that site is a lean allowlist; the 28 Aug vault paper is 715 lines and stays off Pages).

**Already true on AEA** (from the 28 Aug paper, not from 0xWast3): the model starts empty; DATE_RE is one file (`research/daily-briefs/YYYY-MM-DD.md`); uncommitted files are not shared memory; MRC hat merges; no 15th implementer; fail-closed inventory ([[FR-011]] / [[NFR-009]]); honesty = status words need a probe ([[CF-048]] verified #259 / !280; [[CF-054]] **regressed** after !304; live [[J1]] after !300 Unknown).

They overlap on “the model forgets; the system remembers.” They do not share a product.

## Advantages of the article vs AEA harness

These are advantages **as ideas**. They are not AEA results and not Path B evidence.

1. **Sharper “context ≠ memory.”** AEA already says the model starts empty. The article is sharper about **cost and weight**: replaying project history on message one is expensive, and a throwaway comment weighs the same as a hard constraint if nothing separated them.
2. **Procedure vs correction as two axes.** AEA mixes both into “guides.” The article names the failure: a Skill that only gets faster is not the memory that matters.
3. **Edges as first-class.** AEA `[[wikilinks]]` are human and sparse. `check_knowledge_graph.py` is an ID-drift **sensor**, not typed relationship memory (occasion→recipient, SKU→observation).
4. **Write-after as mandatory as read-before.** AEA recovery test is read-only (new session reads committed DATE_RE). Session-end SOP exists in AGENTS.md; compliance is uneven.
5. **Forbids silent conflict resolution.** AEA honesty today is unprobed **status words** and stale stock → unknown. It does not yet name two facts that cannot both be true.

## Drawbacks / mismatches (what does not transfer)

- **Vendor-shaped.** Kimi Skills, Agent Swarm, “up to 300 agents,” Moonshot context graph. AEA does not run that stack.
- **No domain-services layer.** A florist Available badge cannot be a graph node the model drew. [[ADR-016]] keeps AI non-authoritative.
- **No independent merge verifier.** A swarm that writes its own constraints can ratify its own mistakes. AEA: MRC only; producer bias is why the producing hat does not merge.
- **No customer-facing shop, dual viewport, fail-closed inventory, or ID freeze.**
- **Research-swarm example (100 companies) is the wrong product.** Using it as a shop design teaches the wrong system.
- **Author-cited Moonshot numbers and “300 agents” were not re-probed here.** Treat them as the author’s claims. Unknown to AEA.
- **Auto-edges from untrusted text.** Path B reads customer speech. A crafted utterance must not mint a trusted edge. [[ADR-016]] / untrusted-surface rule.

## Honesty contradiction on the 29 Aug evaluate tickets

[CONTRADICTION: `0aa0e60` synthesis on `origin/main` says #289–#292 were “Resolved” / “Adopted into repository SOP” vs GitLab Done-when comments are absent and no CONSTRAINTS / typed-frontmatter / contradiction sensor landed in `AGENTS.md` or `.cursor/`.]

Probed 30 Aug 2026:

| Ticket | GitLab state | Only comment | Done-when required | Landed in repo? |
|---|---|---|---|---|
| #288 | closed | vault-place intent | paper on main | Yes: 29 Aug papers (`b971acd`) |
| #289 | closed | Sponsor “Evaluate only… If adopt, a second issue” | adopt / reject / fold comment | **No.** `CONSTRAINTS.md` does not exist. `AGENTS.md` has no new correction-memory section from that ticket. |
| #290 | closed | same shape | adopt → second issue for thin design | **No.** No `derived_from` / `constrains` / `verifies` schema in skills or rules. |
| #291 | closed | same shape | adopt as SOP line / reject / partial | **Partial at most.** Session-start SOP already existed before the article. Synthesis “Adopted into repository SOP” overclaims a naming pass that was not a distinct SOP edit. |
| #292 | closed | same shape | adopt as guide / sensor / reject | **No.** No `[CONTRADICTION:` rule or computational sensor. |

The synthesis file is useful as a **proposal**. It is not a probe that the four items shipped. Closing evaluate tickets without the Done-when comment is a [[CF-048]]-class honesty miss on tracker status, not a new CF id. Do not invent CF-055.

## Improvements worth considering for a new aea-framework version

A proposed 30 Aug successor lives at `research/random-thoughts/2026-08-30-aea-framework-harness-engineering.md`. It does **not** overwrite the 28 Aug or 29 Aug papers. It does **not** promote into `docs/` or `docs/framework/`. Items below are flagged. Implementation waits for `@aea-product-owner` accept on specific `adopt` / `adapt` rows.

### Flag legend

- **adopt** — clearly better and in-scope (documentation or already-true claim made explicit).
- **adapt** — useful idea, must be rewritten for AEA constraints.
- **defer** — interesting, needs sponsor / PO / research.
- **reject** — conflicts with AEA ADRs, anti-fragility, fail-closed AI, 14-hat freeze, or is hype.

### Ranked flags

| ID | Idea | Flag | Evidence | Risk | What we would **not** change |
|---|---|---|---|---|---|
| I1 | State explicitly: context window is workspace, not memory; DATE_RE vs `random-thoughts/` is the weight split | **adopt** | Article §1; AEA Table V already splits these. 28 Aug paper already says the model forgets. | Low. Language-only. | DATE_RE filename. Cadence must not write DATE_RE (#274). |
| I2 | State explicitly: the system around the model accumulates memory; weights are not retrained | **adopt** | Article loop closer; AEA already ships guides + vault + CF queue, not fine-tunes. | Low if we do not claim a new memory product. | LiteLLM / NFR-003. No AEA training run. |
| I3 | Restate honesty: claimed figures need a probe or Unknown | **adopt** | Article CONSTRAINTS example (“every claimed figure must trace…”); [[CF-048]] / [[CF-054]]. | Low. Already policy. | Do not add a second honesty file. |
| I4 | After a **verified** CF, update the owning existing skill / rule (procedure capture) | **adapt** | Article Skill-after-repeatable-run. AEA skills are 14 role SOPs, not auto-captured customer workflows. | Medium: 15th-hat gravity; fights #275 prune. | Hat count stays 14. No auto-Skill generator. No new FR. |
| I5 | Write a correction only after a probe, into the **owning** guide (not a new `CONSTRAINTS.md`) | **adapt** | Article §3; #289 Done-when offered “fold into AGENTS.md.” #275 prune. Hashimoto ratchet already prefers sensor/CI. | Medium: guide bloat if every miss becomes a paragraph. | No new top-level `CONSTRAINTS.md`. No 15th skill. Sensors that already enforce a line stay the source of truth. |
| I6 | Name the session start-set and stop-set (read-before / write-after) in the **next playbook + existing SOP**, not a new protocol file | **adapt** | Article §5; AGENTS.md already has session start/end; #291. | Medium: a protocol that lets cadence write DATE_RE recreates [[CF-048]]. | Cadence still writes `YYYY-MM-DD-daily-activity.md` only. Uncommitted ≠ shared memory. |
| I7 | Lightweight typed edges in Second Brain **frontmatter** (`derived_from`, `constrains`, `verifies`) for vault notes only | **adapt** | Article §4 (edges matter); synthesis proposed this triple; graph-guard today is ID drift. | Medium: schema without a sensor is costume. Writers will ignore it. | Not a Kimi swarm. Not auto-edges from shop speech. Not a new FR. Shared Understanding ([[FR-001]] / FR-021) stays customer-visible state, not a property graph. |
| I8 | Surface contradictions: two vault facts that cannot both be true → name both, mark Unknown, escalate to PO | **adapt** | Article CONSTRAINTS example; AEA honesty is a different class (unprobed status words). Prefer a **guide** first, computational sensor later. | Medium: an LLM judge is the wrong sensor. Silent “harmony” is the failure. | Do not invent CF-055. Do not add a judge model. Do not silently pick a winner. |
| I9 | Typed relationship graph for Shared Understanding / shop entities | **defer** | Would touch product state, not only vault notes. Needs PO + possibly workbook. | High if treated as a new FR without archive. | Do not invent FR/NFR IDs. Do not restyle tiles. |
| I10 | Obsidian importer for an external swarm graph JSON | **defer** | Article Python snippet. AEA has no Kimi swarm export to import. | Low until someone runs that vendor. | Do not add a vendor SDK. |
| I11 | New `CONSTRAINTS.md` loaded every session as a 15th guide file | **reject** | Fights #275. Synthesis already preferred fold-in. A file that restates CI sensors is vault drift. | High: cognitive split + ratchet in the wrong layer. | Keep 14 skills. Keep prune. |
| I12 | Kimi Agent Swarm / 300 parallel agents / vendor Skills runtime | **reject** | Conflicts with 14-hat permission budget, MRC-only merge, one-CF loop. | High: 15th implementer arrives as a swarm. | Loop stays one CF → one issue → one branch → one MR. |
| I13 | Auto-draw trusted edges from customer speech | **reject** | [[ADR-016]] untrusted surface. Injection. | High. | Speech stays untrusted. Domain services stay authoritative. |
| I14 | Treat Moonshot 1M-window / BrowseComp / “300 agents” as AEA evidence | **reject** | Not probed on Path B. Article footer tells the reader to verify kimi.com. | High: borrowed benches (same class as GAIA / Terminal Bench refusal). | Related-work benches are not AEA results. |
| I15 | Retrain or swap Path B weights because a window is not memory | **reject** | Article itself says weights are not the memory. AEA fail-closed + NFR-003. | High cost, wrong layer. | Model remains whatever LiteLLM calls. |

## Proposed shape of the next aea-framework version (not adopted)

Keep the 28 Aug six layers and the 29 Aug related-work pass. The 30 Aug successor should:

1. **Keep** I1–I3 as explicit sentences (already true; stop implying they came from Kimi).
2. **Propose** I4–I8 as Layer-4 / Layer-1 extensions, each still labeled proposed until PO comments adopt on the implementation issue.
3. **Leave** I9–I10 in a defer appendix.
4. **Refuse** I11–I15 in a “when not to grow memory” section (already the 29 Aug §VIII shape).
5. **Correct** the synthesis overclaim: #289–#292 are closed evaluate tickets, not shipped memory features.

Do not implement from this paper. Do not treat the 29 Aug successor as already containing a 30 Aug flag set.

## Explicit non-goals

- Do not restyle the shop or Adaptive Workspace tiles.
- Do not invent BG / US / FR / NFR / CF IDs (no CF-055).
- Do not weaken, bypass, or comment out guards (`run_all_guards.py` 14/14 ratchet).
- Do not paste this onto `docs/framework/` / architecture.artof.link.
- Do not paste this into DATE_RE.
- Do not open an implementation MR from this comparison.
- Do not copy a 300-agent swarm, a vendor Skill runtime, or an LLM-as-judge contradiction sensor.
- Do not mark [[CF-054]] verified. Live [[J1]] after !300 remains Unknown unless a later session probes a clip dated after CSS.

## Retrieval limits (honest)

- `x.com` and `nitter.net` HTML: 403. Worked from fxtwitter JSON only.
- Article images: not used as evidence.
- Moonshot / kimi.com pages cited by the author: not fetched. Those claims stay Unknown to AEA.
- No PDF existed to fetch. Do not invent citations.
- Local uncommitted `research/daily-briefs/2026-08-30.md` on the dirty primary tree was **not** treated as the live bus. This worktree is `origin/main`.
- DATE_RE `research/daily-briefs/2026-08-30.md` was regenerated in this worktree after `git fetch` (`python scripts/generate_daily_brief.py`). It lists the 30 Aug harness notes. It is committed on this docs branch, not claimed as already on `main` until MRC merges.
