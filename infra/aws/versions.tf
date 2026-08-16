# Terraform AWS stack for AEA web deploy (us-east-1).
# Apply after setting gitlab_project_path, domain_name, and ACM certificate.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "adaptive-experience"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
