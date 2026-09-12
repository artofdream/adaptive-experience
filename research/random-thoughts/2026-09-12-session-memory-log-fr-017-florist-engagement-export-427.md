# Session Memory Log: FR-017 florist zero-PII engagement cohort export (#427)

> **Tags**: #aea #session-memory #fr-017 #florist #crm #adr-020 #nfr-017 #second-brain #knowledge-first
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-017-florist-engagement-cohort-export]] · [[ADR-020]] · [[FR-017]] · #36 · #421 · #427

---

## 1. Why this note exists

Parent [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36) (US-017 / FR-017) stayed open after #421 shipped occasion-cohort counts. Managers still had no downloadable campaign export. Full FR-017 is customer engagement analytics. CF-051: this is not staff live chat.

This session ships child [#427](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/427): operator-gated CSV/JSON of counts and categorical cohort keys. It does **not** close #36. Do not start leftover ML, spend-band dashboards, or leftover #27 purchase-history CRM.

## 2. Slice that shipped

- `format_engagement_export()` / `export_engagement_analytics()` — same allowlist as `get_engagement_analytics()`.
- Internal + BFF `/operator/engagement/export?format=csv|json` (fail-closed florist gate; BFF writes `Content-Disposition`).
- `/florist` `#engagement` download buttons enabled only when operator APIs are live.
- Privacy tests assert hashes, session ids, and contact fields never leave the file.

## 3. Honest leftover on #36

| Still open | Why |
|---|---|
| ML models | No model, no scoring |
| Per-customer browse | Aggregates, not a list |
| Spend-band dashboards | Subject-profile bands not in this export |
| Workbook FR-017 Future | Do not promote IDs from this MR |

## 4. Wikilinks

[[fr-017-florist-engagement-cohort-export]] · [[fr-017-florist-engagement-analytics]] · [[ADR-020]] · [[FR-017]] · [[2026-09-11-session-memory-log-fr-017-florist-engagement-421]]
