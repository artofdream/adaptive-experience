from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.policy import KafkaPolicy
from aea_platform.privacy import (PayloadPrivacyGuard, PrivacyEnforcingPublisher,
                                  SourceGuardedPublisher)


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
    def test_intent_contract_rejects_unsupported_nested_facets(self):
        message = envelope(
            "experience.intent.updated",
            {"structured_intent": {"product_id": "rose-1"}},
        )
        with self.assertRaises(ValueError):
            self.guard.validate_publication("orchestration", "experience.intent.updated", message)

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
        with self.assertRaisesRegex(ValueError, "unauthorized fields"):
            self.guard.validate_publication("orchestration", message["topic"], message)

    def test_source_and_security_context_are_governed(self):
        wrong_source = envelope()
        wrong_source["source"] = "workspace"
        with self.assertRaisesRegex(ValueError, "governed publisher"):
            self.guard.validate_publication("orchestration", wrong_source["topic"], wrong_source)
        unauthorized_context = envelope()
        unauthorized_context["security_context"]["raw_claims"] = {"role": "admin"}
        with self.assertRaisesRegex(ValueError, "unauthorized fields"):
            self.guard.validate_publication("orchestration", unauthorized_context["topic"], unauthorized_context)

    def test_checkout_events_reject_raw_card_data(self):
        # NFR-013: the M5 checkout events cannot carry card data at the broker.
        requested = envelope("order.checkout.requested",
                             {"draft_order_id": "d1", "total": 82.0, "card_number": "4111111111111111"})
        with self.assertRaises(ValueError):
            self.guard.validate_publication("orchestration", "order.checkout.requested", requested)
        confirmed = envelope("order.confirmed",
                            {"order_id": "o1", "confirmation_state": "confirmed", "cvv": "123"})
        confirmed["source"] = "order"
        with self.assertRaises(ValueError):
            self.guard.validate_publication("order", "order.confirmed", confirmed)

    def test_source_guarded_relay_publisher_is_fail_closed(self):
        target = RecordingPublisher()
        relay = SourceGuardedPublisher(self.guard, target)
        # A clean, correctly-sourced event reaches the broker.
        message = envelope()
        relay.publish(message["topic"], "draft-1", message)
        self.assertEqual(1, len(target.messages))
        # A poisoned payload never reaches the broker.
        poisoned = envelope()
        poisoned["payload"]["card_number"] = "4111111111111111"
        with self.assertRaises(ValueError):
            relay.publish(poisoned["topic"], "draft-1", poisoned)
        # A message whose source is not the topic's governed publisher is rejected.
        wrong_source = envelope()
        wrong_source["source"] = "workspace"
        with self.assertRaises(PermissionError):
            relay.publish(wrong_source["topic"], "draft-1", wrong_source)
        self.assertEqual(1, len(target.messages))

    def test_valid_escalation_command_is_authorized(self):
        message = envelope(
            "support.escalation.requested",
            {"escalation_reason": "unresolved_request", "context_reference": "session-1"},
        )
        message["source"] = "support-service"
        message["message_type"] = "command"
        self.guard.validate_publication(
            "support-service", "support.escalation.requested", message)

    def test_valid_inventory_forecast_is_authorized(self):
        message = envelope(
            "inventory.forecast.ready",
            {"product_ids": ["classic-rose-dozen"],
             "recommendations": [{
                 "product_id": "classic-rose-dozen",
                 "trend": "declining",
                 "recommendation": "Plan a replenishment.",
                 "fact_references": ["inventory:classic-rose-dozen:v1"],
             }]},
        )
        message["source"] = "inventory"
        self.guard.validate_publication("inventory", "inventory.forecast.ready", message)

    def test_valid_situation_answer_is_authorized(self):
        message = envelope(
            "support.situation.answered",
            {"answer": "Your order is currently preparing.",
             "situation_kind": "order_status",
             "fact_references": ["session:order"]},
        )
        message["source"] = "support-service"
        self.guard.validate_publication(
            "support-service", "support.situation.answered", message)

    def test_valid_checkout_events_are_authorized(self):
        requested = envelope("order.checkout.requested", {"draft_order_id": "d1", "total": 82.0})
        self.guard.validate_publication("orchestration", "order.checkout.requested", requested)
        confirmed = envelope("order.confirmed", {"order_id": "o1", "confirmation_state": "confirmed"})
        confirmed["source"] = "order"
        self.guard.validate_publication("order", "order.confirmed", confirmed)

    def test_guard_is_fail_closed_for_every_governed_topic(self):
        # NFR-017: no governed topic can carry raw payment/PII at publish or delivery.
        for topic_name, topic in self.guard.policy.topics.items():
            poisoned = envelope(topic_name, {"card_number": "4111111111111111"})
            poisoned["source"] = topic.publisher
            with self.assertRaises(ValueError):
                self.guard.validate_publication(topic.publisher, topic_name, poisoned)
            for subscriber in topic.subscribers:
                with self.assertRaises(ValueError):
                    self.guard.validate_delivery(subscriber, topic_name, poisoned)

    def test_forbidden_field_set_covers_payment_and_pii_families(self):
        forbidden = PayloadPrivacyGuard.RAW_SENSITIVE_FIELDS
        for field in ("card_number", "cvv", "cardholder_name", "recipient_name",
                      "recipient_address", "recipient_email", "email", "phone", "address",
                      "access_token", "refresh_token", "api_key", "authorization", "password"):
            self.assertIn(field, forbidden)

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
