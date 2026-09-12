# Design note — FR-008 Path B multi-order prior SKU history (#426)

status: implemented (thin path)
for_issues: "#426 (child of #27 / FR-008 Recommendations)"
affects: "T-01 Need history chooser; `prior_order` latest row unchanged"
date: 2026-09-12

## Decision

When the same opaque `__Host-aea_recall` map has more than one accepted
order (migration 027: one row per `order_id`, 30-day expiry, cap 5),
project a least-data `prior_orders[]` facet. Each item is catalog SKU plus
size / quantity / card when those tokens exist on the real
`customer_order.product` snapshot. `prior_order` remains the latest row
so #419 / #422 / #424 stay valid.

Need shows `#need-reorder-history` only when two or more distinct items
are present. The shopper picks a **non-latest** prior SKU, then
**Reorder →**. Hide gates from #422 stay: no customer messages, no
occasion, no current selection, journey still on Need.

Not a login. Not CRM (#35 / #36). No recipient or payment prefills.
Parent #27 stays open: cross-device accounts are still out.

## Not in this slice

Cross-device login, persistent purchase-history CRM, recipient or payment
prefills, native push (ADR-019), or replacing FR-007.

## Prove

1. Accept two different SKUs in this browser (two sessions, same recall
   cookie).
2. Open a new experience session that still presents `__Host-aea_recall`.
3. Need shows `#need-reorder-history` with both SKUs. Latest is selected.
4. Pick the non-latest SKU → **Reorder →** → Pick with that SKU selected.
5. After that tap, `#need-reorder` is hidden (#422).

Walker: `python scripts/walk_returning_shopper.py --payment`
(chooser step is blocked until the walk has ≥2 distinct accepted SKUs).
Postgres integration: `test_workspace_projects_multi_order_prior_sku_history`.
