# Companion budget band filter (#387)

> **Tags**: #aea #companion #ux #budget #gap-loop #honesty
> **Captured**: 2026-09-02
> **Issue**: [#387](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/387)
> **Related**: [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-companion-native-web-gap-closing-loop]] · [[2026-09-02-florist-operator-native-web-completeness-gaps]]

## Live evidence (ASUS Play/claimed v3, 2026-09-02)

On Need, chip **`$50–100`** still listed **Budget Mixed Bunch `$35,00`** on Pick (`03-budget-selected.png` → `04-pick.png`, ASUS_I001DC). Filter copy claimed a local price filter.

## Root cause

`SessionRepository.applyBudgetFilterToArrangements` used **ceiling-only** (`price <= 100`). Mid-band `$50–100` therefore kept $35 SKUs.

## Fix

- `parseBudgetBand`: Under $50 → `[null, 50]`; `$50–100` → `[50, 100]`; `$100+` → `[100, null]`; bare numeric → soft ceiling only.
- Inclusive floor+ceiling filter; if band empties catalog, keep full list (honesty UI still shows band).

## Honesty

- Local catalog filter ≠ server ranking. BFF still receives a numeric correction for ranking.
- Sample inbox ≠ live CRM. Do not claim dual-probe / Play honesty closed (#390).

