# deploy-ecs migrate waiter AccessDenied on DescribeTasks (#438)

> **Tags**: #aea #iam #deploy #migrations #aws
> **Captured**: 2026-09-14
> **GitLab**: #438
> **Probe**: RunTask succeeded; `aws ecs wait tasks-stopped` failed — `ecs:DescribeTasks` AccessDenied on task ARN (jobs 16469100710, 16475835256).

## Fix
Add `ecs:DescribeTasks` + `ecs:ListTasks` to `EcsDeployUntaggedRegister` (same untagged pattern as RunTask #437). Terraform apply required.
