resource "random_password" "orchestration_token" {
  length  = 48
  special = false
}

resource "random_password" "browser_token" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "app" {
  name = "${local.prefix}/app"
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    AEA_POSTGRES_DSN = format(
      "postgresql://%s:%s@%s:5432/%s",
      aws_db_instance.main.username,
      random_password.db.result,
      aws_db_instance.main.address,
      aws_db_instance.main.db_name,
    )
    AEA_ORCHESTRATION_TOKEN = random_password.orchestration_token.result
    AEA_LOCAL_BEARER_TOKEN  = random_password.browser_token.result
    # Canonical origin: https://aea.artof.link (no www, no :443, no trailing slash).
    AEA_ALLOWED_ORIGIN      = "https://${var.domain_name}"
    # AEA_AI_ENDPOINT, AEA_AI_API_KEY, and AEA_AI_MODEL stay operator-owned in
    # Secrets Manager (not this JSON, not terraform.tfvars). Wire into the
    # orchestration task in a later slice after the operator puts the values.
    AEA_KAFKA_BOOTSTRAP     = aws_msk_cluster.main.bootstrap_brokers_sasl_scram
    AEA_KAFKA_SASL_USERNAME = "aea"
    AEA_KAFKA_SASL_PASSWORD = random_password.msk_scram.result
    AEA_KAFKA_SECURITY      = "SASL_SSL"
  })
}
