from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass(frozen=True)
class ConsumedRecord:
    topic: str
    partition: int
    offset: int
    message: dict


class ConsumerTransaction(Protocol):
    def outcome(self, consumer_group: str, message_id: str) -> str | None: ...
    def apply(self, consumer_group: str, message: dict, handler: Callable[[dict], None]) -> str: ...
    def record_outcome(self, consumer_group: str, message: dict,
                       outcome: str, failure_code: str | None = None) -> None: ...


class ManualOffsetConsumer(Protocol):
    def commit(self, record: ConsumedRecord) -> None: ...


class DurableFailureRouter(Protocol):
    def route(self, consumer_group: str, record: ConsumedRecord, error: Exception) -> str: ...


class DeliveryGuard(Protocol):
    def validate_delivery(self, subscriber: str, topic: str, envelope: dict) -> None: ...


class GovernedConsumer:
    def __init__(self, group: str, transaction: ConsumerTransaction,
                 offsets: ManualOffsetConsumer, failures: DurableFailureRouter,
                 privacy: DeliveryGuard):
        self.group = group
        self.transaction = transaction
        self.offsets = offsets
        self.failures = failures
        self.privacy = privacy

    def process(self, record: ConsumedRecord, handler: Callable[[dict], None]) -> str:
        envelope = record.message
        self.privacy.validate_delivery(self.group, record.topic, envelope)
        message_id = envelope["message_id"]
        prior = self.transaction.outcome(self.group, message_id)
        if prior is not None:
            self.offsets.commit(record)
            return "duplicate"

        try:
            # The transaction adapter performs the version check while holding
            # the authoritative session lock. A preflight check here would race
            # a concurrent intent change.
            outcome = self.transaction.apply(self.group, envelope, handler)
        except Exception as error:
            outcome = self.failures.route(self.group, record, error)
            if outcome not in {"retry", "dead_letter"}:
                raise RuntimeError("failure router did not durably transfer message")
            self.transaction.record_outcome(
                self.group, envelope, outcome, type(error).__name__[:128]
            )
        self.offsets.commit(record)
        return outcome


class KafkaGovernedConsumerRunner:
    """Poll a Kafka consumer and process each record through a GovernedConsumer.

    This is the runnable wiring for the reference consumer services: it decodes
    the broker record, applies the governed consume path (delivery guard,
    idempotency, version-checked apply, retry/DLQ, manual offset commit), and
    returns the per-record outcomes.
    """

    def __init__(self, consumer, governed: GovernedConsumer):
        self.consumer = consumer
        self.governed = governed

    def run_once(self, handler: Callable[[dict], None], *, timeout: float = 1.0,
                 max_messages: int = 100) -> list[str]:
        outcomes: list[str] = []
        for _ in range(max_messages):
            message = self.consumer.poll(timeout)
            if message is None:
                break
            if message.error() is not None:
                raise RuntimeError(f"kafka consume failed: {message.error()}")
            envelope = json.loads(message.value())
            record = ConsumedRecord(message.topic(), message.partition(),
                                    message.offset(), envelope)
            outcomes.append(self.governed.process(record, handler))
        return outcomes
