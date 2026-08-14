# ADR-015 — RAG and Hybrid Retrieval

Status: Accepted

Date: 2026-08-14

Related requirements: FR-002, FR-005, FR-007, NFR-006
(Related Future: FR-008, FR-010)

Related decisions: [ADR-014 PostgreSQL pgvector](ADR-014-postgresql-pgvector.md),
[ADR-001 Shared Understanding](ADR-001-shared-understanding.md),
[ADR-003 Progressive Thought Completion](ADR-003-progressive-thought-completion.md),
[ADR-011 Experience-State Datastore](ADR-011-experience-state-datastore.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md),
[Automated Support Overlay](../03-functional-design/automated-support-overlay.md)

## Context

[ADR-014](ADR-014-postgresql-pgvector.md) selects `pgvector` on PostgreSQL as the
semantic retrieval store. That decision does not define **when** or **how**
retrieval-augmented generation combines structured filters with vectors, nor
how retrieved candidates become customer-visible claims.

Lily’s Florist recommendations and grounded answers need product knowledge that
matches fuzzy intent while still respecting exact business constraints (budget,
availability, delivery). Treating similarity hits as facts risks incorrect
prices, stock, or policy claims. The MVP automated support path today uses
deterministic approved FAQ answers — not RAG — and must not silently change.

## Alternatives

1. **Structured filters only** — exact constraints; weak fuzzy catalog grounding.
2. **Vector search only** — good semantic recall; weak exact constraint enforcement.
3. **Hybrid retrieval + post-validation** — structured PostgreSQL filters for exact
   constraints, `pgvector` for fuzzy intent, combine when useful; validate hits
   against authoritative domain data before display or transaction.
4. **Replace MVP FAQ with RAG immediately** — premature; current approved-answer
   path already satisfies FR-005/FR-009 for MVP.

## Decision

When semantic retrieval is used to ground recommendations or generative answers,
use **hybrid retrieval**:

- **Structured PostgreSQL filters** for exact business constraints.
- **`pgvector` semantic search** for fuzzy intent and catalog/knowledge grounding.
- **Combine both** when appropriate.

**Retrieved candidates must be validated** against authoritative product,
inventory, pricing, and delivery data before claims are displayed or
transactions are executed. Similarity rank is never a source of business truth.

### Scope — MVP architecture

- This ADR is the Accepted **pattern** for hybrid RAG when those features are
  implemented or extended.
- The current MVP **deterministic approved-FAQ / support** path
  ([design note](../../research/design-notes/m6-support-answers-contract.md))
  remains valid and is **not** replaced by this ADR.
- Enabling embeddings, indexes, and RAG call paths is a separate implementation
  effort under ADR-014 + this decision.

### Scope — Future

Purchase-history personalization (FR-008) and broader automated status/delivery
answers (FR-010) may consume the same hybrid pattern once those capabilities
land, still subject to post-retrieval validation.

## Rationale

Option 3 matches the authority boundary (AI interprets; domain services
validate) and uses the ADR-014 store without inventing a second truth for
price/stock. Option 4 would churn a working MVP FAQ path without necessity.

## Consequences

- Recommendation / concierge features that adopt RAG must query structured
  constraints and vectors, then re-check authoritative services before T-03
  display or downstream mutation.
- Support FAQ may later adopt RAG for approved knowledge only with the same
  validation rule; until then, keep the deterministic matcher.
- Agent tooling that retrieves context (forthcoming agentic-boundary ADR) must
  treat retrieval hits as candidates, not commits.
- Tests for RAG-enabled paths assert validation failure closes the claim path
  when inventory/price/delivery disagree with the retrieved snippet.
