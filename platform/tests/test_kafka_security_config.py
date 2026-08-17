from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.kafka_config import kafka_producer_config, kafka_security_config


class KafkaSecurityConfigTests(unittest.TestCase):
    def test_plaintext_omits_sasl_keys(self):
        conf = kafka_security_config({"AEA_KAFKA_BOOTSTRAP": "localhost:9092"})
        self.assertEqual({}, conf)
        producer = kafka_producer_config("localhost:9092", "relay-1", {})
        self.assertNotIn("security.protocol", producer)
        self.assertNotIn("sasl.password", producer)
        self.assertEqual("all", producer["acks"])
        self.assertTrue(producer["enable.idempotence"])

    def test_path_b_sasl_ssl_defaults_scram_sha_512(self):
        env = {
            "AEA_KAFKA_BOOTSTRAP": "b-1.example:9096",
            "AEA_KAFKA_SECURITY": "SASL_SSL",
            "AEA_KAFKA_SASL_USERNAME": "aea",
            "AEA_KAFKA_SASL_PASSWORD": "not-a-committed-secret",
        }
        conf = kafka_security_config(env)
        self.assertEqual("SASL_SSL", conf["security.protocol"])
        self.assertEqual("SCRAM-SHA-512", conf["sasl.mechanism"])
        self.assertEqual("aea", conf["sasl.username"])
        self.assertEqual("not-a-committed-secret", conf["sasl.password"])
        producer = kafka_producer_config("b-1.example:9096", "outbox-relay", env)
        self.assertEqual("SASL_SSL", producer["security.protocol"])
        self.assertEqual("outbox-relay", producer["client.id"])

    def test_explicit_mechanism_is_honored(self):
        conf = kafka_security_config({
            "AEA_KAFKA_SECURITY": "SASL_SSL",
            "AEA_KAFKA_SASL_MECHANISM": "SCRAM-SHA-256",
            "AEA_KAFKA_SASL_USERNAME": "aea",
        })
        self.assertEqual("SCRAM-SHA-256", conf["sasl.mechanism"])
        self.assertNotIn("sasl.password", conf)


if __name__ == "__main__":
    unittest.main()
