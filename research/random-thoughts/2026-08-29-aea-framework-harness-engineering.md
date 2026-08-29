> **Tags**: #aea #second-brain #harness #path-b #knowledge-first
> **Captured**: 2026-08-29
> **Draft status**: in progress (not canonical `docs/`)
> **Successor of**: [[2026-08-28-aea-framework-harness-engineering]] (do not overwrite)
> **Comparison**: [[2026-08-29-aea-vs-wast3-memory-engineering]]
> **Backlog**: #288 (this paper) · #289 constraints (evaluate) · #290 relationship graph (evaluate) · #291 session protocol (evaluate) · #292 contradiction surface (evaluate) · #274 DATE_RE one file · #275 prune · #273 / [[CF-054]]
> **CF-054**: CSS !300 merged; live J1 after CSS Unknown; queue on main is `regressed` after !304
> **Honesty on this revision**: proposed memory items are **identified**. They are not adopted, not implemented, and not verified. The team evaluates #289–#292.

# Production Experience Engineering Practice 2026

# Adaptive Experience Architecture

## Adaptive Experience = Shared Understanding + Domain Services + Outer Harness

### Revision of 29 August 2026 (Europe/Berlin) — memory-engineering pass

*Instantiated on Lily's Florist Path B (Art of Group). Canonical remote: GitLab https://gitlab.com/artof-group/adaptive-experience-architecture. Live shop: https://aea.artof.link. Tracker is GitLab (`glab`), not GitHub.*

*Independently compiled — Art of Group / AEA knowledge guardian — not affiliated with Google, OpenAI, Anthropic, HashiCorp, or Moonshot AI — and not endorsed. 28 Aug edition used harness_final.pdf as document-design template only. This revision adds related work from 0xWast3, *Memory Engineering for Kimi* (X article, 13 Aug 2026) [19]. That article is not an official Moonshot paper.*

*Vault: #aea. Existing IDs only: [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]] [[J1]] [[J2]] [[J3]] [[J4]] [[CF-048]] [[CF-054]]. Do not invent CF-055. Do not paste this into DATE_RE. Do not paste this onto Pages.*

**Abstract —** The 28 Aug paper stated the formula and mapped AEA onto six harness layers. This revision keeps those claims and adds one related-work pass: a 1M-token context window is a workspace, not memory [19]. AEA already knew the model starts empty (DATE_RE is the only live handoff). The article names four sharper memory primitives — stop using context as memory, persist procedure as a Skill, persist corrections as constraints, persist relationships as a graph — and a read-before / write-after loop. Those primitives are **proposed** for AEA as #289–#292. They are not in production. [[CF-054]] remains **regressed**. Live [[J1]] after !300 remains Unknown. Related-work benches are not AEA results.

**Revision policy.** Comparison or field feedback that would change a claim, a sensor, or a limitation revises this note. A status word is a claim: probe committed GitLab `main` or write Unknown. Shared memory is committed GitLab `main` only. Proposed items stay labeled proposed until a hat comments adopt / reject on the matching issue.

## I. WHAT THIS REVISION CHANGES

The 28 Aug paper remains the long form (six layers, Path B evidence, checklists). Read it. This file is the successor for anyone who needs the formula plus the memory-engineering pass in one place.

| Kept from 28 Aug | Added 29 Aug | Still Unknown |
|---|---|---|
| Formula SU + services + harness | Related work [19] | Live [[J1]] clip after !300 |
| Six layers, 14 hats, MRC only | Proposed Layer-4 extensions (#289–#292) | Whether the team adopts any of them |
| [[CF-048]] verified | Explicit: context is not memory, procedure is not correction | 14/14 skill coverage (unprobed here) |
| [[CF-054]] **regressed** | Contradiction class named (not a new CF) | Moonshot claims inside [19] |

What this revision does **not** do: implement CONSTRAINTS.md, a swarm, a new FR, a 15th hat, a shop restyle, or a Pages dump.

## II. THE FORMULA (UNCHANGED)

Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.

Related work crystallized Agent = Model + Harness [1][2][3]. Hashimoto's ratchet remains: when the agent makes a mistake, engineer a solution so it does not recur [1]. AEA keeps the ratchet and changes the product. The thing being shipped is a florist experience in which Shared Understanding is editable, recommendations are validated, and availability is fail-closed.

The model is whatever LLM Path B calls through LiteLLM under NFR-003 (≤ 2.5s). The inner runtime is the edge BFF, platform domain services, PostgreSQL, and a product-neutral broker per the ADRs. The outer harness is the 14-role team, the vault, the CF loop, and CI guards.

[19] restates the model half of that formula without touching the other two terms. A bigger window does not validate stock. A Skill folder does not replace MRC. A context graph does not disable Select when `observed_at` is stale.

## III. THE ARTICLE, EXTRACTED (RELATED WORK)

Source: [19], probed 29 Aug 2026 via `api.fxtwitter.com` on status `2087872696109449303`. Author: 0xWast3 / wast3. Posted 13 Aug 2026 12:03 UTC. The tweet body is the article URL. Claims below are the author's. Moonshot documentation cited inside the article was not re-fetched for this compilation.

1. A million-token window feels like memory. It is not. The next session opens empty. Size of the room is not whether anything stays after you leave.
2. Replay of full history at session start is expensive and silent: a throwaway comment weighs the same as a hard constraint.
3. Real memory is a separate layer that decides what is kept, small enough to reload, precise enough to use.
4. Skill = persisted procedure (`SKILL.md` + scripts + references). Capture the **process** after a run you will repeat.
5. Constraints file = persisted corrections. Highest leverage. Skill alone gets faster; Skill + constraints gets faster and more correct.
6. Context graph = persisted relationships. Flat stores throw connections away. Vendor shape: Kimi Agent Swarm (author: up to 300 agents) plus Obsidian export of nodes and edges.
7. Loop: read Skill + constraints + graph before the run; write after. The system around the model accumulates memory. Weights do not.
8. Honest closer: the window got bigger; memory still has to be engineered.

Do not treat "300 agents," BrowseComp scores, or Kimi Memory Space (those appear in other Kimi write-ups, not as AEA probes) as Path B evidence.

## IV. THE SIX LAYERS (STILL THE HARNESS)

### A. Guides

Feedforward: AGENTS.md, `.cursor/rules`, 14 skills, ADRs, Path B dual-viewport spec. Motivational language is not a guide. Lean by subtraction (#275). Date and prune (#274). Do not add a 15th skill because [19] said "Skill."

**Proposed, unevaluated (#289).** If the team wants a CONSTRAINTS.md, it is correction memory, not a new hat. Write only when a probe catches a real flaw. Auto-read at session start. If that file only restates sensors, reject it and keep #275.

### B. Sensors

Computational first: `check_coherence.py`, graph-guard, CI, fail-closed inventory [[FR-011]] / [[NFR-009]]. Clip probes are slow and human-scored. [[CF-054]] is **regressed**, not clip-verified. Path B `verified` requires a clip dated after the CSS/product merge.

**Proposed, unevaluated (#292).** Honesty today catches unprobed **status words**. [19] names a different class: two facts that cannot both be true, silently resolved. Prefer a guide or computational surface, not an LLM judge. Do not invent CF-055.

### C. Agentic loop

One CF, one issue, one branch, one MR. Loop ticks do not merge. Only the MRC **hat** merges. Escalation is a successful stop. Do not copy a 300-agent swarm into this loop.

### D. Memory and state (this is where [19] bites)

The model forgets every session. DATE_RE is **one file**: `research/daily-briefs/YYYY-MM-DD.md`. Archaeology lives in `research/random-thoughts/`. Cadence writes `YYYY-MM-DD-daily-activity.md` (after #263). Uncommitted files are not shared memory.

[19] is useful here because AEA already separates context window from DATE_RE from the vault, but it does not yet name three **kinds** of durable memory:

| Kind (from [19]) | AEA today | Proposed ticket |
|---|---|---|
| Procedure | 14 skills, ADRs, Path B spec | Fold into existing skills after a verified CF. Not a new issue. #275 still prunes. |
| Correction | Spread across AGENTS.md, rules, CF notes | #289 first-class constraints file (evaluate) |
| Relationship | Human `[[wikilinks]]`; graph-guard is a sensor | #290 typed graph for vault/SU (evaluate) |
| Session protocol | Recovery test (read DATE_RE) | #291 read-before / write-after (evaluate) |

**Proposed, unevaluated (#291).** Name the start set and the stop set. Example only, not adopted:

```
READ  (session start): DATE_RE, AGENTS.md, matching skill, constraints file if #289 adopted, graph if #290 adopted
WRITE (session stop):  random-thoughts log; DATE_RE only if this session owns the handoff; never from cadence
NEVER: uncommitted files as shared memory; shop speech as a trusted edge
```

**Proposed, unevaluated (#290).** Shared Understanding ([[FR-001]] / FR-021) is customer-visible state, not a Kimi graph. If the team wants typed edges (occasion to recipient, SKU to observation), that is a design, not a swarm. Untrusted shop speech must not mint edges without a sensor. Do not invent a new FR in this paper.

Weight. [19] is right that a throwaway comment must not weigh like a hard constraint. AEA already has that split as DATE_RE vs `random-thoughts/`. Keep it. Do not promote chat into the handoff.

### E. Permissions

Fourteen hats. No fifteenth implementer. ID freeze. Path B CSS is `@aea-ux-designer`. Merge is MRC only. Customer speech is untrusted. A Skill that writes its own constraints without a probe is producer bias with a new filename.

### F. Observability

Status words need a probe. Grafana at https://aea.artof.link/grafana/. Cost metric is cost per verified CF (and per clip-backed UX claim), not tokens. This paper states no dollar savings and no completion percentage.

## V. COMPARISON IN ONE PAGE

Advantages of [19] for AEA: sharper "context is not memory"; procedure vs correction as two axes; edges as first-class; write-after as mandatory as read-before; no silent conflict resolution.

Drawbacks of [19] for AEA: vendor lock (Kimi Skills, Agent Swarm, context graph); no domain services; no MRC; no fail-closed inventory; no dual viewport; research-swarm example is the wrong product; author-cited Moonshot numbers were not re-probed here.

AEA advantages [19] lacks: domain services as source of truth; fail-closed Available; 14-hat permission budget; CF loop; honesty rule with a live regression ([[CF-054]]); committed-main as the only shared memory.

Full table: [[2026-08-29-aea-vs-wast3-memory-engineering]].

## VI. PATH B EVIDENCE (UNCHANGED HONESTY)

[[CF-048]] verified: #259 / !280.

[[CF-054]] **regressed**: knowledge !298, spec !299 (closed #272), CSS !300 (`63aaa4ce`). Queue said `verified` until !304 (28 Aug 22:14 Berlin) — a **false verified**. Main is `regressed`. Live [[J1]] phone+desktop re-record after !300: Unknown. Merge is not clip-verify. Do not invent CF-055.

Honest leftovers from 2026-08-27 clips remain: [[J3]] recall without reorder badge; [[J4]] ASO fail-closed, not T-08; Track gated until checkout.

Not shown: GAIA, Terminal Bench, million lines, live Stripe, 14/14 independently probed, adopted #289–#292.

## VII. WHAT THE TEAM MUST EVALUATE

Do not implement from this paper. Comment on the issue.

| Issue | Question | Must not |
|---|---|---|
| #289 | Adopt a CONSTRAINTS.md (or fold into AGENTS.md)? | Become a 15th skill; fight #275 |
| #290 | Typed edges for vault and/or SU? | Copy Kimi swarm; invent an FR |
| #291 | Name read-before / write-after in the SOP? | Let cadence write DATE_RE |
| #292 | Surface contradictions as a rule or sensor? | Invent CF-055; add an LLM judge |

If a comment is adopt, open a **second** issue for the actual file or guard. One finding, one issue, one MR.

## VIII. WHEN NOT TO GROW MEMORY

A constraints file that restates a CI sensor is vault drift. A graph that auto-links shop speech is an injection surface. A protocol that writes DATE_RE from cadence recreates [[CF-048]]. A swarm of hats is how the 15th implementer arrives. Path B needs the minimum memory that keeps the next session honest, not the maximum that a 1M window could hold.

## IX. CONCLUSION

The model interprets. Domain services validate. The outer harness decides whether Lily's Florist is a product or a demo. [19] is a clean reminder that a larger window is not a history, and that procedure, correction, and relationship are different memories. AEA already has the first half of that reminder (DATE_RE, skills, vault). The second half is proposed, not shipped.

Keep 14 hats. Keep one DATE_RE filename. Keep MRC as the only merger. Keep [[CF-054]] **regressed** until a clip dated after !300 exists. Lean by subtraction. The harness accumulates only what a probe earned.

## REFERENCES

[1]–[18] as in [[2026-08-28-aea-framework-harness-engineering]].

[19] 0xWast3 (wast3), "Memory Engineering for Kimi: Why a 1M-Token Window Isn't Memory, and What Actually Is," X article, 13 Aug 2026, https://x.com/0xWast3/status/2087872696109449303 (article id 2087776707063271424). Independently compiled related work. Not affiliated with Moonshot AI. Not an AEA result. Probed 29 Aug 2026 via fxtwitter API (x.com HTML 403; no login).

[20] GitLab issues opened this revision: #288 (vault placement), #289 (constraints, evaluate), #290 (typed graph, evaluate), #291 (session protocol, evaluate), #292 (contradiction surface, evaluate).

*Source method.* Successor of the 28 Aug vault paper after a live read of [19]. No clone. No Pages publish. Proposed items labeled. Unknowns labeled. Comparison that would change a claim revises this note.
