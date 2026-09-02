# Companion budget label preserve (#388)

> **Tags**: #aea #companion #ux #budget #gap-loop #honesty
> **Captured**: 2026-09-02
> **Issue**: [#388](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/388)
> **Related**: [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-companion-native-web-gap-closing-loop]] · [[2026-09-02-florist-operator-native-web-completeness-gaps]]

## Live evidence (ASUS Play/claimed v3, 2026-09-02)

After selecting a product, budget display collapsed from range `$50–100` to numeric `Budget: 100.0` on filter/Pay.

## Root cause

Need chips PATCH a numeric `budget` correction to the BFF. Later `refreshSharedUnderstanding` (including after `selectArrangement`) overwrote the shopper-facing chip label with that coerced number.

## Fix

Keep `budgetChipLabel` from Need chips/skip; prefer it for UI `sharedUnderstanding.budget` while still sending numeric ceiling for ranking.

## Honesty

Does not claim Play honesty (#390). Local label preserve ≠ server intent shape.

