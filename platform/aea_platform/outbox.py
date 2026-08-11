from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class OutboxRecord:
    message_id: str
    topic: str
    aggregate_key: str
    envelope: dict
    attempt_count: int


class OutboxStore(Protocol):
    def claim(self, worker: str, limit: int) -> list[OutboxRecord]: ...
    def mark_published(self, message_id: str, published_at: datetime) -> None: ...
    def release_for_retry(self, message_id: str, error_code: str, delay_seconds: int) -> None: ...


class AcknowledgedPublisher(Protocol):
    def publish(self, topic: str, key: str, message: dict) -> None:
        """Return only after the broker acknowledgement required by policy."""


class OutboxRelay:
    def __init__(self, store: OutboxStore, publisher: AcknowledgedPublisher, worker: str):
        self.store = store
        self.publisher = publisher
        self.worker = worker

    @staticmethod
    def retry_delay(attempt: int) -> int:
        return min(300, 2 ** min(max(attempt - 1, 0), 8))

    def run_once(self, limit: int = 100) -> tuple[int, int]:
        published = failed = 0
        for record in self.store.claim(self.worker, limit):
            try:
                self.publisher.publish(record.topic, record.aggregate_key, record.envelope)
            except Exception as error:  # adapter maps details to a sanitized code
                failed += 1
                self.store.release_for_retry(
                    record.message_id,
                    type(error).__name__,
                    self.retry_delay(record.attempt_count),
                )
            else:
                self.store.mark_published(record.message_id, datetime.now(timezone.utc))
                published += 1
        return published, failed

