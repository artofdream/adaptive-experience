# deploy-ecs must apply migrations (#436)

> **Tags**: #aea #path-b #deploy #migrations #honesty #keep-learning-and-apply
> **Captured**: 2026-09-12
> **GitLab**: #436
> **Status**: Documented in MR (CI wiring). Live migrate-on-deploy prove = Unknown until next main `deploy-ecs` run.

## Why
Live prove of !506 / #427 hit engagement/export **500** (`UndefinedTable`) because `deploy-ecs` only force-redeployed services and curled `/healthz` — it never ran `platform/scripts/apply_migrations.py`. Manual ECS RunTask recovered (024–028).

Applies Keep Learning and Apply (#434) and deploy-schema-honesty.

## What
- `scripts/ecs_apply_migrations.sh` — discover orchestration awsvpc net config, `ecs run-task` with apply_migrations override, wait, fail-closed on non-zero exit.
- `deploy-ecs` invokes the helper after `update-service` and before `/healthz`.
- Guard: `scripts/test_ecs_apply_migrations_deploy.py`.

## Out
No terraform apply, no secrets in notes, no #27/#35/#36 product scope.
