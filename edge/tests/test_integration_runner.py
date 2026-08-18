import importlib.util
import os
import pathlib
import subprocess
import unittest


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "run_integration_tests.py"
SPEC = importlib.util.spec_from_file_location("run_edge_integration_tests", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IntegrationRunnerTests(unittest.TestCase):
    def test_diagnostics_reject_non_https_endpoint_before_network_access(self):
        environment = {**os.environ, "AEA_EDGE_BASE_URL": "http://docker:8443"}
        result = subprocess.run(
            [MODULE.sys.executable, str(MODULE.root / "edge" / "scripts" / "diagnose.py")],
            cwd=MODULE.root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must be an HTTPS origin", result.stderr)

    def test_cleanup_runs_after_startup_failure(self):
        calls = []

        def failing_run(command, **kwargs):
            calls.append((command, kwargs))
            if "up" in command:
                raise subprocess.CalledProcessError(1, command)

        with self.assertRaises(subprocess.CalledProcessError):
            MODULE.main(run=failing_run)

        cleanup_command, cleanup_options = calls[-1]
        self.assertEqual(MODULE.compose + ["down", "--volumes"], cleanup_command)
        self.assertFalse(cleanup_options["check"])

    def test_diagnostics_and_slo_run_between_startup_and_cleanup(self):
        calls = []

        def recording_run(command, **kwargs):
            calls.append((command, kwargs))

        MODULE.main(run=recording_run)

        self.assertEqual(MODULE.compose + ["up", "--build", "--wait"], calls[0][0])
        self.assertTrue(calls[1][0][-1].endswith("diagnose.py"))
        self.assertTrue(calls[2][0][-1].endswith("check_assistant_slo.py"))
        self.assertEqual(MODULE.compose + ["down", "--volumes"], calls[3][0])


if __name__ == "__main__":
    unittest.main()
