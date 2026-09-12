# Session Memory Log: FR-017 florist operator engagement analytics (#421)

> **Tags**: #aea #session-memory #fr-017 #florist #crm #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-11
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-017-florist-engagement-analytics]] · [[ADR-020]] · [[FR-017]] · #36 · #421

---

## 1. Why this note exists

Parent [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36) (US-017 / FR-017) stayed open after thin zero-PII occasion memory and per-subject insights shipped. `/florist` still labeled FR-017 out of scope. Managers had no aggregate campaign view. Full FR-017 is customer engagement analytics. CF-051: this is not staff live chat.

This session ships child [#421](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/421): zero-PII occasion-cohort counts on `/florist`. It does **not** close #36. Do not start leftover #35 outbound AI reminders or leftover #27 purchase-history CRM.

---

## 2. Slice that shipped

- `EngagementCrmService.get_engagement_analytics()` — memory_count, unique_browsers, upcoming_within_days, occasion / relation / event-month cohorts.
- `GET /internal/v1/operator/engagement` → BFF `GET /api/v1/operator/engagement` (florist-operator fail-closed gate).
- `/florist` `#engagement` panel. Sample data only when operator APIs are fail-closed.
- Allowlist drops hashes, subject refs, and contact fields.

---

## 3. Honest leftover on #36

| Still open | Why |
|---|---|
| Campaign export / ML | Counts only on this slice; CSV/JSON export is #427. ML still open |
| Per-customer browse | Aggregates, not a list |
| Workbook FR-017 Future | Do not promote IDs from this MR |
| Spend-band dashboards | Subject-profile aggregates left for a later slice |

Empty memory shows zeros. That is current product.

---

## 4. Wikilinks

[[fr-017-florist-engagement-analytics]] · [[ADR-020]] · [[FR-017]] · [[CF-051-fr016-017-narrative]] · [[2026-09-11-session-memory-log-fr-016-path-b-need-reminder-420]]
