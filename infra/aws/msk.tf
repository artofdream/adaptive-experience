# MSK with SASL/SCRAM over TLS (plaintext listeners are not enabled).
# SCRAM secrets must use a customer-managed KMS key that kafka.amazonaws.com can use.
resource "aws_kms_key" "msk_scram" {
  description             = "${local.prefix} MSK SCRAM secret"
  deletion_window_in_days = 7
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "Root"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "AllowMSK"
        Effect    = "Allow"
        Principal = { Service = "kafka.amazonaws.com" }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:CreateGrant",
        ]
        Resource = "*"
      },
    ]
  })
}

resource "random_password" "msk_scram" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "msk_scram" {
  # MSK SCRAM secrets must use the AmazonMSK_ name prefix.
  name       = "AmazonMSK_${local.prefix}_aea"
  kms_key_id = aws_kms_key.msk_scram.arn
}

resource "aws_secretsmanager_secret_version" "msk_scram" {
  secret_id = aws_secretsmanager_secret.msk_scram.id
  secret_string = jsonencode({
    username = "aea"
    password = random_password.msk_scram.result
  })
}

resource "aws_msk_configuration" "main" {
  name              = "${local.prefix}-msk"
  kafka_versions    = ["3.6.0"]
  server_properties = <<-PROPS
    auto.create.topics.enable=false
    unclean.leader.election.enable=false
    default.replication.factor=2
    min.insync.replicas=2
  PROPS
}

resource "aws_cloudwatch_log_group" "msk" {
  name              = "/aea/${local.prefix}/msk"
  retention_in_days = 14
}

resource "aws_msk_cluster" "main" {
  cluster_name           = "${local.prefix}-kafka"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = var.msk_broker_nodes

  broker_node_group_info {
    instance_type   = "kafka.t3.small"
    client_subnets  = aws_subnet.private[*].id
    security_groups = [aws_security_group.msk.id]
    storage_info {
      ebs_storage_info {
        volume_size = 50
      }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  client_authentication {
    sasl {
      scram = true
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.main.arn
    revision = aws_msk_configuration.main.latest_revision
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.msk.name
      }
    }
  }

  tags = { Name = "${local.prefix}-kafka" }
}

resource "aws_msk_scram_secret_association" "main" {
  cluster_arn     = aws_msk_cluster.main.arn
  secret_arn_list = [aws_secretsmanager_secret.msk_scram.arn]

  depends_on = [aws_secretsmanager_secret_version.msk_scram]
}

# Allow MSK to read the SCRAM secret.
resource "aws_secretsmanager_secret_policy" "msk_scram" {
  secret_arn = aws_secretsmanager_secret.msk_scram.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AWSKafkaResourcePolicy"
      Effect    = "Allow"
      Principal = { Service = "kafka.amazonaws.com" }
      Action    = "secretsmanager:GetSecretValue"
      Resource  = aws_secretsmanager_secret.msk_scram.arn
    }]
  })
}
