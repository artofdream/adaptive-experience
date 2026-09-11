# AWS web MVP stack (ECS Fargate + RDS + MSK + ALB)

Terraform for the public-web **pilot** stack in `us-east-1` (override via
`aws_region`). Terraform `environment` may stay `pilot` for names and tags.
App task definitions hardcode `AEA_ENVIRONMENT=production` so the local
inventory seeder stays fail-closed. Florist operator APIs stay 404 in
**generic** production. `aea-pilot` is a **named exception** (#209): BFF sets
`AEA_FLORIST_OPERATOR=1` plus `AEA_FLORIST_OPERATOR_EXCEPTION=aea-pilot`.
That is read-only T-09 inbox; it does **not** write inventory or unblock
T-03 Select. Do not open `/florist` in the same browser as the shop (CSRF).

**This directory is IaC + operator docs.** `@aea-devsecops-platform` operates
`plan`/`apply`/bootstrap. The scrum master does not run terraform.
GitLab CI `build-ecr` (OIDC, `main` only) pushes **multi-arch** images
(`linux/amd64` + `linux/arm64` manifest lists) to ECR via
`scripts/ecr_multiarch_push.sh` (#416). `deploy-ecs` force-deploys ECS after
a successful image build and smokes `GET $AEA_PUBLIC_URL/healthz`.
Do **not** apply ARM64 task defs until the verify commands below show both
platforms on the live `:latest` tags.

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
- ECS services: gateway, bff, orchestration, relay, consumer-workspace, litellm, lily-reference-live-test (private; no ALB)

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
5. Live Anthropic via LiteLLM. Operator-merge into `aea-pilot/app` (do not
   replace the blob; keep postgres/kafka/bearer/origin/Anthropic):
   `LITELLM_MASTER_KEY` (proxy bearer, same value as `AEA_AI_API_KEY`),
   `AEA_AI_ENDPOINT` (`http://litellm.aea-pilot.internal:4000/v1/chat/completions`),
   `AEA_AI_API_KEY`, and `AEA_AI_MODEL` (`claude-sonnet-5`). Terraform injects
   `ANTHROPIC_API_KEY` + `LITELLM_MASTER_KEY` into LiteLLM, and all three
   `AEA_AI_*` into orchestration together. Never a raw Anthropic Messages
   URL. Not in git. Not in `terraform.tfvars`.
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

### FinOps #414 apply checklist (data-safe; DSO laptop, not Cloud Agent)

**Partial apply 2026-09-10 Berlin evening (cts-ai AWS CLI, not full
`terraform apply`):** RDS `aea-pilot-postgres` is `db.t4g.small`; CW
retention on the listed `/aea/aea-pilot/*` groups is 14d. Fargate ARM64
task-def replacements are **not** applied — live ECR was linux/amd64 only
when #414 was partially applied (`bff`/`gateway`/`orchestration` amd64;
grafana index amd64-only). Full ARM apply would brick Path B until #416
multi-arch images are on ECR **and** inspected. Vault:
`research/random-thoughts/2026-09-10-finops-414-partial-apply-honesty.md`
and `research/random-thoughts/2026-09-10-path-b-multiarch-ecr-416.md`.
Do **not** apply the 13 add / 20 change / 9 destroy plan.

`variables.tf` already defaults `db_instance_class = db.t4g.small`. Confirm
local `terraform.tfvars` uses `db.t4g.small` or omits the key so the
default wins. Do **not** add a second sizing variable. Do **not** destroy
RDS. Do **not** remove MSK. Do **not** apply from a Cursor Cloud VM.

1. **Wait for the pre-apply snapshot**
   `aea-pilot-postgres-pre-t4g-small-20260910-2151` to reach
   `available` (`aws rds describe-db-snapshots`). Do not apply while it
   is still `creating`.
2. **Plan then apply** from `infra/aws` (amd64 Terraform). Expect
   in-place RDS `instance_class` modify (same identifier, data stays),
   ECS task-def ARM64 for `litellm` + `grafana`, and ECS log-group
   retention 30 → 14. Single-AZ RDS has a brief outage during modify.
3. **Force new ECS deployments** so Fargate picks ARM64 revisions
   (task-def registration alone does not roll running tasks):
   ```bash
   for svc in gateway bff orchestration relay consumer-workspace \
     litellm lily-reference-live-test agent-runner grafana; do
     aws ecs update-service --cluster aea-pilot --service "$svc" \
       --force-new-deployment --query service.serviceName --output text
   done
   ```
   Rebuild/push Grafana via `build-ecr` (`scripts/ecr_multiarch_push.sh`)
   and inspect both platforms before rolling `grafana`. The #331 compose
   pin stays the amd64 digest; CI overrides `AEA_GRAFANA_BASE` to the
   official `grafana/grafana:10.4.0` tag (amd64+arm64). LiteLLM uses the
   public tag — inspect it before ARM cutover (see Image builds).
4. **Verify** after RDS is `available` and services are `STABLE`:
   `https://aea.artof.link/healthz`, `https://aea.artof.link/florist`,
   `https://aea.artof.link/grafana/`. Confirm Grafana `AWS/ECS` panels
   still have data (do not disable those metrics). Vault:
   `research/random-thoughts/2026-09-10-finops-414-rds-arm64-apply-continuity.md`.

Do **not** apply orchestration `AEA_AI_*` `valueFrom` until `aea-pilot/app`
has `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, `AEA_AI_MODEL`, and
`LITELLM_MASTER_KEY` (boolean `has(...)` only). Missing JSON key →
`ResourceInitializationError`.

Copy outputs into GitLab CI/CD variables (masked where needed) when the CI
deploy jobs exist:

| Variable | Source |
|----------|--------|
| `AWS_ROLE_ARN` | `gitlab_ci_role_arn` |
| `AWS_DEFAULT_REGION` | `aws_region` |
| `AEA_ECR_ORCHESTRATION` | `ecr_orchestration_url` |
| `AEA_ECR_BFF` | `ecr_bff_url` |
| `AEA_ECR_GATEWAY` | `ecr_gateway_url` |
| `AEA_ECR_AGENT_RUNNER` | `ecr_agent_runner_url` |
| `AEA_ECR_GRAFANA` | `ecr_grafana_url` (optional; `build-ecr` can derive from `AEA_ECR_GATEWAY`) |
| `AEA_ECS_CLUSTER` | `ecs_cluster_name` |
| `AEA_PUBLIC_URL` | `public_url` |

Optional: set `AEA_OIDC_AUD` if the OIDC audience is not `https://gitlab.com`.

## Image builds (cloud only)

ECS images must be built in GitLab CI and pushed to ECR via OIDC. Local
`docker build` is for compose/dev; do **not** push those images to the pilot
ECR unless break-glass is documented.

`build-ecr` / `build-ecr-agent-runner` run `scripts/ecr_multiarch_push.sh`
(`docker buildx`, platforms `linux/amd64,linux/arm64`, `--push` of `:latest`
and `$CI_COMMIT_SHA`). That is the #416 **build** track. It does **not**
flip live Fargate to ARM64 and does **not** `terraform apply`.

GitLab OIDC role `aea-pilot-gitlab-ci` inline policy `EcrPush` must list
every Path B ECR repo in `ecr.tf` (orchestration, bff, gateway,
agent-runner, **grafana**) and include `ecr:GetDownloadUrlForLayer`.
#418: live IAM omitted grafana; `build-ecr` on main then failed
`GetDownloadUrlForLayer` on `aea-pilot/grafana` (jobs 16438215440,
16435589756). **Merge this IAM first, then DSO `terraform apply` on
cts-ai** (Cloud Agents must not apply). Re-run `build-ecr` on main
only after that apply. Do **not** apply #414 ARM64 task defs until
imagetools inspect shows both platforms (see below).

### Verify arch before ARM cutover (#416)

Run from a host that can reach ECR (DSO laptop / GitLab job), not from a
Cloud Agent with Docker Hub/GHCR egress blocked:

```bash
# After main has built+pushed. Replace the registry prefix with terraform output.
for img in orchestration bff gateway agent-runner grafana; do
  docker buildx imagetools inspect \
    "${AEA_ECR_PREFIX}/aea-pilot/${img}:latest"
done

# Public LiteLLM used by the litellm task (not an ECR build).
docker buildx imagetools inspect ghcr.io/berriai/litellm:main-latest
```

Each inspect must list **linux/amd64** and **linux/arm64**. ECR
`batch-get-image` / `describe-images` showing a single-manifest amd64
config is the old blocker — do not apply ARM64 task defs yet.

LiteLLM: this Cloud Agent cannot reach `ghcr.io`. Official
`ghcr.io/berriai/litellm` tags are published multi-arch; **confirm with
the inspect above** before ARM apply. If `main-latest` lacks `linux/arm64`,
do **not** pin a guessed tag. Either pick a release tag whose inspect
shows both platforms, or add an `aea-pilot/litellm` ECR repo and build it
with the same `ecr_multiarch_push.sh` path. Missing arm64 on LiteLLM is a
cutover **blocker** (the proxy would fail to pull/start on ARM64 Fargate).

image-scan (#332) still builds native amd64 commit-SHA tags and does not
push. #331 digest pins stay on the GitLab-recorded amd64 evidence; CI may
fall back to the same tag when a pin is not an index.

Gateway task defs set `AEA_GATEWAY_MODE=alb`. The gateway image uses
`nginx-alb.conf` (HTTP :8080 behind the ALB). Compose keeps ephemeral TLS on
`:8443` when that variable is unset.

## Fail-closed flags

- `AEA_ENVIRONMENT=production` on orchestration, BFF, relay, consumer, and
  `lily-reference-live-test`
- Do **not** set `AEA_SEED_INVENTORY` (production seeder raises)
- Florist operator: generic production 404s even if `AEA_FLORIST_OPERATOR=1`.
  Named **aea-pilot** exception only: when Terraform `local.prefix` is
  `aea-pilot`, BFF also sets `AEA_FLORIST_OPERATOR=1` and
  `AEA_FLORIST_OPERATOR_EXCEPTION=aea-pilot`. Other prefixes must not copy
  those vars. Inbox is least-data reads; it does not seed inventory or
  enable T-03 Select. Do not open `/florist` beside the customer shop
  (CSRF class !165 / #171).
- Named live-test feed: ECS service `lily-reference-live-test`
  (`AEA_INVENTORY_FEED=lily-reference-live-test`, 30s loop) writes the five
  Lily `REFERENCE_CATALOG` SKUs into `inventory.product_availability` via
  `InventoryAvailabilityService.record()`. That is not a warehouse and not
  the Compose seeder.

## Soft launch

`pilot_ingress_cidrs = ["0.0.0.0/0"]` is the **accepted** Path B public shop
policy (sponsor, 2026-08-30, #335). Risk on the ALB edge is accepted for now
(DSO profile: public gateway only; BFF/RDS/MSK/LiteLLM stay SG-private; no
WAF in this Terraform). Re-evaluate and tighten CIDRs only if
`@aea-devsecops-platform`, `@aea-cost-guardian`, or the sponsor raises a new
residual. Do not invent office/VPN CIDRs in the meantime. Internal services
must stay non-public.

## Path B LiteLLM

Private Fargate service `litellm` (Cloud Map `litellm.aea-pilot.internal:4000`).
Same image/tag and `edge/litellm.yaml` aliases as Path A. No public listener.
Orchestration security group is the only ingress on :4000.

LiteLLM injects `ANTHROPIC_API_KEY` (Anthropic console key, LiteLLM only) and
`LITELLM_MASTER_KEY` (proxy bearer). Orchestration injects all three
`AEA_AI_*` together from the same secret (partial env crashes the process).
`AEA_AI_API_KEY` is the proxy bearer, not the Anthropic console key. Smoke
`GET /internal/v1/ai/health` until `mode` is `primary` (not only
`available: true`). Compose is not NFR-007/012 proof.

Missing JSON keys on a task `valueFrom` make that task fail
`ResourceInitializationError`; other services stay up. Merge vault keys
before applying the task defs, then force-new-deploy `litellm` and
`orchestration`. Keep 2-broker Kafka. No seeder. No florist operator.

## Bootstrap (after first images are in ECR)

See [BOOTSTRAP.md](BOOTSTRAP.md). Services start empty until migrations and
Kafka topics exist; run bootstrap before relying on relay/consumers.
