from __future__ import annotations

import json
import re
import sys
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.adapters import KafkaFailureRouter
from aea_platform.conversation import (
    ConversationService,
    ConversationSessionNotFound,
    ConversationValidationError,
)
from aea_platform.intent import (
    IntentAnalysisService,
    IntentInterpretation,
    IntentValidationError,
    ReferenceIntentInterpreter,
    SharedUnderstandingService,
)
from aea_platform.inventory import (
    AvailabilitySnapshot,
    InventoryAvailabilityService,
    InventoryUnavailableError,
    InventoryValidationError,
)
from aea_platform.recommendation import (
    CatalogProduct,
    RecommendationService,
    RecommendationValidationError,
)
from aea_platform.consumer import ConsumedRecord, GovernedConsumer
from aea_platform.outbox import OutboxRecord, OutboxRelay
from aea_platform.policy import KafkaPolicy
from aea_platform.state import StatePatch, merge_state


class FakeStateStore:
    def __init__(self, current=None):
        self.current = current
        self.applied = []

    def load(self, session_id):
        return self.current

    def apply_patch(self, session_id, expected, schema_version, patch, messages):
        self.applied.append((session_id, expected, schema_version, patch, messages))
        return expected + 1


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


class FakeInventoryStore:
    def __init__(self, availability=None):
        self.availability = availability or {}
        self.recorded = []
        self.validations = []

    def record_snapshot(self, *values):
        self.recorded.append(values)
        return "applied"

    def validate_and_enqueue(self, **values):
        self.validations.append(values)
        return {product_id: self.availability.get(
            product_id, {"status": "unknown", "freshness": "missing"})
                for product_id in values["product_ids"]}


class FakeRecommendationStore:
    def __init__(self):
        self.ready = []

    def enqueue_ready(self, **values):
        self.ready.append(values)


class FoundationTests(unittest.TestCase):
    def test_inventory_records_validated_snapshot_and_deduplicates_request(self):
        now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        store = FakeInventoryStore({"rose-1": {"status": "available", "freshness": "current"}})
        service = InventoryAvailabilityService(store, now=lambda: now)
        self.assertEqual("applied", service.record(AvailabilitySnapshot("rose-1", 4, 7, now)))
        result = service.validate(session_id="session", product_ids=["rose-1", "rose-1"],
            observed_context_version=3, correlation_id="correlation", subject_reference="subject")
        self.assertEqual(("rose-1",), store.validations[0]["product_ids"])
        self.assertEqual("available", result.availability["rose-1"]["status"])

    def test_inventory_selection_fails_closed_for_unknown_or_stale_product(self):
        service = InventoryAvailabilityService(FakeInventoryStore())
        with self.assertRaises(InventoryUnavailableError):
            service.validate(session_id="session", product_ids=["missing"],
                observed_context_version=0, correlation_id="correlation",
                subject_reference="subject", purpose="selection")

    def test_inventory_rejects_invalid_authority_inputs(self):
        service = InventoryAvailabilityService(FakeInventoryStore())
        now = datetime(2026, 8, 12, tzinfo=timezone.utc)
        for snapshot in (AvailabilitySnapshot("", 1, 1, now),
                         AvailabilitySnapshot("rose", -1, 1, now),
                         AvailabilitySnapshot("rose", 1, -1, now)):
            with self.assertRaises(InventoryValidationError):
                service.record(snapshot)

    def test_recommendations_rank_available_products_against_intent_and_budget(self):
        now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        inventory = FakeInventoryStore({
            "pink-flower-vase": {"status": "available", "freshness": "current"},
            "lilac-bouquet": {"status": "available", "freshness": "current"},
            "classic-rose-dozen": {"status": "available", "freshness": "current"},
            "budget-mixed-bunch": {"status": "unavailable", "freshness": "current"},
            "premium-orchid": {"status": "available", "freshness": "current"},
        })
        inventory_service = InventoryAvailabilityService(inventory, now=lambda: now)
        ready_store = FakeRecommendationStore()
        service = RecommendationService(
            ready_store, inventory_service, now=lambda: now,
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000026"),
        )
        result = service.generate(
            session_id="session",
            observed_context_version=2,
            correlation_id="rec-correlation",
            subject_reference="subject",
            intent={"occasion": "birthday", "budget": 100, "flower_preference": "roses"},
        )
        self.assertEqual(["classic-rose-dozen", "lilac-bouquet"], result.eligible_product_ids)
        self.assertEqual("classic-rose-dozen", result.ranking[0]["product_id"])
        self.assertNotIn("premium-orchid", result.eligible_product_ids)
        self.assertNotIn("budget-mixed-bunch", result.eligible_product_ids)
        self.assertEqual(
            ["classic-rose-dozen", "budget-mixed-bunch", "lilac-bouquet"],
            list(inventory.validations[0]["product_ids"]),
        )
        self.assertEqual(
            ["classic-rose-dozen", "lilac-bouquet"],
            ready_store.ready[0]["eligible_product_ids"],
        )

    def test_recommendations_reject_invalid_intent_and_empty_when_none_available(self):
        inventory = InventoryAvailabilityService(FakeInventoryStore())
        service = RecommendationService(FakeRecommendationStore(), inventory)
        with self.assertRaises(RecommendationValidationError):
            service.generate(
                session_id="session", observed_context_version=0,
                correlation_id="c", subject_reference="s", intent={"budget": -1},
            )
        now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        empty = RecommendationService(
            FakeRecommendationStore(),
            InventoryAvailabilityService(FakeInventoryStore(), now=lambda: now),
            catalog=(CatalogProduct("x", 10.0, frozenset({"birthday"}), frozenset(), frozenset()),),
            now=lambda: now,
        )
        result = empty.generate(
            session_id="session", observed_context_version=0,
            correlation_id="c", subject_reference="s",
            intent={"occasion": "birthday", "budget": 50},
        )
        self.assertEqual([], result.eligible_product_ids)

    def test_reference_interpreter_extracts_supported_intent_and_prompts_for_gaps(self):
        result = ReferenceIntentInterpreter().interpret(
            "Bright roses for Mum's birthday tomorrow, budget €75", {}
        )
        self.assertEqual({
            "occasion": "birthday", "budget": 75.0, "recipient": "mother",
            "style": "bright", "flower_preference": "roses", "timing": "tomorrow",
        }, result.facets)
        self.assertEqual((), result.suggestions)

        partial = ReferenceIntentInterpreter().interpret("Something for my friend", {})
        self.assertEqual({"recipient": "friend"}, partial.facets)
        self.assertEqual(3, len(partial.suggestions))
        self.assertIn("occasion", partial.suggestions[0].lower())

    def test_intent_analysis_updates_only_supported_facets_and_publishes_event(self):
        store = FakeStateStore({
            "state_schema_version": 1, "context_version": 4,
            "state": {"shared_understanding": {"occasion": "birthday", "budget": 50},
                      "decisions": {"product": {"completed": True}}},
        })
        class Interpreter:
            def interpret(self, message_text, current_intent):
                self.current = current_intent
                return IntentInterpretation({"budget": 75, "style": "bright"},
                                            ("Any flower preferences?",))
        interpreter = Interpreter()
        service = IntentAnalysisService(
            store, interpreter,
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000021"),
        )
        result = service.analyze(
            session_id="session", message_text="brighter, up to 75", observed_context_version=4,
            correlation_id="correlation", subject_reference="subject",
        )
        self.assertEqual({"occasion": "birthday", "budget": 75, "style": "bright"},
                         result.structured_intent)
        _, expected, _, patch, messages = store.applied[0]
        self.assertEqual(4, expected)
        self.assertEqual({"budget": 75, "style": "bright"},
                         patch.values["shared_understanding"])
        self.assertEqual(["Any flower preferences?"],
                         patch.values["thought_completion"]["suggestions"])
        self.assertEqual({"structured_intent": result.structured_intent},
                         messages[0]["envelope"]["payload"])

    def test_intent_analysis_rejects_interpreter_scope_and_invalid_values(self):
        current = {"state_schema_version": 1, "context_version": 0, "state": {}}
        for interpretation in (
            IntentInterpretation({"product_id": "rose-1"}),
            IntentInterpretation({"budget": -1}),
            IntentInterpretation({"style": "x" * 121}),
            IntentInterpretation({}, ("x" * 161,)),
        ):
            class Interpreter:
                def interpret(self, *_): return interpretation
            store = FakeStateStore(current)
            with self.assertRaises(IntentValidationError):
                IntentAnalysisService(store, Interpreter()).analyze(
                    session_id="session", message_text="flowers", observed_context_version=0,
                    correlation_id="correlation", subject_reference="subject",
                )
            self.assertEqual([], store.applied)

    def test_unrecognized_input_updates_prompts_without_publishing_empty_intent(self):
        store = FakeStateStore({"state_schema_version": 1, "context_version": 0, "state": {}})
        result = IntentAnalysisService(store, ReferenceIntentInterpreter()).analyze(
            session_id="session", message_text="I need some help",
            observed_context_version=0, correlation_id="correlation",
            subject_reference="subject",
        )
        self.assertEqual("", result.message_id)
        self.assertEqual({}, result.structured_intent)
        self.assertEqual([], store.applied[0][4])
        self.assertEqual(("thought_completion.suggestions",),
                         store.applied[0][3].changed_facets)

    def test_corrupted_existing_intent_fails_closed_before_interpretation(self):
        store = FakeStateStore({
            "state_schema_version": 1, "context_version": 0,
            "state": {"shared_understanding": {"product_id": "not-authorized"}},
        })
        with self.assertRaises(IntentValidationError):
            IntentAnalysisService(store, ReferenceIntentInterpreter()).analyze(
                session_id="session", message_text="birthday", observed_context_version=0,
                correlation_id="correlation", subject_reference="subject",
            )
        self.assertEqual([], store.applied)

    def test_shared_understanding_can_be_reviewed_and_partially_corrected(self):
        store = FakeStateStore({
            "state_schema_version": 1, "context_version": 7,
            "state": {
                "shared_understanding": {"occasion": "birthday", "budget": 50},
                "thought_completion": {"suggestions": ["Who are the flowers for?"]},
                "decisions": {"product": {"id": "kept", "completed": True}},
            },
        })
        service = SharedUnderstandingService(
            store,
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000040"),
        )
        projection = service.projection(session_id="session")
        self.assertEqual(7, projection.context_version)
        self.assertEqual({"occasion": "birthday", "budget": 50},
                         projection.structured_intent)
        self.assertEqual(("Who are the flowers for?",), projection.suggestions)

        result = service.correct(
            session_id="session", corrections={"budget": 75, "recipient": "mother"},
            observed_context_version=7, correlation_id="correction",
            subject_reference="subject",
        )
        self.assertEqual(8, result.context_version)
        self.assertEqual({"occasion": "birthday", "budget": 75, "recipient": "mother"},
                         result.structured_intent)
        _, expected, _, patch, messages = store.applied[0]
        self.assertEqual(7, expected)
        self.assertEqual({"budget": 75, "recipient": "mother"},
                         patch.values["shared_understanding"])
        self.assertNotIn("decisions", patch.values)
        self.assertEqual(
            ("shared_understanding.budget", "shared_understanding.recipient",
             "thought_completion.suggestions"), patch.changed_facets,
        )
        self.assertEqual(result.structured_intent,
                         messages[0]["envelope"]["payload"]["structured_intent"])

    def test_shared_understanding_correction_rejects_invalid_or_unchanged_input(self):
        current = {
            "state_schema_version": 1, "context_version": 2,
            "state": {"shared_understanding": {"occasion": "birthday"}},
        }
        for corrections in ({}, {"occasion": "birthday"}, {"product_id": "rose-1"},
                            {"budget": 0}):
            store = FakeStateStore(current)
            with self.assertRaises(IntentValidationError):
                SharedUnderstandingService(store).correct(
                    session_id="session", corrections=corrections,
                    observed_context_version=2, correlation_id="correction",
                    subject_reference="subject",
                )
            self.assertEqual([], store.applied)

    def test_conversation_submission_persists_and_publishes_one_governed_message(self):
        store = FakeStateStore({
            "state_schema_version": 1,
            "context_version": 3,
            "state": {"conversation": {"messages": [{"message_id": "prior"}]},
                      "decisions": {"product": {"completed": True}}},
        })
        fixed_id = uuid.UUID("00000000-0000-0000-0000-000000000020")
        service = ConversationService(
            store,
            now=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc),
            new_id=lambda: fixed_id,
        )
        result = service.submit(
            session_id="session-1", subject_reference="subject-1",
            message_text="  flowers for Mum  ", observed_context_version=3,
            correlation_id="correlation-1",
        )
        self.assertEqual(4, result.context_version)
        _, expected, _, patch, outbox = store.applied[0]
        self.assertEqual(3, expected)
        self.assertEqual(("conversation.messages",), patch.changed_facets)
        self.assertEqual("prior", patch.values["conversation"]["messages"][0]["message_id"])
        self.assertEqual("flowers for Mum", patch.values["conversation"]["messages"][1]["text"])
        envelope = outbox[0]["envelope"]
        self.assertEqual("customer.message.submitted", envelope["topic"])
        self.assertEqual({"message_text": "flowers for Mum"}, envelope["payload"])
        self.assertEqual("subject-1", envelope["security_context"]["subject_reference"])

    def test_conversation_validation_and_missing_session_fail_closed(self):
        service = ConversationService(FakeStateStore())
        with self.assertRaises(ConversationSessionNotFound):
            service.submit(session_id="missing", subject_reference="subject",
                           message_text="roses", observed_context_version=0,
                           correlation_id="correlation")
        store = FakeStateStore({"state_schema_version": 1, "context_version": 0, "state": {}})
        service = ConversationService(store)
        for value in ("", " ", "x" * 2001, "bad\x00text"):
            with self.assertRaises(ConversationValidationError):
                service.submit(session_id="session", subject_reference="subject",
                               message_text=value, observed_context_version=0,
                               correlation_id="correlation")
        self.assertEqual([], store.applied)

    def test_conversation_projection_is_bounded_and_least_data(self):
        messages = [{"message_id": str(index), "role": "customer", "text": str(index),
                     "status": "submitted", "submitted_at": "now", "secret": "omit"}
                    for index in range(60)]
        service = ConversationService(FakeStateStore({
            "state_schema_version": 1, "context_version": 60,
            "state": {"conversation": {"messages": messages}},
        }))
        projection = service.projection(session_id="session")
        self.assertEqual(50, len(projection["messages"]))
        self.assertEqual("10", projection["messages"][0]["message_id"])
        self.assertNotIn("secret", projection["messages"][0])

    @classmethod
    def setUpClass(cls):
        cls.policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")

    def test_registry_matches_all_governed_schemas(self):
        schema_dir = ROOT.parent / "docs" / "04-technical-architecture" / "schemas"
        schemas = {
            json.loads(path.read_text(encoding="utf-8"))["title"]
            for path in schema_dir.glob("*.json")
            if not path.name.startswith("message-envelope")
        }
        self.assertEqual(set(self.policy.topics), schemas)
        self.assertEqual(24, len(self.policy.topics))
        self.assertEqual("support-service",
                         self.policy.topics["support.escalation.requested"].publisher)
        self.assertEqual("support-service",
                         self.policy.topics["support.situation.answered"].publisher)

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

    def test_deep_patch_preserves_completed_and_unaffected_state(self):
        current = {
            "shared_understanding": {"occasion": "birthday", "budget": 60},
            "decisions": {"product": {"id": "rose-1", "completed": True}},
            "tiles": {"delivery": {"status": "complete"}},
        }
        result = merge_state(current, {"shared_understanding": {"budget": 75}})
        self.assertEqual("birthday", result["shared_understanding"]["occasion"])
        self.assertEqual(75, result["shared_understanding"]["budget"])
        self.assertEqual(current["decisions"], result["decisions"])
        self.assertEqual(current["tiles"], result["tiles"])
        self.assertEqual(60, current["shared_understanding"]["budget"])

    def test_state_patch_requires_explicit_changed_facets(self):
        with self.assertRaises(ValueError):
            StatePatch.create({"shared_understanding": {"budget": 75}}, [])
        with self.assertRaises(ValueError):
            StatePatch.create(
                {"shared_understanding": {"budget": 75}},
                ["shared_understanding.occasion"],
            )
        patch = StatePatch.create(
            {"shared_understanding": {"budget": 75}},
            ["shared_understanding.budget", "shared_understanding.budget"],
        )
        self.assertEqual(("shared_understanding.budget",), patch.changed_facets)


if __name__ == "__main__":
    unittest.main()
