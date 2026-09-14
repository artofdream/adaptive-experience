# Session Memory Log: Agent-OS vocabulary → AEA Outer Harness (#441)

> **Tags**: #aea #session-memory #framework #keep-learning-and-apply #outer-harness #agent-coordination #honesty
> **Captured**: 2026-09-14
> **Author**: `@aea-knowledge-guardian` (Grok box, fresh clone `/workspace/aea-article-gaps-20260914/repo`)
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-12-session-memory-log-keep-learning-and-apply-principle]] · #434 · #441 · [X Article](https://x.com/0xwhrrari/status/2095497109524934750)

---

## 1. Why this note exists

Sponsor ask 2026-09-14: capture https://x.com/0xwhrrari/status/2095497109524934750 (X Article **Grok Bot: The AI Team That Never Sleeps** by 0xwhrrari / rari), compare to AEA Outer Harness, update framework where AEA benefits. Discipline: **1 finding → 1 issue → 1 MR**. Cite as external learning via Keep Learning and Apply — **not** product endorsement of Grok Bot features. CloudAgent was HELD; work ran on Grok box with a fresh isolated clone (no dirty checkouts touched).

---

## 2. Source capture (key points)

Article URL: https://x.com/0xwhrrari/status/2095497109524934750  
Article id: `2095160247639777284` · Author: rari (@0xwhrrari) · Created: 2026-09-03

**Unit of work:** chatbot returns an answer; a Bot returns a completed job (changed CRM, draft, repro, folder, sheet, review queue).

**Three control layers around the model:**
1. **Harness** — environment (computer, tools, memory, approval rules)
2. **Loop** — improvement / whether another attempt is allowed
3. **Graph** — coordination among specialists (ownership, routing, escalation)
Plus an **approval system** that decides where autonomy ends.

**Progression of trust:** bounded task → repeatable routine → schedule/trigger → handoff between agents → broader permissions only with evidence.

**Harness lessons called out:** job before task; smallest useful tool surface; **connect once, authorize per role** (plumbing ≠ permission); store work outside the conversation; shared computer is a feature **and** a security boundary; hand off login never password; **draw the approval line by reversibility** (finish reversible steps; stage irreversible).

**Loop lessons:** bounded retries; demonstrations → routines; **verification independent of the first answer** (builder ≠ checker).

**Graph lessons:** specialists not personalities; **pass ownership, not transcripts** (compact handoff packet); parallelize only independent work; grow the graph from bottlenecks.

**Autonomy ladder (AEA adopted wording for Levels 0–4):** Observe / Prepare / Execute-with-approval / Schedule-or-trigger / Coordinate-specialists — promote by evidence; demote on degradation. (Article renders ladder primarily as media; AEA vocabulary fixed in sponsor ask.)

**Irreversible park list (adopted):** send / publish / purchase / delete / production / legal.

**Handoff packet fields (adopted):** from / to / objective / artifacts / decisions / constraints / open_questions / next_gate.

---

## 3. Gap matrix

| Theme | Already in AEA | Gap | Adopted (#441) |
|---|---|---|---|
| Formula + six Outer Harness layers | Yes | — | No rewrite |
| Interpret→Act→Verify→Remember; 1→1→1 | Yes | — | No rewrite |
| Probe / Honesty / Unknown | Yes | — | No rewrite |
| Committed vault memory outside chat | Yes | — | No rewrite |
| Keep Learning and Apply | Yes (#434) | — | Cite as apply path |
| Stakeholder specialists + MRC≠implementer | Yes | Named "independent checker" vocabulary | Glossary + schema map |
| Fail-closed | Yes | — | No rewrite |
| Explicit **autonomy ladder** 0–4 | Implicit trust/evidence culture | Named levels + promotion-by-evidence | Glossary + schema |
| **Approval by reversibility** | Fail-closed + MRC gates | Named reversibility rule + park list | Glossary + schema |
| **Handoff packet** schema | Shared Understanding; vault notes | Compact multi-agent packet fields | Glossary + schema |
| **Account connection vs role authority** | Permissions layer | Explicit plumbing≠permission wording | Glossary + schema |
| Harness/Loop/Graph ↔ six layers map | Six layers exist | Explicit correspondence table | Schema section |
| Vendor Bot product claims | N/A | Risk of endorsement tone | Explicit "external learning, not endorsement"; Documented until probe |

---

## 4. Files touched (this finding)

- `docs/framework/glossary.md` — Agent coordination vocabulary (5 entries)
- `docs/framework/schema.md` — Agent coordination (Harness / Loop / Graph)
- `docs/framework/index.md` — Keep Learning pointer
- `docs/framework/journal.md` — 2026-09-14 Keep Learning entry
- `research/random-thoughts/2026-09-14-session-memory-log-agent-os-vocab-autonomy-ladder-441.md` — this note
- `research/daily-briefs/2026-09-14.md` — brief honesty touch (optional)

`scripts/build_framework_site.py` allowlist already includes glossary/schema/index/journal — **no new Pages**.

---

## 5. Honesty

| Surface | Status |
|---|---|
| Repo framework markdown | **Documented** (this MR) |
| Live Pages `architecture.artof.link` | **Unknown** until fetch after merge/deploy |
| Path B shop / florist UI | **Not applicable** — harness vocabulary only |
| FR/NFR IDs | **None invented** |

Do **not** mark Live without a probe. Do **not** treat the article as a requirement to install any third-party Bot OS.

---

## 6. Wikilinks

[[2026-09-12-session-memory-log-keep-learning-and-apply-principle]] · [[2026-09-14-session-memory-log-path-b-dual-viewport-probe]] · #434 · #441
