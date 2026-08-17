from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import timedelta
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.adapters import PsycopgInventoryAvailabilityStore
from aea_platform.inventory import InventoryAvailabilityService
from aea_platform.lily_reference_live_test import (
    DEFAULT_INTERVAL_SECONDS,
    FEED_NAME,
    assert_live_test_feed_allowed,
    record_reference_catalog,
    snapshots_are_fresh,
)

DSN = os.environ.get(
    "AEA_POSTGRES_DSN",
    "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
)


def wait_for_inventory_table(connection, timeout_seconds: float = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        row = connection.execute(
            "SELECT to_regclass('inventory.product_availability')").fetchone()
        if row[0] is not None:
            return
        time.sleep(1)
    raise RuntimeError("inventory.product_availability is not available")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Named lily-reference-live-test heartbeat for REFERENCE_CATALOG SKUs.")
    parser.add_argument("--loop", action="store_true",
                        help="refresh snapshots until interrupted")
    parser.add_argument("--check", action="store_true",
                        help="exit 0 when reference SKUs are currently available")
    parser.add_argument("--interval", type=float, default=float(os.environ.get(
        "AEA_INVENTORY_FEED_INTERVAL_SECONDS", str(DEFAULT_INTERVAL_SECONDS))),
                        help="seconds between heartbeat refreshes (default: 30)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    assert_live_test_feed_allowed()
    with psycopg.connect(DSN, autocommit=True) as connection:
        if args.check:
            try:
                return 0 if snapshots_are_fresh(connection) else 1
            except Exception:
                return 1
        wait_for_inventory_table(connection)
        service = InventoryAvailabilityService(PsycopgInventoryAvailabilityStore(connection))
        while True:
            results = record_reference_catalog(service, connection)
            applied = ", ".join(f"{product_id}={status}" for product_id, status in results.items())
            print(f"{FEED_NAME}: {applied}")
            if not args.loop:
                return 0
            time.sleep(max(args.interval, 1))
            if not snapshots_are_fresh(connection, max_age=timedelta(minutes=2)):
                print("warning: snapshots were not fresh after live-test tick", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
