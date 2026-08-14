"""Local-only inventory snapshots for the reference catalog (not production authority)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Sequence

from .inventory import AvailabilitySnapshot, InventoryAvailabilityService
from .recommendation import REFERENCE_CATALOG

DEFAULT_AVAILABLE_QUANTITY = 8
DEFAULT_INTERVAL_SECONDS = 30


def reference_product_ids() -> tuple[str, ...]:
    return tuple(product.product_id for product in REFERENCE_CATALOG)


def assert_local_seed_allowed() -> None:
    if os.environ.get("AEA_ENVIRONMENT", "local") == "production":
        raise RuntimeError(
            "local inventory seeder must not run when AEA_ENVIRONMENT=production")
    if os.environ.get("AEA_SEED_INVENTORY") != "1":
        raise RuntimeError("AEA_SEED_INVENTORY=1 is required to seed local inventory")


def next_source_version(connection) -> int:
    row = connection.execute(
        "SELECT COALESCE(MAX(source_version), 0) FROM inventory.product_availability",
    ).fetchone()
    return int(row[0]) + 1


def seed_snapshots(
    service: InventoryAvailabilityService,
    *,
    source_version: int,
    quantity: int = DEFAULT_AVAILABLE_QUANTITY,
    observed_at: datetime | None = None,
    product_ids: Sequence[str] | None = None,
) -> dict[str, str]:
    if quantity <= 0:
        raise ValueError("local seed quantity must be greater than zero")
    observed = observed_at or datetime.now(timezone.utc)
    results = {}
    for product_id in (product_ids or reference_product_ids()):
        results[product_id] = service.record(AvailabilitySnapshot(
            product_id, quantity, source_version, observed))
    return results


def seed_once(service: InventoryAvailabilityService, connection, *,
              quantity: int = DEFAULT_AVAILABLE_QUANTITY,
              observed_at: datetime | None = None) -> dict[str, str]:
    return seed_snapshots(
        service,
        source_version=next_source_version(connection),
        quantity=quantity,
        observed_at=observed_at,
    )


def snapshots_are_fresh(connection, *, max_age: timedelta = timedelta(minutes=1),
                        product_ids: Sequence[str] | None = None) -> bool:
    ids = tuple(product_ids or reference_product_ids())
    cutoff = datetime.now(timezone.utc) - max_age
    rows = connection.execute(
        "SELECT product_id FROM inventory.product_availability "
        "WHERE product_id = ANY(%s) AND available_quantity > 0 AND observed_at > %s",
        (list(ids), cutoff),
    ).fetchall()
    return {row[0] for row in rows} >= set(ids)
