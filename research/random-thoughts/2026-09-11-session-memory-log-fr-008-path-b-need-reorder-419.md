# Session Memory Log: FR-008 Path B Need-phase reorder card (#419)

> **Tags**: #aea #session-memory #fr-008 #path-b #need #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-11
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-008-path-b-need-reorder]] · [[fr-008-session-prior-order-hint]] · [[fr-008-durable-browser-recall]] · [[ADR-020]] · [[FR-008]] · #27 · #190 · #193 · #404 · #419

---

## 1. Why this note exists

Parent [#27](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/27) (US-008 / FR-008) stayed open after the #190 session hint and #193 durable `__Host-aea_recall` ranking hint. Companion Need already has a one-tap Reorder card (#404). Path B web still required conversation before a returning shopper could reorder.

This session ships child [#419](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/419): a Need-phase card on `/` matching companion Need / Pick. It does **not** close #27. Last-SKU browser recall is not full purchase-history CRM. Do not start #35 / #36.

---

## 2. Slice that shipped

- Workspace facet `prior_order.product_id` when `order.prior_product_id` resolves (same-session accepted order or durable recall).
- BFF allowlists that SKU only — drops recipient, order_id, secrets.
- T-01 `#need-reorder` shows **Reorder previous bouquet** / **Reorder →** only when Need is fresh (no customer messages, no occasion).
- Tap posts existing `POST /api/v1/selection` and lands on Pick (T-04). Inventory revalidated now (NFR-009).
- Walker `walk_returning_shopper.py` replays `__Host-aea_recall` into a new session and classifies the Need card. #193 is no longer treated as open.

---

## 3. Honest leftover on #27

| Still open | Why |
|---|---|
| Multi-order purchase history | Recall is last accepted SKU only |
| Modify-before-reorder as a live Path B path | `reorder.py` stays an in-memory helper |
| Cross-device accounts | Cookie / edge-wallet only; no login |
| Workbook FR-008 Future | Do not promote IDs from this MR |

Empty recall hides the card. That is current product, not an empty-state CTA.

---

## 4. Wikilinks

[[fr-008-path-b-need-reorder]] · [[fr-008-durable-browser-recall]] · [[fr-008-session-prior-order-hint]] · [[ADR-020]] · [[FR-008]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]]
