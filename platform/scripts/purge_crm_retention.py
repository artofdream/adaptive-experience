#!/usr/bin/env python3
"""CRM privacy-lifecycle purge (ADR-020 / NFR-017).

Operational retention job that enforces the zero-PII CRM lifecycle:
- purges occasion memory not updated within the retention window
  (`EngagementCrmService.purge_expired`), and
- shreds ephemeral fulfillment records past their 14-day expiry
  (`PsycopgCrmStore.purge_expired_fulfillment`).

Run once by default, or `--loop` for a continuous worker. Retention days
overridable with `--retention-days N` (default from `crm.DEFAULT_RETENTION_DAYS`).
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import os
import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.adapters import PsycopgCrmStore  # noqa: E402
from aea_platform.crm import DEFAULT_RETENTION_DAYS, EngagementCrmService  # noqa: E402

DSN = os.environ.get(
    "AEA_POSTGRES_DSN",
    "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
)


def run_once(connection, *, retention_days: int) -> tuple[int, int]:
    store = PsycopgCrmStore(connection)
    service = EngagementCrmService(store)
    memories_purged = service.purge_expired(retention_days=retention_days)
    fulfillment_shredded = store.purge_expired_fulfillment(now=datetime.now(timezone.utc))
    return memories_purged, fulfillment_shredded


def main() -> None:
    parser = argparse.ArgumentParser(description="CRM retention / shredding purge")
    parser.add_argument("--loop", action="store_true", help="run continuously")
    parser.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS)
    parser.add_argument("--interval-seconds", type=int, default=3600)
    args = parser.parse_args()

    with psycopg.connect(DSN, autocommit=True) as connection:
        while True:
            memories, fulfillment = run_once(connection, retention_days=args.retention_days)
            print(f"crm-retention memories_purged={memories} fulfillment_shredded={fulfillment}")
            if not args.loop:
                return
            time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
