# ADR-001 — Shared Understanding

Status: Accepted

## Context
The AI Floral Concierge infers structured intent (occasion, budget, recipient,
style, timing) from free-form conversation. Inference can be wrong, and hidden
inference erodes trust and produces poor recommendations.

## Alternatives
- Keep inferred intent internal and act on it silently.
- Ask the customer to fill a structured form up front.
- Surface the inferred intent as an editable, always-visible summary.

## Decision
Maintain a visible **Shared Understanding** (the Intent Summary tile, T-02) so
customers can confirm or correct the AI's interpretation (FR-021).

## Rationale
Making inference visible and correctable keeps the customer in control, improves
recommendation accuracy (NFR-006), and reinforces the authority boundary: the AI
interprets, the customer validates intent, and domain services validate facts.

## Consequences
- T-02 must render the current interpretation and accept corrections.
- Corrections update shared experience state and trigger selective regeneration
  of affected tiles (FR-020).
