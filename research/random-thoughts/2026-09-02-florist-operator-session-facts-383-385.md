# Florist operator session facts (#383 / #384 / #385)

> **Tags**: #aea #florist #operator #gap-loop #honesty #least-data
> **Captured**: 2026-09-02
> **Issues**: #383 #384 #385
> **Related**: [[2026-09-02-florist-operator-native-web-completeness-gaps]] · [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [!409](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/409) staff-list columns

## Live evidence (Path B 2026-09-02)

1. card_message on orders but session summary often product_id only.
2. No channel on summary (list persist in !409).
3. Order facet lacked paid total; selection lacked display name.

## This MR

Shapes _operator_summary: flatten card, catalog_title, channel, payment_state, total; florist.js session facts; list total when priced.

## Honesty

FR-013 least-data. Sample inbox != live CRM. Dual-probe PASS != field gaps closed.
