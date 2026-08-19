# AWS ECS Fargate Infrastructure Module for 24/7 Autonomous Cloud Agent Service
# Coherent with ADR-007 (Initial Deployment Topology), NFR-003 (Availability), and NFR-017 (Privacy)

variable "aws_region" {
  type        = string
  default     = "ap-southeast-2"
  description = "AWS Region for ECS Fargate deployment"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment"
}

# AWS CloudWatch Log Group for 24/7 Autonomous Agent Container
resource "aws_cloudwatch_log_group" "aea_agent_runner_logs" {
  name              = "/ecs/aea-agent-runner"
  retention_in_days = 30

  tags = {
    Project     = "AdaptiveExperienceArchitecture"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# AWS Secrets Manager Secret for GITLAB_TOKEN
resource "aws_secretsmanager_secret" "gitlab_token" {
  name        = "aea/gitlab-token"
  description = "GitLab API access token for 24/7 autonomous agent CLI operations"

  tags = {
    Project     = "AdaptiveExperienceArchitecture"
    Environment = var.environment
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "aea-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Attach AWS Managed Policy for ECS Task Execution
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicySupport"
}

# ECS Cluster
resource "aws_ecs_cluster" "aea_cluster" {
  name = "aea-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "aea_agent_runner_task" {
  family                   = "aea-agent-runner"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = templatefile("${path.module}/ecs_task_definition.json.tpl", {
    ecr_repository_url      = "123456789012.dkr.ecr.${var.aws_region}.amazonaws.com/aea-agent-runner"
    gitlab_token_secret_arn = aws_secretsmanager_secret.gitlab_token.arn
    aws_region              = var.aws_region
  })
}
