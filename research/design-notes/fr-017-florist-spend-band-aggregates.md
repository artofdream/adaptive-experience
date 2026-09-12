# Design note — FR-017 florist zero-PII spend-band aggregates (#430)

status: implemented (thin path)
for_issues: "#430 (child of #36 / FR-017 Engagement and CRM)"
affects: "/florist #engagement spend-band table; GET /api/v1/operator/engagement"
date: 2026-09-12

## Decision

#421/#427 shipped occasion-cohort counts and CSV/JSON export. Managers still
had no spend-band dashboard. Full FR-017 is customer engagement analytics.
This slice adds **coarse lifetime spend-band counts** from the existing
completed-order `subject_profile` path — not ML and not a per-customer list.

- Reuse ADR-020 bands from `compute_spend_band` / migration 026:
  `band_0_50`, `band_50_100`, `band_100_250`, `band_250_plus`.
  Do not invent a second 100–200 / 200+ taxonomy.
- `PsycopgCrmStore.count_spend_bands()` selects `lifetime_spend_band` +
  `COUNT(*)` only.
- `EngagementCrmService.get_engagement_analytics()` emits
  `subject_count` and `spend_band_cohorts` (all four bands, zeros included).
- Same florist-operator fail-closed gate. Export allowlist extends #427
  with `spend_band,key,count` rows.

No subject references, cents, hashes, names, or addresses leave the
allowlist. CF-051: this is engagement analytics, not staff live chat.

Not #35 outbound AI reminders. Not #27 full purchase-history CRM.
Parent #36 stays open (no ML, per-customer browse, or workbook promotion).

## Not in this slice

ML models, per-customer browse, unsolicited marketing send, staff
WebSocket chat, or promoting FR-017 out of Future.

## Prove

1. With `AEA_FLORIST_OPERATOR=1` (and the Path B named exception on
   `aea-pilot`), open `/florist` in a browser that is **not** the shop.
2. `#engagement` shows four spend-band rows (zeros when no profiles).
3. `GET /api/v1/operator/engagement` returns `subject_count` and
   `spend_band_cohorts` with the four known keys.
4. Response has no `subject_reference`, `browser_hash`, `session_id`,
   or contact fields.
5. Export CSV includes `spend_band` rows. Operator APIs disabled: 404
   and labeled sample layout.

Unit: `python platform/tests/test_crm.py -v`.
Edge: `python -m unittest edge.tests.test_perimeter edge.tests.test_browser_ui`.
