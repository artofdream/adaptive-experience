#!/usr/bin/env python3
"""Write MVP topic JSON Schemas from the reviewed payload manifest.

TOPICS is imported by check_topic_schemas.py so generation and validation use
one minimum-payload inventory (ADR-008 / #129).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "docs" / "04-technical-architecture" / "schemas"

TOPICS: list[tuple[str, str, dict, list[str]]] = [
    (
        "customer.message.submitted",
        "1.0.0",
        {"message_text": {"type": "string"}},
        ["message_text"],
    ),
    (
        "experience.intent.updated",
        "1.0.0",
        {"structured_intent": {
            "type": "object",
            "properties": {
                "occasion": {"type": "string", "minLength": 1, "maxLength": 120},
                "budget": {"type": "number", "minimum": 1, "maximum": 10000},
                "recipient": {"type": "string", "minLength": 1, "maxLength": 120},
                "style": {"type": "string", "minLength": 1, "maxLength": 120},
                "flower_preference": {"type": "string", "minLength": 1, "maxLength": 120},
                "timing": {"type": "string", "minLength": 1, "maxLength": 120},
            },
            "minProperties": 1,
            "additionalProperties": False,
        }},
        ["structured_intent"],
    ),
    (
        "product.recommendations.requested",
        "1.0.0",
        {"intent_reference": {"type": "string"}},
        ["intent_reference"],
    ),
    (
        "product.recommendations.ready",
        "1.0.0",
        {
            "eligible_product_ids": {"type": "array", "items": {"type": "string"}},
            "ranking": {"type": "array"},
        },
        ["eligible_product_ids"],
    ),
    (
        "product.selected",
        "1.0.0",
        {
            "product_id": {"type": "string"},
            "options": {
                "type": "object",
                "properties": {
                    "size": {"type": "string", "minLength": 1, "maxLength": 40},
                    "card_message": {"type": "string", "minLength": 1, "maxLength": 280},
                    "flower_type": {"type": "string", "minLength": 1, "maxLength": 40},
                    "colour": {"type": "string", "minLength": 1, "maxLength": 40},
                    "ribbon": {"type": "string", "minLength": 1, "maxLength": 40},
                },
                "additionalProperties": False,
            },
        },
        ["product_id"],
    ),
    (
        "product.customization.updated",
        "1.0.0",
        {"product_id": {"type": "string"}, "basic_options": {"type": "object"}},
        ["product_id"],
    ),
    (
        "inventory.availability.requested",
        "1.0.0",
        {
            "product_ids": {"type": "array", "items": {"type": "string"}},
            "delivery_date": {"type": "string"},
        },
        ["product_ids"],
    ),
    (
        "inventory.availability.validated",
        "1.0.0",
        {
            "product_ids": {"type": "array", "items": {"type": "string"}},
            "availability": {"type": "object"},
        },
        ["product_ids", "availability"],
    ),
    (
        "inventory.reservation.confirmed",
        "1.0.0",
        {
            "reservation_id": {"type": "string"},
            "product_ids": {"type": "array", "items": {"type": "string"}},
        },
        ["reservation_id", "product_ids"],
    ),
    (
        "inventory.forecast.ready",
        "1.0.0",
        {
            "product_ids": {"type": "array", "items": {"type": "string"}},
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"},
                        "trend": {
                            "type": "string",
                            "enum": [
                                "declining",
                                "stable",
                                "rising",
                                "depleted",
                                "insufficient",
                            ],
                        },
                        "recommendation": {"type": "string"},
                        "fact_references": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "product_id",
                        "trend",
                        "recommendation",
                        "fact_references",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        ["product_ids", "recommendations"],
    ),
    (
        "delivery.details.updated",
        "1.0.0",
        {
            "destination_reference": {"type": "string"},
            "timing": {"type": "object"},
        },
        ["destination_reference"],
    ),
    (
        "delivery.slots.ready",
        "1.0.0",
        {"eligible_slot_ids": {"type": "array", "items": {"type": "string"}}},
        ["eligible_slot_ids"],
    ),
    ("delivery.slot.selected", "1.0.0", {"slot_id": {"type": "string"}}, ["slot_id"]),
    (
        "order.summary.updated",
        "1.0.0",
        {"itemized_charges": {"type": "array"}, "total": {"type": "number"}},
        ["itemized_charges", "total"],
    ),
    (
        "order.checkout.requested",
        "1.0.0",
        {"draft_order_id": {"type": "string"}, "total": {"type": "number"}},
        ["draft_order_id", "total"],
    ),
    (
        "payment.authorization.requested",
        "1.0.0",
        {
            "draft_order_id": {"type": "string"},
            "amount": {"type": "number"},
            "payment_token": {"type": "string"},
        },
        ["draft_order_id", "amount", "payment_token"],
    ),
    (
        "payment.authorization.succeeded",
        "1.0.0",
        {
            "authorization_id": {"type": "string"},
            "draft_order_id": {"type": "string"},
        },
        ["authorization_id", "draft_order_id"],
    ),
    (
        "payment.authorization.failed",
        "1.0.0",
        {
            "draft_order_id": {"type": "string"},
            "recoverable_error": {"type": "object"},
        },
        ["draft_order_id", "recoverable_error"],
    ),
    (
        "order.confirmed",
        "1.0.0",
        {
            "order_id": {"type": "string"},
            "confirmation_state": {"type": "string"},
        },
        ["order_id", "confirmation_state"],
    ),
    (
        "order.status.updated",
        "1.0.0",
        {
            "order_id": {"type": "string"},
            "authoritative_status": {"type": "string"},
        },
        ["order_id", "authoritative_status"],
    ),
    (
        "support.faq.answered",
        "1.0.0",
        {
            "answer": {"type": "string"},
            "approved_source_references": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        ["answer"],
    ),
    (
        "support.escalation.requested",
        "1.0.0",
        {
            "escalation_reason": {
                "type": "string",
                "enum": [
                    "unresolved_request",
                    "order_issue",
                    "delivery_issue",
                    "product_question",
                ],
            },
            "context_reference": {"type": "string", "minLength": 1, "maxLength": 120},
        },
        ["escalation_reason", "context_reference"],
    ),
    (
        "support.situation.answered",
        "1.0.0",
        {
            "answer": {"type": "string"},
            "situation_kind": {
                "type": "string",
                "enum": ["order_status", "delivery", "availability"],
            },
            "fact_references": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        ["answer", "situation_kind", "fact_references"],
    ),
    (
        "workspace.state.updated",
        "1.0.0",
        {
            "affected_tiles": {"type": "array", "items": {"type": "string"}},
            "state_version": {"type": "integer"},
        },
        ["affected_tiles", "state_version"],
    ),
]


def main() -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    for topic, version, props, required in TOPICS:
        name = f"{topic}.v{version}.json"
        doc = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": (
                "https://gitlab.com/artof-group/adaptive-experience-architecture/"
                f"-/blob/main/docs/04-technical-architecture/schemas/{name}"
            ),
            "title": topic,
            "description": (
                f"Minimum payload contract for {topic} (NFR-015/017). "
                "Envelope fields live in the bus envelope, not this payload schema."
            ),
            "type": "object",
            "properties": props,
            "required": required,
            "additionalProperties": False,
        }
        path = SCHEMAS / name
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
