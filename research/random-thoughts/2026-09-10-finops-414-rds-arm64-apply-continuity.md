# FinOps #414: data-safe RDS t4g.small + ARM64 ECS apply

> **Tags**: #aea #second-brain #finops #rds #fargate #arm64 #devsecops
> **Captured**: 2026-09-10
> **GitLab**: #414 / !492 merged (code/docs). Vault addendum Closes #415.
> **Owners to inherit**: @aea-devsecops-platform, @aea-cost-guardian, @aea-mr-coordinator

## What is already true in git

- `infra/aws/variables.tf` already defaults `db_instance_class = db.t4g.small`.
  Live `aea-pilot` RDS is still `db.t4g.medium` — **apply drift**, not a
  missing second variable. Do not invent another sizing input.
- Most ECS task defs already set `runtime_platform { LINUX, ARM64 }`.
  #414 adds the same block to `litellm` and `grafana`.
- MSK stays. RDS is not destroyed. No Lightsail migration.

## Data continuity

Same-instance `aws_db_instance.main` class change keeps the identifier,
storage, and data. Durability is unchanged (same encrypted volume).
`multi_az = false`, so expect a **brief Single-AZ outage** while RDS
modifies. Performance risk on `db.t4g.small` is **memory headroom**
(2 GB vs 4 GB), not data loss — after cutover watch `FreeableMemory`
and session/inventory working set. This is not a restore and not a
rebuild.

Sponsor required a manual snapshot **before** apply:

- Snapshot id: `aea-pilot-postgres-pre-t4g-small-20260910-2151`
- Status (sponsor, 2026-09-10): **available**. Apply may proceed on
  the DSO laptop. Still no Cloud Agent apply.

## Sponsor 2026-09-10 — region, Savings Plan, re-eval

Stay on the current FinOps path (ARM64 Fargate + RDS `db.t4g.small` +
CW metric prune). Keep MSK. Do not migrate region. Do not buy a plan
in the #414 / #415 MRs.

1. **eu-north-1 vs us-east-1.** Stockholm list is not cheaper: Fargate
   ~+10%, RDS small ~+3%, NAT ~+2%. **Stay `us-east-1` for now.** Do
   not move the pilot stack to `eu-north-1`.
2. **Compute Savings Plan.** Prior tiny `$0.04/hr` Compute SPs are
   **retired**. Re-evaluate buying a plan **after** the FinOps apply
   and a **1-week cost re-check**. Do not purchase in this MR.
3. **1-week re-eval** is scheduled by the coordinator. This note does
   not create that routine.

## DSO apply (laptop amd64 Terraform only)

Never `terraform apply` from a Cursor Cloud VM.

1. Snapshot `aea-pilot-postgres-pre-t4g-small-20260910-2151` is
   **available** (sponsor 2026-09-10).
2. Local `terraform.tfvars` `db_instance_class = db.t4g.small` (or omit).
3. `terraform apply` in `infra/aws`.
4. Force-new-deploy ECS so ARM64 revisions roll (`litellm`, `grafana`,
   and siblings). Rebuild Grafana ECR as `linux/arm64` if `:latest` is
   still amd64-only.
5. Verify `https://aea.artof.link/healthz`,
   `https://aea.artof.link/florist`,
   `https://aea.artof.link/grafana/`.

Operator checklist: `infra/aws/README.md` § FinOps #414.

Existing IDs: [[2026-09-10-finops-cw-metric-prune-grafana]], [[2026-08-29-finops-arm64-and-rds-sizing]], [[2026-08-29-finops-cost-optimization-rationale-and-enforcement]], [[2026-08-22-cloud-grafana-cloudwatch-troubleshooting-sop]], [[2026-09-10-finops-414-partial-apply-honesty]].

## Apply honesty (2026-09-10 Berlin evening)

The “live RDS still `db.t4g.medium` / apply next” reading of this note is
**stale**. Partial apply landed on cts-ai via AWS CLI (RDS `db.t4g.small` +
CW 14d). Fargate ARM64 task-def replacements were **not** applied (amd64-only
ECR; full ARM apply would brick Path B). Canonical status:
[[2026-09-10-finops-414-partial-apply-honesty]]. Leftover ARM: #416. Do not
full-`terraform apply` the 13 add / 20 change / 9 destroy plan.
