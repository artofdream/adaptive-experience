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
    def active_context_version(self, session_id: str) -> int | None: ...
    def apply(self, consumer_group: str, message: dict, handler: Callable[[dict], None]) -> str: ...


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

        session_id = envelope["session_id"]
        active_version = self.transaction.active_context_version(session_id)
        if active_version is not None and envelope["context_version"] < active_version:
            outcome = self.transaction.apply(self.group, envelope, lambda _: None)
            self.offsets.commit(record)
            return "stale" if outcome == "stale" else outcome

        try:
            outcome = self.transaction.apply(self.group, envelope, handler)
        except Exception as error:
            outcome = self.failures.route(self.group, record, error)
            if outcome not in {"retry", "dead_letter"}:
                raise RuntimeError("failure router did not durably transfer message")
        self.offsets.commit(record)
        return outcome
