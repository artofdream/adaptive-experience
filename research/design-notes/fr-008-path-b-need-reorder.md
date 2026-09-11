# Design note — FR-008 Path B Need-phase reorder card (#419)

status: implemented (thin path)
for_issues: "#419 / #422 (children of #27 / FR-008 Recommendations)"
affects: "T-01 Need affordance; T-03 ranking hint unchanged"
date: 2026-09-11

## Decision

When a returning browser already has an accepted-order recall
(`order.prior_product_id` from the same-session accepted order or the
durable `__Host-aea_recall` map), project a least-data `prior_order`
workspace facet (`product_id` only). Path B Need (T-01) shows a
companion-shaped card — **Reorder previous bouquet** / **Reorder →** —
only when Need is still fresh: no customer messages, no occasion, no
current selection, and the journey is still on Need (step ≤ 2). #422
hides the card after **Reorder →** so T-01 does not invite a repeat tap
on Pick / Deliver / Pay / Track.

Tap posts the existing selection command. Inventory and price are
revalidated now (NFR-009). The shopper lands on Pick (T-04). Ranking on
T-03 remains FR-007 plus the existing `prior_order_hint`.

Not AI-ranked. Not CRM (#35 / #36). Not a PII account. Parent #27 stays
open: this is last-SKU browser recall, not multi-order purchase history.

## Not in this slice

Cross-device accounts, persistent purchase-history lists,
modify-before-reorder, recipient or payment prefills, native push
(ADR-019), or replacing FR-007.

## Prove

1. Accept an order in this browser (session payment reference).
2. Open a new experience session that still presents `__Host-aea_recall`
   (do not wipe the recall cookie).
3. Need shows `#need-reorder` before any chat. Empty recall: card hidden.
4. Tap **Reorder →** → Pick with the recalled SKU selected.
5. After that tap, `#need-reorder` is hidden (selection exists and/or step is past Need). A repeat tap must not re-post selection.
6. Starting Need (typed message or occasion) also hides the card.

Walker: `python scripts/walk_returning_shopper.py --payment`.
