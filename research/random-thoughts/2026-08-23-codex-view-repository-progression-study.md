# Codex View: AEA Repository Progression Over Time

> **Tags**: #aea #second-brain #codex #project-history #repository-evolution #lessons-learned
> **Captured**: 2026-08-23
> **Role Context**: @aea-knowledge-guardian
> **Period reviewed**: 2026-08-09 through 2026-08-23
> **Companion extraction**: [[2026-08-23-session-memory-log-cross-chat-knowledge-extraction]]

---

## Why this perspective matters

This study follows the repository as Codex encountered it across successive
tasks. It is not only a commit chronology. It records how the available
evidence changed, how Codex's interpretation changed with it, and where later
evidence invalidated earlier confidence.

The progression is best understood as six evidence transitions:

```text
canonical documents
  → exact coherence and governance
  → executable platform/edge foundation
  → journey and pilot integration
  → autonomous loops and multi-model governance
  → extension acceleration
  → runtime-honesty reconciliation
```

Dates and examples are grounded in accessible Codex/ChatGPT task histories and
repository Git history. Commit subjects describe author intent at the time;
they are not automatically accepted as proof that the subject's capability was
fully delivered.

---

## Phase 0 — Before the executable repository: document and workbook design

### Codex/ChatGPT view at the time

The earliest accessible sessions operated on uploaded XLSX, DOCX, PDF, and
wireframe assets. The main work was to make the architecture narrative
internally consistent:

- Introduce the persistent Adaptive Workspace.
- Align the event-driven user journey with the requirements hierarchy.
- Add architecture-derived FR-018–023 and NFR-015–017.
- Clarify AI interpretation versus authoritative service validation.
- Add T-08 tracking and Future T-09 escalation.
- Improve wireframe annotations and requirement traceability.
- Rename a short architecture matrix as representative rather than exhaustive.
- Add governance and observability verification language.

### What Codex learned

Document coherence was initially evaluated visually and semantically. This was
useful for shaping the architecture, but it did not create reproducible proof.
Repeated “9.9/10” style assessments were subjective and depended on the latest
uploaded artifact. They helped find gaps, but scores were not calibrated.

### Lasting outcome

The conceptual architecture became stable before the runtime existed. That
made later implementation possible, but it also created a recurring risk:
well-developed prose could look like deployed software.

---

## Phase 1 — 2026-08-09 to 2026-08-10: canonicalization and honest naming

### Repository movement

Representative commits include:

- `3907fcf` — regenerate requirements from the canonical model.
- `10ad443` — align technical architecture with requirements.
- `f7f458f` — reconcile functional design with T-01…T-09.
- `d7cfa76` — compare documentation counts with the XLSX workbook.
- `cb75ee9` — validate exact coherence inventories.
- `5ce5037` — add governed MVP topic contracts.
- `1de4636` — trace FR-019 through payment outcomes.
- `eab20aa` — rename Lily's Florist as a reference design.
- `e23246d` — add a reviewable canonical requirements export.
- `2880d7a` — extend the guard to full chain and scope validation.

### Codex view

The `Assess repository coherence` task initially described the repository as
documentation/architecture rather than working software. It found that the
first guard checked counts rather than true coherence; topic governance was
mostly declarative; FR-019 stopped at initiation instead of authoritative
outcome; binary XLSX was not meaningfully diffable; and “reference
implementation” overstated the contents.

### Progression in evidence

```text
human-readable documents
  → normalized CSV
  → exact ID sets
  → canonical chain and scope comparison
  → governed topic catalog
```

### Lesson

This was the repository's most important epistemic improvement: replacing
“looks consistent” with deterministic checks. Later guard growth follows the
same pattern.

---

## Phase 2 — 2026-08-10 to 2026-08-11: coherence findings become a delivery loop

### Repository movement

CF-001 onward turned review comments into durable work units. Examples:

- Wireframe availability badges, customization fields, and escalation actions
  became separate findings and MRs.
- GitLab wiki and repository naming were reconciled.
- Misnumbered ADR candidates were quarantined.
- ADR-006–010 established customization scope, BFF topology, contract-first
  messaging, state ownership, and command/event boundaries.
- Schema stubs and topic publisher boundaries became CI-enforced artifacts.
- PostgreSQL and Kafka were selected through ADRs rather than assumed.

### Codex view

Codex moved from reviewer to governed remediation participant. The key process
was established:

```text
one falsifiable finding
  → one stable CF ID
  → one GitLab issue
  → one branch
  → one focused MR
  → verify merged main
```

### Lesson

The stable queue did more than organize work. It preserved why a change was
made and stopped later agents from re-opening the same semantic disagreement
under a new label.

---

## Phase 3 — 2026-08-11 to 2026-08-12: architecture becomes executable

### Repository movement

Representative commits include:

- `d9f46be` — PostgreSQL/Kafka platform foundation.
- `4674c5c` — BFF/gateway perimeter.
- `b749928` — minimum-data broker contracts.
- `50761ca` — executable topic governance.
- `9dbf4e2` — auditable message tracing.
- `69cddf5` / `2ba428e` — preserve unaffected experience state.
- `1d95636` / `cd390cb` — reject stale asynchronous results.
- `1b086c2` — conversational discovery entry point.
- `2e9a23a` — governed intent analysis.
- `8f22a6e` — editable Shared Understanding.
- `f7e64c1` — wire Edge to M2 orchestration.
- `1d87e17` — available generative-assistant boundary.
- `172520b` and `a11706a` — disclosure and response-SLO enforcement.

### Codex view

This phase invalidated the earlier “docs-only” description. The architectural
principles acquired runtime representations:

- Session/context versions became code and database constraints.
- Latest-intent-wins became stale-result rejection.
- Minimum-data and authority boundaries became executable contracts.
- The browser-facing path reached orchestration through a BFF perimeter.

### Lesson

Architecture becomes materially stronger when every principle has at least one
failure-mode test. “Preserve state” is not a useful implementation claim until
a test changes one facet and proves unrelated facets survive.

---

## Phase 4 — 2026-08-13 to 2026-08-17: journey depth, UX corrections, and pilot reality

### Repository movement

The repository expanded from M2 foundations into customer and deployment
behavior:

- Recommendation, selection, delivery, checkout, tracking, and support paths
  gained runtime slices and tests.
- UX defects were treated as requirement failures: unreachable mobile steps,
  covered actions, past delivery dates, unclear product names, tablet ordering,
  and misleading disclosure.
- Path B integration exposed session binding, Kafka, image, authentication,
  inventory, and live-intent problems.
- AWS IaC was recovered and ECR/ECS deployment jobs were introduced.
- M8 returning-shopper work began with same-session and durable browser hints.
- RAG/pgvector and ADR-016 agentic boundaries were added as thin scaffolding.

### Codex view

The repository stopped being assessable through unit tests alone. Local and
pilot paths could diverge because of cookies, proxy headers, native Kafka
clients, protected variables, service discovery, or missing seeded inventory.

### Key decision

M8 exposed a dangerous assumption: a shared local subject could not represent
customer purchase history. The Product Owner chose opaque browser-bound recall,
with cross-device identity deferred. Engineering then corrected persistence to
occur only after authoritative confirmation, never on submitted or declined
payment.

### Lesson

Journey integration is where abstract boundaries are tested. Identity,
authority, and state-transition problems often appear only when the UI,
gateway, persistence, and confirmation path are exercised together.

---

## Phase 5 — 2026-08-18 to 2026-08-19: loops, CI evidence, and multi-model operation

### Repository movement

Representative commits include:

- `f1aef3f` — four-way stakeholder skills plus Product Owner and Coherence
  Guardian.
- `2de3a1a` — cross-tool session-start briefing SOP.
- `ea5361e` and follow-ups — scheduled daily-brief generation.
- `a794b12` — explicit governance loop graph.
- `c602470` / `d625880` — requirement-to-issue and extended evidence guards.
- `72a2e85` — process-coherence guard.
- `b52103d` — blocking Edge Docker integration evidence.
- `4723390` — conservative handling of GitLab MR-diff API 404.
- `298ffc2` / `c3f894e` — browser recall and confirmation correction.
- `556e449` then `f87e255` — Gemini and Grok adapters, reaching six-way sync.
- `fd8ed98` — unified guard runner.
- `92807c9`, `ef87b26`, `a169da0`, `8752340` — traceability,
  governance, session, and knowledge graph implementations.

### Codex view

The `Analyze repository prerequisites` task shows Codex operating as a
stakeholder coordinator rather than a single patch author: sequencing
overlapping MRs, routing conflicts to engineering, sending product slices to PO
acceptance, and reserving merge authority for the MR Coordinator.

### Operational lessons

- Merge overlapping CI/loop-graph changes sequentially.
- Verify combined `main`, not only individual source branches.
- Treat API evidence as unknown when unavailable rather than crashing or
  silently passing.
- A service account should create reports/MRs without gaining merge or project
  administration authority.
- Schedule ownership can remain human while API work runs as a bounded bot.

### Epistemic change

Codex increasingly trusted machine guards and pipelines. This improved
repeatability, but it also planted the next failure mode: assuming the growing
guard count covered all meaningful delivery claims.

---

## Phase 6 — 2026-08-20 to 2026-08-21: operational ambition and institutional memory

### Repository movement

- Multi-product cart, Grafana IaC, webhooks, and automated status email landed.
- Nginx conflict-marker and Grafana routing incidents were fixed.
- A Locust load engine and LOAD-001…004 safeguards were created.
- M9 quality/SLO monitoring received PO acceptance language.
- Anti-fragility was elevated into a governing principle.
- Knowledge Guardian and Cost Guardian roles were added.
- Strategic studies and session-memory extraction created the in-repo Second
  Brain.
- Session-start rules began requiring every AI model to read daily briefs and
  memory logs.

### Codex view

Codex's role expanded from implementation/review into long-running operational
coordination: live GitLab schedules, service accounts, AWS pilot paths, load
testing, reporting, and team utilization.

### Lessons

1. The internal telemetry API is intentionally isolated from the perimeter;
   monitoring must use the internal network and identity boundary.
2. High-concurrency tests need both WAF authorization and mock-AI routing to
   prevent rate-limit and LLM-cost explosions.
3. Session memory must preserve why a workaround or boundary exists, not only
   the resulting file diff.
4. Automated reports become a dependency for future agents; stale or
   uncommitted briefs are a governance incident.

Related: [[2026-08-21-session-memory-building-process-and-lessons-learned]]
and [[2026-08-21-kb-project-building-lessons]].

---

## Phase 7 — 2026-08-22 to early 2026-08-23: extension acceleration

### Repository movement

- Thin `forecast.py` and `crm.py` slices landed or were prepared.
- DEP-001 Grafana subpath behavior was corrected.
- A broad M15–M18 commit added SSR/LCP scripts, live-chat/stem/multi-tenant
  migrations, bakery catalog artifacts, and the 14th stakeholder role.
- MR/commit subjects described these extensions as “complete.”
- Daily briefs repeated 15/16 completion and sub-100ms claims.

### Codex/model view at the time

The repository's velocity and guard results encouraged a “paper complete means
delivered” interpretation. Artifacts, schemas, routes, test doubles, and
benchmark scripts were aggregated into milestone completion claims.

### Why this happened

Several evidence categories were collapsed:

```text
file exists
≈ unit test exists
≈ route/schema is connected
≈ integration path works
≈ deployed path works
≈ production requirement is satisfied
```

Those are not equivalent.

---

## Phase 8 — later 2026-08-23: reconciliation and a stricter evidence model

### Repository movement

- `9249773` persisted the paper-complete M14–M18 correction.
- `2d26c0e` reconciled the later Antigravity 94/100 assessment.
- `a57cfac` independently queued CF-048–053.
- `c94c7ec` consolidated accessible chat lessons for the Second Brain.

### What the independent assessment verified

- 14/14 guards passed.
- 245 platform tests passed with 48 environment-dependent skips.
- 68 edge tests passed.
- Canonical ID, chain, scope, schema, and knowledge-graph checks passed.
- Nevertheless:
  - Daily reporting still hardcodes unsupported status.
  - Static SPA TTFB is mislabeled as SSR/browser LCP.
  - Extension migrations 019–022 are outside the migration runner path.
  - FR-016/017 and M12 prose conflict semantically.
  - The claimed M14 merchant-domain artifact is absent.
  - M17 says pgvector is Future despite existing retrieval enablement.

### Codex's corrected position

The repository is neither docs-only nor production-complete. It is an
executable reference foundation with strong canonical/governance checks and a
set of thin or disconnected extensions requiring honest scope labels and
specific integration evidence.

Current truth set: [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]]
and [[2026-08-23-antigravity-assessment-reconciliation]].

---

## The progression in one table

| Period | Repository center of gravity | Codex confidence source | Main blind spot discovered later |
|---|---|---|---|
| Uploaded artifact sessions | Workbook, report, diagrams | Semantic review | Subjective scores and non-reproducible artifact state |
| Aug 9–10 | Canonical docs and exact IDs | Workbook/CSV/Markdown checks | Mapping/runtime evidence still incomplete |
| Aug 10–11 | CF queue, ADRs, topic contracts | One-finding remediation and CI | Mostly architectural artifacts |
| Aug 11–12 | Platform/BFF executable foundation | Unit and contract tests | End-to-end and deployment behavior |
| Aug 13–17 | Journeys, UX, Path B | Docker/integration and live-path evidence | Identity and operational boundary gaps |
| Aug 18–19 | Loops, graphs, skills, CI | Pipelines and guard network | Guard coverage mistaken for universal truth |
| Aug 20–21 | Operations, load, memory | Telemetry, load runs, daily briefs | Report freshness and claim calibration |
| Aug 22–23 acceleration | M11–M18 artifacts | File/test/guard aggregation | Stub/reference artifacts labeled shipped |
| Aug 23 reconciliation | Evidence taxonomy and CF-048–053 | Claim-by-claim falsification | Remediation still pending |

---

## Repository growth versus evidence maturity

The repository progressed along two curves that did not always move together:

```text
artifact volume       ████████████████████████████
runtime evidence      ██████████████████
claim confidence      █████████████████████████
                                     ↑
                      overclaim gap exposed here
```

This is not an argument to slow implementation. It is an argument to make the
evidence state explicit for every milestone:

- Designed
- Represented in code/schema/IaC
- Unit verified
- Integration verified
- Deployed and observed
- Product accepted

Only the last three should support strong delivery language, and they answer
different questions.

---

## What Codex should do differently in future sessions

1. **Date every status statement.** Repository state changes faster than
   strategic architecture.
2. **Name the evidence layer.** Say “ID inventory passes,” “unit tests pass,” or
   “live journey observed,” not simply “coherent.”
3. **Treat commit/MR titles as claims.** Verify their contents and connectivity.
4. **Inspect negative evidence.** Skipped integration tests, unreachable
   migrations, uncalled functions, Future prose, and stale MRs are often more
   revealing than file presence.
5. **Keep product acceptance separate.** A thin slice can be valid and useful
   without satisfying the full canonical requirement.
6. **Prefer correction over score negotiation.** A falsifiable claim table is
   more useful than debating 94/100 versus 100/100.
7. **Preserve superseded beliefs.** Mark them clearly instead of deleting them;
   future agents need to understand how the error arose.
8. **Make memory durable.** Commit and push session logs; local-only memory does
   not help another model or machine.

---

## Current handoff

The repository's next coherence action remains a separate CF-048 remediation
iteration. This progression study is knowledge capture only and does not change
product scope, queue order, or merge authority.

Related nodes:

- [[2026-08-23-session-memory-log-cross-chat-knowledge-extraction]]
- [[2026-08-21-aea-strategic-architecture-study]]
- [[2026-08-22-team-velocity-and-daily-progression]]
- [[2026-08-22-agile-process-evolution-and-role-autonomy-study]]
- [[2026-08-23-session-memory-log-m15-m18-execution-and-mr269-merge]] — historical acceleration claim
- [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]] — corrective truth set
- [[2026-08-23-antigravity-assessment-reconciliation]] — assessment reconciliation
- [[2026-08-23-claude-view-repository-progression-and-alignment]] — Claude's independent alignment response: source-level confirmation of CF-048/049/050/053, plus a newly surfaced discrepancy in the vault's "14/14 guards" baseline

