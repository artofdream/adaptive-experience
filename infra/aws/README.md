# AWS web MVP stack (ECS Fargate + RDS + MSK + ALB)

Terraform for the public-web **pilot** stack in `us-east-1` (override via
`aws_region`). Terraform `environment` may stay `pilot` for names and tags.
App task definitions hardcode `AEA_ENVIRONMENT=production` so the local
inventory seeder and florist operator stay fail-closed.

**This directory is IaC + operator docs.** `@aea-devsecops-platform` operates
`plan`/`apply`/bootstrap. The scrum master does not run terraform.
GitLab CI `build-ecr` (OIDC, `main` only) pushes images to ECR.
`deploy-ecs` force-deploys ECS after a successful image build and smokes
`GET $AEA_PUBLIC_URL/healthz`.

Canonical public origin: `https://aea.artof.link` (no `www`, no `:443`, no
trailing slash). `AEA_ALLOWED_ORIGIN` must be that exact value.

Path B BFF `AEA_LOCAL_BEARER_TOKEN` must match the shipped UI fixture
`local-browser-token` in `edge/gateway/ui/assets/app.js` (same value as local
Compose). Terraform no longer generates a random browser token. Align a live
secret by merging that one JSON key (do not replace the whole secret blob —
operator `ANTHROPIC_API_KEY` / later `AEA_AI_*` keys would be dropped), then
`aws ecs update-service --cluster aea-pilot --service bff --force-new-deployment`
so Fargate re-injects the secret. Do not weaken CSRF, origin checks, or
fail-closed auth.

## What it creates

- VPC with public/private subnets and NAT (two AZs — required for 2 MSK brokers)
- ALB HTTPS → gateway (ECS) → BFF → orchestration (Cloud Map DNS)
- ECR repos for `orchestration`, `bff`, `gateway`
- RDS PostgreSQL 16 (private, `storage_encrypted`)
- MSK Kafka **3.9.x** with TLS + SASL/SCRAM, **2 brokers / RF=2 / MinISR=1** (pilot; AWS Health 3.6.0 EOL — upgrade before 8 Sep 2026; MinISR = RF-1)
- Secrets Manager app secret (`AEA_*` including Kafka SASL)
- GitLab OIDC IAM role for CI push/deploy (main branch only)
- ECS services: gateway, bff, orchestration, relay, consumer-workspace, litellm (private; no ALB)

Do not commit `terraform.tfvars`, `.env`, vault credentials, or `AEA_AI_API_KEY`.
`.gitignore` already excludes `*.tfvars` (exception: `*.tfvars.example`).

## Dual-path integration

- **Path A (local):** keep `python platform/scripts/run_integration_tests.py`
  and `python edge/scripts/run_integration_tests.py`. Compose is not
  NFR-007 / NFR-012 or ADR-012 production proof.
- **Path B (this stack):** RDS encryption at rest, ALB TLS via ACM, MSK TLS
  + SASL. Evidence is the applied cloud stack, not Compose. DevSecOps applies;
  SM does not.

## Prerequisites (needed for apply; ACM ARN stays in local tfvars)

1. AWS account access with rights to create the stack (account id stays out of git)
2. ACM certificate in **us-east-1** for `aea.artof.link` — put the ARN only in
   local `terraform.tfvars` (gitignored)
3. DNS CNAME/ALIAS from `aea.artof.link` to the ALB (after apply)
4. GitLab project path matching `gitlab_project_path`, plus OIDC CI variables
   after apply (`AWS_ROLE_ARN`, ECR URLs, cluster name)
5. Live Anthropic (two slices). **Today:** merge JSON key `ANTHROPIC_API_KEY`
   into Secrets Manager `aea-pilot/app` (do not replace the blob; keep
   postgres/kafka/bearer/origin). Do **not** add `AEA_AI_*` yet. Terraform
   injects that key into the LiteLLM task only. **Follow-up:** after the proxy
   is up and a `LITELLM_MASTER_KEY` is in the same secret, merge all three
   `AEA_AI_*` (`http://litellm.aea-pilot.internal:4000/v1/chat/completions`,
   the proxy bearer, `claude-sonnet-5`) and inject them into orchestration
   together. Never a raw Anthropic Messages URL. Not in git. Not in
   `terraform.tfvars`.
6. Confirm `pilot_ingress_cidrs` (default public `0.0.0.0/0`)

## Apply (DevSecOps skill; not the scrum master)

Laptop on this ARM64 Windows machine: use amd64 Terraform at
`C:\apps\terraform-amd64\terraform.exe` (ARM64 `C:\apps\terraform\terraform.exe`
cannot fetch AWS provider 5.x).

```bash
cd infra/aws
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars — ACM ARN, never commit that file
terraform init
terraform plan
terraform apply
```

Do **not** apply the LiteLLM service until the scrum master confirms
`ANTHROPIC_API_KEY` is in `aea-pilot/app` (no value in chat). Missing JSON
key → LiteLLM `ResourceInitializationError`.

Copy outputs into GitLab CI/CD variables (masked where needed) when the CI
deploy jobs exist:

| Variable | Source |
|----------|--------|
| `AWS_ROLE_ARN` | `gitlab_ci_role_arn` |
| `AWS_DEFAULT_REGION` | `aws_region` |
| `AEA_ECR_ORCHESTRATION` | `ecr_orchestration_url` |
| `AEA_ECR_BFF` | `ecr_bff_url` |
| `AEA_ECR_GATEWAY` | `ecr_gateway_url` |
| `AEA_ECS_CLUSTER` | `ecs_cluster_name` |
| `AEA_PUBLIC_URL` | `public_url` |

Optional: set `AEA_OIDC_AUD` if the OIDC audience is not `https://gitlab.com`.

## Image builds (cloud only)

ECS images must be built in GitLab CI and pushed to ECR via OIDC. Local
`docker build` is for compose/dev; do **not** push those images to the pilot
ECR unless break-glass is documented.

Gateway task defs set `AEA_GATEWAY_MODE=alb`. The gateway image uses
`nginx-alb.conf` (HTTP :8080 behind the ALB). Compose keeps ephemeral TLS on
`:8443` when that variable is unset.

## Fail-closed flags

- `AEA_ENVIRONMENT=production` on orchestration, BFF, relay, and consumer
- Do **not** set `AEA_SEED_INVENTORY` (production seeder raises)
- Do **not** set `AEA_FLORIST_OPERATOR` (BFF 404s florist in production)
- Prefer a live-test inventory feed into `inventory.product_availability`;
  do not invent a warehouse in this stack

## Soft launch

Keep `pilot_ingress_cidrs` as `["0.0.0.0/0"]` for open public access (current
decision). To restrict later, set office/VPN CIDRs and re-apply.

## Path B LiteLLM

Private Fargate service `litellm` (Cloud Map `litellm.aea-pilot.internal:4000`).
Same image/tag and `edge/litellm.yaml` aliases as Path A. No public listener.
Orchestration security group is the only ingress on :4000.

This slice injects `ANTHROPIC_API_KEY` from `aea-pilot/app` into **LiteLLM
only**. Orchestration does **not** get `AEA_AI_ENDPOINT` / `AEA_AI_API_KEY` /
`AEA_AI_MODEL` (partial env crashes the process). Regex intent stays in
production until a follow-up wires all three after:

1. Scrum master confirms `ANTHROPIC_API_KEY` is in `aea-pilot/app` (no value
   in chat/git).
2. A proxy master key `LITELLM_MASTER_KEY` is in the same secret (operator
   generated; not the Anthropic console key; never a committed placeholder).
3. Those three `AEA_AI_*` keys are merged (not replaced) and injected
   together, plus `LITELLM_MASTER_KEY` on LiteLLM. Then force-new-deploy
   `litellm` and `orchestration`.

**Do not apply this LiteLLM service until step 1 is confirmed.** A missing
`ANTHROPIC_API_KEY` JSON key makes the LiteLLM task fail
`ResourceInitializationError`; other services stay up. Keep 2-broker Kafka.
No seeder. No florist operator.

## Bootstrap (after first images are in ECR)

See [BOOTSTRAP.md](BOOTSTRAP.md). Services start empty until migrations and
Kafka topics exist; run bootstrap before relying on relay/consumers.
