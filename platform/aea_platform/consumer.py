from __future__ import annotations

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
