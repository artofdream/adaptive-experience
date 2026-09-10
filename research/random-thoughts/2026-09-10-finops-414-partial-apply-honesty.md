# FinOps #414 partial apply honesty (RDS small + CW; ARM blocked)

> **Tags**: #aea #second-brain #finops #honesty #rds #fargate #arm64 #cloudwatch #knowledge-first
> **Captured**: 2026-09-10
> **GitLab**: #414 (scope split; leave open) · leftover ARM #416 · !492 merged `ae9ecf0`
> **Owners to inherit**: @aea-knowledge-guardian, @aea-cost-guardian, @aea-devsecops-platform, @aea-mr-coordinator
> **This node is knowledge, not an apply ticket.** Do not `terraform apply` from this note.

Later agents: do not treat !492 merge or a closed #414 as “ARM64 Fargate is live.” Probe ECR arch or write Unknown.

Inherits [[2026-09-10-finops-414-rds-arm64-apply-continuity]], [[2026-09-10-finops-cw-metric-prune-grafana]], [[2026-09-10-session-memory-log-finops-414-arm64-rds-cw]], [[2026-08-29-finops-arm64-and-rds-sizing]].

---

## What landed in git (not the same as live apply)

Issue #414 / MR !492 merged (commit `ae9ecf0`): Terraform ARM64 `litellm`/`grafana` + RDS `db.t4g.small` apply path + CW notes.

That MR did **not** run `terraform apply`. Code/docs path only.

## Sponsor (2026-09-10)

- Stay **us-east-1**.
- No Savings Plan this week.
- Re-eval **17 Sep**.

## Pre-modify snapshot

- Snapshot id: `aea-pilot-postgres-pre-t4g-small-20260910-2151`
- Status: **available**

## Applied on cts-ai via AWS CLI

**Not** a full `terraform apply` of ECS task defs.

1. RDS `aea-pilot-postgres` modify to `db.t4g.small` apply-immediately (was `db.t4g.medium` Single-AZ).
2. CW log retention 30→14 on `/aea/aea-pilot/{agent-runner,bff,consumer,gateway,grafana,lily-reference-live-test,litellm,orchestration,relay}`.
3. Local `terraform.tfvars` `db_instance_class` synced to `db.t4g.small` (gitignored).

## Not applied — ARM blocker

Fargate ARM64 task-def replacements were **not** applied.

Reason: live ECR images are **linux/amd64 only** (`bff`/`gateway`/`orchestration` config arch=`amd64`; grafana index amd64-only). Full ARM apply would brick Path B.

Follow-up issue **#416**: multi-arch (ARM64) ECR builds before Fargate ARM cutover.
Build-track SOP: [[2026-09-10-path-b-multiarch-ecr-416]]. Live ARM prove +
task-def apply remain on #414.

## Full terraform plan (intentionally not applied)

Full `terraform plan` showed **13 add / 20 change / 9 destroy**, mostly task-def replaces + incidental drift (ALB http listener, grafana ECR). Avoided intentional full apply.

## Tracker honesty

- !492 used `Closes #414`. GitLab closed #414 on merge. That close is **code-path done**, not live ARM done.
- #414 description still includes ARM apply. Safer: leave #414 **open** and point at #416. Do not close #414 from a vault MR.
- This honesty MR **closes nothing**.

Do **not** `terraform apply`. Do **not** purchase a Savings Plan. Do **not** move region. Keep MSK. Do not touch secrets.
