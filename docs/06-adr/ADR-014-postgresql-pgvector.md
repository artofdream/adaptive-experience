# ADR-014 — PostgreSQL pgvector for Semantic Retrieval

Status: Accepted

Date: 2026-08-14

Related requirements: FR-002, FR-005, FR-007, NFR-006
(Related Future retrieval consumers: FR-008, FR-010)

Related decisions: [ADR-011 Experience-State Datastore](ADR-011-experience-state-datastore.md),
[ADR-008 Contract-First Messaging](ADR-008-contract-first-messaging.md),
[ADR-009 Experience-State Ownership](ADR-009-experience-state-ownership.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md)

## Context

[ADR-011](ADR-011-experience-state-datastore.md) Accepted PostgreSQL as the MVP
experience-state datastore and **explicitly deferred `pgvector`**: experience-state
persistence must not depend on vector search. Semantic retrieval for product
knowledge, recommendations, and grounded answers still needs a store decision.

Without a chosen retrieval substrate, implementers risk introducing a separate
vector database, coupling orchestration session state to embeddings, or treating
similarity hits as authoritative business facts.

## Alternatives

1. **Defer indefinitely** — keep structured SQL only; fuzzy intent and catalog
   grounding stay keyword/rules based until a later ADR.
2. **Separate vector database** (dedicated ANN service) — strong scale path;
   second operational product and consistency story for MVP.
3. **`pgvector` on PostgreSQL** — vector similarity beside relational filters in
   the same operational family as ADR-011, without making experience-state depend
   on embeddings.
4. **In-process / file-only embeddings** — fine for prototypes; weak durability,
   sharing, and operational governance for reference deployments.

## Decision

Use **PostgreSQL with the `pgvector` extension as the MVP semantic retrieval
store** for embeddings that support retrieval-augmented and hybrid search.

- Embeddings support **retrieval only**. Transactional facts — price, stock,
  order state, payment state, delivery slots — remain authoritative **structured**
  data owned by domain services.
- **Experience-state persistence remains independent of vector search** (ADR-011).
  Orchestration tables and outbox must not require `pgvector` to commit, restore,
  or serve Shared Understanding.
- Catalog / knowledge embeddings may live in PostgreSQL schemas owned by the
  retrieving domain (or a dedicated retrieval module), not in the orchestration
  experience-state aggregate.
- A separate vector database is out of MVP scope unless revisit conditions below
  are met.

Retrieval **policy** (hybrid filters, post-retrieval validation, when RAG is
used vs deterministic FAQ) is decided in a follow-on ADR; this ADR selects only
the store/extension.

## Rationale

Option 3 reuses the Accepted PostgreSQL operational baseline, keeps relational
filters and vector similarity in one query surface for hybrid retrieval, and
preserves ADR-011’s boundary that session experience state must not depend on
vectors. Option 2 adds operational cost before MVP evidence demands it. Option 1
blocks grounded semantic paths without a clear substitute.

## Consequences

- Enabling `pgvector` in production (and optionally in local/CI images when
  retrieval features are exercised) is an infrastructure/migration concern for
  the retrieval-owning schema — not a change to experience-state migrations
  required for FR-020…022.
- Embedding pipelines, index types, and model choice are implementation details
  under this ADR; they must not invent a second source of truth for price/stock.
- Hybrid RAG behavior and authority validation are specified in ADR-015 (or the
  next free number after this ADR merges).
- Local Compose may omit `pgvector` until a retrieval feature needs it; omission
  must not break experience-state or messaging foundations.

## Revisit conditions

Revisit when measured recall/latency or scale cannot be met with PostgreSQL +
`pgvector`; when a separate security or tenancy boundary for vectors is required;
or when a managed vector service is mandated by deployment constraints. Do not
revisit by folding vectors into the experience-state aggregate.
