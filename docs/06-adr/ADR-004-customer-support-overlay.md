# ADR-004 — Customer Support Overlay

Status: Amended

## Context
Customers need help at any point in the journey (discovery, recommendation,
delivery, checkout, tracking). Two kinds of help exist: automated assistance
(answers from approved product and policy information) and human assistance
(a staff representative resolving complex cases).

## Alternatives
- A dedicated support page separate from the workspace.
- Human live chat available in the MVP throughout the journey.
- An automated support overlay in the MVP, with human escalation deferred.

## Decision
Provide the **Automated Support Overlay (ASO)** throughout the journey in the
MVP (FR-009, backed by FR-005 approved product/policy answers). ASO is a
cross-cutting UX surface — not a journey tile and not T-09.

**Amendment (2026-08-15):** Deliver a **thin T-09 / FR-006 Contact Florist
path**. The customer confirms an allowlisted reason; Support Service records
`support.escalation.requested` (escalation reason + opaque session/context
reference) and acknowledges the request. This is not live chat, staff CRM, or
ticketing (FR-016 / FR-017 remain Future). FR-006 stays Future in the
requirements source of truth; the overlay is implemented as a Future-backlog
slice.

## Rationale
Automated support covers the majority of questions immediately and keeps the
customer inside the persistent workspace. A governed escalation command is
enough for human handoff without a CRM product. Live chat and staff tooling
remain deferred.

## Consequences
- The MVP ships ASO across all stages; it never blocks the workspace.
- Contact Florist opens T-09, not ASO. Chat with Lily / Help remain FR-009.
- Technical architecture assigns `support.faq.answered` to the AI Floral
  Concierge and `support.escalation.requested` to Support Service.
- Payloads stay least-data (NFR-017): allowlisted reason and opaque
  references; raw contact, address, and payment fields are rejected.
- A local florist operator console may read those least-data escalations
  (`/florist`, fail-closed). It is not live chat or FR-016 / FR-017 CRM.
- **FR-010** (Future automated responses about order status, delivery, and
  availability) stays outside ASO and T-09. It does not replace FR-009 FAQ
  answers or authoritative tracking via FR-015 / FR-023 / T-08.
