# ADR-008 — Contract-First Messaging and Transactional Outbox

Status: Accepted

Date: 2026-08-11

Related requirements: NFR-015, NFR-016, NFR-017, FR-022

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md),
[MVP Topic Contracts](../04-technical-architecture/topic-contracts.md)

## Context

The repository defines 21 MVP topics and NFR-015 through NFR-017, but publication
atomicity and the authoritative contract workflow were undecided. Without a
single rule for schemas, envelopes, and outbox publication, domain commits and
bus events can diverge, compatibility cannot be tested before publishers ship,
and stale-context rejection (FR-022) loses its transport guarantees.

## Alternatives

1. **Code-defined event classes only** — fast for early prototypes; opaque to
   cross-language consumers and CI contract gates.
2. **Direct broker publication from domain writes** — simple path; domain
   commits and publications can diverge on failure.
3. **JSON Schema contracts plus transactional outbox** — schemas are reviewable,
   versioned, and CI-testable; outbox keeps commit and publication atomic.
4. **Ungoverned database polling** — avoids a bus; weakens ownership, audit, and
   least-privilege payload rules (NFR-015…017).

## Decision

**Use contract-first JSON Schema payloads on the Central Message Bus, with a
transactional outbox for every authoritative publication.**

### Envelope

Every bus message uses the versioned envelope in `technical-architecture.md`:
message ID, topic, type (event / command / query / response), schema version,
session ID, correlation ID, source, context version, publication time, security
context, minimum authorized payload, and outcome or recoverable error.

### Payload contracts

- Each MVP topic in `topic-contracts.md` (all 21 rows) declares an explicit
  schema version and maps to a machine-readable JSON Schema under
  `docs/04-technical-architecture/schemas/` named
  `{topic}.v{schema-version}.json` before implementation.
- Concrete field inventories live in those schemas and the topic table’s
  minimum-payload column — not in this ADR.
- Owners approve schemas and subscriber access. The bus rejects unregistered
  publishers and subscribers (NFR-015).

### Schema evolution

- Schema versions use semantic versioning.
- Incompatible payload changes require a new major version and coordinated
  consumer readiness.
- Compatible additive changes may use minor/patch versions with dual-publish
  only when an owner-approved compatibility window is documented.

### Transactional outbox

- Authoritative domain state changes and the corresponding outbox rows are
  committed in the **same local transaction**.
- A relay publishes outbox rows to the bus; publication success marks the row
  relayed. Failed relays retry without rewriting domain state.
- Direct “fire and forget” broker writes from domain code paths are forbidden
  for authoritative facts.

### Delivery and consumption

- At-least-once delivery is assumed; consumers **must be idempotent by message
  ID**.
- Consumers **reject** messages whose context version does not match the active
  experience state (FR-022 / ADR-005).
- Envelope and outcome fields are recorded for auditable tracing (NFR-016).
- Payloads carry only minimum authorized fields (NFR-017).

### Compatibility gates (CI expectations)

Before a publisher ships:

1. Schema file exists for every topic it publishes, matching `topic-contracts.md`.
2. Envelope-required fields are present in fixtures or contract tests.
3. Unauthorized publisher/subscriber combinations are rejected in policy tests.
4. `python scripts/check_coherence.py` remains green for published inventories.

## Rationale

Option 3 prevents domain/event divergence, makes NFR-015…017 testable, and
preserves FR-022 without blocking the adaptive workspace. Broker product choice
remains outside this ADR (see ADR-007 / CF-016).

## Consequences

- Implementation must provision outbox storage beside each authoritative writer.
- Topic owners maintain schemas under `schemas/` in lockstep with
  `topic-contracts.md`.
- CI gains contract checks; advisory markdown lint remains separate (CF-005).
- This ADR does not invent requirement IDs or change MVP topic membership.
  `support.escalation.requested` was later added to the governed catalog for
  the thin FR-006 / T-09 path (22 topics total) without reclassifying FR-006
  as MVP in the requirements source of truth.
