from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provision_kafka import admin_client_config, min_insync_replicas, replication_from_env


class ProvisionKafkaPolicyTests(unittest.TestCase):
    def test_min_insync_is_rf_minus_one_for_replicated_topics(self):
        self.assertEqual(1, min_insync_replicas(1))
        self.assertEqual(1, min_insync_replicas(2))
        self.assertEqual(2, min_insync_replicas(3))

    def test_min_insync_rejects_zero_replication(self):
        with self.assertRaises(ValueError):
            min_insync_replicas(0)

    def test_replication_honors_explicit_override(self):
        defaults = {
            "local_replication_factor": 1,
            "pilot_replication_factor": 2,
            "production_replication_factor": 3,
        }
        self.assertEqual(2, replication_from_env(defaults, {
            "AEA_ENVIRONMENT": "production",
            "AEA_KAFKA_REPLICATION_FACTOR": "2",
        }))

    def test_replication_uses_pilot_profile_on_production_fail_closed_env(self):
        defaults = {
            "local_replication_factor": 1,
            "pilot_replication_factor": 2,
            "production_replication_factor": 3,
        }
        self.assertEqual(2, replication_from_env(defaults, {
            "AEA_ENVIRONMENT": "production",
            "AEA_KAFKA_REPLICATION_PROFILE": "pilot",
        }))
        self.assertEqual(3, replication_from_env(defaults, {"AEA_ENVIRONMENT": "production"}))
        self.assertEqual(1, replication_from_env(defaults, {"AEA_ENVIRONMENT": "local"}))

    def test_admin_config_adds_sasl_without_logging_password(self):
        conf = admin_client_config({
            "AEA_KAFKA_BOOTSTRAP": "b-1.example:9096",
            "AEA_KAFKA_SECURITY": "SASL_SSL",
            "AEA_KAFKA_SASL_USERNAME": "aea",
            "AEA_KAFKA_SASL_PASSWORD": "not-a-committed-secret",
        })
        self.assertEqual("SASL_SSL", conf["security.protocol"])
        self.assertEqual("SCRAM-SHA-512", conf["sasl.mechanism"])
        self.assertEqual("aea", conf["sasl.username"])
        self.assertIn("sasl.password", conf)
        local = admin_client_config({"AEA_KAFKA_BOOTSTRAP": "localhost:9092"})
        self.assertNotIn("sasl.password", local)
        self.assertNotIn("security.protocol", local)


if __name__ == "__main__":
    unittest.main()
