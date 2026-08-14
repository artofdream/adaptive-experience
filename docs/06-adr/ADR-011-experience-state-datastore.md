# ADR-011 — Experience-State Datastore

Status: Accepted

Date: 2026-08-11

Related requirements: FR-020, FR-021, FR-022, NFR-007, NFR-012, NFR-017

Related decisions: [ADR-007 Initial Deployment Topology](ADR-007-initial-deployment-topology.md),
[ADR-008 Contract-First Messaging](ADR-008-contract-first-messaging.md),
[ADR-009 Experience-State Ownership](ADR-009-experience-state-ownership.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md)

Related issue: [#121 — Select experience-state datastore](https://gitlab.com/artof-group/adaptive-experience-architecture/-/issues/121)

## Context

ADR-009 makes the Experience Orchestration Engine authoritative for persisted
session experience state, context versions, workspace projections, selective
invalidation, and recovery. ADR-008 additionally requires an authoritative
state change and its outbox rows to commit in the same local transaction.

The datastore product was deliberately deferred. The MVP now needs a concrete
choice that supports atomic state and version changes, concurrent correction,
session expiry, schema evolution, backup and recovery, and local development
without weakening module ownership in the modular monolith.

The datastore stores orchestration-owned experience state. Products, stock,
prices, slots, payments, and orders remain authoritative in their owning domain
modules. Sensitive customer, recipient, and payment data is referenced or
tokenized wherever possible.

## Decision Drivers

- Commit an experience-state change, context-version increment, invalidation
  metadata, and corresponding outbox rows atomically.
- Detect conflicting writes and prevent stale work from becoming authoritative.
- Restore active sessions after refresh, reconnect, or process failure.
- Support explicit schemas and controlled migrations while allowing bounded
  flexibility in evolving workspace projections.
- Apply lifecycle retention and least-data controls to session state.
- Provide established backup, restore, monitoring, and local-development paths.
- Avoid a second datastore solely for MVP experience state.
- Keep domain authority and the future broker choice independent of the product.

## Considered Options

### Option A — PostgreSQL with relational metadata and JSONB state

Store stable identity, lifecycle, version, ownership, and outbox fields in
relational columns. Store the bounded experience-state document and projection
metadata in versioned JSONB where their shape is expected to evolve.

PostgreSQL provides transactions, row and predicate locking, multiple isolation
levels, constraints, indexes, JSONB querying, migrations, and established
backup and recovery mechanisms. It allows the outbox to reside beside the
authoritative state in the same transaction.

### Option B — Document database

Store each experience session primarily as a document and use multi-document
transactions where state and outbox records span documents or collections.

This matches the aggregate shape, but introduces a separate operational model
without a material MVP advantage. Cross-document transaction, migration, and
outbox rules still require explicit implementation.

### Option C — Durable key-value store

Store a session document by key and use optimistic commands or scripts for
atomic updates.

This offers low-latency access, but durability configuration, backup, query,
migration, and multi-record outbox behavior require more product-specific
discipline. It is better suited to an optional cache than the sole MVP system
of record.

### Option D — Event-sourced experience store

Persist every experience-state transition and rebuild current state by replay.

This provides a detailed history but adds event evolution, replay, snapshot,
and operational complexity that ADR-009 explicitly avoids for the MVP.

## Decision

Use **PostgreSQL as the authoritative MVP experience-state datastore**.

The orchestration module owns its PostgreSQL schema and repository interfaces.
Other modules, the BFF, and the Workspace must use Orchestration APIs or
governed topics; they must not read or write orchestration tables directly.

`pgvector` is not part of this decision. It may be evaluated separately for
semantic retrieval, but experience-state persistence must not depend on vector
search.

### Storage model

The initial schema separates stable control fields from evolvable state:

- `experience_session` stores the session identifier, state schema version,
  current context version, lifecycle status, timestamps, expiry, and a bounded
  JSONB experience-state document;
- projection and invalidation metadata may be stored in the same aggregate or
  in orchestration-owned child tables when query or update behavior warrants it;
- `outbox_message` stores the governed envelope, payload, creation time,
  publication state, attempt count, and last recoverable error;
- unique constraints protect message IDs and the session/context-version
  identity used for idempotency and stale-result rejection.

JSONB is used for orchestration-owned state that evolves as a cohesive
aggregate, not as a substitute for ownership, constraints, or migration. Fields
used for identity, lifecycle, concurrency, retention, audit, or frequent
selection remain typed and indexed columns.

### Transactions and concurrency

- Every accepted customer correction or decision change atomically updates the
  experience state, increments the context version, records invalidation, and
  inserts its outbox rows.
- A command supplies the context version it observed. The write uses an
  optimistic compare-and-set condition on that version; a mismatch is rejected
  as stale or re-evaluated by Orchestration rather than silently overwriting a
  newer decision.
- Read Committed plus an explicit version predicate or row lock is the default
  for single-session changes. Transactions involving broader invariants must
  use appropriate locking or Serializable isolation and retry serialization
  failures.
- Transaction retries must preserve the original command and message identity
  so they cannot create duplicate authoritative changes or outbox messages.
- The outbox relay runs outside the state-changing transaction. It claims
  unpublished rows safely, publishes through the selected broker, and marks
  success without changing domain state.

### Lifecycle and privacy

- Session expiry is represented by an indexed expiry timestamp and enforced by
  an idempotent cleanup process.
- Retention durations are configuration backed by an approved lifecycle policy;
  they are not hard-coded in domain logic.
- Abandoned or expired sessions remove unnecessary personal data and associated
  projections while retaining only explicitly required audit records.
- Customer, recipient, and payment details are stored as opaque references or
  tokens unless the field is essential to orchestration-owned behavior.
- Database roles grant the application and migration processes only the
  privileges they require. Production access uses encrypted transport and
  secrets supplied outside the repository.
- Production PostgreSQL data volumes (or equivalent provider disk / TDE) **must
  be encrypted at rest** to satisfy NFR-007 and NFR-012 storage requirements.
  Local Compose and CI volumes may be unencrypted for developer ergonomics and
  are not production evidence. See
  [nfr-007-012-encryption.md](../04-technical-architecture/nfr-007-012-encryption.md).
  Application-level column encryption is out of MVP scope.

### Migration, backup, and recovery

- All schema changes are ordered, reviewable migrations exercised in CI from an
  empty database and from the previous supported schema.
- JSONB state carries a schema version. Readers support the active version and
  the explicitly documented migration window; background migrations are
  restartable and idempotent.
- Production uses automated backups and point-in-time recovery appropriate to
  the hosting environment. Restore drills verify both state and pending outbox
  rows before the service is declared recovered.
- Local development and CI use an ordinary PostgreSQL instance with the same
  migrations and constraints as production. An in-memory substitute must not
  be used for persistence, concurrency, outbox, migration, or recovery tests.

## Rationale

Option A directly satisfies the atomicity required by ADR-008 and the ownership,
versioning, correction, and recovery behavior required by ADR-009. Relational
control fields make concurrency and lifecycle rules explicit, while JSONB
allows the orchestration aggregate to evolve without forcing every projection
field into a premature fixed schema.

PostgreSQL also keeps the MVP operationally focused: one established
transactional product can hold module-owned schemas and outboxes without making
tables shared sources of authority. Document and key-value products are viable,
but do not offer enough benefit here to justify a second persistence model.
Full event sourcing remains disproportionate to the current audit and replay
needs.

## Consequences

### Positive

- Experience-state and outbox atomicity use one local database transaction.
- Context-version conflicts can be enforced with constraints and explicit write
  predicates.
- Typed columns and JSONB balance governance with projection flexibility.
- Backup, restore, migration, and local-development practices use a common
  product.
- A future cache, vector extension, or extracted module remains optional rather
  than foundational.

### Negative

- The team must operate PostgreSQL, migrations, connection pooling, backup, and
  restore from the beginning.
- JSONB can hide an ungoverned schema if versioning, size, and indexing rules are
  not enforced.
- Serializable or heavily locked transactions can reduce throughput and require
  retry handling.
- A shared PostgreSQL cluster can be mistaken for shared data ownership unless
  schema and access boundaries are tested.

### Risks

- Other modules may bypass Orchestration and query its tables for convenience.
- State documents may accumulate domain facts or unnecessary personal data.
- An outbox relay may publish duplicates after failure; consumers must remain
  idempotent under ADR-008.
- Cleanup may remove data still needed by an active order if session and order
  lifecycle references are not modeled explicitly.
- Restore procedures may recover state without the matching unpublished outbox
  rows unless drills verify them together.

## Implementation Constraints

- The orchestration schema is private to the Orchestration module even when a
  PostgreSQL cluster is shared by modules in the modular monolith.
- Foreign keys must not create write authority across module-owned schemas.
- Domain facts are stored only as identifiers, tokens, or explicitly documented
  snapshots needed by the experience workflow.
- Each accepted state mutation uses one transaction for state, version,
  invalidation, and outbox insertion.
- Every mutable session aggregate uses optimistic context-version enforcement.
- Outbox message IDs are unique, stable across retries, and compatible with
  consumer idempotency.
- State JSONB has a schema version, documented size limit, validation boundary,
  and an index only when a demonstrated query requires it.
- Migration and application roles are separate; runtime privileges do not
  include schema modification.
- Logs, traces, backups, fixtures, and dead-letter diagnostics must not expose
  raw sensitive payloads.
- PostgreSQL extensions, including `pgvector`, require separate justification
  and must not be assumed by the base persistence model.

## Verification

- Concurrency tests submit two commands against the same observed context
  version and prove that only one authoritative version increment commits.
- Transaction tests inject failure between state mutation and outbox insertion
  and prove that both commit or both roll back.
- Relay tests cover restart before and after broker acknowledgement and prove
  recoverable publication with stable message identity.
- Recovery tests restore an active session, its context version, projections,
  invalidation metadata, and pending outbox rows after process and database
  restart.
- Functional tests cover refresh, reconnect, correction, selective
  regeneration, and stale-result rejection for FR-020 through FR-022.
- Lifecycle tests expire abandoned sessions idempotently without deleting state
  still referenced by an active workflow or order.
- Privacy tests prove sensitive values are tokenized or omitted and unavailable
  to unauthorized database roles, logs, and projections.
- Migration tests build from empty and upgrade from the previous schema without
  losing state, context versions, or pending outbox messages.
- Backup and restore drills verify record counts, context-version continuity,
  referential integrity, and outbox publication after recovery.
- Architecture tests fail when another module or the BFF accesses the
  orchestration persistence implementation directly.

## Revisit Conditions

Revisit the decision when measured scale or latency cannot meet requirements
with appropriate PostgreSQL indexing and connection management; when a separate
security or availability boundary is required; when session state must span
regions with conflicting writes; or when event replay becomes a product or
regulatory requirement.

Evaluate `pgvector` under [ADR-014](ADR-014-postgresql-pgvector.md): semantic
retrieval may use the extension, but experience-state persistence must remain
independent of vector search. A cache may be added only as a disposable
acceleration layer; PostgreSQL remains authoritative for experience state unless
a later ADR replaces this decision.
