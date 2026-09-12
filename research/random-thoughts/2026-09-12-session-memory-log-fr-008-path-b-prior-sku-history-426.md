# Session Memory Log: FR-008 Path B multi-order prior SKU history (#426)

> **Tags**: #aea #session-memory #fr-008 #path-b #need #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-008-path-b-prior-sku-history]] · [[fr-008-path-b-need-reorder]] · [[fr-008-durable-browser-recall]] · [[ADR-020]] · [[FR-008]] · #27 · #419 · #422 · #424 · #426

---

## 1. Why this note exists

Parent [#27](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/27) (US-008 / FR-008) stayed open after #419 last-SKU Need Reorder, #422 hide gates, and #424 modify-before-reorder. Honest leftover on #27 was **multi-order purchase history** — recall was still one `prior_order` facet.

This session ships child [#426](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/426): a Path B history chooser for the same opaque browser recall. It does **not** close #27. Do not reopen #419 / #422 / #424. Do not start #35 / #36.

---

## 2. Slice that shipped

- Migration 027: `browser_order_recall` primary key is `(recall_id, order_id)`. Last five unexpired accepted orders are kept.
- Workspace `prior_orders[]` is least-data (`product_id` plus size / quantity / card). `prior_order` stays the latest row.
- BFF allowlists those fields and drops recipient, `order_id`, payment, and secrets.
- Need `#need-reorder-history` appears when ≥2 items exist. Shopper picks a non-latest SKU, then **Reorder →**.
- #422 hide gates stay. No login. No PII prefills.

---

## 3. Honest leftover on #27

| Still open | Why |
|---|---|
| Cross-device login | Cookie / edge-wallet only; no account |
| Workbook FR-008 Future | Do not promote IDs from this MR |
| Full purchase-history CRM | Same-browser cap of 5 least-data SKUs is not #35 / #36 |

#424 modify-before-reorder remains its own child if it has not merged; this slice reuses the same option allowlist and does not reopen that issue.

---

## 4. Wikilinks

[[fr-008-path-b-prior-sku-history]] · [[fr-008-path-b-need-reorder]] · [[fr-008-durable-browser-recall]] · [[ADR-020]] · [[FR-008]] · [[2026-09-11-session-memory-log-fr-008-path-b-need-reorder-419]]
