# Bootstrap AWS data plane

One-time (and after schema/topic changes) from a network path that can reach
**private** RDS and MSK (ECS RunTask, bastion, or CI job in the VPC).

## 1. Load secrets

Export from Secrets Manager `${prefix}/app` (see Terraform `app_secret_arn`):

```bash
export AEA_POSTGRES_DSN=...
export AEA_KAFKA_BOOTSTRAP=...
export AEA_KAFKA_SECURITY=SASL_SSL
export AEA_KAFKA_SASL_USERNAME=aea
export AEA_KAFKA_SASL_PASSWORD=...
export AEA_KAFKA_SASL_MECHANISM=SCRAM-SHA-512
# Fail-closed seeder/florist. Kafka RF is selected separately: 2-broker
# pilot cannot host production RF=3. MinISR is RF-1 (pilot: RF=2 MinISR=1).
export AEA_ENVIRONMENT=production
export AEA_KAFKA_REPLICATION_PROFILE=pilot
```

Or run the orchestration image with those secrets injected (same as the relay task).

Do **not** export `AEA_SEED_INVENTORY=1`. Production fail-closed forbids the
local seeder. Inventory for a live test must come from an operator feed into
`inventory.product_availability` (POS/export or curated fixture load), not
this Terraform.

Live intent (optional, later slice): put `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`,
and `AEA_AI_MODEL` in Secrets Manager. Use an OpenAI-compatible URL (LiteLLM
or equivalent). Do not put the key in `terraform.tfvars` or git. Task defs in
this recover MR do not inject those three yet — orchestration stays on regex
intent until they are wired.

## 2. Migrations

```bash
python platform/scripts/apply_migrations.py
python platform/scripts/apply_migrations.py   # idempotent second pass
```

## 3. Kafka topics

```bash
python platform/scripts/provision_kafka.py
```

## 4. ACLs

Render intended ACLs and apply them to the MSK SCRAM principal `aea`
(and any additional consumer principals) using your admin tooling:

```bash
python platform/scripts/render_kafka_acls.py
```

MSK SCRAM ACL application is operator-owned (console, `kafka-acls`, or
automation). Do not leave topics world-writable.

## 5. Workers

Terraform already defines ECS services `relay` and `consumer-workspace`.
After bootstrap:

1. Confirm desired count ≥ 1 and tasks are RUNNING.
2. `python platform/scripts/diagnose.py` — `pending_outbox` should drain under load.
3. CloudWatch log groups `/aea/<prefix>/relay` and `.../consumer`.

## ECS RunTask example

Use the same task definition family as orchestration (or a one-off override
command). Example with AWS CLI after OIDC login:

```bash
aws ecs run-task \
  --cluster "$AEA_ECS_CLUSTER" \
  --launch-type FARGATE \
  --task-definition "${AEA_ECS_CLUSTER}-orchestration" \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-orch],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"orchestration","command":["python","platform/scripts/apply_migrations.py"]}]}'
```

Repeat with `provision_kafka.py` on the **relay** task definition (Kafka SASL
secrets are injected there). Worker task defs set
`AEA_KAFKA_REPLICATION_PROFILE=pilot` so new topics get RF=2 MinISR=1, not
production RF=3. Prefer a documented runbook ticket when changing production
schema.
