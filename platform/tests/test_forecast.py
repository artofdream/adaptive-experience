from __future__ import annotations

import sys
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.inventory import (
    InventoryForecastService,
    InventoryValidationError,
)


class FakeForecastStore:
    def __init__(self, observations=None):
        self.observations = list(observations or [])
        self.forecasts = []

    def list_observations(self, product_ids=None):
        if product_ids is None:
            return list(self.observations)
        allowed = set(product_ids)
        return [row for row in self.observations if row["product_id"] in allowed]

    def record_forecast(self, **values):
        self.forecasts.append(values)


def observation(product_id, quantity, version, observed_at):
    return {
        "product_id": product_id,
        "available_quantity": quantity,
        "source_version": version,
        "observed_at": observed_at,
    }


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
        self.store = FakeForecastStore()
        self.service = InventoryForecastService(
            self.store, now=lambda: self.now,
            new_id=lambda: uuid.UUID("00000000-0000-0000-0000-000000000012"),
        )

    def recommend(self, **kwargs):
        return self.service.recommend(
            session_id="11111111-1111-4111-8111-111111111111",
            context_version=0,
            correlation_id="forecast-1",
            subject_reference="manager-1",
            **kwargs,
        )

    def test_declining_quantity_recommends_replenishment(self):
        self.store.observations = [
            observation("classic-rose-dozen", 10, 1, self.now - timedelta(days=2)),
            observation("classic-rose-dozen", 4, 2, self.now),
        ]
        result = self.recommend()
        self.assertEqual("00000000-0000-0000-0000-000000000012", result.message_id)
        self.assertEqual(1, len(result.items))
        item = result.items[0]
        self.assertEqual("classic-rose-dozen", item.product_id)
        self.assertEqual("declining", item.trend)
        self.assertIn("Plan a replenishment", item.recommendation)
        self.assertEqual(
            ("inventory:classic-rose-dozen:v1", "inventory:classic-rose-dozen:v2"),
            item.fact_references,
        )
        self.assertEqual(1, len(self.store.forecasts))

    def test_stable_rising_depleted_and_insufficient_are_honest(self):
        self.store.observations = [
            observation("lilac-bouquet", 8, 1, self.now - timedelta(days=1)),
            observation("lilac-bouquet", 8, 2, self.now),
            observation("premium-orchid", 2, 1, self.now - timedelta(days=1)),
            observation("premium-orchid", 6, 2, self.now),
            observation("budget-mixed-bunch", 0, 1, self.now),
            observation("pink-flower-vase", 5, 1, self.now),
        ]
        items = {item.product_id: item for item in self.recommend().items}
        self.assertEqual("stable", items["lilac-bouquet"].trend)
        self.assertIn("no replenishment", items["lilac-bouquet"].recommendation)
        self.assertEqual("rising", items["premium-orchid"].trend)
        self.assertEqual("depleted", items["budget-mixed-bunch"].trend)
        self.assertIn("Restock now", items["budget-mixed-bunch"].recommendation)
        self.assertEqual("insufficient", items["pink-flower-vase"].trend)
        self.assertIn("only one validated snapshot", items["pink-flower-vase"].recommendation)

    def test_stale_latest_snapshot_does_not_invent_a_trend(self):
        self.store.observations = [
            observation("classic-rose-dozen", 10, 1, self.now - timedelta(days=3)),
            observation("classic-rose-dozen", 4, 2, self.now - timedelta(minutes=5)),
        ]
        item = self.recommend().items[0]
        self.assertEqual("insufficient", item.trend)
        self.assertIn("stale", item.recommendation)

    def test_empty_history_returns_no_event(self):
        result = self.recommend()
        self.assertIsNone(result.message_id)
        self.assertEqual((), result.items)
        self.assertEqual([], self.store.forecasts)

    def test_rejects_invalid_authority_inputs(self):
        with self.assertRaises(InventoryValidationError):
            self.service.recommend(
                session_id="", context_version=0, correlation_id="c",
                subject_reference="s")
        with self.assertRaises(InventoryValidationError):
            self.recommend(product_ids=[])


if __name__ == "__main__":
    unittest.main()
