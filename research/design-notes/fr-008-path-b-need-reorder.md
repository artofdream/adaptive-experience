# Design note — FR-008 Path B Need-phase reorder card (#419)

status: implemented (thin path)
for_issues: "#419 / #422 / #424 (children of #27 / FR-008 Recommendations)"
affects: "T-01 Need affordance; T-04 modify-before-reorder; T-03 ranking hint unchanged"
date: 2026-09-12

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

#424 adds modify-before-reorder on that same path: `prior_order` also
projects least-data `size` / `quantity` / `card_message` from the real
`customer_order.product` snapshot (same-session accepted order or the
durable `order_id` join). **Reorder →** and sibling **Modify →** post the
existing selection command with those options. T-04 remains the edit
surface. Modifications persist only through the normal selection /
delivery / checkout commands. No recipient or payment prefills.

Not AI-ranked. Not CRM (#35 / #36). Not a PII account. Parent #27 stays
open: last-SKU recall is the #419 slice. Multi-SKU same-browser history
is #426. Cross-device login is still leftover.

## Not in this slice

Cross-device accounts, recipient or payment prefills, native push
(ADR-019), or replacing FR-007. Multi-order history is #426. The
in-memory `ReorderService` store is not the live Path B path.

## Prove

1. Accept an order in this browser (session payment reference).
2. Open a new experience session that still presents `__Host-aea_recall`
   (do not wipe the recall cookie).
3. Need shows `#need-reorder` before any chat. Empty recall: card hidden.
4. Tap **Reorder →** (or **Modify →**) → Pick with the recalled SKU selected
   and size / quantity / card prefilled from the accepted order when present.
5. After that tap, `#need-reorder` is hidden (selection exists and/or step is past Need). A repeat tap must not re-post selection.
6. Change size / quantity / card on T-04 and confirm. The modified fields
   remain on `selection` / order summary for the next checkout step.
7. Starting Need (typed message or occasion) also hides the card.

Walker: `python scripts/walk_returning_shopper.py --payment`.
