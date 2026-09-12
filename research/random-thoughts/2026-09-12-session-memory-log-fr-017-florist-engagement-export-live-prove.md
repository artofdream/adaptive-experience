# Session Memory Log: FR-017 florist engagement export Path B live prove (!506 / #427)

> **Tags**: #aea #session-memory #fr-017 #florist #crm #adr-020 #nfr-017 #path-b #honesty #second-brain #knowledge-first
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-devsecops-platform`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **GitLab**: [#431](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/431) (this vault MR) · related merged [!506](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/506) / [#427](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/427) · do **not** close [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36) or #427
> **Related**: [[2026-09-12-session-memory-log-fr-017-florist-engagement-export-427]] · [[2026-09-12-fr-017-florist-engagement-cohort-export]] · [[fr-017-florist-engagement-cohort-export]] · [[ADR-020]] · [[FR-017]] · #36 · #427 · !506

---

## 1. Why this note exists

[!506](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/506) shipped operator-gated CSV/JSON engagement export (child [#427](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/427)). Code on Path B `aea-pilot` was ahead of RDS schema. This node records the **2026-09-12 cts-ai live prove** against `https://aea.artof.link` and the migration unblock. It does **not** close #36 or #427. Do not invent extra live facts from this note.

## 2. First prove (before migrate)

cts-ai used a shop session plus Bearer `local-browser-token` plus Origin against `https://aea.artof.link`.

| Check | Result |
|---|---|
| `GET /api/v1/operator/engagement` | **500** |
| `GET /api/v1/operator/engagement/export?format=csv` | **500** |
| `GET /api/v1/operator/engagement/export?format=json` | **500** |
| Operator orders | **200** |
| Operator escalations | **200** |
| Bad format `xlsx` (once auth worked) | **422** (correct) |
| `/florist` HTML Download CSV / Download JSON markers | Already present before migrate |

Orchestration logs: `UndefinedTable` for `orchestration.subject_profile` and `crm.reminder_outbox`.

## 3. Unblock (ECS RunTask, not deploy-ecs)

Pending migrations applied via ECS RunTask on `aea-pilot-orchestration:3` (private subnets, SG `aea-pilot-orchestration`, `assignPublicIp` DISABLED). Command: `python platform/scripts/apply_migrations.py`. Exit 0. Applied **024, 025, 026, 027, 028**. Idempotent pattern per `infra/aws/BOOTSTRAP.md`. No DSN recorded here.

Root cause honesty: `deploy-ecs` does **not** auto-run `apply_migrations`. Code shipped ahead of RDS schema. Same class as the #384 / migration-023 Path B miss ([[2026-09-03-path-b-florist-384-redeploy-prove]]).

## 4. After migrate (live prove)

| Check | Result |
|---|---|
| `GET /api/v1/operator/engagement` | **200** |
| CSV attachment `florist-engagement-cohorts.csv` | **200** |
| JSON attachment | **200** |
| reminder-outbox | **200** |
| `xlsx` | **422** |

Live counts included `memory_count=22`, occasion / relation / month cohorts, and spend_band rows present (zeros). Forbidden tokens absent in bodies: `browser_hash`, `subject_reference`, `email`, `phone`.

## 5. Tracker honesty

- !506 already merged and closed #427. This vault MR closes **#431 only**.
- Parent **#36 stays open**. Do not `Closes #36` or `Closes #427`.
- This node is knowledge, not a product or apply ticket. Do not `terraform apply` from this note.

## 6. Wikilinks

[[2026-09-12-session-memory-log-fr-017-florist-engagement-export-427]] · [[2026-09-12-fr-017-florist-engagement-cohort-export]] · [[fr-017-florist-engagement-cohort-export]] · [[2026-09-03-path-b-florist-384-redeploy-prove]] · [[ADR-020]] · [[FR-017]] · [[NFR-017]] · [[CF-051-fr016-017-narrative]]
