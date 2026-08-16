locals {
  prefix = "${var.name_prefix}-${var.environment}"
  common_tags = {
    Name = local.prefix
  }
  # GitLab OIDC subject for branch pipelines on main (project_path:ref_type:ref).
  gitlab_ci_sub = "project_path:${var.gitlab_project_path}:ref_type:branch:ref:main"
}

data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}
