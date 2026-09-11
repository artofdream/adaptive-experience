# Session Memory Log: FinOps #414 ARM64 + RDS small + CW prune

> **Tags**: #aea #session-memory #second-brain #finops #414
> **Captured**: 2026-09-10
> **Author**: `@aea-devsecops-platform` with `@aea-knowledge-guardian`
> **Related**: [[2026-09-10-finops-414-rds-arm64-apply-continuity]] · [[2026-09-10-finops-cw-metric-prune-grafana]] · [[2026-09-11-finops-414-arm-cutover-honesty]] · #414 · #415

**2026-09-11:** live ARM leftover landed — see
[[2026-09-11-finops-414-arm-cutover-honesty]]. This 2026-09-10 log is
the RDS/CW + code/docs MR memory only.

## Why

Sponsor probed live Path B: RDS still `db.t4g.medium` despite the
`db.t4g.small` Terraform default; LiteLLM and Grafana task defs still
defaulted to x86 Fargate; CloudWatch cost was `MetricMonitorUsage`, not
log retention. Snapshot
`aea-pilot-postgres-pre-t4g-small-20260910-2151` started before apply.

## Decisions

- Code/docs MR only. No Cloud Agent `terraform apply`. No RDS destroy.
  Keep MSK. No Lightsail.
- Same `db_instance_class` variable; align example + apply checklist.
- ARM64 `runtime_platform` on `litellm` + `grafana` to match siblings.
- ECS log retention 14 days (secondary). Metric prune is a vault note
  so Grafana `AWS/ECS` + Logs Insights panels stay intact.
- Sponsor 2026-09-10: stay **us-east-1** (Stockholm Fargate ~+10%,
  RDS small ~+3%, NAT ~+2% — not cheaper). Prior `$0.04/hr` Compute
  SPs **retired**; re-evaluate a plan only after apply + 1-week cost
  check (coordinator schedules the re-eval; do not buy in this MR).
  Snapshot `aea-pilot-postgres-pre-t4g-small-20260910-2151` is
  **available**. Keep MSK. No Cloud Agent apply.

## Artifacts

- `infra/aws/ecs.tf`, `variables.tf`, `rds.tf`, `terraform.tfvars.example`
- `infra/aws/README.md`, `infra/aws/BOOTSTRAP.md`
- Vault notes linked above
