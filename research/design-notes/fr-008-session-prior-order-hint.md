# Design note — FR-008 session prior-order hint (#190)

status: implemented (thin path)
for_issues: "#190 (child of #27 / FR-008 Recommendations)"
affects: "T-03 ranking behind FR-007; does not replace FR-007"
date: 2026-08-16

## Decision

If the same browser session already has an accepted customer order
(`submitted` or later), use that product as a deterministic ranking hint on
the existing FR-007 catalog ranker. The hint is a modest score bump plus a
tie-break. T-03 stays the reference catalog. Ranking is not AI.

FR-008 stays Future in the requirements source of truth. Parent #27 stays
open. This slice is not persistent purchase history.

## Not in this slice

Cross-session / logged-in purchase history, CRM memory (FR-016 / FR-017),
LLM catalog picks, replacing FR-007, or treating a draft `created` order as
history.
