# FR-017 florist zero-PII engagement cohort export (#427)

> **Tags**: #aea #second-brain #fr-017 #florist #crm #adr-020 #nfr-017 #knowledge-first
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-017-florist-engagement-cohort-export]] · [[fr-017-florist-engagement-analytics]] · [[ADR-020]] · [[FR-017]] · #36 · #421 · #427

---

## 1. Why this note exists

[#421](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/421) shipped `/florist` `#engagement` counts. Leftover on parent [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36): campaign export / ML, per-customer browse, spend-band dashboards. This note records child [#427](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/427): operator-gated CSV/JSON of **counts + categorical keys only**.

Do **not** close #36. Do not start leftover ML, spend-band dashboards, or per-customer lists.

## 2. Slice that shipped

- `EngagementCrmService.export_engagement_analytics()` — CSV (`section,key,count`) or JSON from the same allowlisted analytics object.
- `GET /internal/v1/operator/engagement/export` → BFF `GET /api/v1/operator/engagement/export?format=csv|json` (florist-operator fail-closed gate).
- `/florist` `#engagement` Download CSV / Download JSON. Disabled on labeled sample layout.
- Allowlist drops hashes, subject refs, and contact fields before the attachment is written.

## 3. Honest leftover on #36

| Still open | Why |
|---|---|
| ML models | Export is aggregates only; no model |
| Per-customer browse | Counts, not a list |
| Spend-band dashboards | Subject-profile aggregates left for a later slice |
| Workbook FR-017 Future | Do not promote IDs from this MR |

Empty memory exports zeros. That is current product.

## 4. Wikilinks

[[fr-017-florist-engagement-cohort-export]] · [[fr-017-florist-engagement-analytics]] · [[ADR-020]] · [[FR-017]] · [[CF-051-fr016-017-narrative]] · [[2026-09-11-session-memory-log-fr-017-florist-engagement-421]]
