# Design note — FR-016 outbound reminder outbox dry-run (#428)

status: implemented (thin path)
for_issues: "#428 (child of #35 / FR-016 Engagement and CRM)"
affects: "CRM reminder outbox; florist `#reminder-outbox`; stub send"
date: 2026-09-12

## Decision

When zero-PII occasion memory is inside the 30-day lookahead, enqueue a
least-data **outbox** row: categorical `occasion_type`, `recipient_relation`,
`days_until_event`, plus AI or template copy from #425. Rows are marked
`status=dry_run` and `send_disposition=not_sent`. There is no email, phone,
or push-token column.

Florist / internal operators can list counts and rows on
`GET /api/v1/operator/reminder-outbox` (and `/florist` `#reminder-outbox`).
`POST .../enqueue` rescans memory. `POST .../{id}/send` is the documented
send path and stays **stubbed fail-closed**: `code=not_implemented`,
`status=dry_run`, `sent=false`. No cron delivers. No SES/SMTP/SendGrid.
No FCM/APNs (ADR-019 stays a decision record).

Parent #35 stays open. Leftover is a **live outbound channel**.

## Not in this slice

Live email/SMS providers, native push, workbook promotion of FR-016 from
Future, or closing parent #35.

## Prove

1. Record an occasion inside lookahead → one outbox row (`dry_run` / `not_sent`).
2. Operator list has counts and categorical copy; no contact PII.
3. Calling send never sets `sent=true` and never changes `status` off `dry_run`.
4. Parent #35 remains open; MR may `Closes #428` only.
