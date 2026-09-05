# DevSecOps posture map

Do not treat local Compose or CI plaintext Kafka as the cloud.

## What is on main (reference MVP)

| Area | Path | Production? |
|---|---|---|
| Platform Compose | `platform/docker-compose.yml` | No. Postgres volume unencrypted; Kafka `PLAINTEXT`. |
| Edge Compose | `edge/docker-compose.yml` | No. `AEA_ENVIRONMENT=local`, inventory-seeder, `AEA_FLORIST_OPERATOR=1`. TLS is ephemeral self-signed on `:8443`. BFF has no host port. |
| GitLab CI | `.gitlab-ci.yml` | Verify + Docker-service integration (pgvector, Kafka plaintext). Not an AWS deploy pipeline on main. |
| Topology | ADR-007, `docs/04-technical-architecture/reference-deployment-validation.md` | Modular monolith + gateway + BFF + broker. |
| Broker | ADR-012 | Production **TLS + SASL required**. Local/CI plaintext tests delivery semantics only. |
| ACLs | `platform/scripts/render_kafka_acls.py` | Plan is tested; applying to a real cluster is a deploy-target activity. |
| Migrations | `platform/scripts/apply_migrations.py` | Idempotent. Must run in cloud. |
| Perimeter tests | `edge/tests/test_perimeter.py`, `docs/04-technical-architecture/mvp-security-audit.md` | Cookie/CSRF/origin/privacy. |
| Encryption docs | `docs/04-technical-architecture/nfr-007-012-encryption.md` | Local Compose **must not** be cited as at-rest encryption evidence. |
| Privacy | NFR-013 / NFR-017 `PayloadPrivacyGuard` | Fail-closed on every governed topic. |
| SLO | NFR-003 / NFR-004 notes; `edge/scripts/check_assistant_slo.py` | Measured on the reference stack, not a fabricated 99.5% from one laptop run. |

Fail-closed production flags (must hold in cloud task defs):

- `AEA_ENVIRONMENT=production` → seeder raises
  (`platform/aea_platform/local_inventory_seed.py`)
- Florist operator 404 when environment is production even if
  `AEA_FLORIST_OPERATOR=1`, unless named exception
  `AEA_FLORIST_OPERATOR_EXCEPTION=aea-pilot` (`edge/bff/aea_bff/runtime.py`).
  Generic production stays 404. Inbox does not write inventory.
- Kafka provision treats production as non-local
  (`platform/scripts/provision_kafka.py`)

## Cloud track (prefer this; do not reinvent)

AWS is **unparked**. `@aea-devsecops-platform` **operates** Path B
(`plan`/`apply`/bootstrap/Secrets Manager/OIDC handoff). The human is
**sponsor**, not Scrum Master: the human does not terraform. PM-SM also
does not terraform. This skill still applies. Do not wait for the SM to
apply. Escalate secrets and GitLab CI var paste to the **sponsor**. Path A
stays local Compose. Wait tags: `none` while this skill applies; `user`
for DNS/GitLab vars the **sponsor** must paste. Parked AWS is no longer a
skip.

Documented AWS GitLab web deploy (ECR, ECS Fargate, ALB+ACM TLS,
`aea.artof.link`, RDS PostgreSQL 16, MSK, Secrets Manager, GitLab OIDC).
Look for:

- Branch `feat/aws-gitlab-web-deploy` (may be unmerged)
- `infra/aws/` Terraform, `README.md`, `BOOTSTRAP.md`
- `research/aws-gitlab-web-deploy.md`

If those files are missing on the current branch, the **gap is “IaC not on
main”**, not “invent Elastic Beanstalk.”

**Never commit** `infra/aws/terraform.tfvars` (account, ACM ARN, ingress
CIDRs, domain). Prefer `terraform.tfvars.example` without live ARNs. `.env`
and vault credentials stay out of git (`.obsidian/` already gitignored).

Laptop pushes to pilot ECR are disallowed unless break-glass. Merge AWS
work as its **own** MR — not a coherence finding dump.

## GitLab CI jobs (main)

- `coherence-guard`, `topic-schema-guard` (NFR-015)
- `platform-foundation-unit`, `edge-perimeter-unit`
- `platform-foundation-integration` (Postgres + Kafka services,
  `AEA_INTEGRATION=1`)
- required `markdownlint` (#325); required `linkcheck` (#326); required `ruff` (#327); required `bandit` (#328)

A cloud deploy job belongs with the AWS track, using OIDC, not static AWS
access keys in the repo.

## Review checklists (do not replace IaC)

- This repo: ADR-007, ADR-012, mvp-security-audit, nfr-007-012, nfr-013,
  reference-deployment-validation
- Optional: AWS Well-Architected (security, reliability, cost) via
  deploy-on-aws / awsknowledge MCP — **review only**
- Optional architecture diagram skill: only if the user asks for a diagram
  of **existing** `infra/aws`

## Typical one-MR findings (do not batch)

| Severity | Example |
|---|---|
| blocker | Production task def still seeds inventory, or enables `/florist` **without** the named `aea-pilot` exception; secrets in git; public BFF port; plaintext MSK in prod |
| high | No RDS encryption flag; CI using long-lived AWS keys; compose/cloud image drift |
| medium | Missing CloudWatch alarms; backup window undocumented; `.gitignore` does not exclude `*.tfvars` |
| low | Base-image pin hygiene; README compose-vs-cloud table |

## Docker integration before MR

Same SOP as other skills: only the impacted runner. Compose up is
verification, not a cloud apply.
