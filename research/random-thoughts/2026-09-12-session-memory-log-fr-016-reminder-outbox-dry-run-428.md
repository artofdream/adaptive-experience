# Session Memory Log: FR-016 outbound reminder outbox dry-run (#428)

> **Tags**: #aea #session-memory #fr-016 #path-b #outbox #adr-019 #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-016-reminder-outbox-dry-run]] · [[fr-016-ai-need-reminder-copy]] · [[fr-016-path-b-need-reminder]] · [[ADR-019]] · [[ADR-020]] · [[FR-016]] · #35 · #420 · #425 · #428

---

## 1. Why this note exists

Parent [#35](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/35) (US-016 / FR-016) stayed open after #425 / !503 shipped AI-authored in-session `#need-reminder` copy. Leftover was unsolicited outbound send. Sponsor AFK: do not invent live mail credentials. This session ships child [#428](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/428): a dry-run outbox. It does **not** close #35. Do not implement FCM/APNs.

---

## 2. Slice that shipped

- Migration `027_crm_reminder_outbox.sql` — least-data rows (`occasion_type`, `recipient_relation`, `days_until_event`, copy). No contact columns. `ON DELETE CASCADE` from occasion memory.
- `EngagementCrmService` enqueues when a recorded occasion is inside lookahead; `enqueue_upcoming_dry_run` rescans. Copy reuses #425 `_authored_copy` (`ai` or `template`).
- Operator `GET /internal/v1/operator/reminder-outbox` + BFF `/api/v1/operator/reminder-outbox` + `/florist` `#reminder-outbox` list counts and rows without contact PII.
- `POST .../send` is stubbed fail-closed: `not_implemented` / `dry_run` / `sent=false`. Never delivers.

---

## 3. Honest leftover on #35

| Still open | Why |
|---|---|
| Live outbound channel | No SES/SMTP/SendGrid (or SMS) path on Path B; dry-run only |
| ADR-019 native push | Decision record only — do not implement FCM/APNs |
| Workbook FR-016 Future | Do not promote IDs from this MR |

In-session pull card (#420) and AI copy (#425) are no longer leftover.

---

## 4. Wikilinks

[[fr-016-reminder-outbox-dry-run]] · [[fr-016-ai-need-reminder-copy]] · [[fr-016-path-b-need-reminder]] · [[ADR-019]] · [[ADR-020]] · [[FR-016]] · [[2026-09-12-session-memory-log-fr-016-ai-need-reminder-copy-425]]
