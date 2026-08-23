# Session Memory Log: Cross-Chat Knowledge Extraction

> **Tags**: #aea #second-brain #session-memory #cross-model #architecture #governance #lessons-learned
> **Captured**: 2026-08-23
> **Role Context**: @aea-knowledge-guardian
> **Repository**: Adaptive Experience Architecture / Lily's Florist reference design
> **Current reconciliation**: [[2026-08-23-antigravity-assessment-reconciliation]] and [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]]

---

## Purpose and source boundary

This node extracts durable AEA knowledge from every related Codex or ChatGPT
task visible to the Codex desktop app on 2026-08-23, then reconciles it with
the committed Second Brain session logs. It records decisions, rationale,
failed approaches, and reusable lessons—not raw transcripts.

Accessible task histories reviewed:

- `Analyze repository prerequisites` (`019fed6f-896d-7f52-9585-0f8a68b5c06a`)
- `Improve Excel workbook coherence` (`019fed54-47d9-7be2-8d8a-aeb36b78f0be`)
- `Excel Coherence Review` (`6a7a3230-8358-83eb-9f31-8c36a66c674c`)
- `Compare architecture approaches` (`019fed52-07db-7560-9677-af8aa9c7df18`)
- `Assess repository coherence` (`019fea6d-91d4-7f10-b37f-76bb76699719`)
- `Troubleshoot GitLab Duo DCR4001` (`019fe8cb-c27a-7af1-a3ce-899408c85194`)
- `Figma Wireframe Generation` (`6a6f0dcf-11ac-83ed-bef5-e06538fedc2d`)
- Current `Review repo context` task (`01a02f80-0bdb-7f62-9081-4b43f28cfd2b`)

Cursor, Claude, Gemini, Grok, and Copilot private transcripts are not available
through the Codex app. Their durable repository handoffs under
`research/random-thoughts/`, `research/daily-briefs/`, commits, and GitLab
metadata were used instead. This limitation matters: “all chats” here means
all accessible chat histories plus the committed cross-model memory layer.

No credentials, token values, private chat dumps, or raw personal data are
copied into this note.

---

## 1. Stable product and architecture intent

Across the earliest workbook/document sessions and the later executable
foundation, the core idea remained stable:

1. Replace page-centric e-commerce funnels with a persistent Adaptive
   Workspace.
2. Let AI interpret intent, but never grant it commercial authority over
   inventory, pricing, delivery, payment, or order state.
3. Make structured intent inspectable and correctable by the customer.
4. Use context versions and dependency-aware invalidation so stale asynchronous
   results cannot overwrite newer intent.
5. Regenerate only affected tiles and preserve unaffected decisions.
6. Carry the chain from business goal → epic → story → requirement → ADR →
   runtime evidence → verification.

This is the architectural center of gravity. The implementation may be thin,
but changing this boundary would be a product/architecture decision rather
than an ordinary refactor.

Related: [[2026-08-21-aea-strategic-architecture-study]],
[[2026-08-21-pilot-vs-production-live-architecture-study]], and
[[2026-08-21-rag-architecture-challenges-and-refactoring-study]].

---

## 2. Canonical workbook and traceability evolution

### What the sessions established

- The workbook is the canonical requirements source. Do not invent BG, EP,
  US, FR, or NFR identifiers.
- The consolidated model settled on 7 BGs, 7 EPs, 23 USs, 17 NFR-USs, 23 FRs,
  17 NFRs, and 40 end-to-end chains.
- Binary XLSX is not meaningfully reviewable through a normal Git diff. A
  deterministic normalized CSV export is required for reviewability.
- Counts alone are insufficient. Early `check_coherence.py` behavior could
  miss a duplicated ID compensating for a missing ID. The guard later evolved
  to exact sets, mapping chains, scope fidelity, membership links, and CSV
  comparison.
- A short architecture traceability table should be labeled
  **representative**, not exhaustive. Exhaustive truth belongs in the canonical
  mapping/export and machine-readable evidence.
- Wireframes must map both visible UI behavior and the architectural behavior
  they demonstrate: customer correction, state preservation, stale-result
  rejection, authoritative payment, and versioned tracking.

### Durable lesson

There are at least three separate meanings of “coherent”:

1. **Inventory coherence** — expected identifiers exist.
2. **Mapping coherence** — identifiers and scope form the canonical chains.
3. **Runtime coherence** — code and operational evidence actually satisfy the
   published delivery claim.

A pass at one layer must never be reported as proof of the others.

---

## 3. Reference design versus implementation maturity

An early Codex assessment correctly observed that the repository was then
primarily documentation and architecture. It recommended “reference design”
instead of “reference implementation,” explicit topic contracts, stronger CI,
normalized requirements exports, and real traceability checks.

Those observations drove useful improvements, but the historical “docs-only”
description is no longer current: executable `platform/`, `edge/`, migrations,
tests, Compose, and AWS IaC now exist.

The opposite overcorrection later appeared: thin modules, schemas, routes, or
benchmark scripts were described as production-complete milestones. The
current truth is between those extremes:

- A real executable reference foundation exists.
- Many post-MVP/reference-extension surfaces remain thin or disconnected.
- M14–M18 are not production-shipped merely because files and tests exist.

Current truth set: [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]],
[[2026-08-23-antigravity-assessment-reconciliation]], and the independent
assessment at `research/assessments/2026-08-23-codex-independent-runtime-coherence-assessment.md`.

---

## 4. Topic governance and consequential boundaries

Early assessment found that NFR-015 governance was described conceptually but
not instantiated per topic. The repository subsequently added versioned
schemas and a topic-schema guard. The reusable design lesson is broader:

- Every consequential topic needs an owner, version, publisher/subscriber
  boundary, minimum payload, identity context, compatibility rule, and
  failure/idempotency semantics.
- Traceability must include the outcome, not only the initiating command.
  For example, FR-019 is not satisfied by `order.checkout.requested` alone;
  authoritative payment success/failure and order-confirmation boundaries are
  part of the claim.
- An event name in a document is not runtime evidence. Schema, producer,
  consumer, integration test, and operational observation are progressively
  stronger evidence.

---

## 5. Privacy-preserving returning-shopper decision

The M8 implementation surfaced a critical identity-boundary problem: local
tokens resolved to a shared subject, so treating that subject as customer
purchase history could mix shoppers' data.

The Product Owner selected the safe slice:

- Browser-bound opaque recall, not authenticated identity.
- Cross-device/account history deferred.
- Persist only minimal reorder facts: opaque recall ID, product ID, opaque
  order ID, expiry, and timestamp.
- Exclude historical PII, address, delivery details, options, and payment data.
- Revalidate current inventory and pricing.
- Record recall only after authoritative payment/order confirmation; a
  submitted or declined checkout must never create “ordered earlier” history.

### Lesson

An apparently simple personalization feature is an identity and data-isolation
decision. Resolve ownership semantics before persistence, and bind history to
the strongest available confirmation event—not an attempted command.

---

## 6. RAG and AI boundary lessons

The chat and Second Brain studies converge on the following RAG approach:

- Apply hard relational filters (availability, budget, pet safety, policy
  category) before semantic ranking.
- Combine lexical and vector retrieval where useful, for example with
  reciprocal-rank fusion.
- Cache embeddings for common queries to control latency and cost.
- Require source references and a fail-closed quality gate for customer-facing
  answers.
- Keep AI interpretation non-authoritative under ADR-016; authoritative domain
  services validate commercial facts.

Do not confuse “PostgreSQL + pgvector is enabled for retrieval” with “all
future semantic-cache or advanced composition work is delivered.” That
confusion is now tracked as CF-053.

---

## 7. Figma and UX delivery workflow

The Figma-related sessions established a practical design-to-development
contract:

- Structure the file around foundations, components, journeys, experiments,
  and archive pages.
- Model `initial`, `thinking`, `partial`, `complete`, `error`, and `superseded`
  as component variants instead of duplicated uncontrolled frames.
- Use semantic variables/tokens and mirror them in code.
- Link GitLab work to exact Figma node URLs, not only the file homepage.
- “Ready for development” requires acceptance criteria, responsive behavior,
  empty/loading/error states, interaction annotations, accessibility, content
  examples, token use, and export settings.
- Require design review for new patterns or material deviations, not for every
  pixel of every MR.
- Wireframe annotations should explain requirement and authority behavior, not
  only name visible controls.

The strongest wireframe traceability includes FR-020/021/022 for shared
understanding and selective refresh, plus FR-018/019/023 for summary, payment,
confirmation, and tracking.

---

## 8. Local and pilot architecture documentation

The architecture sessions insisted on separate HLD/LLD views for:

- Local Docker Compose development.
- AWS `aea-pilot` Path B.

Diagrams should show components, protocols, trust boundaries, startup or
deployment sequences, security controls, and evidence status. Most
importantly, they must visually distinguish:

- Implemented and exercised.
- Represented in IaC but not operationally verified.
- Planned/future.

### Lesson

An IaC resource, a diagram box, and a deployed healthy service are three
different evidence states. Architecture documents should label them rather
than flattening them into “exists.”

---

## 9. GitLab automation and least-privilege lessons

### Service account and schedule ownership

The daily-reporting work established a safe authority split:

- Human `artofdream` owns the protected-branch schedule.
- `aea-ci-reporter` performs bounded API/report/MR actions with a protected,
  masked/hidden token.
- Short-lived CI job credentials perform supported pushes.
- The MR Coordinator retains merge authority.

Attempting to transfer a schedule to a Developer service account returned 403
because GitLab requires higher project authority for schedule ownership. The
right response was not to over-privilege the bot: keep human ownership and use
the service account only inside the job.

Existing masked variables cannot simply be converted to hidden; replacement
requires rotation and recreation. Tokens should be read securely, never placed
in shell history, chat, repository files, schedule variables, or issue/MR
comments.

### Conservative automation failure

When GitLab change-detail APIs returned 404, the process-coherence guard was
changed to report evidence as unverifiable rather than crash or assume a pass.
This is the correct posture for governance automation: unknown is not success,
but it also should not destroy the reporting loop.

### Merge sequencing

Overlapping MRs touching `.gitlab-ci.yml` and `research/loop-graph.md` had to be
merged sequentially, with the dependent branch rebased and both loop
definitions preserved. The recurring lesson is: shared automation surfaces
create dependency edges even when feature scopes differ.

---

## 10. GitLab Duo and external-tool integration lessons

GitLab Duo `DCR4001` was traced to a missing/not-ready foundational-flow
service account at the top-level group—not an IDE or MR-content problem.
Recovery belongs to group administration and may require disabling flows,
waiting for leases/workers to clear, re-enabling, and verifying membership.

### Lesson

Classify integration failures by authority layer before retrying:

- IDE/client failure
- Project configuration
- Group-level service account
- Background worker/lease
- External provider

Retries at the wrong layer create noise and can obscure the real control-plane
fault.

---

## 11. Performance evidence and its limits

Recorded load evidence includes approximately 1,837.6 RPS at N=1000 and about
417 ms TTFB in the associated study. These measurements demonstrate a load-run
result under its recorded configuration; they do not prove sub-100ms LCP.

The current M15 script labels TTFB as an estimated LCP score and checks static
HTML markers. Browser LCP requires browser-observed paint timing and cannot be
substituted with server response timing. This is tracked as CF-049.

Related: [[2026-08-23-n1000-load-test-and-capacity-study]] and
[[2026-08-23-load-testing-results-and-capacity-study]].

---

## 12. Process and team-governance lessons

- One finding → one issue → one branch → one focused MR preserves auditability.
- Product acceptance, implementation, infrastructure, security, UX, coherence,
  and merge authority are different roles; do not collapse them into one
  “agent did everything” action.
- Bench capacity is not the same as available scope. The PM must assign or park
  work; missing owner labels can make active work appear idle.
- A successful MR pipeline does not prove combined-main behavior. Re-run the
  scheduled or post-merge verification against the merged graph.
- Duplicate issues and branches that became identical to `main` should be
  closed with audit notes, not kept alive for activity optics.
- A failed required pipeline remains important even if an MR was manually
  merged. MR !271 is a recent example: its knowledge correction was valuable,
  but the failed pipeline must not be erased from the historical record.

---

## 13. Stale statements future models must not inherit

The following were true or believed during earlier chats but are not current
session-start facts:

- “The repository is docs-only.” Executable platform and edge foundations now
  exist.
- “Gemini and Grok synchronization remains outstanding.” Six-way stakeholder
  adapters now exist and the sync guard passes.
- “M14–M18 are complete/production-ready.” They are reference extensions or
  paper-complete, with specific gaps recorded in CF-048–053.
- “14/14 guards means perfect coherence.” It means the guarded properties pass;
  it does not prove shipped runtime behavior.
- “Static pre-render markers and TTFB prove sub-100ms LCP.” They do not.

Always date status claims and prefer commit/MR/runtime evidence over prose.

---

## 14. Current actionable handoff

The independent coherence intake queued:

1. CF-048 — hardcoded daily-brief milestone and M15 claims.
2. CF-049 — SSR/LCP measurement semantics.
3. CF-050 — unreachable extension migrations 019–022.
4. CF-051 — FR-016/017 and M12 semantic contradiction.
5. CF-052 — absent merchant-domain artifact behind the M14 wording.
6. CF-053 — pgvector already enabled versus M17 “Future” wording.

The next separate remediation iteration is CF-048 only. Do not batch these
findings, and do not implement Stripe, WebSocket chat, WebRTC, or cross-region
RDS without the appropriate product/engineering/infrastructure authority.

---

## Related Second Brain nodes

- [[2026-08-23-codex-view-repository-progression-study]] — chronological Codex view of evidence and repository maturity.
- [[2026-08-21-kb-project-building-lessons]]
- [[2026-08-21-session-memory-building-process-and-lessons-learned]]
- [[2026-08-21-aea-strategic-architecture-study]]
- [[2026-08-21-pilot-vs-production-live-architecture-study]]
- [[2026-08-21-rag-architecture-challenges-and-refactoring-study]]
- [[2026-08-22-agile-process-evolution-and-role-autonomy-study]]
- [[2026-08-22-domain-boundary-audit-and-performance-guardian-proposal]]
- [[2026-08-22-missing-skill-gap-assessment-framework]]
- [[2026-08-23-session-memory-log-m15-m18-execution-and-mr269-merge]] — historical claim source, not ship evidence
- [[2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18]] — current correction
- [[2026-08-23-antigravity-assessment-reconciliation]] — current correction
- [[2026-08-23-repository-coherence-assessment-report]] — superseded outside its ID-inventory result
- [[2026-08-23-claude-view-repository-progression-and-alignment]] — Claude's independent alignment response to the Codex handoff; confirms CF-048/049/050/053 at source level and flags that the vault's "14/14 guards" baseline is not currently reproducible from the committed record
