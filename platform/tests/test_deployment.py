from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from aea_platform.policy import KafkaPolicy
from render_kafka_acls import command_for, render


class DeploymentAclTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
        cls.entries = render(cls.policy)

    def test_plan_grants_every_publisher_and_subscriber(self):
        for topic in self.policy.topics.values():
            self.assertIn({"principal": topic.publisher, "operation": "Write",
                           "topic": topic.name}, self.entries)
            for subscriber in topic.subscribers:
                self.assertIn({"principal": subscriber, "operation": "Read",
                               "topic": topic.name, "group": subscriber}, self.entries)
                self.assertIn({"principal": subscriber, "operation": "Write",
                               "topic": topic.dlq_topic(subscriber)}, self.entries)
                for tier in self.policy.defaults["retry_tiers"]:
                    self.assertIn({"principal": subscriber, "operation": "Write",
                                   "topic": topic.retry_topic(subscriber, tier["name"])},
                                  self.entries)

    def test_plan_is_least_privilege(self):
        base_topics = set(self.policy.topics)
        for entry in self.entries:
            # The only Write on a governed base topic belongs to its publisher.
            if entry["operation"] == "Write" and entry["topic"] in base_topics:
                self.assertEqual(self.policy.topics[entry["topic"]].publisher, entry["principal"])
            # Reads are always bound to the principal's own group, and only for
            # topics it actually subscribes to.
            if entry["operation"] == "Read":
                self.assertEqual(entry.get("group"), entry["principal"])
                self.assertIn(entry["principal"], self.policy.topics[entry["topic"]].subscribers)

    def test_command_rendering_is_group_bound_for_reads(self):
        read = command_for({"principal": "workspace", "operation": "Read",
                            "topic": "order.confirmed", "group": "workspace"}, "${BOOTSTRAP}")
        self.assertIn("--allow-principal User:workspace", read)
        self.assertIn("--operation Read", read)
        self.assertIn("--group workspace", read)
        write = command_for({"principal": "order", "operation": "Write",
                             "topic": "order.confirmed"}, "${BOOTSTRAP}")
        self.assertNotIn("--group", write)


if __name__ == "__main__":
    unittest.main()
