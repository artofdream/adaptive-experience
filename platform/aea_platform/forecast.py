"""Deterministic inventory demand forecast (FR-012 / NFR-010, M11).

Analyzes validated snapshot history and recommends replenishment. Uses only
current, validated observations (NFR-010). Does not invent seasonality, ML
demand, or stock. FR-012 stays Future. Does not replace FR-011.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from .inventory import InventoryAvailabilityService, InventoryValidationError

FORECAST_TRENDS = frozenset({
    "declining", "stable", "rising", "depleted", "insufficient",
})


@dataclass(frozen=True)
class ForecastItem:
    product_id: str
    trend: str
    recommendation: str
    fact_references: tuple[str, ...]


@dataclass(frozen=True)
class ForecastResult:
    message_id: str | None
    items: tuple[ForecastItem, ...]


class InventoryForecastService:
    """Replenishment demand forecast from validated snapshot history (FR-012).

    Two-point history matches the thin /florist path. Three or more validated
    snapshots use the run after the most recent restock so a mid-series
    replenishment does not hide later burn (M11 depth).
    """

    def __init__(self, store, *, max_age: timedelta = timedelta(minutes=1),
                 now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None):
        if max_age <= timedelta(0):
            raise ValueError("inventory freshness window must be positive")
        self.store = store
        self.max_age = max_age
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

    def recommend(self, *, session_id: str, context_version: int,
                  correlation_id: str, subject_reference: str,
                  product_ids: list[str] | None = None) -> ForecastResult:
        if not isinstance(session_id, str) or not session_id.strip():
            raise InventoryValidationError("session ID is required")
        if (not isinstance(context_version, int)
                or isinstance(context_version, bool)
                or context_version < 0):
            raise InventoryValidationError("context version is invalid")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            raise InventoryValidationError("correlation ID is required")
        if not isinstance(subject_reference, str) or not subject_reference.strip():
            raise InventoryValidationError("subject reference is required")
        products = None
        if product_ids is not None:
            products = tuple(dict.fromkeys(
                InventoryAvailabilityService._product_id(item) for item in product_ids))
            if not products or len(products) > 100:
                raise InventoryValidationError("between 1 and 100 product IDs are required")
        published_at = self.now().astimezone(timezone.utc)
        cutoff = published_at - self.max_age
        grouped: dict[str, list[dict]] = {}
        for row in self.store.list_observations(product_ids=products):
            if not self._is_validated_observation(row):
                continue
            grouped.setdefault(row["product_id"], []).append(row)
        items = tuple(
            self._item(product_id, rows, cutoff)
            for product_id, rows in sorted(grouped.items())
        )
        if not items:
            return ForecastResult(None, ())
        message_id = str(self.new_id())
        self.store.record_forecast(
            session_id=session_id.strip(),
            context_version=context_version,
            message_id=message_id,
            correlation_id=correlation_id.strip(),
            subject_reference=subject_reference.strip(),
            published_at=published_at,
            items=items,
        )
        return ForecastResult(message_id, items)

    def _item(self, product_id: str, rows: list[dict],
              cutoff: datetime) -> ForecastItem:
        ordered = sorted(rows, key=lambda row: (row["observed_at"], row["source_version"]))
        latest = ordered[-1]
        refs = self._refs(ordered[0], latest)
        if latest["observed_at"] < cutoff:
            return ForecastItem(
                product_id, "insufficient",
                "Latest validated snapshot is stale; no forecast.", refs)
        if latest["available_quantity"] == 0:
            return ForecastItem(
                product_id, "depleted",
                "Restock now; validated quantity is 0.", refs)
        if len(ordered) < 2:
            return ForecastItem(
                product_id, "insufficient",
                "This product has only one validated snapshot; no trend yet.", refs)
        run = self._active_run(ordered)
        first = run[0]
        refs = self._refs(first, latest)
        span = (latest["observed_at"] - first["observed_at"]).total_seconds()
        if span <= 0:
            return ForecastItem(
                product_id, "insufficient",
                "Validated snapshots share the same observation time; no trend yet.",
                refs)
        delta = latest["available_quantity"] - first["available_quantity"]
        if delta == 0:
            return ForecastItem(
                product_id, "stable",
                f"Quantity is stable at {latest['available_quantity']}; "
                "no replenishment recommended.", refs)
        if delta > 0:
            return ForecastItem(
                product_id, "rising",
                f"Quantity rose from {first['available_quantity']} to "
                f"{latest['available_quantity']}; monitor, no replenishment recommended.",
                refs)
        daily_burn = (-delta) / (span / 86400)
        days = latest["available_quantity"] / daily_burn
        if days >= 365:
            horizon = "more than a year"
        else:
            horizon = f"about {max(1, round(days))} day" + (
                "s" if max(1, round(days)) != 1 else "")
        return ForecastItem(
            product_id, "declining",
            f"Quantity declined from {first['available_quantity']} to "
            f"{latest['available_quantity']}; {horizon} to stockout at this rate. "
            "Plan a replenishment.", refs)

    @staticmethod
    def _active_run(ordered: list[dict]) -> list[dict]:
        """Observations after the most recent restock; else the full series.

        A restock that is the latest point is treated as a rising pair so
        two-point 2→6 stays rising.
        """
        if len(ordered) < 2:
            return ordered
        peak = 0
        for index in range(1, len(ordered)):
            if (ordered[index]["available_quantity"]
                    > ordered[index - 1]["available_quantity"]):
                peak = index
        if peak == len(ordered) - 1:
            return ordered[peak - 1:]
        return ordered[peak:]

    @staticmethod
    def _is_validated_observation(row) -> bool:
        if not isinstance(row, dict):
            return False
        try:
            product_id = row["product_id"]
            quantity = row["available_quantity"]
            version = row["source_version"]
            observed_at = row["observed_at"]
        except (KeyError, TypeError):
            return False
        if not isinstance(product_id, str) or not product_id.strip():
            return False
        if (not isinstance(quantity, int) or isinstance(quantity, bool)
                or quantity < 0):
            return False
        if (not isinstance(version, int) or isinstance(version, bool)
                or version < 0):
            return False
        return getattr(observed_at, "tzinfo", None) is not None

    @staticmethod
    def _refs(first: dict, latest: dict) -> tuple[str, ...]:
        refs = [f"inventory:{first['product_id']}:v{first['source_version']}"]
        latest_ref = f"inventory:{latest['product_id']}:v{latest['source_version']}"
        if latest_ref != refs[0]:
            refs.append(latest_ref)
        return tuple(refs)
