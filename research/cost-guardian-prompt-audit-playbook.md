# Cost-guardian prompt-audit / cache / effort playbook

> **Captured**: 2026-09-10
> **Owner**: `@aea-cost-guardian` with `@aea-ai-engineer`
> **Traceability**: Issue #413 (X2 adapt from the 10 Sep compare)
> **Cite, do not duplicate**: [[2026-09-10-aea-vs-x-scan-gipp-beam-avid]] · #411 · !489
> **Related**: [`after-run-lesson-candidate.md`](after-run-lesson-candidate.md) (#412) — do not re-implement that SOP here

AEA already has Cost Guardian, ADR-016 fail-closed, and the assistant SLO.
This playbook writes the missing loop: prune stale instructions, use cache,
and match effort on AEA paths. Config changes are **eval-gated**. Paid API
hillclimb stays **parked** (sponsor).

The 10 Sep compare already mapped beamnxw's named actions (prompt-audit,
cost-optimize, hillclimb cheaper configs against an eval) to this ticket.
Cite that note. Do not copy it.

## Paid API hillclimb — parked (sponsor)

Do **not** spend production LLM budget to search cheaper model tiers,
prompt variants, or provider routes. That is X3 in the 10 Sep compare and
stays **parked** until the sponsor unparks it.

Eval-gated config change (below) is the allowed substitute: change a
setting, run the existing evals, keep or revert. It is not a paid sweep.

## Why this exists

Stale instructions, missing cache, and unmatched effort waste tokens.
AEA already fail-closes unpaid or unavailable providers (`ADR-016`,
`QualityMonitor`, `AEA_LOAD_TEST_MOCK_AI=1`). What was missing was a
written order of operations for harness and product AI paths.

#412 (small lesson files, no skill auto-edit) is the memory half of the
same 10 Sep map. This playbook is the token half.

## AEA paths (where tokens can leak)

| Path | Honest live status | Cost rule |
|------|--------------------|-----------|
| Intent | Optional LLM only when `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, and `AEA_AI_MODEL` are set together; else `ReferenceIntentInterpreter` | Do not call a paid model when reference/regex is enough |
| Load / CI intent | `AEA_LOAD_TEST_MOCK_AI=1` forces `ReferenceIntentInterpreter` (`LOAD-003`) | Never point load or guard traffic at a paid endpoint |
| FAQ / `POST /support` | Keyword FAQ (FR-005 / FR-009) | Do not dump generative tokens into T-01 or support |
| Retrieval `embed_text` | Local hashed bag-of-words scaffold, not a paid embedder | Do not "optimize" by adding a paid embedding API |
| AgentRuntime | Fail-closed scaffold; not wired to live support | Prepare/read only; domain services execute (`ADR-016`) |
| Harness prompts (skills, rules, briefs) | Git-versioned; monthly prune already named in session-start briefing | Prefer small files over growing one prompt |
| Assistant SLO | p95 latency budget 3.0s; availability 99.5% (`edge/scripts/check_assistant_slo.py`) | Latency/availability eval — not a token hillclimb |

Intent-cache SQL `021` is an M17 reference extension. Do not claim it as
a live shop cache.

LRU / Redis embedding cache remains a Cost Guardian *duty* when a remote
embedder exists. It is not a claim that Redis is on the live Path B path
today.

## 1. Prompt-audit (stale-instruction prune)

Run this when a skill, always-apply rule, or agent prompt grew, or when
the same guard text is restated in three places.

1. List the instruction surfaces you are about to send: role skill,
   always-apply rules, DATE_RE, and any extra vault notes.
2. Drop prose that a sensor already enforces (`check_coherence.py`,
   `run_all_guards.py`, `run_verify_job.py`, assistant SLO). The monthly
   prune in `.cursor/rules/session-start-briefing.mdc` is this step.
3. Do not paste the full vault or a stack of session logs into context.
   Read DATE_RE, then the one note or SOP the task needs.
4. Prefer a small #412 lesson candidate over appending another paragraph
   to a skill or to a giant session log.
5. Do not auto-edit `.cursor/skills/` or canonical `docs/` from an audit.
   Skill text still uses `.cursor/rules/stakeholder-skills-sync-sop.mdc`.

An audit that only deletes duplication and points at an existing guard
is in scope. An audit that rewrites product UX or weakens `ADR-016` is
not.

## 2. Cache

Use what is already wired before adding a new paid call.

| Situation | Do this |
|-----------|---------|
| Load test or high-concurrency guard | `AEA_LOAD_TEST_MOCK_AI=1` — reference interpreter, no paid tokens |
| Same retrieval query text | Reuse the local `embed_text` vector; do not introduce a hosted embedder to "cache" it |
| Static role / rule text | Let the tool load the skill once; do not re-send the full skill body every turn |
| Repeat FAQ / approved knowledge | Keyword FAQ + `QualityMonitor` fail-closed; do not regenerate approved copy |

Do not invent a Redis or LiteLLM cache ticket in this playbook. Wiring a
new cache is a separate, eval-gated change owned with `@aea-ai-engineer`.

## 3. Effort-matching

Match model and context size to the path.

| Task | Effort |
|------|--------|
| Intent when AI env is unset or load-test mock is on | Reference / regex — no flagship model |
| Keyword FAQ, T-03 ranking, inventory | Deterministic services — not LLM-ranked |
| Honest disclosure / fallback | `assistant_mode` already names `fallback` / `reference` — do not spend tokens to sound "more AI" |
| Complex synthesis the product actually asked for | Allowed only inside `ADR-016` (agent prepares; services execute) |
| Harness work (docs, CI, coherence) | DATE_RE + targeted files; not the whole Second Brain |

Unmatched effort is sending a flagship model, a full vault dump, or a
paid embedder at a path that already has a cheaper honest answer.

## Eval-gated config change

Allowed without sponsor unpark: a *named* cheaper config tried against
**existing** evals. Not allowed: a paid search across models or prompts.

1. Name the change (model key, timeout, mock vs live, prompt length,
   cache TTL) and the cheaper claim.
2. Run the eval that already exists for that surface:
   - Harness / docs / skills: `python scripts/run_all_guards.py`
   - Assistant latency / availability: `edge/scripts/check_assistant_slo.py`
   - Platform interpreters / quality / retrieval: Docker integration
     `python platform/scripts/run_integration_tests.py`
   - Edge disclosure / workspace: `python edge/scripts/run_integration_tests.py`
3. `QualityMonitor` stays fail-closed. Raw prompts and answers still must
   not land in quality events.
4. If guards, SLO, or integration fail, **revert**. Do not ship
   cheaper-but-worse. Do not weaken `ADR-016` to make a cheaper config
   pass.
5. Record the result (issue/MR note or a #412 lesson candidate). Do not
   treat a green local unit file as a paid-model bake-off.

Guards and CI *are* the eval. This repo does not run a separate model-tier
hillclimb suite.

## Hard no

- Do not spend production LLM budget to hillclimb (parked — sponsor).
- Do not change Path B shop UX from this playbook.
- Do not invent FR/NFR IDs or edit the Future workbook.
- Do not weaken `ADR-016`, inventory fail-closed, or NFR-005 disclosure.
- Do not stack unrelated DSO/CI work on a cost-playbook change.
- Do not treat the beamnxw post as AEA evidence. The compare already
  mapped X2; this playbook implements that flag only.
- Do not install a second cost-optimizer product or auto-rewrite skills.

## Who runs it

| Step | Owner |
|------|--------|
| Prompt-audit / prune / effort on harness paths | `@aea-cost-guardian` |
| Product AI path honesty (intent, FAQ, disclosure) | `@aea-ai-engineer` |
| Paid hillclimb unpark | Sponsor |
| Promote a durable token lesson | `@aea-knowledge-guardian` (via #412 candidate) |

## Pointers

- 10 Sep taxonomy (X2 adapt / X3 park):
  `research/random-thoughts/2026-09-10-aea-vs-x-scan-gipp-beam-avid.md`
- FinOps rationale (infra + `LOAD-003`):
  `research/random-thoughts/2026-08-29-finops-cost-optimization-rationale-and-enforcement.md`
- After-run lesson candidate (#412): [`after-run-lesson-candidate.md`](after-run-lesson-candidate.md)
- Role: `.cursor/skills/aea-cost-guardian/SKILL.md`
- Boundary: `docs/06-adr/ADR-016-agentic-ai-boundary.md`
