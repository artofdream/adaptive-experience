from __future__ import annotations

import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aea_platform.policy import KafkaPolicy

ROOT = Path(__file__).resolve().parents[1]


def render(policy: KafkaPolicy) -> list[dict]:
    """Return the least-privilege ACL plan for the governed topics.

    Each publisher may Write only its own topics; each subscriber may Read only the
    topics it consumes (bound to its own group) and Write only its own retry/DLQ
    topics (so the failure router can durably transfer failures). No other grant is
    produced.
    """
    entries: list[dict] = []
    for topic in policy.topics.values():
        entries.append({"principal": topic.publisher, "operation": "Write",
                        "topic": topic.name})
        for subscriber in topic.subscribers:
            entries.append({"principal": subscriber, "operation": "Read",
                            "topic": topic.name, "group": subscriber})
            for physical in [topic.dlq_topic(subscriber),
                             *[topic.retry_topic(subscriber, tier["name"])
                               for tier in policy.defaults["retry_tiers"]]]:
                entries.append({"principal": subscriber, "operation": "Write",
                                "topic": physical})
    return entries


def command_for(entry: dict, bootstrap: str) -> str:
    parts = ["kafka-acls.sh", "--bootstrap-server", bootstrap, "--add", "--allow-principal",
             f"User:{entry['principal']}", "--operation", entry["operation"],
             "--topic", entry["topic"]]
    if "group" in entry:
        parts += ["--group", entry["group"]]
    return " ".join(shlex.quote(part) for part in parts)


def main() -> None:
    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    bootstrap = "${AEA_KAFKA_BOOTSTRAP}"
    for entry in render(policy):
        print(command_for(entry, bootstrap))


if __name__ == "__main__":
    main()
