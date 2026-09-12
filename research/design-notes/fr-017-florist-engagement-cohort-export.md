# Design note — FR-017 florist zero-PII engagement cohort export (#427)

status: implemented (thin path)
for_issues: "#427 (child of #36 / FR-017 Engagement and CRM)"
affects: "/florist #engagement export; GET /api/v1/operator/engagement/export"
date: 2026-09-12

## Decision

#421 shipped zero-PII occasion-cohort counts on `/florist`. Managers still
could not download those aggregates for campaign planning. Full FR-017 is
customer engagement analytics. This slice adds **campaign export** of the
same allowlist — not ML and not a per-customer list.

- `EngagementCrmService.export_engagement_analytics()` formats
  `get_engagement_analytics()` as CSV or JSON (`section,key,count` or the
  same JSON object).
- `GET /internal/v1/operator/engagement/export?format=csv|json` → BFF
  `GET /api/v1/operator/engagement/export` (same florist-operator
  fail-closed gate as `#engagement`).
- BFF re-allowlists via `_least_data_operator_engagement` before writing
  the attachment (`Content-Disposition`).
- `/florist` `#engagement` offers Download CSV / Download JSON only when
  operator APIs are live. Sample layout keeps the buttons disabled.

No browser hashes, subject references, names, or addresses leave the
allowlist. CF-051: this is engagement analytics, not staff live chat.

Not #35 outbound AI reminders. Not #27 full purchase-history CRM.
Parent #36 stays open (no ML, spend-band dashboard, or workbook promotion).

## Not in this slice

Per-customer browse, spend-band dashboards, ML models, unsolicited
marketing send, staff WebSocket chat, or promoting FR-017 out of Future.

## Prove

1. With `AEA_FLORIST_OPERATOR=1` (and the Path B named exception on
   `aea-pilot`), open `/florist` in a browser that is **not** the shop.
2. `#engagement` Download CSV / Download JSON are enabled only when
   operator APIs are live.
3. `GET /api/v1/operator/engagement/export?format=csv` returns
   `section,key,count` rows for totals + occasion / relation / event-month.
4. `format=json` returns the same allowlisted object as
   `GET /api/v1/operator/engagement`.
5. Response has no `browser_hash`, `session_id`, or contact fields.
6. Operator APIs disabled: 404 and labeled sample layout (buttons stay
   disabled).

Unit: `python platform/tests/test_crm.py -v`.
Edge: `python -m unittest edge.tests.test_perimeter edge.tests.test_browser_ui`.
