# GitLab CI ecs:RunTask AccessDenied after #436 (#437)

> **Tags**: #aea #iam #deploy #migrations #aws
> **Captured**: 2026-09-13
> **GitLab**: #437 (follow-up of #436 / !515)
> **Probe**: pipeline 2843744259 job 16466124650 — `deploy-ecs` **failed** on `ecs:RunTask` AccessDenied for `aea-pilot-orchestration:3`.

## Why
`ecs:RunTask` was only on tagged `EcsDeploy` statement (`aws:ResourceTag/Project=adaptive-experience`). Task definitions are not tagged that way; `UpdateService` already uses `EcsDeployUntaggedRegister`.

## What
Add `ecs:RunTask` to `EcsDeployUntaggedRegister`. Terraform apply required for live CI.

## Honesty
Migrate-on-deploy remains **Unknown/failed** until IAM apply + green `deploy-ecs`.
