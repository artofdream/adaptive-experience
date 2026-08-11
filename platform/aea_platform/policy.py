from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TopicPolicy:
    name: str
    owner: str
    publisher: str
    subscribers: tuple[str, ...]
    key: str
    schema_version: str

    @property
    def schema_filename(self) -> str:
        return f"{self.name}.v{self.schema_version}.json"

    def retry_topic(self, consumer_group: str, tier: str) -> str:
        self.require_subscriber(consumer_group)
        return f"{self.name}.retry.{consumer_group}.{tier}"

    def dlq_topic(self, consumer_group: str) -> str:
        self.require_subscriber(consumer_group)
        return f"{self.name}.dlq.{consumer_group}"

    def require_subscriber(self, consumer_group: str) -> None:
        if consumer_group not in self.subscribers:
            raise PermissionError(f"{consumer_group} cannot consume {self.name}")


class KafkaPolicy:
    def __init__(self, raw: dict):
        self.defaults = raw["defaults"]
        self.topics = {
            item["name"]: TopicPolicy(
                item["name"], item["owner"], item["publisher"],
                tuple(item["subscribers"]), item["key"], item["schema_version"]
            )
            for item in raw["topics"]
        }
        if len(self.topics) != len(raw["topics"]):
            raise ValueError("duplicate canonical topic")

    @classmethod
    def load(cls, path: Path) -> "KafkaPolicy":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def require_publish(self, principal: str, topic: str) -> TopicPolicy:
        policy = self.topics[topic]
        if principal != policy.publisher:
            raise PermissionError(f"{principal} cannot publish {topic}")
        return policy

    def require_consume(self, consumer_group: str, topic: str) -> TopicPolicy:
        policy = self.topics[topic]
        policy.require_subscriber(consumer_group)
        return policy

    def physical_topics(self) -> list[str]:
        names: list[str] = []
        tiers = [tier["name"] for tier in self.defaults["retry_tiers"]]
        for policy in self.topics.values():
            names.append(policy.name)
            for subscriber in policy.subscribers:
                names.extend(policy.retry_topic(subscriber, tier) for tier in tiers)
                names.append(policy.dlq_topic(subscriber))
        return names
