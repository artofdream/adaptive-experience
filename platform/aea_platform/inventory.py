from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable


class InventoryValidationError(ValueError):
    pass


class InventoryUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class AvailabilitySnapshot:
    product_id: str
    available_quantity: int
    source_version: int
    observed_at: datetime


@dataclass(frozen=True)
class AvailabilityValidation:
    message_id: str
    context_version: int
    availability: dict[str, dict]


class InventoryAvailabilityService:
    """Inventory authority and freshness-aware validation boundary (FR-011)."""

    def __init__(self, store, *, max_age: timedelta = timedelta(minutes=1),
                 now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None):
        if max_age <= timedelta(0):
            raise ValueError("inventory freshness window must be positive")
        self.store = store
        self.max_age = max_age
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

    def record(self, snapshot: AvailabilitySnapshot) -> str:
        product_id = self._product_id(snapshot.product_id)
        if (not isinstance(snapshot.available_quantity, int)
                or isinstance(snapshot.available_quantity, bool)
                or snapshot.available_quantity < 0):
            raise InventoryValidationError("available quantity is invalid")
        if (not isinstance(snapshot.source_version, int)
                or isinstance(snapshot.source_version, bool)
                or snapshot.source_version < 0):
            raise InventoryValidationError("source version is invalid")
        if snapshot.observed_at.tzinfo is None:
            raise InventoryValidationError("observed time must be timezone-aware")
        return self.store.record_snapshot(product_id, snapshot.available_quantity,
                                          snapshot.source_version,
                                          snapshot.observed_at.astimezone(timezone.utc))

    def validate(self, *, session_id: str, product_ids: list[str],
                 observed_context_version: int, correlation_id: str,
                 subject_reference: str,
                 purpose: str = "recommendation") -> AvailabilityValidation:
        products = tuple(dict.fromkeys(self._product_id(item) for item in product_ids))
        if not products or len(products) > 100:
            raise InventoryValidationError("between 1 and 100 product IDs are required")
        if (not isinstance(observed_context_version, int)
                or isinstance(observed_context_version, bool)
                or observed_context_version < 0):
            raise InventoryValidationError("observed context version is invalid")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            raise InventoryValidationError("correlation ID is required")
        if not isinstance(subject_reference, str) or not subject_reference.strip():
            raise InventoryValidationError("subject reference is required")
        if purpose not in {"recommendation", "selection"}:
            raise InventoryValidationError("validation purpose is invalid")
        message_id = str(self.new_id())
        published_at = self.now().astimezone(timezone.utc)
        result = self.store.validate_and_enqueue(
            session_id=session_id, expected_context_version=observed_context_version,
            product_ids=products, freshness_cutoff=published_at - self.max_age,
            message_id=message_id, correlation_id=correlation_id.strip(),
            subject_reference=subject_reference.strip(), published_at=published_at)
        if purpose == "selection" and result[products[0]]["status"] != "available":
            raise InventoryUnavailableError(products[0])
        return AvailabilityValidation(message_id, observed_context_version, result)

    @staticmethod
    def _product_id(value: str) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 120:
            raise InventoryValidationError("product ID is invalid")
        return value.strip()
