variable "aws_region" {
  type        = string
  description = "AWS region for the web MVP stack."
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Terraform stack name for tags and resource prefixes (pilot). App task defs hardcode AEA_ENVIRONMENT=production so the seeder stays fail-closed. Florist operator is a named aea-pilot exception only, not generic production."
  default     = "pilot"
}

variable "name_prefix" {
  type        = string
  description = "Prefix for resource names."
  default     = "aea"
}

variable "gitlab_url" {
  type        = string
  description = "GitLab instance URL for OIDC."
  default     = "https://gitlab.com"
}

variable "gitlab_project_path" {
  type        = string
  description = "GitLab path group/project used in OIDC sub claim (e.g. artof-group/adaptive-experience-architecture)."
}

variable "gitlab_oidc_audience" {
  type        = string
  description = "OIDC audience configured in GitLab CI (AWS_ROLE_ARN job)."
  default     = "https://gitlab.com"
}

variable "domain_name" {
  type        = string
  description = "Public HTTPS hostname. Canonical origin is https://<this> with no www, no :443, no trailing slash."
  default     = "aea.artof.link"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN in the same region as the ALB (or us-east-1 only if using CloudFront; ALB needs regional cert)."
}

variable "container_image_tag" {
  type        = string
  description = "ECR image tag to deploy (usually git SHA)."
  default     = "latest"
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "pilot_ingress_cidrs" {
  type        = list(string)
  description = "CIDRs allowed to reach the ALB during soft launch. Use [\"0.0.0.0/0\"] only when opening publicly."
  default     = ["0.0.0.0/0"]
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.small"
}

variable "msk_broker_nodes" {
  type        = number
  description = "Pilot Kafka broker count. Locked at 2 (RF=2, MinISR=1, two private subnets). Do not raise to 3 without SM unpark."
  default     = 2
  validation {
    condition     = var.msk_broker_nodes >= 2
    error_message = "MSK broker count must be at least 2 so min.insync.replicas can be RF-1."
  }
}

variable "desired_count" {
  type        = number
  description = "Desired ECS tasks per service."
  default     = 1
}

variable "litellm_image" {
  type        = string
  description = "Public LiteLLM image. Same rolling tag as Path A (edge/docker-compose.litellm.yml) so Anthropic model ids stay current. Not an ECR build."
  default     = "ghcr.io/berriai/litellm:main-latest"
}
