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
from aea_platform.lily_reference_live_test import (
    FEED_NAME,
    assert_live_test_feed_allowed,
    next_source_version,
    record_reference_catalog,
    reference_product_ids,
)
from aea_platform.local_inventory_seed import assert_local_seed_allowed
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


class LilyReferenceLiveTestTests(unittest.TestCase):
    def test_records_available_snapshots_for_reference_catalog(self):
        now = datetime(2026, 8, 17, 11, 0, tzinfo=timezone.utc)
        store = FakeInventoryStore()
        service = InventoryAvailabilityService(store, now=lambda: now)
        results = record_reference_catalog(
            service, FakeConnection(3), quantity=8, observed_at=now)
        expected = {product.product_id for product in REFERENCE_CATALOG}
        self.assertEqual(5, len(expected))
        self.assertEqual(expected, set(results))
        self.assertEqual(expected, set(reference_product_ids()))
        self.assertTrue(all(status == "applied" for status in results.values()))
        self.assertEqual(len(REFERENCE_CATALOG), len(store.recorded))
        for product_id, quantity, version, observed_at in store.recorded:
            self.assertIn(product_id, expected)
            self.assertGreater(quantity, 0)
            self.assertEqual(4, version)
            self.assertEqual(now, observed_at)

    def test_rejects_non_positive_quantity(self):
        service = InventoryAvailabilityService(FakeInventoryStore())
        with self.assertRaises(ValueError):
            record_reference_catalog(service, FakeConnection(0), quantity=0)

    def test_next_source_version_is_monotonic(self):
        self.assertEqual(1, next_source_version(FakeConnection(0)))
        self.assertEqual(8, next_source_version(FakeConnection(7)))

    def test_named_feed_allows_production_and_refuses_compose_seeder(self):
        production_feed = {
            "AEA_ENVIRONMENT": "production",
            "AEA_INVENTORY_FEED": FEED_NAME,
        }
        with patch.dict(os.environ, production_feed, clear=True):
            assert_live_test_feed_allowed()
            with self.assertRaisesRegex(RuntimeError, "must not run"):
                assert_local_seed_allowed()
        with patch.dict(os.environ, {
            "AEA_ENVIRONMENT": "production",
            "AEA_INVENTORY_FEED": FEED_NAME,
            "AEA_SEED_INVENTORY": "1",
        }, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AEA_SEED_INVENTORY"):
                assert_live_test_feed_allowed()
        with patch.dict(os.environ, {"AEA_ENVIRONMENT": "production"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AEA_INVENTORY_FEED"):
                assert_live_test_feed_allowed()
        with patch.dict(os.environ, {
            "AEA_ENVIRONMENT": "local",
            "AEA_SEED_INVENTORY": "1",
        }, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AEA_SEED_INVENTORY"):
                assert_live_test_feed_allowed()


if __name__ == "__main__":
    unittest.main()
