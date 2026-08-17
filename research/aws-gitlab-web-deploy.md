# AWS web deploy from GitLab — plan & checklist

tags: #aea #deployment #aws #gitlab
status: ci-jobs-awaiting-merge
target: public web MVP (no native apps yet)
domain: aea.artof.link
canonical_origin: https://aea.artof.link
region: us-east-1
assessed_ref: origin/main
branch: ci/build-ecr-deploy-ecs
issue: "#199"
plan: GitLab CI build-ecr + deploy-ecs on main (OIDC) plus gateway ALB-mode image so ALB /healthz can pass; no terraform apply

## Goal

Deploy the existing containers from GitLab CI to AWS so the public reaches only
the TLS gateway (`https://aea.artof.link`), with BFF and Orchestration private,
backed by RDS Postgres and MSK Kafka (TLS + SASL, **2 brokers / RF=2**).

Canonical origin is `https://aea.artof.link` (no `www`, no `:443`, no trailing
slash). Terraform stack name may stay `pilot`. App task defs set
`AEA_ENVIRONMENT=production` (seeder off, florist operator off).

## Target topology

```text
Internet → ALB :443 → Gateway (nginx+UI)
                         ↓ private
                       BFF :8080
                         ↓ private
                   Orchestration :8081
                         ↓
              RDS Postgres  |  MSK (TLS/SASL, 2 brokers / RF=2)
                         ↑
              Relay + consumers (ECS tasks)
```

Images:

| Image | Dockerfile |
|-------|------------|
| orchestration | `platform/Dockerfile.orchestration` |
| bff | `edge/bff/Dockerfile` |
| gateway | `edge/gateway/Dockerfile` (`AEA_GATEWAY_MODE=alb` → `nginx-alb.conf` HTTP :8080) |

IaC: `infra/aws/` · Bootstrap: `infra/aws/BOOTSTRAP.md` · CI `build-ecr` /
`deploy-ecs`: this MR (#199). Gateway ALB mode is in the same image (required
for a healthy ALB target).

**Image policy (locked):** cloud-only. Laptop builds stay on compose/dev; they
are not the promotion path into ECS.

**Dual-path:** keep local Docker integration runners. Path B is this AWS stack
(encryption + TLS) after a future apply. Do not cite Compose as NFR-007/012 or
ADR-012 production proof.

## Phased plan

### Phase 0 — Prerequisites (human + accounts)

- [ ] AWS account access (+ IAM admin or least-privilege deploy role for apply)
- [ ] Region `us-east-1` (Terraform default)
- [ ] Domain `aea.artof.link` + ACM cert in `us-east-1` (ARN in local gitignored `terraform.tfvars` only) + DNS to ALB after apply
- [ ] GitLab runners with Docker-in-Docker (needed when CI jobs land)
- [x] Pilot access: open to everyone (`pilot_ingress_cidrs = ["0.0.0.0/0"]`)
- [x] Secrets strategy: AWS Secrets Manager (Terraform `app` secret)
- [x] Operator: `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, `AEA_AI_MODEL` in Secrets Manager (LiteLLM OpenAI-compatible URL + proxy bearer). Not in git. Injected into orchestration together (#208).

### Phase 1 — GitLab builds images → ECR (cloud-only)

- [ ] CI `build-ecr` on `main` — this MR (#199)
- [ ] Push to **ECR** via GitLab OIDC
- [ ] Tag `$CI_COMMIT_SHA` (+ `latest` on main)

### Phase 2 — AWS landing zone

- [x] Terraform VPC / NAT / SGs / ALB / ACM hook / ECR / ECS / Secrets / OIDC (in repo; not applied)
- [x] RDS PostgreSQL 16 (private, storage encrypted)
- [x] MSK Kafka TLS + SASL/SCRAM, 2 brokers / RF=2
- [ ] Operator: `terraform apply` + DNS + set GitLab CI variables from outputs
- [ ] CloudWatch alarms (5xx, unhealthy hosts) — post-pilot

### Phase 3 — Bootstrap data plane

- [x] Documented in `infra/aws/BOOTSTRAP.md`
- [ ] Operator: migrations + `provision_kafka.py` + ACL apply
- [ ] Confirm relay/consumers drain outbox
- [x] Live-test inventory feed (not `AEA_SEED_INVENTORY`): named
      `lily-reference-live-test` heartbeat (#210). Merge then apply the ECS
      service. In-VPC RunTask of the same writer is allowed after the MR exists.

### Phase 4 — GitLab deploy

- [ ] Manual `deploy-ecs` on `main` — auto after `build-ecr` in this MR (#199)
- [x] OIDC IAM role in Terraform (no long-lived keys in git)
- [ ] Rolling ECS update + `GET $AEA_PUBLIC_URL/healthz` smoke

### Phase 5 — Soft launch then harden

See **Soft launch checklist** below. IaC recovered onto main-based branch;
operator apply pending a later explicit ask.

### Deferred

- Native apps / Cognito full customer IdP
- Gateway ALB-mode image + Kafka SASL app adapters (ALB mode is in #199; Kafka SASL clients remain later)
- SSE durable recall (#193) and NFR-008 (#196)
- Multi-AZ / large load test
- Florist SoT replacements for reference authorities
- Local → ECR promotion for pilot (disallowed)
- Production inventory warehouse (do not invent one)

## GitLab CI variables (from Terraform outputs)

Needed when CI deploy jobs exist; not required to merge this IaC.

| Variable | Output / value |
|----------|----------------|
| `AWS_ROLE_ARN` | `gitlab_ci_role_arn` |
| `AWS_DEFAULT_REGION` | `aws_region` (e.g. `us-east-1`) |
| `AEA_ECR_ORCHESTRATION` | `ecr_orchestration_url` |
| `AEA_ECR_BFF` | `ecr_bff_url` |
| `AEA_ECR_GATEWAY` | `ecr_gateway_url` |
| `AEA_ECS_CLUSTER` | `ecs_cluster_name` |
| `AEA_PUBLIC_URL` | `public_url` |
| `AEA_OIDC_AUD` | optional; default `https://gitlab.com` |

OIDC is restricted to `project_path:<gitlab_project_path>:ref_type:branch:ref:main`.

## Soft launch checklist

1. ALB ingress is open (`0.0.0.0/0`); tighten later only if needed.
2. Point DNS at ALB; confirm ACM on listener for `aea.artof.link`.
3. Bootstrap migrations + Kafka topics + ACLs (`infra/aws/BOOTSTRAP.md`).
4. Cloud `build-ecr` then `deploy-ecs` on `main`; confirm `/healthz`.
5. Browser journey: session → recommendations → selection → checkout (pilot bearer).
6. Confirm `AEA_ALLOWED_ORIGIN` = `https://aea.artof.link`; no Compose fixture secrets.
7. Watch CloudWatch `/aea/<prefix>/*` for 15–30 minutes; check outbox via `diagnose.py`.
8. Keep RDS backups; add WAF/CIDR restriction later only if intentional.

## Operator sequence

1. Merge this CI/ALB-mode MR (#199). Terraform is already applied; GitLab OIDC vars are already set.
2. Pipeline on `main` → **cloud** `build-ecr` (not a local docker push) then `deploy-ecs`.
3. Bootstrap once; thereafter migrations only when schema changes.
4. Confirm `/healthz` (deploy job smokes this).
5. Soft-launch → public is already open (`0.0.0.0/0`); harden with WAF/CIDR later if needed.

## Local vs cloud builds

| | Local (compose/dev) | Cloud (GitLab → ECR) |
|--|---------------------|----------------------|
| Purpose | Iterate Dockerfiles, run edge stack | Images ECS actually runs |
| Push to pilot ECR | No (blocked by default) | Yes (`build-ecr`, #199) |
| Tag | ad hoc | `$CI_COMMIT_SHA` (+ `latest` on main) |

## Checklist — “ready for public web”

- [ ] Only ALB:443 is public
- [ ] BFF/Orchestration/RDS/MSK private
- [ ] Kafka TLS+SASL + ACLs applied
- [ ] Secrets from Secrets Manager, not Compose fixtures
- [ ] `AEA_ALLOWED_ORIGIN` matches public HTTPS origin
- [ ] ACM cert valid
- [ ] Migrations at latest; topics provisioned
- [ ] Relay/consumers healthy; outbox not backing up
- [ ] `/healthz` and full journey succeed
- [ ] Backups + alerts configured
- [ ] Pilot CIDR removed only when intentional (N/A — already `0.0.0.0/0`)
