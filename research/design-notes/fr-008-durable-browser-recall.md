# Design note — FR-008 durable prior-order recall (#193)

status: implementing (thin path)
for_issues: "#193 (child of #27 / FR-008 Recommendations)"
affects: "T-03 ranking behind FR-007; does not replace FR-007"
date: 2026-08-17

## Decision

Remember the last accepted catalog product in this browser after the current
checkout, without login. An opaque `__Host-aea_recall` cookie outlives the
experience session. Orchestration stores only `recall_id` → `product_id`.
That SKU is a deterministic FR-007 ranking hint on T-03 when the new session
has no accepted order of its own.

Not AI-ranked. Not CRM (#35 / #36). FR-008 stays Future. Parent #27 stays
open.

## Not in this slice

Cross-device accounts, persistent purchase-history lists, reorder /
modify-before-reorder, recipient or payment prefills, or replacing FR-007.
