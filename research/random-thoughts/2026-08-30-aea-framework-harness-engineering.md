> **Tags**: #aea #second-brain #harness #path-b #knowledge-first
> **Captured**: 2026-08-30
> **Draft status**: proposed next version (not canonical `docs/`, not adopted, not Pages)
> **Successor of**: [[2026-08-29-aea-framework-harness-engineering]] (do not overwrite 28 Aug or 29 Aug)
> **Comparison**: `research/2026-08-30-aea-harness-vs-wast3-memory-engineering.md`
> **GitLab**: #337 (PO must accept I4–I8 before any implement issue)
> **Honesty on this revision**: I1–I3 are restatements of what AEA already does. I4–I8 are **proposed**. I9–I10 are **deferred**. I11–I15 are **rejected**. #289–#292 closed ≠ shipped.

# Production Experience Engineering Practice 2026

# Adaptive Experience Architecture

## Adaptive Experience = Shared Understanding + Domain Services + Outer Harness

### Proposed revision of 30 August 2026 — honest re-flag after a second read of [19]

*Instantiated on Lily's Florist Path B (Art of Group). Canonical remote: GitLab https://gitlab.com/artof-group/adaptive-experience-architecture. Live shop: https://aea.artof.link. Tracker is GitLab (`glab`), not GitHub.*

*Independently compiled — Art of Group / AEA knowledge guardian — not affiliated with Google, OpenAI, Anthropic, HashiCorp, or Moonshot AI — and not endorsed. 28 Aug edition used harness_final.pdf as document-design template only. 29 Aug added related work [19]. This file is the proposed **next version** of that playbook after a 30 Aug re-read of the same article. It is not a promotion into `docs/` or `docs/framework/`.*

*Vault: #aea. Existing IDs only: [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]] [[J1]] [[J2]] [[J3]] [[J4]] [[CF-048]] [[CF-054]] [[ADR-016]] [[ADR-005]]. Do not invent CF-055. Do not paste this into DATE_RE. Do not paste this onto Pages.*

**Abstract —** The 28 Aug paper stated the formula and mapped AEA onto six harness layers. The 29 Aug successor added [19] and opened evaluate tickets #289–#292. A 30 Aug re-read of the same X article (full text via fxtwitter; `x.com` 403) does not change the formula. It adds a flag set: **adopt** I1–I3 (already-true claims, say them once), **adapt** I4–I8 (rewrite for 14 hats, #275, DATE_RE, [[ADR-016]]), **defer** I9–I10, **reject** I11–I15 (new CONSTRAINTS.md, Kimi swarm, untrusted auto-edges, borrowed benches, weight training). A synthesis on main (`0aa0e60`) that says #289–#292 were adopted is a **proposal**, not a probe. Those issues closed without Done-when adopt/reject comments. [[CF-054]] remains **regressed**. Live [[J1]] after !300 remains Unknown.

**Revision policy.** Comparison or field feedback that would change a claim, a sensor, or a limitation revises this note. A status word is a claim: probe committed GitLab `main` or write Unknown. Shared memory is committed GitLab `main` only. Proposed items stay labeled proposed until `@aea-product-owner` comments adopt on the implementation issue.

## I. WHAT THIS VERSION CHANGES

Read [[2026-08-28-aea-framework-harness-engineering]] for the long form. Read [[2026-08-29-aea-framework-harness-engineering]] for the first [19] pass. This file is the successor if the team wants a version that **flags** instead of implying evaluate-tickets-closed means shipped.

| Kept | Added 30 Aug | Still Unknown |
|---|---|---|
| Formula SU + services + harness | Flag set I1–I15 | Whether PO accepts any `adapt` row |
| Six layers, 14 hats, MRC only | Honesty contradiction on #289–#292 | Live [[J1]] clip after !300 |
| [[CF-048]] verified | I1–I3 written as adopt (language only) | Moonshot claims inside [19] |
| [[CF-054]] **regressed** | I4–I8 still proposed | 14/14 independently probed here |

What this version does **not** do: implement CONSTRAINTS.md, a swarm, a new FR, a 15th hat, a shop restyle, a Pages dump, or a judge model.

## II. THE FORMULA (UNCHANGED)

Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.

[19] restates the model half of Agent = Model + Harness without touching domain services or the outer harness. A bigger window does not validate stock. A Skill folder does not replace MRC. A context graph does not disable Select when `observed_at` is stale. [[ADR-016]] stays: AI interprets; services decide.

**Adopt I1.** The context window is a workspace for one sitting, not memory. AEA already splits weight: DATE_RE is the only live handoff; `research/random-thoughts/` is archaeology; chat is not shared memory. A throwaway comment must not weigh like a hard constraint.

**Adopt I2.** Memory accumulates in the system around the model (guides, vault, CF queue, CI). Weights are not retrained between sessions.

**Adopt I3.** A claimed figure or status word needs a probe or the word Unknown. That is [[CF-048]] / [[CF-054]], not a new file.

## III. [19] EXTRACT (RELATED WORK, RE-PROBED)

Source: [19], re-probed 30 Aug 2026 via `api.fxtwitter.com` on status `2087872696109449303`. Author: 0xWast3 / wast3. Posted 13 Aug 2026 12:03 UTC. Article id `2087776707063271424`. Title: *Memory Engineering for Kimi: Why a 1M-Token Window Isn't Memory, and What Actually Is.* Claims below are the author’s. Moonshot documentation cited inside the article was not re-fetched.

Same eight moves as 29 Aug §III (empty window; replay is expensive and unweighted; separate memory layer; Skill = procedure; constraints = corrections; graph = relationships; read/write loop; “the window got bigger”). Do not treat “300 agents” as Path B evidence.

## IV. SIX LAYERS — ONLY THE DELTAS

### A. Guides — adapt I4, I5; reject I11

Feedforward stays AGENTS.md, `.cursor/rules`, 14 skills, ADRs, Path B spec. Lean by subtraction (#275). Do not add a 15th skill because [19] said “Skill.”

**Adapt I4 (proposed).** After a **verified** CF, update the owning existing skill with the procedure that worked. That is Hashimoto’s ratchet, not a new hat.

**Adapt I5 (proposed).** Write a correction only after a probe, into that owning guide or into AGENTS.md if it is cross-hat. **Reject I11:** a top-level `CONSTRAINTS.md` fights #275 and splits the guide surface.

### B. Sensors — adapt I8; reject judge models

Computational first. [[CF-054]] is **regressed**, not clip-verified.

**Adapt I8 (proposed).** Honesty today catches unprobed status words. [19] names a second class: two facts that cannot both be true, silently resolved. Prefer a guide line, then a computational surface. Escalate to `@aea-product-owner`. Do not invent CF-055. Do not add an LLM judge.

### C. Agentic loop — reject I12

One CF, one issue, one branch, one MR. Loop ticks do not merge. Only the MRC hat merges. **Reject I12:** do not copy a 300-agent swarm into this loop.

### D. Memory — adopt I1–I2; adapt I6–I7; defer I9–I10; reject I13–I15

DATE_RE is **one file**. Uncommitted files are not shared memory.

**Adapt I6 (proposed).** Name the start set and the stop set. Example only, not adopted:

```
READ  (session start): DATE_RE, AGENTS.md, matching skill
WRITE (session stop):  random-thoughts log; DATE_RE only if this session owns the handoff; never from cadence
NEVER: uncommitted files as shared memory; shop speech as a trusted edge
```

If I5 or I7 later land, they join the READ set. They are not in the READ set today.

**Adapt I7 (proposed).** Vault-only frontmatter keys `derived_from` / `constrains` / `verifies` as a thin convention. graph-guard remains an ID sensor until a later issue asks it to check those keys. **Defer I9:** typed SU / shop graph. **Defer I10:** swarm-JSON Obsidian importer. **Reject I13:** auto-edges from customer speech. **Reject I14:** Moonshot benches as AEA evidence. **Reject I15:** retraining Path B weights.

### E. Permissions

Fourteen hats. No fifteenth implementer. [[ADR-005]] latest relevant intent. Customer speech is untrusted. A Skill that writes its own constraints without a probe is producer bias with a new filename.

### F. Observability

Status words need a probe. Cost metric is cost per verified CF (and per clip-backed UX claim), not tokens. This paper states no dollar savings.

## V. WHEN NOT TO GROW MEMORY

A constraints file that restates a CI sensor is vault drift. A graph that auto-links shop speech is an injection surface. A protocol that writes DATE_RE from cadence recreates [[CF-048]]. A swarm of hats is how the 15th implementer arrives. Path B needs the minimum memory that keeps the next session honest.

## VI. PATH B EVIDENCE (UNCHANGED HONESTY)

[[CF-048]] verified: #259 / !280.

[[CF-054]] **regressed**: CSS !300 (`63aaa4ce`); queue false `verified` until !304; main is `regressed`. Live [[J1]] phone+desktop re-record after !300: Unknown. Merge is not clip-verify. Do not invent CF-055.

Not shown: adopted I4–I8, GAIA, Terminal Bench, live Stripe, 14/14 independently probed.

## VII. WHAT THE TEAM MUST STILL ACCEPT

Do not implement from this paper. Comment on the implementation-backlog issue.

| Flag | Question | Must not |
|---|---|---|
| I4 adapt | Fold verified-CF procedures into existing skills? | 15th hat; auto-Skill |
| I5 adapt | Probe-gated corrections in the owning guide? | New CONSTRAINTS.md; fight #275 |
| I6 adapt | Name start/stop set in SOP? | Cadence writes DATE_RE |
| I7 adapt | Vault frontmatter triple only? | Swarm; SU graph; new FR |
| I8 adapt | Contradiction guide (then sensor)? | CF-055; LLM judge |

If a comment is adopt, open a **second** issue for the actual file or guard. One finding, one issue, one MR. #289–#292 already closed as evaluate-only; do not reopen them to hide a missing Done-when comment. Use the new backlog issue.

## VIII. CONCLUSION

The model interprets. Domain services validate. The outer harness decides whether Lily's Florist is a product or a demo. [19] is still a clean reminder that a larger window is not a history. AEA already had the first half of that reminder. The second half is flagged, not shipped. Closed tickets are not memory.

Keep 14 hats. Keep one DATE_RE filename. Keep MRC as the only merger. Keep [[CF-054]] **regressed** until a clip dated after !300 exists.

## REFERENCES

[1]–[18] as in [[2026-08-28-aea-framework-harness-engineering]].

[19] 0xWast3 (wast3), "Memory Engineering for Kimi: Why a 1M-Token Window Isn't Memory, and What Actually Is," X article, 13 Aug 2026, https://x.com/0xWast3/status/2087872696109449303 (article id 2087776707063271424). Independently compiled related work. Not affiliated with Moonshot AI. Not an AEA result. Re-probed 30 Aug 2026 via fxtwitter API (`x.com` HTML 403; no login).

[20] 29 Aug evaluate tickets #288–#292 (closed). Synthesis `research/random-thoughts/2026-08-29-harness-memory-engineering-evaluation-synthesis.md` is a proposal, not a ship probe.

*Source method.* Proposed successor after a second live read of [19]. No clone required for the article (API). No Pages publish. Flags labeled. Unknowns labeled.
