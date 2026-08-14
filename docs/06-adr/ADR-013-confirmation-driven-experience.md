# ADR-013 — Confirmation-Driven Experience

Status: Accepted

Date: 2026-08-14

Related requirements: FR-014, FR-018, FR-019, FR-020, NFR-012, NFR-017
(Future sources of prior context: FR-008, FR-016, FR-017)

Related decisions: [ADR-001 Shared Understanding](ADR-001-shared-understanding.md),
[ADR-002 Experiences Instead of Pages](ADR-002-experiences-instead-of-pages.md),
[ADR-003 Progressive Thought Completion](ADR-003-progressive-thought-completion.md),
[ADR-005 Latest Relevant Intent Wins](ADR-005-latest-relevant-intent-wins.md),
[ADR-009 Experience-State Ownership](ADR-009-experience-state-ownership.md)

Related architecture: [Customer Journey](../03-functional-design/customer-journey.md),
[Functional Design](../03-functional-design/functional-design.md)

## Context

ADR-001 and ADR-003 establish confirmation and “thought before form” for
**intent discovery**: customers confirm or correct AI interpretation (T-02) and
complete partial thoughts with suggestions (T-01) instead of blank structured
intake.

Transaction steps still risk the opposite failure mode. Delivery and recipient
(T-05), order summary (T-06), and checkout (T-07) can force customers to
re-enter recipient, address, delivery slot, payment, or preference data that
trusted services or already-approved context already hold. Silent auto-apply of
that data is equally wrong: consequential fields must stay customer-validated,
and privacy constraints (NFR-012, NFR-017) forbid exposing more than each step
needs.

ADR-002 and ADR-009 preserve workspace continuity and completed decisions
(FR-020), but they do not state the UX rule for how prior or service-supplied
transaction facts should be presented. This ADR does.

## Alternatives

1. **Blank re-entry at every step** — maximum explicitness; high friction and
   duplicates data the session or domain services already hold.
2. **Silent prefill and auto-submit** — fast; weak trust, weak audit of
   consequential choices, and easy privacy overreach.
3. **Confirmation-driven presentation** — surface trusted or prior-approved
   values for validation; ask only for missing, ambiguous, or consequential
   deltas.
4. **Defer entirely to Future CRM memory (FR-008 / engagement)** — postpones a
   session-scoped rule the MVP journey already needs at T-05…T-07.

## Decision

Prefer **confirmation over repetitive data gathering** for transaction
execution.

When trusted services or prior approved context can supply recipient, address,
delivery, payment, or preference information, **present that information for
customer validation** and ask only for missing, ambiguous, or consequential
decisions.

This extends the Thought Before Form principle from intent discovery
(ADR-001 / ADR-003) into delivery, summary, and checkout execution (T-05…T-07).

### Scope — MVP

In MVP, “prior approved context” means values already established in the
**active shopping session** or returned by **authoritative domain services** for
that session, for example:

- recipient and delivery choices already accepted in T-05 (FR-014)
- itemized totals already shown in T-06 (FR-018)
- payment initiation state and provider references for T-07 (FR-019)
- completed decisions preserved across selective regeneration (FR-020 / ADR-009)

MVP does **not** require cross-session customer memory, prior-order recall, or
CRM-driven prefills.

### Scope — Future

Cross-session recall (previous recipients, addresses, payment preferences,
occasion history) may become additional sources of confirmable context when
Future capabilities such as FR-008 (purchase-history personalization) and
engagement/CRM features (FR-016, FR-017) land. Those sources remain subject to
the same rule: present for validation; never silent auto-apply of consequential
fields.

### Authority and privacy

- Domain services remain authoritative for business facts; the workspace and AI
  only present projections for confirmation (ADR-009).
- Sensitive customer, recipient, and payment material appears as references,
  tokens, or minimized displays where possible (NFR-012, NFR-017).
- Consequential actions (place order, charge payment, change delivery identity)
  still require explicit customer approval before domain mutation.

## Rationale

Option 3 keeps friction low without hiding consequential choices. It aligns
intent-time confirmation (ADR-001) with execution-time confirmation, uses the
persistent workspace (ADR-002) as the place those values remain visible, and
avoids pulling Future CRM scope into MVP while still stating the rule T-05…T-07
need now.

## Consequences

- T-05, T-06, and T-07 should prefer confirmable summaries of known values over
  empty forms when session or domain context already supplies them.
- Missing or ambiguous fields still open focused capture; consequential changes
  remain explicit customer decisions.
- Selective regeneration must not wipe confirmed transaction choices (FR-020).
- Implementations must not treat this ADR as authorization to load Future
  CRM/memory features into MVP.
- Related agentic-boundary guidance (agent prepares plans; services execute after
  approval) stays complementary and is not replaced here.
