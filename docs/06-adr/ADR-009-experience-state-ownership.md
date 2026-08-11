# ADR-009 — Experience-State Ownership and Persistence

Status: Accepted

Date: 2026-08-11

Related requirements: FR-020, FR-021, FR-022, NFR-007, NFR-012

Related decisions: [ADR-001 Shared Understanding](ADR-001-shared-understanding.md),
[ADR-005 Latest Relevant Intent Wins](ADR-005-latest-relevant-intent-wins.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md)

## Context

ADR-001 and ADR-005 establish Shared Understanding and latest-relevant-intent
behavior, but not authoritative ownership, persistence, projections, or
invalidation. Without those rules, tiles and clients can diverge, completed
choices can be lost during regeneration (FR-020), corrections (FR-021) lack a
single write path, and stale rejection (FR-022) has no owned version counter.

## Alternatives

1. **Client-owned state** — fast UI; weak authority, audit, and multi-device
   consistency (NFR-007 / NFR-012 risk).
2. **Independent tile-owned state** — local simplicity; breaks Shared
   Understanding and selective regeneration.
3. **Orchestration-owned server state with domain projections** — one
   experience-state authority; domain services remain authoritative for business
   facts.
4. **Fully event-sourced experience state** — strong audit; heavier MVP cost
   before evidence demands it.

## Decision

**The Experience Orchestration Engine owns authoritative experience state on the
server.** The Adaptive UI Workspace holds a projection for rendering; domain
services own business facts and feed orchestration via governed topics
(ADR-008).

### Ownership

| Concern | Authoritative owner |
|---|---|
| Shared Understanding / session experience state | Experience Orchestration Engine |
| Tile layout presentation | Workspace (projection of orchestration state) |
| Products, stock, prices, slots, payments, orders | Domain services (unchanged) |
| Intent interpretation / explanations | AI Floral Concierge (non-authoritative) |

### Persistence and session

- Experience state is persisted server-side for the active shopping session so
  refresh and reconnect restore Shared Understanding.
- Sensitive customer, recipient, and payment material is stored as references or
  tokens where possible (NFR-007, NFR-012, NFR-017).
- Retention follows session and order lifecycle policy; abandoned sessions expire
  without retaining unnecessary PII.

### Context version

- Orchestration increments **context version** on every accepted intent or
  decision change that supersedes prior in-flight work.
- Messages carry the context version (envelope / ADR-008); consumers reject
  mismatched versions (FR-022 / ADR-005).

### Projections and invalidation

- Workspace tiles subscribe to orchestration projections (`workspace.state.updated`
  and related topics), not to raw domain facts alone.
- Dependency invalidation is selective: only affected tiles regenerate;
  completed customer decisions and unrelated state remain stable (FR-020).
- Customers may correct intent; orchestration accepts corrections and
  invalidates dependent projections (FR-021).

### Recovery

- After failure, orchestration rebuilds the workspace projection from persisted
  experience state plus authoritative domain queries — not from client guesswork.
- Outbox-backed publications (ADR-008) remain the path for state-change events.

## Rationale

Option 3 preserves FR-020…022 and Shared Understanding without forcing full
event sourcing in the MVP, and keeps AI and tiles from becoming sources of
business truth.

## Consequences

- BFF or API edges (if introduced by deployment ADRs) read/write experience
  state only through orchestration APIs — never as a second store of record.
- Domain services must not silently mutate experience-state fields they do not
  own.
- Test plans assert context-version increments, selective regeneration, and
  stale rejection.
- Datastore product choice (e.g. PostgreSQL) remains a separate ADR candidate.
