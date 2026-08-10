# Experience Contract — Automated Support Overlay (ASO)

## Purpose
Provide immediate, automated answers to frequently asked customer questions
from approved florist product and policy information while the customer stays
inside the adaptive workspace (FR-009, backed by FR-005).

## Entry Conditions
- Customer is in any MVP journey stage (discovery through tracking).
- Customer opens help / asks a common question via conversation or the overlay.

## Exit Conditions
- Question answered from approved content, or
- No approved answer is available (customer continues in-workspace; human
  escalation via T-09 is Future scope only).

## Inputs
- Customer question text
- Active experience / context version
- Approved product and policy knowledge

## Outputs
- AI-labeled automated answer (NFR-005)
- Optional deep-link back into the relevant tile without navigation reset

## Knowledge Consumed
- Approved product catalog facts
- Pricing and delivery policy snippets
- FAQ corpus for common ordering questions

## Knowledge Contributed
- None required for MVP (no CRM memory write-back)

## Events Published
- `support.faq.answered` (informational; does not mutate order state)

## Events Consumed
- None required to open the overlay; may read current Shared Understanding for
  contextual answers without overriding customer decisions (FR-020)

## Success Criteria
- Common FAQ answered without leaving the workspace
- Overlay never blocks tile interaction
- Distinct from Future T-09 / FR-006 human escalation (see ADR-004)
