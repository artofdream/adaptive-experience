import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_assistant_slo.py"
SPEC = importlib.util.spec_from_file_location("check_assistant_slo", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssistantSloTests(unittest.TestCase):
    def test_endpoints_default_to_local_https_origin(self):
        self.assertEqual(
            ("https://localhost:8443", "https://localhost:8443"),
            MODULE.configured_endpoints({}),
        )

    def test_ci_endpoint_does_not_change_browser_origin(self):
        self.assertEqual(
            ("https://docker:8443", "https://localhost:8443"),
            MODULE.configured_endpoints({
                "AEA_EDGE_BASE_URL": "https://docker:8443/",
                "AEA_EDGE_ORIGIN": "https://localhost:8443",
            }),
        )

    def test_endpoint_configuration_rejects_non_https_or_paths(self):
        for value in ("http://docker:8443", "https://docker:8443/api", "https://u:p@docker:8443"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.configured_endpoints({"AEA_EDGE_BASE_URL": value})

    def test_nearest_rank_p95_includes_slowest_sample_for_ten_queries(self):
        samples = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 2.9]
        self.assertEqual(2.9, MODULE.nearest_rank_percentile(samples, 0.95))

    def test_percentile_requires_evidence(self):
        with self.assertRaises(ValueError):
            MODULE.nearest_rank_percentile([], 0.95)


if __name__ == "__main__":
    unittest.main()
