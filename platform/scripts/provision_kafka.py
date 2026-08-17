from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aea_platform.kafka_config import kafka_security_config
from aea_platform.policy import KafkaPolicy


ROOT = Path(__file__).resolve().parents[1]


def min_insync_replicas(replication: int) -> int:
    """AWS Health requires MinISR = RF - 1 when RF >= 2. RF=1 keeps MinISR=1."""
    if replication < 1:
        raise ValueError("replication_factor must be >= 1")
    return max(1, replication - 1)


def replication_from_env(defaults: dict, environ: dict | None = None) -> int:
    env = os.environ if environ is None else environ
    override = env.get("AEA_KAFKA_REPLICATION_FACTOR")
    if override not in (None, ""):
        return int(override)
    profile = (env.get("AEA_KAFKA_REPLICATION_PROFILE") or "").strip().lower()
    if profile == "pilot":
        return int(defaults["pilot_replication_factor"])
    local = env.get("AEA_ENVIRONMENT", "local") != "production"
    key = "local_replication_factor" if local else "production_replication_factor"
    return int(defaults[key])


def admin_client_config(environ: dict | None = None) -> dict:
    env = os.environ if environ is None else environ
    conf = {"bootstrap.servers": env.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092")}
    conf.update(kafka_security_config(env))
    return conf


def _topic_replication(metadata_topic) -> int:
    partitions = list(metadata_topic.partitions.values())
    if not partitions:
        return 0
    return len(partitions[0].replicas)


def align_min_insync_replicas(admin, names: list[str]) -> None:
    from confluent_kafka.admin import (
        AlterConfigOpType,
        ConfigEntry,
        ConfigResource,
        RESOURCE_TOPIC,
    )

    if not names:
        print("provision_kafka: no topics to align")
        return
    metadata = admin.list_topics(timeout=15)
    resources = [ConfigResource(RESOURCE_TOPIC, name) for name in names]
    described = admin.describe_configs(resources)
    to_alter: list[ConfigResource] = []
    for resource, future in described.items():
        name = resource.name
        try:
            entries = future.result()
        except Exception as exc:
            print(f"topic {name} describe_configs failed: {exc}")
            continue
        current = entries["min.insync.replicas"].value
        md_topic = metadata.topics.get(name)
        rf = _topic_replication(md_topic) if md_topic is not None else 0
        desired = min_insync_replicas(rf) if rf else int(current)
        print(f"topic {name} replication_factor={rf} min.insync.replicas={current} desired={desired}")
        if rf >= 2 and str(current) != str(desired):
            to_alter.append(ConfigResource(
                RESOURCE_TOPIC,
                name,
                incremental_configs=[ConfigEntry(
                    "min.insync.replicas",
                    str(desired),
                    incremental_operation=AlterConfigOpType.SET,
                )],
            ))
    if not to_alter:
        print("provision_kafka: min.insync.replicas already aligned")
        return
    for resource, future in admin.incremental_alter_configs(to_alter).items():
        try:
            future.result()
            print(f"updated min.insync.replicas on {resource.name}")
        except Exception as exc:
            print(f"topic {resource.name} alter min.insync.replicas failed: {exc}")


def main() -> None:
    from confluent_kafka.admin import AdminClient, NewTopic

    policy = KafkaPolicy.load(ROOT / "config" / "kafka-policy.json")
    admin = AdminClient(admin_client_config())
    existing = set(admin.list_topics(timeout=10).topics)
    replication = replication_from_env(policy.defaults)
    min_isr = min_insync_replicas(replication)
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
            config={
                "retention.ms": str(retention),
                "max.message.bytes": str(policy.defaults["max_message_bytes"]),
                "cleanup.policy": "delete",
                "unclean.leader.election.enable": "false",
                "min.insync.replicas": str(min_isr),
            },
        ))
    if not topics:
        print("provision_kafka: all policy topics already present, nothing to create")
    else:
        for name, future in admin.create_topics(topics).items():
            future.result()
            print(f"created {name}")
    cluster_topics = sorted(
        name for name, meta in admin.list_topics(timeout=10).topics.items()
        if meta.error is None
    )
    align_min_insync_replicas(admin, cluster_topics)


if __name__ == "__main__":
    main()
