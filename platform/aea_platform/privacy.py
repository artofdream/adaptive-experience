from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .policy import KafkaPolicy


class Publisher(Protocol):
    def publish(self, topic: str, key: str, message: dict) -> None: ...


class PayloadPrivacyGuard:
    """Fail-closed enforcement for NFR-017 at broker boundaries."""

    ENVELOPE_FIELDS = {
        "message_id", "topic", "message_type", "schema_version", "session_id",
        "correlation_id", "source", "context_version", "publication_time",
        "security_context", "payload", "outcome",
    }
    RAW_SENSITIVE_FIELDS = {
        "address", "card_number", "cardholder_name", "customer_email",
        "customer_name", "cvv", "email", "phone", "recipient_address",
        "recipient_email", "recipient_name",
    }

    def __init__(self, policy: KafkaPolicy, schema_dir: Path):
        self.policy = policy
        self.schema_dir = schema_dir
        self._schemas: dict[tuple[str, str], dict] = {}

    def validate_publication(self, principal: str, topic: str, envelope: dict) -> None:
        policy = self.policy.require_publish(principal, topic)
        self._validate(topic, policy.schema_version, envelope)

    def validate_delivery(self, subscriber: str, topic: str, envelope: dict) -> None:
        policy = self.policy.require_consume(subscriber, topic)
        self._validate(topic, policy.schema_version, envelope)

    def _validate(self, topic: str, active_version: str, envelope: dict) -> None:
        if set(envelope) != self.ENVELOPE_FIELDS:
            raise ValueError("envelope differs from the minimum governed contract")
        if envelope.get("topic") != topic:
            raise ValueError("envelope topic does not match transport topic")
        version = envelope.get("schema_version")
        if not isinstance(version, str):
            raise ValueError("schema_version is required")
        if version != active_version:
            raise ValueError("schema_version is not the active governed version")
        schema = self._schema(topic, version)
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        allowed = set(schema["properties"])
        actual = set(payload)
        extra = sorted(actual - allowed)
        missing = sorted(set(schema["required"]) - actual)
        if extra:
            raise ValueError(f"payload exposes fields outside its minimum contract: {extra}")
        if missing:
            raise ValueError(f"payload omits required fields: {missing}")
        leaked = sorted(self._sensitive_keys(envelope))
        if leaked:
            raise ValueError(f"raw sensitive fields are prohibited; use references or tokens: {leaked}")

    def _schema(self, topic: str, version: str) -> dict:
        key = (topic, version)
        if key not in self._schemas:
            safe_name = f"{topic}.v{version}.json"
            path = self.schema_dir / safe_name
            if not path.is_file() or path.parent.resolve() != self.schema_dir.resolve():
                raise ValueError("unregistered payload schema")
            self._schemas[key] = json.loads(path.read_text(encoding="utf-8"))
        return self._schemas[key]

    def _sensitive_keys(self, value) -> set[str]:
        found: set[str] = set()
        if isinstance(value, dict):
            for key, nested in value.items():
                if key.lower() in self.RAW_SENSITIVE_FIELDS:
                    found.add(key)
                found.update(self._sensitive_keys(nested))
        elif isinstance(value, list):
            for nested in value:
                found.update(self._sensitive_keys(nested))
        return found


class PrivacyEnforcingPublisher:
    """Only publish messages authorized for this principal and payload contract."""

    def __init__(self, principal: str, guard: PayloadPrivacyGuard, publisher: Publisher):
        self.principal = principal
        self.guard = guard
        self.publisher = publisher

    def publish(self, topic: str, key: str, message: dict) -> None:
        self.guard.validate_publication(self.principal, topic, message)
        self.publisher.publish(topic, key, message)
