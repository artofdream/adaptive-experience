# FR-017 florist zero-PII spend-band aggregates (#430)

> **Tags**: #aea #second-brain #fr-017 #florist #crm #adr-020 #nfr-017 #knowledge-first
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-017-florist-spend-band-aggregates]] · [[fr-017-florist-engagement-analytics]] · [[fr-017-florist-engagement-cohort-export]] · [[ADR-020]] · [[FR-017]] · #36 · #421 · #427 · #430

---

## 1. Why this note exists

[#421](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/421) and [#427](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/427) shipped `/florist` `#engagement` occasion counts and export. Leftover on parent [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36): spend-band dashboards, ML, per-customer browse. This note records child [#430](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/430): operator-gated **band + count** aggregates from existing completed-order `subject_profile` rows.

Do **not** close #36. Do not start leftover ML or per-customer lists.

## 2. Slice that shipped

- `PsycopgCrmStore.count_spend_bands()` — `GROUP BY lifetime_spend_band` only.
- `GET /internal/v1/operator/engagement` → BFF `GET /api/v1/operator/engagement` includes `subject_count` and `spend_band_cohorts` (florist-operator fail-closed gate).
- `/florist` `#engagement` spend-band table next to occasion / relation / month.
- Export extension: `spend_band,<band>,<count>` plus `totals,subject_count`.
- Bands are the existing ADR-020 set (`band_0_50` … `band_250_plus`), not a new 100–200 / 200+ taxonomy.

## 3. Honest leftover on #36

| Still open | Why |
|---|---|
| ML models | Aggregates only; no model |
| Per-customer browse | Counts, not a list |
| Workbook FR-017 Future | Do not promote IDs from this MR |

Empty profiles export four zero bands. That is current product.

## 4. Wikilinks

[[fr-017-florist-spend-band-aggregates]] · [[fr-017-florist-engagement-analytics]] · [[fr-017-florist-engagement-cohort-export]] · [[ADR-020]] · [[FR-017]] · [[CF-051-fr016-017-narrative]] · [[2026-09-11-session-memory-log-fr-017-florist-engagement-421]]
