resource "aws_ecr_repository" "orchestration" {
  name                 = "${local.prefix}/orchestration"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "bff" {
  name                 = "${local.prefix}/bff"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "gateway" {
  name                 = "${local.prefix}/gateway"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "agent_runner" {
  name                 = "${local.prefix}/agent-runner"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "grafana" {
  name                 = "${local.prefix}/grafana"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_lifecycle_policy" "keep_last_20" {
  for_each = {
    orchestration = aws_ecr_repository.orchestration.name
    bff           = aws_ecr_repository.bff.name
    gateway       = aws_ecr_repository.gateway.name
    agent_runner  = aws_ecr_repository.agent_runner.name
    grafana       = aws_ecr_repository.grafana.name
  }
  repository = each.value
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 20 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 20
      }
      action = { type = "expire" }
    }]
  })
}
