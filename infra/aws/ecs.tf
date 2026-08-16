resource "aws_service_discovery_private_dns_namespace" "main" {
  name = "${local.prefix}.internal"
  vpc  = aws_vpc.main.id
}

resource "aws_service_discovery_service" "bff" {
  name = "bff"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    dns_records {
      ttl  = 10
      type = "A"
    }
    routing_policy = "MULTIVALUE"
  }
  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_service_discovery_service" "orchestration" {
  name = "orchestration"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    dns_records {
      ttl  = 10
      type = "A"
    }
    routing_policy = "MULTIVALUE"
  }
  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_cloudwatch_log_group" "ecs" {
  for_each          = toset(["gateway", "bff", "orchestration", "relay", "consumer"])
  name              = "/aea/${local.prefix}/${each.key}"
  retention_in_days = 30
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.prefix}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_execution_secrets" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.app.arn, aws_secretsmanager_secret.msk_scram.arn]
  }
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name   = "${local.prefix}-ecs-execution-secrets"
  role   = aws_iam_role.ecs_execution.id
  policy = data.aws_iam_policy_document.ecs_execution_secrets.json
}

resource "aws_iam_role" "ecs_task" {
  name               = "${local.prefix}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

resource "aws_ecs_cluster" "main" {
  name = local.prefix
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = { Project = "adaptive-experience" }
}

locals {
  orchestration_image = "${aws_ecr_repository.orchestration.repository_url}:${var.container_image_tag}"
  bff_image           = "${aws_ecr_repository.bff.repository_url}:${var.container_image_tag}"
  gateway_image       = "${aws_ecr_repository.gateway.repository_url}:${var.container_image_tag}"
  discovery_bff_host  = "bff.${local.prefix}.internal"
  discovery_orch_host = "orchestration.${local.prefix}.internal"
}

resource "aws_ecs_task_definition" "orchestration" {
  family                   = "${local.prefix}-orchestration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name      = "orchestration"
    image     = local.orchestration_image
    essential = true
    portMappings = [{ containerPort = 8081, protocol = "tcp" }]
    environment = [
      { name = "AEA_ENVIRONMENT", value = "production" },
      { name = "AEA_KAFKA_REPLICATION_PROFILE", value = "pilot" },
    ]
    secrets = [
      { name = "AEA_POSTGRES_DSN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_POSTGRES_DSN::" },
      { name = "AEA_ORCHESTRATION_TOKEN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_ORCHESTRATION_TOKEN::" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs["orchestration"].name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "orchestration"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "bff" {
  family                   = "${local.prefix}-bff"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name      = "bff"
    image     = local.bff_image
    essential = true
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
    environment = [
      { name = "AEA_ENVIRONMENT", value = "production" },
      { name = "AEA_ORCHESTRATION_URL", value = "http://${local.discovery_orch_host}:8081" },
    ]
    secrets = [
      { name = "AEA_ORCHESTRATION_TOKEN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_ORCHESTRATION_TOKEN::" },
      { name = "AEA_LOCAL_BEARER_TOKEN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_LOCAL_BEARER_TOKEN::" },
      { name = "AEA_ALLOWED_ORIGIN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_ALLOWED_ORIGIN::" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs["bff"].name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "bff"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "gateway" {
  family                   = "${local.prefix}-gateway"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name      = "gateway"
    image     = local.gateway_image
    essential = true
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
    environment = [
      { name = "AEA_GATEWAY_MODE", value = "alb" },
      { name = "AEA_BFF_UPSTREAM", value = "http://${local.discovery_bff_host}:8080" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs["gateway"].name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "gateway"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "relay" {
  family                   = "${local.prefix}-relay"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name      = "relay"
    image     = local.orchestration_image
    essential = true
    command   = ["python", "platform/scripts/run_relay.py", "--loop"]
    environment = [
      { name = "AEA_ENVIRONMENT", value = "production" },
      { name = "AEA_KAFKA_REPLICATION_PROFILE", value = "pilot" },
    ]
    secrets = [
      { name = "AEA_POSTGRES_DSN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_POSTGRES_DSN::" },
      { name = "AEA_KAFKA_BOOTSTRAP", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_BOOTSTRAP::" },
      { name = "AEA_KAFKA_SASL_USERNAME", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_SASL_USERNAME::" },
      { name = "AEA_KAFKA_SASL_PASSWORD", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_SASL_PASSWORD::" },
      { name = "AEA_KAFKA_SECURITY", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_SECURITY::" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs["relay"].name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "relay"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "consumer_workspace" {
  family                   = "${local.prefix}-consumer-workspace"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name      = "consumer"
    image     = local.orchestration_image
    essential = true
    command   = ["python", "platform/scripts/run_consumer.py", "workspace", "--loop"]
    environment = [
      { name = "AEA_ENVIRONMENT", value = "production" },
      { name = "AEA_KAFKA_REPLICATION_PROFILE", value = "pilot" },
    ]
    secrets = [
      { name = "AEA_POSTGRES_DSN", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_POSTGRES_DSN::" },
      { name = "AEA_KAFKA_BOOTSTRAP", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_BOOTSTRAP::" },
      { name = "AEA_KAFKA_SASL_USERNAME", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_SASL_USERNAME::" },
      { name = "AEA_KAFKA_SASL_PASSWORD", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_SASL_PASSWORD::" },
      { name = "AEA_KAFKA_SECURITY", valueFrom = "${aws_secretsmanager_secret.app.arn}:AEA_KAFKA_SECURITY::" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs["consumer"].name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "workspace"
      }
    }
  }])
}

resource "aws_ecs_service" "orchestration" {
  name            = "orchestration"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.orchestration.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.orchestration.id]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = aws_service_discovery_service.orchestration.arn
  }
  tags = { Project = "adaptive-experience" }
}

resource "aws_ecs_service" "bff" {
  name            = "bff"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.bff.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.bff.id]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = aws_service_discovery_service.bff.arn
  }
  depends_on = [aws_ecs_service.orchestration]
  tags       = { Project = "adaptive-experience" }
}

resource "aws_ecs_service" "gateway" {
  name            = "gateway"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.gateway.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.gateway.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.gateway.arn
    container_name   = "gateway"
    container_port   = 8080
  }
  depends_on = [aws_lb_listener.https, aws_ecs_service.bff]
  tags       = { Project = "adaptive-experience" }
}

resource "aws_ecs_service" "relay" {
  name            = "relay"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.relay.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.orchestration.id]
    assign_public_ip = false
  }
  tags = { Project = "adaptive-experience" }
}

resource "aws_ecs_service" "consumer_workspace" {
  name            = "consumer-workspace"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.consumer_workspace.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.orchestration.id]
    assign_public_ip = false
  }
  tags = { Project = "adaptive-experience" }
}
