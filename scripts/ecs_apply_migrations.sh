#!/bin/sh
# Path B: apply DB migrations via ECS RunTask (in-VPC). Fail-closed.
# Used by deploy-ecs so schema cannot lag the shipped image (#436).
set -eu

CLUSTER="${AEA_ECS_CLUSTER:?AEA_ECS_CLUSTER required}"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
SERVICE="${AEA_ECS_MIGRATE_SERVICE:-orchestration}"
TASK_FAMILY="${AEA_ECS_ORCHESTRATION_TASK_FAMILY:-${CLUSTER}-orchestration}"
CONTAINER="${AEA_ECS_ORCHESTRATION_CONTAINER:-orchestration}"

echo "ecs_apply_migrations: cluster=${CLUSTER} family=${TASK_FAMILY} service=${SERVICE}"

NET_JSON=$(aws ecs describe-services \
  --region "$REGION" \
  --cluster "$CLUSTER" \
  --services "$SERVICE" \
  --query 'services[0].networkConfiguration.awsvpcConfiguration' \
  --output json)

SUBNETS=$(printf '%s' "$NET_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(",".join(d["subnets"]))')
SGS=$(printf '%s' "$NET_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(",".join(d["securityGroups"]))')
test -n "$SUBNETS"
test -n "$SGS"

OVERRIDES=$(printf '{"containerOverrides":[{"name":"%s","command":["python","platform/scripts/apply_migrations.py"]}]}' "$CONTAINER")

TASK_ARN=$(aws ecs run-task \
  --region "$REGION" \
  --cluster "$CLUSTER" \
  --launch-type FARGATE \
  --task-definition "$TASK_FAMILY" \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNETS}],securityGroups=[${SGS}],assignPublicIp=DISABLED}" \
  --overrides "$OVERRIDES" \
  --query 'tasks[0].taskArn' \
  --output text)

test -n "$TASK_ARN"
test "$TASK_ARN" != "None"
echo "ecs_apply_migrations: started ${TASK_ARN}"

aws ecs wait tasks-stopped --region "$REGION" --cluster "$CLUSTER" --tasks "$TASK_ARN"

EXIT_CODE=$(aws ecs describe-tasks \
  --region "$REGION" \
  --cluster "$CLUSTER" \
  --tasks "$TASK_ARN" \
  --query 'tasks[0].containers[0].exitCode' \
  --output text)

STOP=$(aws ecs describe-tasks \
  --region "$REGION" \
  --cluster "$CLUSTER" \
  --tasks "$TASK_ARN" \
  --query 'tasks[0].stoppedReason' \
  --output text)

echo "ecs_apply_migrations: exitCode=${EXIT_CODE} stoppedReason=${STOP}"

if [ "$EXIT_CODE" != "0" ]; then
  echo "ecs_apply_migrations: FAILED (deploy must not continue with schema lag)" >&2
  exit 1
fi

echo "ecs_apply_migrations: OK"
