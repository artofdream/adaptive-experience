# FinOps: ARM64 Graviton Fargate migration and RDS PostgreSQL right-sizing

> **Tags**: #aea #second-brain #finops #aws #fargate #rds #devsecops #knowledge-first
> **Captured**: 2026-08-29
> **GitLab**: Closes #282 (MRC merges; do not self-merge)
> **Owners to inherit**: @aea-devsecops-platform, @aea-cost-guardian, @aea-mr-coordinator

## Background & Decision

In accordance with approved August FinOps right-sizing recommendations:
1. **ECS Fargate ARM64 Migration**: Configured `runtime_platform { operating_system_family = "LINUX", cpu_architecture = "ARM64" }` across all custom python microservice task definitions (`orchestration`, `bff`, `gateway`, `relay`, `consumer_workspace`, `lily_reference_live_test`, `agent_runner`). This yields an immediate 20% compute savings on AWS Fargate.
2. **RDS PostgreSQL Right-Sizing**: Updated default `db_instance_class` in `infra/aws/variables.tf` from `db.t4g.medium` to `db.t4g.small`, saving 50% on database compute during pilot load while maintaining ample headroom (2 vCPU, 2 GB RAM).

Existing IDs: [[2026-08-29-sprint-coordination-finops-and-ux]], [[2026-08-29-public-voice-pass]], [[2026-08-28-public-schema-page]].
