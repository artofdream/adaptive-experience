from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.adapters import KafkaFailureRouter
from aea_platform.consumer import ConsumedRecord, GovernedConsumer
from aea_platform.outbox import OutboxRecord, OutboxRelay
from aea_platform.policy import KafkaPolicy


class FakeOutbox:
    def __init__(self, records):
        self.records = records
        self.published = []
        self.retried = []

    def claim(self, worker, limit):
        return self.records[:limit]

    def mark_published(self, message_id, published_at):
        self.published.append(message_id)

    def release_for_retry(self, message_id, error_code, delay_seconds):
        self.retried.append((message_id, error_code, delay_seconds))


class FakePublisher:
    def __init__(self, fail=False):
        self.fail = fail
        self.messages = []

    def publish(self, topic, key, message):
        self.messages.append((topic, key, message["message_id"]))
        if self.fail:
            raise TimeoutError("not acknowledged")


class FakeTransaction:
    def __init__(self, version=1, prior=None):
        self.version = version
        self.prior = prior
        self.applied = []
        self.recorded = []

    def outcome(self, group, message_id):
        return self.prior

    def apply(self, group, message, handler):
        if message["context_version"] != self.version:
            return "stale"
        handler(message)
        self.applied.append(message["message_id"])
        return "applied"

    def record_outcome(self, group, message, outcome, failure_code=None):
        self.recorded.append((group, message["message_id"], outcome, failure_code))


class FakeOffsets:
    def __init__(self):
        self.committed = []

    def commit(self, record):
        self.committed.append(record.offset)


class FakeFailures:
    def __init__(self, outcome="retry"):
        self.outcome = outcome

    def route(self, group, record, error):
        return self.outcome


class FakePrivacy:
    def validate_delivery(self, subscriber, topic, envelope):
        return None


class FoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")

    def test_registry_matches_all_21_schemas(self):
        schema_dir = ROOT.parent / "docs" / "04-technical-architecture" / "schemas"
        schemas = {
            json.loads(path.read_text(encoding="utf-8"))["title"]
            for path in schema_dir.glob("*.json")
            if not path.name.startswith("message-envelope")
        }
        self.assertEqual(set(self.policy.topics), schemas)
        self.assertEqual(21, len(self.policy.topics))

    def test_registry_enforces_publisher_and_consumer(self):
        self.policy.require_publish("orchestration", "customer.message.submitted")
        self.policy.require_consume("workspace", "customer.message.submitted")
        with self.assertRaises(PermissionError):
            self.policy.require_publish("workspace", "customer.message.submitted")
        with self.assertRaises(PermissionError):
            self.policy.require_consume("payment", "customer.message.submitted")

    def test_every_topic_has_distinct_authorized_parties_and_key(self):
        schema_dir = ROOT.parent / "docs" / "04-technical-architecture" / "schemas"
        for topic in self.policy.topics.values():
            self.assertTrue(topic.owner)
            self.assertTrue(topic.publisher)
            self.assertTrue(topic.key)
            self.assertRegex(topic.schema_version, r"^[0-9]+\.[0-9]+\.[0-9]+$")
            self.assertTrue((schema_dir / topic.schema_filename).is_file())
            self.assertEqual(len(topic.subscribers), len(set(topic.subscribers)))
            self.assertTrue(topic.subscribers)

    def test_registry_governance_matches_documented_contracts(self):
        contracts = (ROOT.parent / "docs" / "04-technical-architecture" / "topic-contracts.md").read_text(encoding="utf-8")
        rows = re.findall(
            r"^\| ([a-z0-9_.]+) \| ([0-9.]+) \| ([^|]+) \| ([^|]+) \|",
            contracts.split("## Future topics", 1)[0], re.MULTILINE,
        )
        documented = {
            name: (version, owner.strip().lower().replace(" ", "-"),
                   tuple(item.strip().lower().replace(" ", "-") for item in subscribers.split(",")))
            for name, version, owner, subscribers in rows
        }
        executable = {
            topic.name: (topic.schema_version, topic.owner, topic.subscribers)
            for topic in self.policy.topics.values()
        }
        self.assertEqual(documented, executable)

    def test_retry_and_dlq_names_are_consumer_specific(self):
        topic = self.policy.topics["customer.message.submitted"]
        self.assertEqual("customer.message.submitted.retry.workspace.1m", topic.retry_topic("workspace", "1m"))
        self.assertEqual("customer.message.submitted.dlq.workspace", topic.dlq_topic("workspace"))

    def test_relay_marks_only_acknowledged_publication(self):
        record = OutboxRecord("id-1", "topic", "session", {"message_id": "id-1"}, 1)
        store = FakeOutbox([record])
        relay = OutboxRelay(store, FakePublisher(), "relay-1")
        self.assertEqual((1, 0), relay.run_once())
        self.assertEqual(["id-1"], store.published)

    def test_relay_keeps_identity_and_retries_unacknowledged_publication(self):
        record = OutboxRecord("stable-id", "topic", "session", {"message_id": "stable-id"}, 2)
        store = FakeOutbox([record])
        publisher = FakePublisher(fail=True)
        relay = OutboxRelay(store, publisher, "relay-1")
        self.assertEqual((0, 1), relay.run_once())
        self.assertEqual("stable-id", publisher.messages[0][2])
        self.assertEqual([], store.published)
        self.assertEqual("stable-id", store.retried[0][0])

    def test_duplicate_commits_offset_without_reapplying(self):
        offsets = FakeOffsets()
        consumer = GovernedConsumer("workspace", FakeTransaction(prior="applied"), offsets, FakeFailures(), FakePrivacy())
        record = ConsumedRecord("topic", 0, 9, {"message_id":"id", "session_id":"s", "context_version":1})
        self.assertEqual("duplicate", consumer.process(record, lambda _: self.fail("must not apply")))
        self.assertEqual([9], offsets.committed)

    def test_stale_context_is_rejected_then_offset_commits(self):
        offsets = FakeOffsets()
        consumer = GovernedConsumer("workspace", FakeTransaction(version=3), offsets, FakeFailures(), FakePrivacy())
        record = ConsumedRecord("topic", 0, 10, {"message_id":"id", "session_id":"s", "context_version":2})
        self.assertEqual("stale", consumer.process(record, lambda _: self.fail("must not apply")))
        self.assertEqual([10], offsets.committed)

    def test_future_context_is_rejected_then_offset_commits(self):
        offsets = FakeOffsets()
        transaction = FakeTransaction(version=3)
        consumer = GovernedConsumer("workspace", transaction, offsets, FakeFailures(), FakePrivacy())
        record = ConsumedRecord("topic", 0, 11, {"message_id":"id", "session_id":"s", "context_version":4})
        self.assertEqual("stale", consumer.process(record, lambda _: self.fail("must not apply")))
        self.assertEqual([], transaction.applied)
        self.assertEqual([11], offsets.committed)

    def test_missing_session_is_rejected_then_offset_commits(self):
        offsets = FakeOffsets()
        transaction = FakeTransaction(version=None)
        consumer = GovernedConsumer("workspace", transaction, offsets, FakeFailures(), FakePrivacy())
        record = ConsumedRecord("topic", 0, 12, {"message_id":"id", "session_id":"missing", "context_version":0})
        self.assertEqual("stale", consumer.process(record, lambda _: self.fail("must not apply")))
        self.assertEqual([], transaction.applied)
        self.assertEqual([12], offsets.committed)

    def test_handler_failure_commits_only_after_durable_retry(self):
        offsets = FakeOffsets()
        transaction = FakeTransaction()
        consumer = GovernedConsumer("workspace", transaction, offsets, FakeFailures("retry"), FakePrivacy())
        record = ConsumedRecord("topic", 0, 11, {"message_id":"id", "session_id":"s", "context_version":1})
        self.assertEqual("retry", consumer.process(record, lambda _: (_ for _ in ()).throw(ValueError())))
        self.assertEqual([("workspace", "id", "retry", "ValueError")], transaction.recorded)
        self.assertEqual([11], offsets.committed)

    def test_offset_does_not_commit_when_retry_transfer_fails(self):
        offsets = FakeOffsets()

        class FailedRouter:
            def route(self, group, record, error):
                raise TimeoutError("retry topic unavailable")

        consumer = GovernedConsumer("workspace", FakeTransaction(), offsets, FailedRouter(), FakePrivacy())
        record = ConsumedRecord("topic", 0, 12, {"message_id":"id", "session_id":"s", "context_version":1})
        with self.assertRaises(TimeoutError):
            consumer.process(record, lambda _: (_ for _ in ()).throw(RuntimeError()))
        self.assertEqual([], offsets.committed)

    def test_failure_router_preserves_identity_and_canonical_topic(self):
        publisher = FakePublisher()
        router = KafkaFailureRouter(self.policy, publisher, max_attempts=2)
        message = {"message_id":"stable-id", "topic":"customer.message.submitted",
                   "session_id":"session-1", "context_version":1, "outcome": {}}
        record = ConsumedRecord("customer.message.submitted", 0, 1, message)
        self.assertEqual("retry", router.route("workspace", record, TimeoutError()))
        destination, key, message_id = publisher.messages[0]
        self.assertEqual("customer.message.submitted.retry.workspace.1m", destination)
        self.assertEqual("session-1", key)
        self.assertEqual("stable-id", message_id)
        self.assertEqual("customer.message.submitted", message["topic"])

    def test_nonrecoverable_failure_routes_to_consumer_dlq(self):
        publisher = FakePublisher()
        router = KafkaFailureRouter(self.policy, publisher)
        message = {"message_id":"stable-id", "topic":"customer.message.submitted",
                   "session_id":"session-1", "context_version":1, "outcome": {}}
        record = ConsumedRecord("customer.message.submitted", 0, 1, message)
        self.assertEqual("dead_letter", router.route("workspace", record, ValueError()))
        self.assertEqual("customer.message.submitted.dlq.workspace", publisher.messages[0][0])


if __name__ == "__main__":
    unittest.main()
