# Recommendation: CF-050 — Migration runner includes 019–022

> **Finding:** CF-050 (High)  
> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Suggested owner:** `@aea-senior-software-engineer` / `@aea-devsecops-platform`  
> **Suggested branch:** `fix/cf-050-migration-runner-root`  
> **Do not merge from this sandbox.**

## Problem

- `platform/scripts/apply_migrations.py` only applies  
  `sorted((ROOT / "migrations").glob("[0-9][0-9][0-9]_*.sql"))`  
  → `platform/migrations/` (001–018).
- Reference-extension SQL **019–022** live under  
  `platform/aea_platform/migrations/` and are **not** applied by the documented path.
- Roadmap still cites those schemas as delivered reference-extension artifacts.

## Desired outcome

One governed apply path that either:

- **Option A (preferred):** Discovers and orders **both** trees (or moves 019–022 into `platform/migrations/`), with a test that versions 019–022 are visible to the runner; or  
- **Option B:** Keeps files where they are but documents explicitly that they are **not** auto-applied, and roadmap stops calling them “delivered” apply-path artifacts.

Prefer **Option A** so local Compose and docs match.

## Proposed change (focused)

### Option A

1. Move `019_*.sql` … `022_*.sql` into `platform/migrations/` **or** extend `apply_migrations.py` to merge both directories, sort by version, reject duplicate version numbers.
2. Add a unit/smoke test: expected version set includes 019–022 when files exist.
3. Update `platform/README.md` apply instructions if paths change.
4. Do **not** implement WebSocket chat, stem pricing product logic, or multi-tenant product behavior in this MR—schema discoverability only.

### Option B (doc-only, weaker)

1. Roadmap/README: “019–022 are reference SQL checked in under `aea_platform/migrations/`; not applied by `apply_migrations.py` until promoted.”
2. Still leaves runtime drift; use only if move is blocked.

## Out of scope

- Shipping staff live chat, stem composition UI, or production multi-tenant isolation.
- Archive/workbook requirement changes.

## Acceptance checks

- [ ] Documented apply path can list/apply 019–022 (Option A) **or** docs/roadmap no longer claim them as applied (Option B)
- [ ] No duplicate version numbers
- [ ] Guards/tests updated for the chosen option
- [ ] One finding only

## Manual GitLab steps

1. Issue CF-050 → `fix/cf-050-migration-runner-root`
2. Implement Option A (or B with sponsor agreement)
3. MR → Docker/integration if runner behavior changes (SOP)

## Evidence paths

- `platform/scripts/apply_migrations.py`
- `platform/migrations/`
- `platform/aea_platform/migrations/019_*.sql` … `022_*.sql`
- `docs/07-roadmap/roadmap.md` (M16–M18)
