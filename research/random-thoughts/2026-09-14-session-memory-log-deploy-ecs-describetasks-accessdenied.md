# deploy-ecs migrate waiter AccessDenied on DescribeTasks (#438)

> **Tags**: #aea #iam #deploy #migrations #aws
> **Captured**: 2026-09-14
> **GitLab**: #438
> **Probe**: RunTask succeeded; `aws ecs wait tasks-stopped` failed — `ecs:DescribeTasks` AccessDenied on task ARN (jobs 16469100710, 16475835256).

## Fix
Add `ecs:DescribeTasks` + `ecs:ListTasks` to `EcsDeployUntaggedRegister` (same untagged pattern as RunTask #437). Terraform apply required.

## Live prove (same day)
!517 merged. `(aws) deploy-ecs` [job 16488714090](https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16488714090) **SUCCESS** `2026-09-14T14:36:48Z` — `ecs_apply_migrations: OK` (task `0a419082d9924c73ad35e1c0bd439df0` exitCode=0) then healthz `{"status":"ok"}`. Full vault node: [[2026-09-14-session-memory-log-migrate-on-deploy-438-prove]].
