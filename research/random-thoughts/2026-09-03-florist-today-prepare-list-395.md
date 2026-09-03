# Florist today's arrangements to prepare (#395)

> **Tags**: #aea #florist #operator #395 #least-data #fr-013
> **Captured**: 2026-09-03
> **Issue**: #395
> **Related**: [[2026-09-02-florist-operator-session-facts-383-385]] · [[2026-09-02-native-web-gap-closing-technical-handoff]] · [[2026-09-02-florist-operator-native-web-completeness-gaps]]

## Slice

`/florist` now has a least-data **Today's arrangements to prepare** table derived from the existing Staff orders payload (`GET /api/v1/operator/orders`). No new API. Group by `product_id` or catalog title. Columns: count, delivery windows, truncated cards (40 chars, two unique), channel mix.

Live: today by `timing.date` or `updated_at`. Empty if no today-orders. Live fetch fail stays empty (`Could not load today's arrangements`). Labeled sample shows all sample rows so grouping is visible. Not CRM. No street/email. Claim/Resolve stay gone (!417).

## Honesty

This list is **not live on Path B** until the MR merges and `deploy-ecs` ships `gateway` (florist.html/js). Existing live `/florist` is still the checkout table + T-09 inbox + FR-012 forecast. Staff orders themselves can still 500 if migration 023 is not applied ([[2026-09-03-path-b-florist-384-redeploy-prove]]).

Out of this slice: persist Claim, #382 destination handle, #381/ADB companion, shop CSS, M12 CRM.
