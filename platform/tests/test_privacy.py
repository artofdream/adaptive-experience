from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.policy import KafkaPolicy
from aea_platform.privacy import PayloadPrivacyGuard, PrivacyEnforcingPublisher


class RecordingPublisher:
    def __init__(self):
        self.messages = []

    def publish(self, topic, key, message):
        self.messages.append((topic, key, message))


def envelope(topic="payment.authorization.requested", payload=None):
    return {
        "message_id": "message-1", "topic": topic, "message_type": "command",
        "schema_version": "1.0.0", "session_id": "session-1",
        "correlation_id": "correlation-1", "source": "orchestration",
        "context_version": 3, "publication_time": "2026-08-12T00:00:00Z",
        "security_context": {"classification": "confidential"},
        "payload": payload or {
            "draft_order_id": "draft-1", "amount": 49.0,
            "payment_token": "provider-token-1",
        },
        "outcome": {},
    }


class PrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
        schemas = ROOT.parent / "docs" / "04-technical-architecture" / "schemas"
        cls.guard = PayloadPrivacyGuard(policy, schemas)

    def test_minimum_tokenized_payment_payload_is_authorized_only_for_payment(self):
        message = envelope()
        self.guard.validate_publication("orchestration", message["topic"], message)
        self.guard.validate_delivery("payment", message["topic"], message)
        with self.assertRaises(PermissionError):
            self.guard.validate_delivery("workspace", message["topic"], message)

    def test_undeclared_customer_or_payment_data_never_reaches_publisher(self):
        target = RecordingPublisher()
        publisher = PrivacyEnforcingPublisher("orchestration", self.guard, target)
        message = envelope()
        message["payload"]["card_number"] = "4111111111111111"
        with self.assertRaisesRegex(ValueError, "outside its minimum contract"):
            publisher.publish(message["topic"], "draft-1", message)
        self.assertEqual([], target.messages)

    def test_nested_raw_sensitive_fields_are_rejected(self):
        message = envelope(
            "experience.intent.updated",
            {"structured_intent": {"occasion": "birthday", "recipient_name": "Private Person"}},
        )
        with self.assertRaisesRegex(ValueError, "raw sensitive fields"):
            self.guard.validate_publication("orchestration", message["topic"], message)

    def test_extra_envelope_metadata_is_rejected(self):
        message = envelope()
        message["debug_customer_email"] = "private@example.invalid"
        with self.assertRaisesRegex(ValueError, "minimum governed contract"):
            self.guard.validate_publication("orchestration", message["topic"], message)

    def test_sensitive_data_cannot_hide_in_security_or_outcome_metadata(self):
        message = envelope()
        message["security_context"]["email"] = "private@example.invalid"
        with self.assertRaisesRegex(ValueError, "raw sensitive fields"):
            self.guard.validate_publication("orchestration", message["topic"], message)

    def test_missing_minimum_field_and_unknown_schema_are_rejected(self):
        message = envelope()
        del message["payload"]["payment_token"]
        with self.assertRaisesRegex(ValueError, "omits required"):
            self.guard.validate_publication("orchestration", message["topic"], message)
        unknown = copy.deepcopy(envelope())
        unknown["schema_version"] = "9.0.0"
        with self.assertRaisesRegex(ValueError, "active governed version"):
            self.guard.validate_publication("orchestration", unknown["topic"], unknown)


if __name__ == "__main__":
    unittest.main()
