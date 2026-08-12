# Coherence + implementation status — 2026-08-12

tags: #aea #coherence-assessment #implementation-status
status: refreshed-intake-complete
assessed_ref: 49fa772
assessed_by: codex

## Scope

- Guards: `check_coherence.py` passes; `check_topic_schemas.py` passes for the
  21 governed MVP payload schemas and envelope.
- Code: merged `platform/`, `edge/`, CI unit tests, and PostgreSQL/Kafka
  integration evidence through issue #40.
- Docs: ADR-001…012 Accepted; roadmap M0–M7; canonical requirements and topic
  contracts.
- GitLab milestones: M0 and M1 closed; M2 active for 2026-09-06…2026-09-19.
- M2 issue inventory: 5 closed and 5 open across its six FRs and four NFRs.
- CF queue: CF-030…034 remain queued; this refresh performs intake/status
  reconciliation only and does not remediate a finding.

## Coherence verdict

**Requirements and canonical documentation remain coherent.** The executable
foundation and the core M2 state behavior are now merged. The principal
docs-to-code/runtime gap is that the Edge BFF still uses an unavailable
orchestration adapter and does not expose the merged Conversation and Shared
Understanding services end to end.

| ID | Claim | Sev | Queue |
|----|-------|-----|-------|
| CF-030 | Wiki ADR index lists only ADR-001…010 and still describes the broker product as deferred / Kafka as draft although ADR-011/012 are Accepted | Medium | queued |
| CF-034 | Edge BFF uses `UnavailableOrchestration`; Conversation and Shared Understanding are not wired to browser-facing routes | Medium | queued |
| CF-031 | `CLAUDE.md` still describes the repository as docs-only although `platform/` and `edge/` are executable | Medium | queued |
| CF-033 | `platform/README.md` introduction says M2 behavior is not implemented although Conversation, Intent, and Shared Understanding services are present | Medium | queued |
| CF-032 | Root README repository areas omit `platform/` and `edge/` | Low | queued |

## Implementation status (milestones)

| MS | GitLab | Coverage | Assessment |
|----|--------|----------|------------|
| M0 | Closed | 5/5 tracked issues closed; ADR-006…012 Accepted | Complete |
| M1 | Closed | 8/8 tracked issues closed | Complete platform baseline; final production hardening remains in M7 |
| M2 | Active | 5/10 planned issues closed; 5/6 functional requirements implemented | Partial; platform behavior exists but the runnable Edge-to-Orchestration path and four NFR validations remain |
| M3–M7 | Active/planned | Contracts and schemas only | Not implemented in this assessment scope |

## M0 coverage

| Activity | Evidence | Status |
|----------|----------|--------|
| MVP customization boundary | ADR-006 / #104 | Complete |
| Initial deployment topology | ADR-007 / #105 | Complete |
| Contract-first messaging and transactional outbox | ADR-008 / #106 | Complete |
| Experience-state ownership | ADR-009 / #107 | Complete |
| Command/event boundaries | ADR-010 / #108 | Complete |
| PostgreSQL and Kafka product decisions | ADR-011 / #121; ADR-012 / #120 | Complete |

## M1 coverage

| Activity | Evidence | Status |
|----------|----------|--------|
| Topic governance and 21 semantic payload contracts | #57, #129 | Complete baseline |
| Auditable message tracing | #58 | Complete baseline |
| Least-data privacy and security enforcement | #59 | Complete baseline |
| PostgreSQL state, transactional outbox, and Kafka integration | #128 | Complete baseline |
| BFF and Edge API Gateway perimeter | #127 | Perimeter complete; orchestration runtime wiring remains CF-034 |
| CI schema, coherence, unit, PostgreSQL, and Kafka checks | repository CI and integration suite | Complete baseline |

## M2 coverage

| Requirement / capability | Issue | Status | Implementation evidence |
|--------------------------|-------|--------|-------------------------|
| FR-001 conversational discovery | #20 | Closed | Validated customer-message acceptance, bounded transcript state, and governed outbox event |
| FR-002 intent analysis | #21 | Closed | Provider-neutral interpreter, six structured facets, progressive prompts, and atomic intent event |
| FR-004 24/7 Generative AI chatbot | #23 | Open | Deterministic reference interpreter exists; production provider and availability behavior are not implemented |
| FR-020 preserve unaffected state | #39 | Closed | Deep selective patches retain siblings and completed decisions |
| FR-021 review and correct inference | #40 | Closed | Least-data review projection and optimistic partial corrections |
| FR-022 stale-response rejection | #41 | Closed | Exact active-context matching and durable stale outcomes |
| NFR-001 usability | #43 | Open | No measurable usability acceptance evidence yet |
| NFR-002 browser/device compatibility | #44 | Open | No defined automated compatibility matrix yet |
| NFR-004 standard query response within 3 seconds | #46 | Open | No end-to-end SLO instrumentation or representative performance evidence yet |
| NFR-005 transparency | #47 | Open | Shared Understanding is reviewable, but transparency criteria and evidence remain open |

The latest merged M2 implementation was validated locally with 51/51 full
PostgreSQL/Kafka tests, plus passing topic-schema and coherence guards. This is
strong platform-layer evidence, not proof of a browser-to-AI production path.

## Coverage (MVP capabilities)

| Capability | Status |
|------------|--------|
| M0 architecture decisions | Complete |
| M1 contracts, outbox/Kafka, governance, audit, privacy, and Edge perimeter | Complete baseline |
| T-01 Conversation | Implemented in platform; browser-facing orchestration runtime disconnected |
| T-02 Shared Understanding | Implemented in platform; browser-facing routes disconnected |
| Progressive thought completion | Implemented in platform |
| Context versioning, state preservation, and stale-result rejection | Implemented and integration-tested |
| Production Generative AI provider and 24/7 behavior | Missing |
| M2 usability, compatibility, performance, and transparency evidence | Missing or partial |
| T-03…T-08, FAQ, inventory, pricing, payment, and tracking | Planned for M3–M6; not implemented |

## Recommended priority

1. **P0 — CF-034:** create one remediation issue and wire the existing Edge BFF
   to Conversation and Shared Understanding orchestration commands/queries with
   end-to-end context-version and correlation propagation.
2. **P0 — #23 / FR-004:** add the production Generative AI adapter, availability
   behavior, timeouts, health checks, and graceful degradation behind the
   existing provider-neutral port.
3. **P1 — #47 / NFR-005:** make inference, uncertainty, prompts, and corrections
   visibly transparent.
4. **P1 — #46 / NFR-004:** instrument and prove the three-second standard-query
   SLO against the real end-to-end path.
5. **P2 — #43 / NFR-001:** establish measurable T-01/T-02 usability acceptance
   and accessibility evidence.
6. **P2 — #44 / NFR-002:** define the supported browser/device matrix and add
   responsive compatibility tests.

Do not close M2 until CF-034 and issues #23, #43, #44, #46, and #47 are
addressed with end-to-end acceptance evidence.

## Intake stop condition

This refresh introduces no new CF identifier and performs no remediation.
Under the coherence-findings SOP, the next remediation iteration remains the
first queued finding by severity and dependency: CF-030, unless the owner
explicitly prioritizes the runtime-blocking CF-034 first.
