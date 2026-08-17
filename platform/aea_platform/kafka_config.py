"""librdkafka client options for local plaintext and Path B SASL/SSL."""

from __future__ import annotations

import os


def kafka_security_config(environ: dict | None = None) -> dict:
    """Return SASL/TLS librdkafka keys when AEA_KAFKA_SECURITY is set.

    Local Compose and CI omit the variable so clients stay PLAINTEXT.
    Path B injects SASL_SSL plus SCRAM credentials from Secrets Manager.
    """
    env = os.environ if environ is None else environ
    security = env.get("AEA_KAFKA_SECURITY")
    if not security:
        return {}
    conf = {
        "security.protocol": security,
        "sasl.mechanism": env.get("AEA_KAFKA_SASL_MECHANISM") or "SCRAM-SHA-512",
    }
    username = env.get("AEA_KAFKA_SASL_USERNAME")
    password = env.get("AEA_KAFKA_SASL_PASSWORD")
    if username:
        conf["sasl.username"] = username
    if password:
        conf["sasl.password"] = password
    return conf


def kafka_producer_config(bootstrap_servers: str, client_id: str,
                          environ: dict | None = None) -> dict:
    """Idempotent producer config, plus SASL when the environment requires it."""
    conf = {
        "bootstrap.servers": bootstrap_servers,
        "client.id": client_id,
        "acks": "all",
        "enable.idempotence": True,
        "max.in.flight.requests.per.connection": 5,
    }
    conf.update(kafka_security_config(environ))
    return conf
