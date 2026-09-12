# Session Memory Log: FR-008 Path B modify-before-reorder (#424)

> **Tags**: #aea #session-memory #fr-008 #path-b #need #reorder #second-brain
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-008-path-b-need-reorder]] · [[fr-008-durable-browser-recall]] · [[fr-008-session-prior-order-hint]] · [[ADR-020]] · [[FR-008]] · [[2026-09-11-session-memory-log-fr-008-path-b-need-reorder-419]] · [[2026-09-11-session-memory-log-need-reorder-visibility-422]] · #27 · #419 · #422 · #424

---

## 1. Why this note exists

Parent [#27](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/27) (US-008 / FR-008) stayed open after #419 Need Reorder and #422 hide-after-pick. `ReorderService.prepare_reorder` was still an in-memory helper. Migration 017 stores opaque recall → `order_id` + product only.

This session ships child [#424](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/424): a falsifiable Path B modify-before-reorder path. It does **not** close #27. It does **not** reopen #419 / #422.

---

## 2. Slice that shipped

- Live Path B reads size / quantity / card from the real `customer_order.product` snapshot (same-session accepted order or the durable `order_id` join). Options are not copied onto `browser_order_recall`.
- Workspace `prior_order` is still least-data: SKU plus those three fields. BFF drops recipient, `order_id`, payment, secrets.
- `#need-reorder` keeps **Reorder →** and adds sibling **Modify →**. Both post the existing selection command with recalled options and land on T-04. #422 hide gates stay.
- Shopper edits the existing T-04 size / quantity / card fields and confirms. Modifications persist only through the normal selection command.
- `least_data_reorder_options` is the live equivalent of `ReorderService`. The in-memory store is not wired as Path B.
- Walker `walk_returning_shopper.py --payment` changes those fields after Reorder and classifies whether they survive into `selection`.

---

## 3. Honest leftover on #27

| Still open | Why |
|---|---|
| Multi-order purchase history | Recall is last accepted SKU only |
| Cross-device accounts | Cookie / edge-wallet only; no login |
| Workbook FR-008 Future | Do not promote IDs from this MR |

Recipient and payment prefills stay out. That is current product, not a missing CTA.

---

## 4. Wikilinks

[[fr-008-path-b-need-reorder]] · [[fr-008-durable-browser-recall]] · [[fr-008-session-prior-order-hint]] · [[ADR-020]] · [[FR-008]] · [[2026-09-11-session-memory-log-fr-008-path-b-need-reorder-419]] · [[2026-09-11-session-memory-log-need-reorder-visibility-422]]
