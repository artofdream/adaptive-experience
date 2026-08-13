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
        "access_token", "address", "api_key", "authorization", "card_number", "cardholder_name", "customer_email",
        "customer_name", "cvv", "email", "phone", "recipient_address",
        "password", "recipient_email", "recipient_name", "refresh_token",
    }
    SECURITY_CONTEXT_FIELDS = {
        "authentication_strength", "classification", "scopes",
        "subject_reference", "tenant_reference",
    }

    def __init__(self, policy: KafkaPolicy, schema_dir: Path):
        self.policy = policy
        self.schema_dir = schema_dir
        self._schemas: dict[tuple[str, str], dict] = {}

    def validate_publication(self, principal: str, topic: str, envelope: dict) -> None:
        policy = self.policy.require_publish(principal, topic)
        self._validate(topic, policy.schema_version, policy.publisher, envelope)

    def validate_delivery(self, subscriber: str, topic: str, envelope: dict) -> None:
        policy = self.policy.require_consume(subscriber, topic)
        self._validate(topic, policy.schema_version, policy.publisher, envelope)

    def _validate(self, topic: str, active_version: str,
                  expected_source: str, envelope: dict) -> None:
        if set(envelope) != self.ENVELOPE_FIELDS:
            raise ValueError("envelope differs from the minimum governed contract")
        if envelope.get("topic") != topic:
            raise ValueError("envelope topic does not match transport topic")
        if envelope.get("source") != expected_source:
            raise ValueError("envelope source does not match the governed publisher")
        security_context = envelope.get("security_context")
        if not isinstance(security_context, dict):
            raise ValueError("security_context must be an object")
        unknown_security = sorted(set(security_context) - self.SECURITY_CONTEXT_FIELDS)
        if unknown_security:
            raise ValueError(f"security_context contains unauthorized fields: {unknown_security}")
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
        self._validate_schema(payload, schema, "payload")

    def _validate_schema(self, value, schema: dict, path: str) -> None:
        expected = schema.get("type")
        valid = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
        }
        if expected in valid and not valid[expected]:
            raise ValueError(f"{path} does not match its governed schema type")
        if expected == "object":
            properties = schema.get("properties", {})
            required = set(schema.get("required", []))
            missing = required - set(value)
            if missing:
                raise ValueError(f"{path} omits required fields: {sorted(missing)}")
            if schema.get("additionalProperties") is False:
                unknown = set(value) - set(properties)
                if unknown:
                    raise ValueError(f"{path} contains unsupported fields: {sorted(unknown)}")
            if len(value) < int(schema.get("minProperties", 0)):
                raise ValueError(f"{path} contains too few fields")
            for key, nested in value.items():
                if key in properties:
                    self._validate_schema(nested, properties[key], f"{path}.{key}")
        elif expected == "array":
            item_schema = schema.get("items", {})
            for index, item in enumerate(value):
                self._validate_schema(item, item_schema, f"{path}[{index}]")
        elif expected == "string":
            if len(value) < int(schema.get("minLength", 0)):
                raise ValueError(f"{path} is too short")
            if "maxLength" in schema and len(value) > int(schema["maxLength"]):
                raise ValueError(f"{path} is too long")
        elif expected in {"number", "integer"}:
            if "minimum" in schema and value < schema["minimum"]:
                raise ValueError(f"{path} is below its minimum")
            if "maximum" in schema and value > schema["maximum"]:
                raise ValueError(f"{path} exceeds its maximum")

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


class SourceGuardedPublisher:
    """Relay publisher that enforces the privacy guard per message.

    The outbox relay carries messages from many publishers, so the publishing
    principal is each message's declared `source`. The guard validates that the
    source is the governed publisher for the topic and that the payload is clean
    before the broker acknowledgement, keeping the relay fail-closed.
    """

    def __init__(self, guard: PayloadPrivacyGuard, publisher: Publisher):
        self.guard = guard
        self.publisher = publisher

    def publish(self, topic: str, key: str, message: dict) -> None:
        source = message.get("source") if isinstance(message, dict) else None
        if not isinstance(source, str) or not source:
            raise ValueError("envelope source is required for guarded publication")
        self.guard.validate_publication(source, topic, message)
        self.publisher.publish(topic, key, message)
