"""Unit tests for agent_gateway.py in platform/aea_platform/agent_gateway.py."""

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.agent_gateway import AutonomousAgentGateway


class TestAutonomousAgentGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = AutonomousAgentGateway()

    def test_kill_switch_enabled_by_default(self):
        os.environ["AEA_AUTONOMOUS_LOOP_ENABLED"] = "true"
        self.assertTrue(self.gateway.is_autonomous_loop_enabled())

    def test_kill_switch_disabled(self):
        os.environ["AEA_AUTONOMOUS_LOOP_ENABLED"] = "false"
        self.assertFalse(self.gateway.is_autonomous_loop_enabled())
        res = self.gateway.run_preflight_guards()
        self.assertEqual(res["status"], "paused")

    def test_process_gitlab_webhook_issue(self):
        os.environ["AEA_AUTONOMOUS_LOOP_ENABLED"] = "true"
        payload = {
            "object_attributes": {
                "title": "Fix card message validation bug"
            }
        }
        res = self.gateway.process_gitlab_webhook("Issue Hook", payload)
        self.assertTrue(res["processed"])
        self.assertEqual(res["action"], "triaged")

    def test_process_gitlab_webhook_merge_request_missing_validation(self):
        os.environ["AEA_AUTONOMOUS_LOOP_ENABLED"] = "true"
        payload = {
            "object_attributes": {
                "iid": 238,
                "description": "Short PR description without validation"
            }
        }
        res = self.gateway.process_gitlab_webhook("Merge Request Hook", payload)
        self.assertTrue(res["processed"])
        self.assertEqual(res["action"], "auto_remediation_triggered")
        self.assertEqual(res["remediation"]["status"], "triggered")


if __name__ == "__main__":
    unittest.main()
