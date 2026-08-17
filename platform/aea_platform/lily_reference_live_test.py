"""Named live-test inventory heartbeat for the Lily reference catalog.

This is not the Compose seeder. It does not read AEA_SEED_INVENTORY and does
not call assert_local_seed_allowed. Production (AEA_ENVIRONMENT=production) is
the intended Path B environment. Gate is AEA_INVENTORY_FEED=lily-reference-live-test.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Sequence

from .inventory import AvailabilitySnapshot, InventoryAvailabilityService
from .recommendation import REFERENCE_CATALOG

FEED_NAME = "lily-reference-live-test"
FEED_ENV = "AEA_INVENTORY_FEED"
DEFAULT_AVAILABLE_QUANTITY = 8
DEFAULT_INTERVAL_SECONDS = 30


def reference_product_ids() -> tuple[str, ...]:
    return tuple(product.product_id for product in REFERENCE_CATALOG)


def assert_live_test_feed_allowed() -> None:
    if os.environ.get("AEA_SEED_INVENTORY") == "1":
        raise RuntimeError(
            "lily-reference-live-test must not run with AEA_SEED_INVENTORY=1")
    if os.environ.get(FEED_ENV) != FEED_NAME:
        raise RuntimeError(
            f"{FEED_ENV}={FEED_NAME} is required for the named live-test "
            "inventory heartbeat")


def next_source_version(connection) -> int:
    row = connection.execute(
        "SELECT COALESCE(MAX(source_version), 0) FROM inventory.product_availability",
    ).fetchone()
    return int(row[0]) + 1


def record_reference_catalog(
    service: InventoryAvailabilityService,
    connection,
    *,
    quantity: int = DEFAULT_AVAILABLE_QUANTITY,
    observed_at: datetime | None = None,
    product_ids: Sequence[str] | None = None,
) -> dict[str, str]:
    if quantity <= 0:
        raise ValueError("live-test quantity must be greater than zero")
    observed = observed_at or datetime.now(timezone.utc)
    source_version = next_source_version(connection)
    results = {}
    for product_id in (product_ids or reference_product_ids()):
        results[product_id] = service.record(AvailabilitySnapshot(
            product_id, quantity, source_version, observed))
    return results


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
