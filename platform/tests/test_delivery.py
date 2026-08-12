from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.delivery import DeliveryValidationError, normalize_delivery_details


class DeliveryContractTests(unittest.TestCase):
    def _valid(self, **overrides):
        details = {"destination_reference": "addr-ref-1",
                   "timing": {"date": "2026-09-01", "window": "morning"}}
        details.update(overrides)
        return details

    def test_valid_details_are_normalized(self):
        self.assertEqual(
            {"destination_reference": "addr-ref-1",
             "timing": {"date": "2026-09-01", "window": "morning"}},
            normalize_delivery_details(self._valid(destination_reference="  addr-ref-1  ")))

    def test_reference_and_timing_are_required(self):
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details({"timing": {"date": "2026-09-01", "window": "morning"}})
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details({"destination_reference": "addr-ref-1"})

    def test_raw_recipient_pii_and_unknown_keys_are_rejected(self):
        for pii in ("recipient_name", "recipient_address", "address", "phone", "extra"):
            with self.assertRaises(DeliveryValidationError):
                normalize_delivery_details(self._valid(**{pii: "leak"}))

    def test_timing_date_and_window_are_validated(self):
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details(self._valid(timing={"date": "nope", "window": "morning"}))
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details(self._valid(timing={"date": "2026-09-01", "window": "midnight"}))
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details(self._valid(
                timing={"date": "2026-09-01", "window": "morning", "extra": 1}))

    def test_reference_bounds(self):
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details(self._valid(destination_reference="x" * 201))
        with self.assertRaises(DeliveryValidationError):
            normalize_delivery_details(self._valid(destination_reference="bad\x07ref"))


if __name__ == "__main__":
    unittest.main()
