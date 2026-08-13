from __future__ import annotations

import os
import sys
from pathlib import Path

from confluent_kafka.admin import AdminClient, ConfigResource, NewTopic, RESOURCE_TOPIC

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aea_platform.policy import KafkaPolicy


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    admin = AdminClient({"bootstrap.servers": os.environ.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092")})
    existing = set(admin.list_topics(timeout=10).topics)
    local = os.environ.get("AEA_ENVIRONMENT", "local") != "production"
    replication = policy.defaults["local_replication_factor" if local else "production_replication_factor"]
    topics = []
    for name in policy.physical_topics():
        if name in existing:
            continue
        is_dlq = ".dlq." in name
        retention = policy.defaults["dlq_retention_ms"] if is_dlq else policy.defaults["retention_ms"]
        topics.append(NewTopic(
            name,
            num_partitions=policy.defaults["partitions"],
            replication_factor=replication,
            config={"retention.ms": str(retention), "max.message.bytes": str(policy.defaults["max_message_bytes"]),
                    "cleanup.policy": "delete", "unclean.leader.election.enable": "false"},
        ))
    if not topics:
        print("provision_kafka: all topics already present, nothing to create")
        return
    for name, future in admin.create_topics(topics).items():
        future.result()
        print(f"created {name}")


if __name__ == "__main__":
    main()

