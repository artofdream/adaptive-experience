# ADR-016 — Agentic AI Boundary

Status: Accepted

Date: 2026-08-14

Related requirements: FR-001, FR-002, FR-004, FR-005, FR-007, FR-021, NFR-005,
NFR-006
(Consequential execution ties: FR-019, ADR-013)

Related decisions: [ADR-001 Shared Understanding](ADR-001-shared-understanding.md),
[ADR-009 Experience-State Ownership](ADR-009-experience-state-ownership.md),
[ADR-010 Command and Event Boundaries](ADR-010-command-event-boundaries.md),
[ADR-013 Confirmation-Driven Experience](ADR-013-confirmation-driven-experience.md),
[ADR-015 RAG and Hybrid Retrieval](ADR-015-rag-hybrid-retrieval.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md)

## Context

The AI Floral Concierge interprets intent, retrieves grounded context, reasons,
recommends, and may prepare execution plans. Technical architecture already
states that AI is never the authoritative source of business facts, and ADR-009
records AI as non-authoritative for experience state. Those statements are
scattered; implementers still risk letting the LLM write orders, payments, or
inventory tables directly, or auto-applying consequential actions without
customer approval.

ADR-013 requires confirmation for consequential execution. ADR-015 (when
landed) requires retrieved candidates to be validated before claims become
transactions. This ADR states the **agentic boundary** as a first-class
decision.

## Alternatives

1. **LLM as system of record** — agent mutates transactional tables directly;
   fastest demos; breaks audit, authority, and NFR privacy boundaries.
2. **LLM suggestions only, no tools** — safest; too weak for approved tool
   invocation and plan preparation the product expects.
3. **Agent prepares; services execute** — LLM understands, retrieves, reasons,
   recommends, invokes **approved** tools, and prepares plans; **business
   services** validate rules, perform transactions, persist state, and publish
   events; consequential actions need explicit customer approval where
   appropriate.
4. **Defer boundary to code comments** — already insufficient given ADR sprawl.

## Decision

Use the LLM/agent layer to **understand intent, retrieve grounded context,
reason, recommend, invoke approved tools, and prepare execution plans**.

The agent **shall not** directly mutate authoritative transactional tables
(orders, payments, inventory, pricing, experience-state SoT).

**Business services** validate rules, perform transactions, persist state, and
publish resulting events on the governed bus (ADR-008 / ADR-010).

**Consequential actions** (place order, charge payment, change delivery
identity, and similar) require **explicit customer approval** where appropriate
(ADR-013).

Retrieved or tool-sourced candidates remain non-authoritative until domain
validation (ADR-015 when RAG is used).

## Rationale

Option 3 matches the published authority boundary, keeps FR-021 corrections and
FR-019 payment authority in domain services, and aligns confirmation-driven
execution (ADR-013) with agent plan preparation. Option 1 is incompatible with
NFR-015…017 and auditability.

## Consequences

- Concierge / agent code paths may call approved read tools and draft plans;
  writes go through Orchestration and domain APIs only.
- Tool allowlists and publishers must not grant the agent direct DB credentials
  for authoritative tables.
- Customer-visible AI output continues to disclose AI generation (NFR-005) and
  remains correctable (FR-021 / ADR-001).
- Checkout, delivery, and payment flows keep human confirmation for
  consequential steps (ADR-013); agents must not silent-auto-submit.
- Implementation of tool-calling runtimes is out of scope for this docs ADR;
  future work must obey this boundary.
