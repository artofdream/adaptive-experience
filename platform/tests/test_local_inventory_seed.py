from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.inventory import InventoryAvailabilityService
from aea_platform.local_inventory_seed import (
    assert_local_seed_allowed,
    next_source_version,
    reference_product_ids,
    seed_snapshots,
)
from aea_platform.recommendation import REFERENCE_CATALOG


class FakeInventoryStore:
    def __init__(self):
        self.recorded = []

    def record_snapshot(self, *values):
        self.recorded.append(values)
        return "applied"


class FakeConnection:
    def __init__(self, maximum=0):
        self.maximum = maximum

    def execute(self, sql, params=None):
        class Result:
            def __init__(self, maximum):
                self.maximum = maximum

            def fetchone(self):
                return (self.maximum,)
        return Result(self.maximum)


class LocalInventorySeedTests(unittest.TestCase):
    def test_seed_records_available_snapshots_for_reference_catalog(self):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
        store = FakeInventoryStore()
        service = InventoryAvailabilityService(store, now=lambda: now)
        results = seed_snapshots(service, source_version=4, quantity=8, observed_at=now)
        expected = {product.product_id for product in REFERENCE_CATALOG}
        self.assertEqual(expected, set(results))
        self.assertEqual(expected, set(reference_product_ids()))
        self.assertTrue(all(status == "applied" for status in results.values()))
        self.assertEqual(len(REFERENCE_CATALOG), len(store.recorded))
        for product_id, quantity, version, observed_at in store.recorded:
            self.assertIn(product_id, expected)
            self.assertGreater(quantity, 0)
            self.assertEqual(4, version)
            self.assertEqual(now, observed_at)

    def test_seed_rejects_non_positive_quantity(self):
        service = InventoryAvailabilityService(FakeInventoryStore())
        with self.assertRaises(ValueError):
            seed_snapshots(service, source_version=1, quantity=0)

    def test_next_source_version_is_monotonic(self):
        self.assertEqual(1, next_source_version(FakeConnection(0)))
        self.assertEqual(8, next_source_version(FakeConnection(7)))

    def test_seeder_refuses_production_and_requires_explicit_flag(self):
        with patch.dict(os.environ, {"AEA_ENVIRONMENT": "production", "AEA_SEED_INVENTORY": "1"},
                        clear=True):
            with self.assertRaisesRegex(RuntimeError, "must not run"):
                assert_local_seed_allowed()
        with patch.dict(os.environ, {"AEA_ENVIRONMENT": "local"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AEA_SEED_INVENTORY=1"):
                assert_local_seed_allowed()
        with patch.dict(os.environ, {"AEA_ENVIRONMENT": "local", "AEA_SEED_INVENTORY": "1"},
                        clear=True):
            assert_local_seed_allowed()


if __name__ == "__main__":
    unittest.main()
