# ADR-004 — Customer Support Overlay

Status: Accepted

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
cross-cutting UX surface — not a journey tile and not T-09. **Human support
escalation (T-09 / FR-006) is Future scope** — a separate conditional overlay
outside the initial MVP.

## Rationale
Automated support covers the majority of questions immediately and keeps the
customer inside the persistent workspace. Human escalation adds staffing and
routing concerns that are not required to prove the MVP, so it is deferred while
leaving a defined extension point (T-09).

## Consequences
- The MVP ships ASO across all stages; it never blocks the workspace.
- Functional design catalogs ASO under MVP overlays; the UX guide maps it as a
  distinct surface from T-09 (see `functional-design.md`,
  `automated-support-overlay.md`, and `ux-design-guide.md`).
- The support tile T-09 and human-escalation topic remain a Future overlay.
- Roadmap must continue to list automated FAQ (FR-009) as MVP and human
  escalation (FR-006 / T-09) as Future.
