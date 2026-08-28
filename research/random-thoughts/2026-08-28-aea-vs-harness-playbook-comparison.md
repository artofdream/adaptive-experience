#aea

# AEA draft vs. harness playbook template

> **Tags**: #aea #second-brain #harness #path-b #knowledge-first
> **Captured**: 2026-08-28
> **Draft status**: in progress (not canonical `docs/`)
> **Related**: [[2026-08-28-aea-framework-harness-engineering]] [[2026-08-28-where-harness-playbook-lives]]
> **CF-054**: **regressed** on main after !304 (was false `verified`); live [[J1]] after !300 Unknown
> **Revision policy**: comparison or field feedback that would change a claim, a sensor, or a limitation revises the playbook. Do not leave the playbook stale while this sibling is more honest.

**A.** `/workspace/aea-paper/harness_final.pdf` — *Production Agent Engineering Practice 2026 / Harness Engineering / Agent = Model + Harness: The 6-Layer Production Playbook.* Independently compiled, August 2026. Header/footer carry a "Google" mark; the disclaimer states it is **not affiliated with Google, OpenAI, Anthropic, or HashiCorp, and not endorsed.** It is a practice note / visual template. **It is not an official Google research paper.**

**B.** `research/random-thoughts/2026-08-28-aea-framework-harness-engineering.md` (local PDF optional) — *Adaptive Experience Architecture: Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.* Independently compiled, August 2026, Art of Group / AEA knowledge guardian. Instantiated on Lily's Florist Path B. Same document design, different claims. Vault: #aea. Existing IDs only: [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]] [[J1]] [[J2]] [[J3]] [[J4]] [[CF-048]] [[CF-054]].

This note compares the two. No new AEA metrics. Unknowns labeled. GitLab MCP `user-GitLab` is now used (no clone; `glab` is the tracker, not `gh`).

---

## 1. Similarities

Both are short IEEE-ish practice notes (A: 9 pages, B: 8 pages), Letter, Helvetica titles, Times body, Courier for templates, two-column after Fig. 1, compact tables, glossary, references, Source Method footer.

Both use **six layers** with the same names and the same steering geometry: Guides (feedforward) and Sensors (feedback) around an Agentic Loop; Memory, Permissions, and Observability as the runtime foundation. Fig. 1 is an ASCII 2×3 box in both.

Both inherit Fowler/Böckeler **guides-and-sensors**, Hashimoto's **ratchet** (encode the failure class so it does not recur), inner vs. outer harness, computational sensors before LLM-as-judge, escalation as a first-class outcome, a recovery test for memory, a production checklist, a "when not to build/grow" filter, and a multi-agent extension (typed handoffs + independent verifier).

Both refuse to treat prompt engineering as enough. Both say the harness, not the model, is the product team's moat. Both cite the same related-work spine [Hashimoto, Lopopolo/Codex, Böckeler/Fowler, LangChain, Tan/Cursor] — in B, strictly as related work.

Section numbering is deliberately parallel (I–XII, then XVI–XVIII, XIV twice, XV), including the template's skipped XIII.

---

## 2. Differences

| Axis | A — template playbook | B — AEA draft |
|---|---|---|
| Formula | Agent = Model + Harness | Adaptive Experience = Shared Understanding + Domain Services + Outer Harness |
| Product | Generic coding / ops / research agent | Lily's Florist Path B (AI-native florist; dual viewport) |
| Model | Unspecified LLM / Codex | Whatever Path B calls via LiteLLM; NFR-003 ≤ 2.5s |
| Evidence | Third-party benches: 95% fail claim; GAIA 30.91→74.55 (+43.64); Terminal Bench 30th→5th; 1M lines / 0 manual | Probed AEA only: [[CF-048]] #259/!280; dual-viewport !298/!299/!300 + #272; [[CF-054]] **regressed** on main after !304 (was false `verified`; live [[J1]] re-record after !300 **Unknown**); fail-closed [[FR-011]]/[[NFR-009]]; 2026-08-27 clip leftovers. **Does not inherit A's numbers.** |
| Loop | Plan → execute → verify → fix, retry budget (defaults: 3 retries, 30 min, $5, 50 tool calls) | One CF → one GitLab issue → one branch → one MR; **one layer per finding**; loop ticks must not merge and must not restyle Path B CSS unless `@aea-ux-designer`; only @aea-mr-coordinator merges. **Does not copy A's $5 / 3 retries / 80% completion.** |
| Guides | AGENTS.md / CLAUDE.md / .cursorrules, generic | AGENTS.md SOP; four .cursor/rules; 14 skills `aea-*`; ADRs; FR/NFR workbook; Path B dual-viewport spec |
| Sensors | Linter, tests, schema, LLM-as-judge | `check_coherence.py`, graph-guard, `run_all_guards.py`, GitLab CI, fail-closed inventory, journey×viewport clips ([[CF-054]]). DATE_RE 14/14 is a generator claim, **not** independently probed |
| Memory | plan.md / decisions.jsonl / filesystem checkpoint | DATE_RE `research/daily-briefs/YYYY-MM-DD.md` is the only live handoff; `random-thoughts/` is archaeology; cadence writes `YYYY-MM-DD-daily-activity.md` after #263; uncommitted ≠ shared memory |
| Permissions | Tool/file capability budgets | **14 hats, no 15th implementer**; ID freeze; UX owns Path B CSS; workbook/archive need human confirm; knowledge MR does not close a UI finding |
| Observability | Trace, cost, generic trip wires | Grafana `aea.artof.link/grafana/`; CF Last seen; honesty rule (status words need a probe); cost metric is **cost per verified CF** (and clip-backed UX claim), not tokens; CloudWatch for LiteLLM; DATE_RE trip ([[CF-048]]) |
| Build path | Fake-seven-day greenfield to MVP harness | Layers already instantiated unevenly; strengthen from CFs. DATE_RE 2026-08-28 Active Focus **Unknown**. Do not claim M14–M18 production-ready. Backlog #273 (!304 merged; clip Unknown) #274 (this MR) #275 (queued) is in progress, not done |
| Multi-agent | Generic producer/verifier agents | 14 named hats; typed handoffs via GitLab issue/MR + vault; MRC is the independent verifier |
| Tracker | Implicit Git | GitLab (`glab`). GitHub is a one-way mirror. MCP `user-GitLab` used for this revision (no clone) |
| Honesty posture | Implicit in sensors | Explicit: [[CF-048]] as AEA's "demos that never ship"; [[CF-054]] **regressed** on main after !304; clip after CSS Unknown |

---

## 3. Advantages of each

### A (template playbook)

- **Portable.** One six-layer sketch covers coding agents, research agents, and ops agents without a product vault.
- **Rhetorical punch.** Bench deltas (GAIA, Terminal Bench, Codex 1M lines) make the "harness beats model" claim vivid for readers who have never seen Path B.
- **Greenfield on-ramp.** The seven-day path and numeric loop bounds (retries, dollars, tokens) are easy to copy into a new repo.
- **Generic multi-agent.** Typed handoffs + independent verifier apply even when you do not have fourteen named hats.
- **Design completeness.** The visual system (Fig. 1, Tables I–XVII, templates, glossary) is a finished teaching object. B copied that shape on purpose.

### B (AEA draft)

- **Falsifiable on a shop.** Claims are tied to FR/NFR IDs, CF numbers, GitLab MRs, and a live URL. A reader can disagree with a row, not just a slogan.
- **Honesty as a sensor.** [[CF-048]] and the DATE_RE trip wire name a failure class A's generic "quality drift" table leaves vague: status words without a probe. Reporting [[CF-054]] as **regressed** after main's false `verified` (corrected by !304) is the same sensor.
- **Permissions that match a real org.** Fourteen hats + ID freeze + MRC-only merge + UX CSS ownership are stronger than a file glob allow-list for an experience system, because the blast radius is a customer-facing florist, not a local branch.
- **Product-shaped loop.** One-finding GitLab routing beats unbounded Plan-Execute-Retry when many hats share main.
- **Won't borrow benches.** Refusing GAIA/+43.64/Terminal Bench/1M lines as AEA results is itself an advantage: B cannot be accused of decorating a florist with coding-agent trophies.
- **Lean by subtraction.** Not a 15th skill. Delete guide/skill lines CI already enforces (#275 queued). Cost is per verified CF (and clip-backed UX claim), not tokens. Ratchet at the strongest layer (sensor/CI). Same error 3× becomes a sensor. Escalation to MRC/PO is a successful stop. Trusted guides (`docs/`/spec) are not live-shop evidence.
- **Inner runtime is named.** Edge BFF + domain services + PostgreSQL + broker-per-ADRs sits beside the outer harness. A collapses "inner" to lab-built model safety.
- **Revision policy.** Comparison feedback revises B. That is how this note forced CF-054 language to **regressed** / false verified on main, and how !304 is named as merged (22:14 Berlin) rather than assumed still open.

---

## 4. Drawbacks of each

### A (template playbook)

- **Affiliation theatre.** A "Google" footer plus a not-affiliated disclaimer invites misreading. Treat A as an independent compilation, not Google research.
- **Evidence is not yours.** 95% fail, GAIA +43.64, 25 Terminal Bench ranks, 1M lines belong to cited third parties. They do not transfer to a florist, a vault, or a 14-hat team.
- **Coding-agent bias.** Guides = linters and AGENTS.md; sensors = unit tests; memory = plan.md. That mapping under-specifies Shared Understanding, fail-closed inventory, dual viewport, and payment-mockup honesty.
- **Numeric defaults that look like policy.** "$5 per task," "3 retries," "completion rate ≥ 80%" are teaching placeholders. Copying them into AEA would invent metrics.
- **Seven-day greenfield** hides the cost of an already-living vault. AEA cannot honestly start on Day 1 with a blank AGENTS.md.
- **Multi-agent is abstract.** No named verifier, no merge owner, no rule against a shadow 15th implementer.

### B (AEA draft)

- **Narrow audience.** Useless to a team that is not shipping Path B or a close cousin. The 14 hat names are load-bearing, not decorative.
- **Evidence is thin by A's standards.** One verified CF ([[CF-048]]), one dual-viewport trail that is **regressed** not clip-verified ([[CF-054]]), clip leftovers, and a specified fail-closed rule. No completion rate, no $/journey (Unknown), no DATE_RE 14/14 probe (Unknown). Readers who wanted a bench swing will find a case file.
- **Harness weight.** Fourteen skills, four always-on rules, CF queue, MRC, DATE_RE, graph-guard: easy to overfit. B's own limitation section names the 15th hat and DATE_RE pollution. Whether the current harness is already too heavy is **Unknown**. Guide prune is #275 (queued), not this MR.
- **Queue lag is visible.** CSS !300 merged; !304 merged and set main to `regressed` (was false `verified`). Finding note on main after !304 is `regressed` / #273. Clip after CSS Unknown. Honesty is not the same as a closed loop. Live [[J1]] after !300: Unknown.
- **Design twin, not a new visual language.** B will be read as a reskin of A. That is intended (template match) and a citation risk if someone treats B as the source of A's benches.

---

## Bottom line

A is a **coding-agent field manual** with borrowed benches and a reusable six-layer sketch. B is an **experience-system instantiation** of that sketch on Lily's Florist Path B, with a different formula, a 14-hat permission model, an honesty sensor, and a GitLab one-finding loop. Use A to explain why harness engineering exists. Use B to see what it looks like when the "agent" is a shop that must not lie about flowers. Do not mix the evidence columns. Do not treat !304 as clip-verify. Do not copy A's `$5` / 3 retries / 80% completion into AEA. Comparison or field feedback that would change a claim, a sensor, or a limitation revises B; do not leave the playbook stale while this sibling is more honest.

*Independently compiled, 28 August 2026 evening Berlin. Not affiliated with Google, OpenAI, Anthropic, or HashiCorp. Related #274. Tracker is GitLab (`glab`), not GitHub.*
