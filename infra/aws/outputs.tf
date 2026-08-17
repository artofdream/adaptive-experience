output "aws_region" {
  value = var.aws_region
}

output "ecr_orchestration_url" {
  value = aws_ecr_repository.orchestration.repository_url
}

output "ecr_bff_url" {
  value = aws_ecr_repository.bff.repository_url
}

output "ecr_gateway_url" {
  value = aws_ecr_repository.gateway.repository_url
}

output "gitlab_ci_role_arn" {
  description = "Set GitLab CI variable AWS_ROLE_ARN to this value (OIDC)."
  value       = aws_iam_role.gitlab_ci.arn
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  value = aws_lb.public.dns_name
}

output "public_url" {
  value = "https://${var.domain_name}"
}

output "app_secret_arn" {
  value = aws_secretsmanager_secret.app.arn
}

output "rds_endpoint" {
  value = aws_db_instance.main.address
}

output "msk_bootstrap_sasl_scram" {
  value     = aws_msk_cluster.main.bootstrap_brokers_sasl_scram
  sensitive = true
}

output "service_names" {
  value = {
    gateway                  = aws_ecs_service.gateway.name
    bff                      = aws_ecs_service.bff.name
    orchestration            = aws_ecs_service.orchestration.name
    relay                    = aws_ecs_service.relay.name
    consumer                 = aws_ecs_service.consumer_workspace.name
    litellm                  = aws_ecs_service.litellm.name
    lily_reference_live_test = aws_ecs_service.lily_reference_live_test.name
  }
}

output "litellm_internal_url" {
  description = "OpenAI-compatible chat-completions URL. Operator-merged as AEA_AI_ENDPOINT and injected into orchestration with AEA_AI_API_KEY and AEA_AI_MODEL."
  value       = "http://${local.discovery_litellm_host}:4000/v1/chat/completions"
}
