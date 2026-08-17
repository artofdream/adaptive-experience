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
# Fail-closed seeder. Florist operator is a named aea-pilot BFF exception
# (AEA_FLORIST_OPERATOR_EXCEPTION), not this bootstrap env. Kafka RF is
# selected separately: 2-broker
# pilot cannot host production RF=3. MinISR is RF-1 (pilot: RF=2 MinISR=1).
export AEA_ENVIRONMENT=production
export AEA_KAFKA_REPLICATION_PROFILE=pilot
```

Or run the orchestration image with those secrets injected (same as the relay task).

Do **not** export `AEA_SEED_INVENTORY=1`. Production fail-closed forbids the
local Compose seeder (`assert_local_seed_allowed`). The SM-authorized Path B
feed is the named heartbeat **`lily-reference-live-test`**: ECS service
`lily-reference-live-test` loops every 30s and writes the five
`REFERENCE_CATALOG` SKUs through `InventoryAvailabilityService.record()`.
Gate is `AEA_INVENTORY_FEED=lily-reference-live-test`. EventBridge
`rate(1 minute)` is too tight for the one-minute freshness window, so this
is a long-running task, not a scheduled one-shot. Prefer merge-then-apply
for that service. A one-off in-VPC RunTask of the same named writer is
allowed after the issue/MR exists.

Live intent: merge `ANTHROPIC_API_KEY`, `LITELLM_MASTER_KEY`,
`AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, and `AEA_AI_MODEL` into `${prefix}/app`
(do not replace the blob). `AEA_AI_ENDPOINT` =
`http://litellm.${prefix}.internal:4000/v1/chat/completions`. `AEA_AI_API_KEY`
is the proxy bearer (same value as `LITELLM_MASTER_KEY`), not the Anthropic
console key. `AEA_AI_MODEL` = `claude-sonnet-5`. Inject all three `AEA_AI_*`
into orchestration together. Do not put keys in `terraform.tfvars` or git.
Smoke `GET /internal/v1/ai/health` for `mode: "primary"`.

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

Named live-test inventory (after the `lily-reference-live-test` image tag
includes `platform/scripts/lily_reference_live_test.py`):

```bash
aws ecs run-task \
  --cluster "$AEA_ECS_CLUSTER" \
  --launch-type FARGATE \
  --task-definition "${AEA_ECS_CLUSTER}-lily-reference-live-test" \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-orch],assignPublicIp=DISABLED}"
```

Or override the orchestration family with `AEA_INVENTORY_FEED=lily-reference-live-test`
and `python platform/scripts/lily_reference_live_test.py --loop`. Do not set
`AEA_SEED_INVENTORY`. Keep `AEA_ENVIRONMENT=production`.
