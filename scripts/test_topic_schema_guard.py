#!/usr/bin/env python3
"""Regression tests for the semantic MVP topic schema guard (#129)."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import check_topic_schemas as guard


class TopicSchemaGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.schemas = Path(self.temporary.name) / "schemas"
        shutil.copytree(guard.SCHEMAS, self.schemas)
        self.contract_topics = guard.mvp_topics()
        self.manifest = guard.manifest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def validate(self) -> list[str]:
        return guard.validate_inventory(
            self.contract_topics, self.schemas, self.manifest
        )

    def mutate(self, name: str, change) -> None:
        path = self.schemas / name
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def test_repository_contracts_pass(self) -> None:
        self.assertEqual([], self.validate())

    def test_missing_active_topic_fails(self) -> None:
        (self.schemas / "customer.message.submitted.v1.0.0.json").unlink()
        self.assertTrue(any("missing active schema" in error for error in self.validate()))

    def test_unknown_topic_and_identity_drift_fail(self) -> None:
        source = self.schemas / "customer.message.submitted.v1.0.0.json"
        unknown = self.schemas / "unknown.topic.v1.0.0.json"
        shutil.copyfile(source, unknown)
        self.mutate(
            "customer.message.submitted.v1.0.0.json",
            lambda data: data.update({"title": "wrong.topic"}),
        )
        errors = self.validate()
        self.assertTrue(any("not in the governed topic registry" in error for error in errors))
        self.assertTrue(any("title must be" in error for error in errors))

    def test_minimum_payload_drift_fails(self) -> None:
        self.mutate(
            "payment.authorization.requested.v1.0.0.json",
            lambda data: data["required"].remove("payment_token"),
        )
        self.assertTrue(
            any("required fields differ" in error for error in self.validate())
        )

    def test_envelope_inventory_drift_fails(self) -> None:
        def remove_context(data: dict) -> None:
            data["properties"].pop("context_version")
            data["required"].remove("context_version")

        self.mutate(guard.ENVELOPE_NAME, remove_context)
        self.assertTrue(
            any("ADR-008 envelope inventory" in error for error in self.validate())
        )

    def test_same_major_breaking_change_fails(self) -> None:
        old = {
            "properties": {"message_text": {"type": "string"}},
            "required": ["message_text"],
        }
        new = {
            "properties": {"message_text": {"type": "integer"}},
            "required": ["message_text", "new_field"],
        }
        errors = guard.compatibility_errors(
            "customer.message.submitted", [("1.0.0", old), ("1.1.0", new)]
        )
        self.assertTrue(any("changes properties" in error for error in errors))
        self.assertTrue(any("adds required fields" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
