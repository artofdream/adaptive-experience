# Design note — M6 automated support answers (#28 FR-009, #24 FR-005)

status: accepted (2026-08-13)
for_issues: "#28 (FR-009 automated FAQ), #24 (FR-005 approved product/policy answers)"
affects: "M6; mirrors the M2 conversation/intent synchronous pattern"
author: claude
date: 2026-08-13

> **Decisions (2026-08-13):**
> 1. One mechanism satisfies both FRs: an approved-answer service grounded in a
>    reference knowledge base of FAQ + product/policy entries, each with
>    `approved_source_references`. FR-009 = the automated FAQ match; FR-005 = the
>    approved product/policy grounding. One MR closes both.
> 2. Synchronous request/response (mirrors conversation), no running bus needed.
>    The governed `support.faq.answered` event is still emitted for
>    governance/audit and future bus consumers (#149).
> 3. Grounding safety: the assistant answers ONLY from approved sources. An
>    unmatched question returns a safe "no approved information" answer with no
>    fabricated content and empty sources - it never hallucinates. Human escalation
>    is FR-006/T-09 Future, out of scope.

## Grounding

- FR-009: "The system shall automatically respond to frequently asked customer
  questions."
- FR-005: "The AI assistant shall answer questions using approved florist product
  and policy information."
- Governed topic `support.faq.answered` (ai-concierge -> workspace, key
  `session_id`): payload `{answer (required), approved_source_references}`.

## Model

- **`support.py`**: `SupportService.answer(question)` normalizes the question
  (bounded, control-free), matches it against `ReferenceSupportKnowledge` (a
  deterministic reference base of approved FAQ + product/policy entries, each with
  source references), and returns `{answer, approved_source_references, matched}`.
  A miss returns the safe no-approved-information answer with `matched=false` and
  empty sources.
- **Emission**: `PsycopgSupportStore.record_answer` inserts `support.faq.answered`
  into the outbox (source `ai-concierge`) at the session's current context version
  (no state mutation, no version bump), so it is audited and bus-ready.
- **Internal**: `POST .../support` -> validate question, answer, emit, return.
- **BFF**: `POST /api/v1/support` (CSRF-guarded) accepts only `{question}` and
  returns `{answer, approved_source_references, matched}`.

## Not changing

- No experience-state mutation (support is a stateless Q&A). No new schema/topic
  (support.faq.answered is governed). No workspace facet: the answer is the
  response; in the running-bus future (#149) the workspace consumer would also
  reflect `support.faq.answered`.

## Build order within M6

Single build closing #28 + #24. This completes M6 (with #42 tracking already
merged): FR-005, FR-009, FR-023.
