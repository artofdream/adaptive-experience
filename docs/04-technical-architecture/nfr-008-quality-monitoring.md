# NFR-008 AI response quality monitoring (first slice)

Status: Accepted (Future first slice — live intent and FAQ paths)

Requirement NFR-008: The system shall maintain AI response quality monitoring
and error tracking. Traceability: EP-004 -> NFR-US-008 -> NFR-008.

This note describes the first slice only. It does not add assistant surfaces,
CRM analytics, an inventory seeder, or an Anthropic key. Remaining Future depth
(warehouse quality dashboards, additional AI paths) stays out of scope.

## Live paths

Quality events are recorded only for:

- **Intent** — `POST /internal/v1/sessions/{id}/conversation` runs
  `IntentAnalysisService` with the live interpreter (`AvailableIntentInterpreter`
  when `AEA_AI_*` is fully set, otherwise `ReferenceIntentInterpreter`).
- **FAQ** — `POST /internal/v1/sessions/{id}/support` when the answer is an
  approved-knowledge FAQ (FR-005 / FR-009). Situational FR-010 answers and T-09
  escalation are not in this slice.

## Fail-closed controls

1. **Least-data events.** `orchestration.ai_quality_event` stores path, outcome,
   allowlisted `error_code` / `quality_flags`, optional `assistant_mode`, and FAQ
   `matched`. It does not store prompts, answers, payloads, session IDs, or raw
   sensitive fields. `QualityMonitor.record` rejects unknown fields and the same
   class of raw PII/PAN keys as the broker privacy guard (NFR-013 / NFR-017).
2. **Intent output gate.** Interpreter facets that escape the six Shared
   Understanding keys, or fail value checks, are recorded as `error` /
   `invalid_output` or `unsupported_facets` and are not applied. Provider
   failures already degrade through `AvailableIntentInterpreter`; those live
   interpretations are recorded as `fallback` with `degraded` rather than
   silently disappearing.
3. **FAQ output gate.** A matched FAQ answer must equal approved knowledge and
   carry those source references. An unmatched question must use the safe
   no-information answer with no sources. Anything else is recorded as
   `unapproved_answer` and is not published (`support.faq.answered` is not
   written).

## Observability

`GET /internal/v1/ai/quality` (same internal bearer and subject headers as
`/internal/v1/ai/health`) returns aggregate counts per path/outcome and a
recent error/fallback list. It is an operator/internal read, not a customer
assistant surface. Availability mode remains on `/internal/v1/ai/health`
(NFR-003). Diagnostics report a quality-failure count without event payloads.

## Verification

- `platform/tests/test_quality.py` — fail-closed event schema; FAQ unapproved
  answers are rejected; intent fallback and invalid output are tracked.
- `platform/tests/test_support.py` / `test_generative_ai.py` — live FAQ and
  intent services record on the existing paths.
- `platform/tests/test_postgres_integration.py` — conversation and FAQ HTTP
  paths persist payload-free rows; `/internal/v1/ai/quality` returns counts;
  the table has no prompt/answer/payload columns.

## Scope

This slice establishes the monitoring and error-tracking mechanism on the two
live AI-supported paths. It does not claim complete Future NFR-008 coverage
(no CRM quality warehouse, no new concierge surfaces).
