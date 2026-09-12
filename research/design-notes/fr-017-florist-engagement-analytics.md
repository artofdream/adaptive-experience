# Design note — FR-017 florist operator engagement analytics (#421)

status: implemented (thin path)
for_issues: "#421 (child of #36 / FR-017 Engagement and CRM)"
affects: "/florist #engagement; GET /api/v1/operator/engagement"
date: 2026-09-11

## Decision

Managers need customer insights to improve campaigns (US-017 / FR-017).
Occasion memory already exists (`crm.customer_occasion_memory`, migration
018). Per-subject `GET /api/v1/operator/subjects/{ref}` is not a campaign
view. `/florist` still had no aggregate surface.

This slice adds **zero-PII occasion cohorts** on the existing operator
console:

- `EngagementCrmService.get_engagement_analytics()` counts memories,
  distinct browser hashes (count only), upcoming-in-30-days, and
  occasion / relation / event-month cohorts.
- `GET /internal/v1/operator/engagement` → BFF
  `GET /api/v1/operator/engagement` (same florist-operator fail-closed
  gate as orders / inbox / forecast).
- `/florist` `#engagement` renders totals + three count tables. Sample
  data only when operator APIs are fail-closed.

No browser hashes, subject references, names, or addresses leave the
allowlist. CF-051: this is engagement analytics, not staff live chat.

Not #35 outbound AI reminders. Not #27 full purchase-history CRM.
Parent #36 stays open (no ML or workbook promotion). Campaign cohort
export shipped later as #427.

## Not in this slice

Unsolicited marketing send, per-customer browse, spend-band dashboards,
staff WebSocket chat, or promoting FR-017 out of Future. CSV/JSON
cohort export is #427.

## Prove

1. With `AEA_FLORIST_OPERATOR=1` (and the Path B named exception on
   `aea-pilot`), open `/florist` in a browser that is **not** the shop.
2. `#engagement` shows live counts, or zeros when memory is empty.
3. `GET /api/v1/operator/engagement` returns
   `memory_count`, `unique_browsers`, `upcoming_within_days`,
   `occasion_cohorts`, `relation_cohorts`, `event_month_cohorts`.
4. Response has no `browser_hash`, `session_id`, or contact fields.
5. Operator APIs disabled: 404 and labeled sample layout.

Unit: `python platform/tests/test_crm.py -v`.
Edge: `python -m unittest edge.tests.test_perimeter edge.tests.test_browser_ui edge.tests.test_orchestration_adapter`.
