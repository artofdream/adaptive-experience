# 10 Sep X-scan: gipp / beam / avid vs AEA Outer Harness

> **Tags**: #aea #second-brain #harness #x-scan #memory #cost #agentic-stack
> **Captured**: 2026-09-10
> **Author**: `@aea-knowledge-guardian` with `@aea-product-owner` (taxonomy accept only)
> **Draft status**: vault compare (not Path B product; not a new FR/NFR)
> **Related**: [[2026-09-01-aea-vs-rvaniaaaa-second-brain-agent-team]] · [[2026-09-01-aea-framework-harness-engineering]] · [[2026-08-31-aea-framework-harness-engineering]] · [[ADR-016]] · [[CF-054]] · #411 · #412 · #413
> **Public map**: `https://architecture.artof.link/` · `docs/framework/comparison.md`

---

## Probe honesty

x.com returned **403** from this session. Post text was recovered 2026-09-10 via fxtwitter API for:

| Post | Claimed topic |
|---|---|
| [gippp69/2097659069456654812](https://x.com/gippp69/status/2097659069456654812) | Dual loop: task + reviewer; small reusable lesson files |
| [beamnxw/2097746415632155110](https://x.com/beamnxw/status/2097746415632155110) | Claude cost playbook (audit / cache / effort) + agent-memory article quote |
| [Av1dlive/2097639365644279857](https://x.com/Av1dlive/status/2097639365644279857) | Shared “second brain” prompt (Agentic Stack + Karpathy wiki gist) |

These are **related commentary**, not AEA evidence. Anthropic “just dropped” and “Grok engineer” claims were **not** independently verified beyond the post text. [[CF-054]] stays **regressed**. No FR/NFR IDs invented.

---

## Concepts (extracted)

### gipp — dual-loop after-run learning

- Most agents drop what failed, what changed, and which fix worked when the task ends.
- Two loops: one does the work; one reviews, extracts a lesson, stores it for the next run.
- Prefer **small memory files** over growing one giant prompt.
- One solid correction reused across later tasks.

### beam — cost playbook + memory architecture

- Stale instructions, missing cache, and unmatched effort waste tokens.
- Named actions: prompt-audit, cost-optimize, hillclimb cheaper configs **against an eval**.
- Quoted article: persistent queryable agent memory beats stuffing chat; a smaller model with a better harness/memory can beat a larger model without one.

### avid — shared wiki / second brain prompt

- Pain: 12k sessions / tool-switching; re-explaining the project.
- Portable wiki with inbox → catalog → compiled pages; **provenance** (source ID, digest, approval).
- **Knowledge ≠ authority**: imported chats do not override the current request or live tool rules.
- Two retrieval paths: original conversation vs compiled wiki. Verify connections; do not claim “installed = works.”
- Bounded first import; exclude secrets; staging; no silent background sync unless tested.

---

## Advantages vs AEA

| Pattern | Advantage (theirs) | AEA already |
|---|---|---|
| Dual-loop lessons | Mechanical extract after **every** run | Session-end SOP + DATE_RE + vault; optional, not automatic |
| Small lesson files | Cheap reuse without prompt bloat | `research/random-thoughts/` + inbox; git-versioned |
| Prompt-audit / cache / effort | Explicit token FinOps loop | `@aea-cost-guardian` + ADR-016 fail-closed + assistant SLO |
| Eval-gated cheaper config | Prevents silent quality drop | Guards/CI are the eval; not a model-tier hillclimb |
| Provenance + knowledge≠authority | Safer ingest of chat dumps | Domain services decide; inbox ≠ `docs/`; 6-way skill pointers |
| Cross-tool wiki | One brain across Cursor/Claude/Codex | Canonical `.cursor/skills/` + adapters; DATE_RE single live bus |

---

## Disadvantages / reject

| Pattern | Disadvantage | AEA stance |
|---|---|---|
| Ungoverned self-improve | Reviewer can fabricate “lessons” into skills | **Reject** auto-edit of `.cursor/skills/` or canonical `docs/` |
| Paid hillclimb | Spends production LLM budget | **Park** (sponsor) |
| Agentic Stack / extra SecondBrain tree | Second product; invents sync | **Reject** install; AEA vault stays `research/` + `docs/` |
| Conversation ingest without approval | Secrets / PII / tool dumps | Bounded import; backups out of git |
| “Memory of a goldfish” rhetoric | Ignores live domain services | Shop memory is session + inventory, not only a wiki |

AEA advantages they lack: fail-closed inventory, MRC no-self-merge, 14-hat freeze, honesty/Unknown, Path B probes.

---

## Improvements (flagged only)

| ID | Flag | Improvement | Ticket |
|---|---|---|---|
| X1 | **adapt** | After-run **lesson candidate** in `research/inbox/` (failed / changed / worked). Promote only via Knowledge Guardian | #412 |
| X2 | **adapt** | Cost-guardian playbook: prune stale instructions, cache, match effort; eval-gated | #413 |
| X3 | **park** | Paid API hillclimb | sponsor |
| X4 | **reject** | Install Agentic Stack or a second SecondBrain product | — |
| X5 | **adapt** | Keep provenance + knowledge≠authority language in vault SOPs (already mostly true) | this note |
| X6 | **reject** | Auto-self-modifying prompts / skill auto-merge | — |

Paper close ≠ implement. #411 is this compare + public cite + paper/PDF revision only.
