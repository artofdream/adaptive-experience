from __future__ import annotations

import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aea_platform.policy import KafkaPolicy


ROOT = Path(__file__).resolve().parents[1]


def command(*parts: str) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def main() -> None:
    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    bootstrap = "${AEA_KAFKA_BOOTSTRAP}"
    for topic in policy.topics.values():
        print(command("kafka-acls.sh", "--bootstrap-server", bootstrap, "--add", "--allow-principal",
                      f"User:{topic.publisher}", "--operation", "Write", "--topic", topic.name))
        for subscriber in topic.subscribers:
            print(command("kafka-acls.sh", "--bootstrap-server", bootstrap, "--add", "--allow-principal",
                          f"User:{subscriber}", "--operation", "Read", "--topic", topic.name,
                          "--group", subscriber))
            for physical in [topic.dlq_topic(subscriber), *[
                topic.retry_topic(subscriber, tier["name"]) for tier in policy.defaults["retry_tiers"]
            ]]:
                print(command("kafka-acls.sh", "--bootstrap-server", bootstrap, "--add", "--allow-principal",
                              f"User:{subscriber}", "--operation", "Write", "--topic", physical))


if __name__ == "__main__":
    main()
