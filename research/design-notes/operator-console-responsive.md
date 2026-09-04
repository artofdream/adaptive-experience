# Florist operator console — responsive UX (laptop / tablet / phone)

> Scope: `edge/gateway/ui/florist.html` + `assets/florist.js` + `assets/styles.css`
> (served at `/florist`). Goal: a florist operator works **efficiently** from a
> laptop, tablet, or phone.

## Status (2026-09-04)

**AGY (Antigravity) implemented the responsive redesign in `#382`** (merged to
`main`): `operator-table-wrap` scroll containers, a jump-nav pill bar, proper
filter pill buttons, and — at ≤48rem — the Staff Orders / Prepare tables collapse
to key columns (Updated/Order/Status) with an `.order-mobile-meta` summary and a
**"Details" trigger that opens a bottom-sheet order-details `<dialog>`**. Session
splits stack ≤60rem.

This branch **verified AGY's `#382` live from this remote session** across laptop
(1280), tablet (768 + 900), and phone (390) — full 9-col table on laptop, clean
3-col collapse + working order-details dialog on phone/tablet, no horizontal
scroll at any width (evidence: screen recording + screenshots), and added two
**surgical polish fixes** (building on `#382`, not clobbering it):

1. **Phone nav wrap** — `.operator-nav { flex-wrap: wrap }` ≤40rem so the 5th pill
   ("Forecast") is never clipped/hidden behind the horizontal-scroll edge.
2. **≥44px tap targets** — the mobile `.order-detail-trigger` and the dialog close
   button bumped 36px → 44px (objective requires ≥44px).

Edge unit tests green (77). The reference spec below is retained for context.

---

> Original spec (pre-`#382`): implementation-ready responsive plan. Keep
> least-data / zero-PII operator reads (NFR-017); do not invent IDs.

## Baseline (verified live in-session, current `main`)

| Viewport | Result |
|---|---|
| Laptop ~1280 | ✅ 9-col Staff Orders table fits; splits side-by-side |
| Tablet ~768 | ⚠️ Staff Orders cramped ("marginal"); splits still 2-col |
| Phone ~390 | ❌ **Unusable** — 9-col table headers collapse to single stacked letters |

Root cause: `.operator-table` has no narrow-viewport treatment. `.operator-layout`
/ `.operator-split` / `.operator-facts` already stack (≤60rem), and 44px targets
are enforced (≤40rem), but the **multi-column tables** do not adapt.

## Viewport contract (target)

- **Laptop/desktop > 960px:** current tabular layout (works). No change beyond tuning.
- **Tablet 641–960px:** no horizontal scroll. Wide tables (Staff Orders 9-col,
  Prepare 5-col) switch to the card layout below; narrow 3-col tables stay tabular.
- **Phone ≤ 640px:** no horizontal scroll. **All** operator tables use the card
  layout; one card per row, full width; key fields first.

## Card-layout pattern (CSS-first, per-tbody, no data-label needed)

Column orders are fixed, so labels are injected by `nth-child::before` scoped to
each tbody id — **no `florist.js` row-builder changes required** (lower collision
with AGY). Hide `thead`, make each `tr` a card, each `td` a label→value row.

Column maps (from `florist.html`):
- `#order-rows` (Staff Orders): 1 Updated · 2 Order · 3 Status · 4 Arrangement · 5 Card · 6 Channel · 7 Paid · 8 When · 9 Destination
- `#prepare-rows`: 1 Arrangement · 2 Count · 3 Windows · 4 Cards · 5 Channels
- `#inbox-rows`: 1 Requested · 2 Reason · 3 Session
- `#forecast-rows`: 1 Product · 2 Trend · 3 Recommendation

Sketch (final CSS added to the operator block in `styles.css`):

```css
@media (max-width: 60rem) {            /* wide tables: tablet + phone */
  #orders .operator-table thead,
  #prepare .operator-table thead { position: absolute; width: 1px; height: 1px;
    overflow: hidden; clip: rect(0 0 0 0); }           /* visually-hidden headers */
  #orders .operator-table tr,
  #prepare .operator-table tr { display: block; border: 1px solid var(--lavender);
    border-radius: .6rem; padding: .5rem .75rem; margin-bottom: .6rem; }
  #orders .operator-table td,
  #prepare .operator-table td { display: flex; justify-content: space-between;
    gap: 1rem; border: 0; padding: .3rem 0; }
  #orders .operator-table td::before { content: attr(data-col); font-weight: 650;
    color: var(--muted); }              /* label from a small CSS map below */
  /* per-column labels via nth-child when data-col is not emitted */
  #order-rows td:nth-child(1)::before { content: "Updated"; }
  #order-rows td:nth-child(2)::before { content: "Order"; }
  /* … through 9; #prepare-rows 1–5 … */
}
@media (max-width: 40rem) {            /* narrow 3-col tables: phone only */
  #inbox .operator-table thead,
  #forecast .operator-table thead { /* visually-hidden */ }
  /* same tr/td card treatment; #inbox-rows 1–3, #forecast-rows 1–3 labels */
}
```

Notes:
- Prefer emitting `data-col` on each `<td>` in the `florist.js` row-builders and
  using `td::before{content:attr(data-col)}` (robust to column reorder) **iff**
  AGY's phase 1 hasn't already restructured those builders; otherwise use the
  pure-CSS `nth-child` labels above to avoid touching `florist.js`.
- Right-align the value, keep `overflow-wrap: anywhere` for opaque refs.

## Efficiency + a11y checklist (must pass in-session across all 3 widths)

- No horizontal page scroll at 390 / 768 / 1280; no clipped content.
- Filter controls (`Today · Delayed · All`) become real ≥44px tap targets with
  spacing on phone (not mid-dot-separated inline text links).
- Most-scanned fields first in each card (Order, Status, When, Destination).
- Section landmarks/headings preserved; skip-link works; `:focus-visible` rings
  on all controls; `prefers-reduced-motion` + `forced-colors` already covered.
- Preserve section ids (`orders`, `prepare`, `inbox`, `session`, `forecast`) and
  any selectors asserted in `edge/tests/test_perimeter.py` / `test_browser_ui.py`;
  update those tests in the same change if copy/selectors move.

## Delivery (post-AGY)

1. Rebase onto AGY's merged phase-1 `main`. 2. Apply the CSS (and optional
`data-col`) change. 3. `python edge/scripts/run_integration_tests.py` green.
4. Verify live `/florist` at laptop/tablet/phone (screenshots + screen recording).
5. Figma operator-chrome mirror sync + `figma/README.md`. 6. One issue → branch →
draft MR → `@aea-mr-coordinator` handoff. Reconcile with peer !434 (operator
efficiency: parallel boot/pagination) — different concern, low overlap.
