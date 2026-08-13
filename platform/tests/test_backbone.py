from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.consumer import GovernedConsumer, KafkaGovernedConsumerRunner


class FakeTransaction:
    def __init__(self, prior=None):
        self.prior = prior
        self.applied = []

    def outcome(self, group, message_id):
        return self.prior

    def apply(self, group, message, handler):
        handler(message)
        self.applied.append(message["message_id"])
        return "applied"

    def record_outcome(self, *args, **kwargs):
        pass


class FakeOffsets:
    def __init__(self):
        self.committed = []

    def commit(self, record):
        self.committed.append(record.offset)


class FakeFailures:
    def route(self, group, record, error):
        return "dead_letter"


class FakeGuard:
    def __init__(self):
        self.validated = []

    def validate_delivery(self, subscriber, topic, envelope):
        self.validated.append((subscriber, topic))


class FakeMessage:
    def __init__(self, envelope, offset=5):
        self._value = json.dumps(envelope).encode()
        self._offset = offset

    def error(self):
        return None

    def value(self):
        return self._value

    def topic(self):
        return "order.status.updated"

    def partition(self):
        return 0

    def offset(self):
        return self._offset


class FakeKafkaConsumer:
    def __init__(self, messages):
        self._messages = list(messages)

    def poll(self, timeout):
        return self._messages.pop(0) if self._messages else None


class ConsumerRunnerTests(unittest.TestCase):
    def _runner(self, messages, transaction=None, guard=None, offsets=None):
        governed = GovernedConsumer("workspace", transaction or FakeTransaction(),
                                    offsets or FakeOffsets(), FakeFailures(), guard or FakeGuard())
        return KafkaGovernedConsumerRunner(FakeKafkaConsumer(messages), governed), governed

    def test_runner_processes_guards_and_commits(self):
        guard, offsets = FakeGuard(), FakeOffsets()
        envelope = {"message_id": "m1", "session_id": "s", "context_version": 1}
        runner, _ = self._runner([FakeMessage(envelope, offset=7)], guard=guard, offsets=offsets)
        handled = []
        outcomes = runner.run_once(handled.append, timeout=0.0)
        self.assertEqual(["applied"], outcomes)
        self.assertEqual(["m1"], [item["message_id"] for item in handled])
        self.assertEqual([("workspace", "order.status.updated")], guard.validated)
        self.assertEqual([7], offsets.committed)

    def test_runner_idempotency_skips_reapplication(self):
        offsets = FakeOffsets()
        envelope = {"message_id": "m1", "session_id": "s", "context_version": 1}
        runner, _ = self._runner([FakeMessage(envelope)], transaction=FakeTransaction(prior="applied"),
                                 offsets=offsets)
        outcomes = runner.run_once(lambda _: self.fail("must not reapply"), timeout=0.0)
        self.assertEqual(["duplicate"], outcomes)
        self.assertEqual(1, len(offsets.committed))

    def test_runner_stops_on_empty_poll(self):
        runner, _ = self._runner([])
        self.assertEqual([], runner.run_once(lambda _: None, timeout=0.0))


if __name__ == "__main__":
    unittest.main()
