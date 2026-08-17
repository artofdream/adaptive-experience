resource "random_password" "orchestration_token" {
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
    # Same fixture as edge/gateway/ui/assets/app.js (already in git). A random
    # value here made Path B reject the shipped UI with authentication_required.
    AEA_LOCAL_BEARER_TOKEN = "local-browser-token"
    # Canonical origin: https://aea.artof.link (no www, no :443, no trailing slash).
    AEA_ALLOWED_ORIGIN = "https://${var.domain_name}"
    # ANTHROPIC_API_KEY, LITELLM_MASTER_KEY, and AEA_AI_* are operator-merged
    # into the live JSON. Terraform must not own those values. Inject all
    # three AEA_AI_* into orchestration together (partial env crashes).
    AEA_KAFKA_BOOTSTRAP     = aws_msk_cluster.main.bootstrap_brokers_sasl_scram
    AEA_KAFKA_SASL_USERNAME = "aea"
    AEA_KAFKA_SASL_PASSWORD = random_password.msk_scram.result
    AEA_KAFKA_SECURITY      = "SASL_SSL"
  })
  # Live JSON is merged out of band (bearer alignment, ANTHROPIC_API_KEY,
  # LITELLM_MASTER_KEY, AEA_AI_*). Applying this version blob would drop
  # those keys and revert a running BFF.
  lifecycle {
    ignore_changes = [secret_string]
  }
}
