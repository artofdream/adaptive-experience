# ADR-003 — Progressive Thought Completion

Status: Accepted

## Context
Customers often start with a partial idea ("I need flowers...") and are unsure
how to specify occasion, budget, or recipient. Rigid forms force premature,
structured input.

## Alternatives
- A structured intake form with required fields.
- Free-text only, with no guidance.
- Evolving, context-aware suggestions that help complete the thought.

## Decision
Help users **complete intent through evolving suggestions** instead of scripted
forms (FR-002), while keeping the free-form conversation primary (FR-001).

## Rationale
Progressive suggestions lower the effort of expressing intent and adapt as
understanding grows, feeding the Shared Understanding (ADR-001) without forcing a
form. This matches the "thought before form" principle.

## Consequences
- The conversation tile (T-01) offers contextual completions seeded by season,
  inventory, and business context.
- Suggestions must stay optional; the customer can always type freely.
- Accepted suggestions update intent and the Intent Summary (T-02).
