# Session Memory Log: Path B Need-reorder visibility after selection (#422)

> **Tags**: #aea #session-memory #fr-008 #path-b #need #honesty #second-brain
> **Captured**: 2026-09-11
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-008-path-b-need-reorder]] · [[ADR-020]] · [[FR-008]] · [[2026-09-11-session-memory-log-fr-008-path-b-need-reorder-419]] · #27 · #419 · #422 · !498

---

## 1. Why this note exists

Merged !498 / #419 shipped T-01 `#need-reorder`. GitLab Duo on that MR flagged two leftovers. This session remediates them as child [#422](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/422). It does **not** close #27. It does **not** reopen #419.

---

## 2. Visibility leak (confirmed)

`#need-reorder` sits in the always-visible T-01 panel (no `data-journey-steps`). `setJourneyStep` therefore never hides it. `renderNeedReorder` already required `prior_order.product_id` plus #420-style freshness (no customer messages, no occasion). **Reorder →** posts `POST /api/v1/selection` only — it does not write a message or occasion — so the card could stay visible on Pick / Deliver / Pay / Track and invite a repeat tap.

Fix: `needReorderShouldShow` also requires no `selection.product_id` and `state.step <= 2`. `setJourneyStep` re-renders the card. The CTA no-ops if the gate is false.

---

## 3. `[REDACTED]` test-method claim (not reproducible)

Duo note 3823577359 said a `test_perimeter.py` method name contained literal `[REDACTED]` brackets (invalid Python identifier). Verified on `main` at `6ae1d73` and on the !498 tip `bd60dd8` / `f1ef063`: every `def test_` in `edge/tests/test_perimeter.py` is a valid identifier (`test_workspace_keeps_prior_order_facet_and_drops_secrets`, `test_workspace_omits_empty_prior_order_facet`, …). No rename. The comment was a review-redaction artifact.

---

## 4. Honest leftover on #27

Last-SKU browser recall is still not full purchase-history CRM. #422 only closes the post-merge visibility leak. Parent #27 stays open.

---

## 5. Wikilinks

[[fr-008-path-b-need-reorder]] · [[ADR-020]] · [[FR-008]] · [[2026-09-11-session-memory-log-fr-008-path-b-need-reorder-419]]
