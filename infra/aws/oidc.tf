# GitLab.com OIDC provider for CI (no long-lived AWS keys in GitLab).
data "tls_certificate" "gitlab" {
  url = var.gitlab_url
}

resource "aws_iam_openid_connect_provider" "gitlab" {
  url             = var.gitlab_url
  client_id_list  = [var.gitlab_oidc_audience]
  thumbprint_list = [data.tls_certificate.gitlab.certificates[0].sha1_fingerprint]
}

data "aws_iam_policy_document" "gitlab_ci_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.gitlab.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.gitlab_url, "https://", "")}:aud"
      values   = [var.gitlab_oidc_audience]
    }
    condition {
      test     = "StringLike"
      variable = "${replace(var.gitlab_url, "https://", "")}:sub"
      values   = ["project_path:${var.gitlab_project_path}:ref_type:branch:ref:main"]
    }
  }
}

resource "aws_iam_role" "gitlab_ci" {
  name               = "${local.prefix}-gitlab-ci"
  assume_role_policy = data.aws_iam_policy_document.gitlab_ci_assume.json
}

data "aws_iam_policy_document" "gitlab_ci" {
  statement {
    sid = "EcrAuth"
    actions = [
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
  }
  statement {
    sid = "EcrPush"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
      "ecr:BatchGetImage",
      "ecr:DescribeRepositories",
      "ecr:DescribeImages",
    ]
    resources = [
      aws_ecr_repository.orchestration.arn,
      aws_ecr_repository.bff.arn,
      aws_ecr_repository.gateway.arn,
      aws_ecr_repository.agent_runner.arn,
    ]
  }
  statement {
    sid = "EcsDeploy"
    actions = [
      "ecs:DescribeClusters",
      "ecs:DescribeServices",
      "ecs:DescribeTaskDefinition",
      "ecs:RegisterTaskDefinition",
      "ecs:UpdateService",
      "ecs:ListTasks",
      "ecs:DescribeTasks",
      "ecs:RunTask",
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Project"
      values   = ["adaptive-experience"]
    }
  }
  statement {
    sid       = "EcsDeployUntaggedRegister"
    actions   = ["ecs:RegisterTaskDefinition", "ecs:DescribeTaskDefinition", "ecs:UpdateService", "ecs:DescribeServices", "ecs:DescribeClusters", "iam:PassRole"]
    resources = ["*"]
  }
  statement {
    sid = "LogsRead"
    actions = [
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:GetLogEvents",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "gitlab_ci" {
  name   = "${local.prefix}-gitlab-ci"
  role   = aws_iam_role.gitlab_ci.id
  policy = data.aws_iam_policy_document.gitlab_ci.json
}
