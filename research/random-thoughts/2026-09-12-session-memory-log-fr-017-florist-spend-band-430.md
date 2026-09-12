# Session Memory Log: FR-017 florist zero-PII spend-band aggregates (#430)

> **Tags**: #aea #session-memory #fr-017 #florist #crm #adr-020 #nfr-017 #second-brain #knowledge-first
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-017-florist-spend-band-aggregates]] · [[ADR-020]] · [[FR-017]] · #36 · #421 · #427 · #430

---

## 1. Why this note exists

Parent [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36) (US-017 / FR-017) stayed open after #421/#427 shipped occasion-cohort counts and export. Managers still had no spend-band dashboard. Full FR-017 is customer engagement analytics. CF-051: this is not staff live chat.

This session ships child [#430](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/430): coarse lifetime spend-band counts on `/florist`. It does **not** close #36. Do not start leftover ML, per-customer browse, leftover #35 outbound AI reminders, or leftover #27 purchase-history CRM.

## 2. Slice that shipped

- `count_spend_bands()` / `normalize_spend_band_cohorts()` — four ADR-020 bands, zeros included, no subject refs.
- Operator engagement JSON + CSV/JSON export allowlist extended with bands + counts.
- `/florist` `#engagement` spend-band table. Sample data only when operator APIs are fail-closed.

## 3. Honest leftover on #36

| Still open | Why |
|---|---|
| ML models | No model, no scoring |
| Per-customer browse | Aggregates, not a list |
| Workbook FR-017 Future | Do not promote IDs from this MR |

## 4. Wikilinks

[[fr-017-florist-spend-band-aggregates]] · [[fr-017-florist-engagement-analytics]] · [[fr-017-florist-engagement-cohort-export]] · [[ADR-020]] · [[FR-017]] · [[2026-09-11-session-memory-log-fr-017-florist-engagement-421]]
