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

    def test_cloud_deployment_status(self):
        os.environ["AEA_AUTONOMOUS_LOOP_ENABLED"] = "true"
        os.environ["AWS_REGION"] = "us-east-1"
        status = self.gateway.get_cloud_deployment_status()
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["aws_region"], "us-east-1")
        self.assertEqual(status["cluster"], "aea-pilot")
        self.assertEqual(status["secret_name"], "aea/gitlab-token")


if __name__ == "__main__":
    unittest.main()
