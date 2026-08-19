"""Unit tests for AWS ECS Fargate configuration in platform/terraform/."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestAWSECSConfig(unittest.TestCase):
    def test_task_definition_template_valid_json(self):
        tpl_path = ROOT / "terraform" / "ecs_task_definition.json.tpl"
        self.assertTrue(tpl_path.exists())

        content = tpl_path.read_text(encoding="utf-8")
        # Replace Terraform placeholders with mock values for JSON parsing validation
        mock_json = content.replace("${ecr_repository_url}", "mock_url").replace(
            "${gitlab_token_secret_arn}", "mock_arn"
        ).replace("${aws_region}", "ap-southeast-2")

        data = json.loads(mock_json)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        container = data[0]
        self.assertEqual(container["name"], "aea-agent-runner")
        self.assertEqual(container["cpu"], 512)
        self.assertEqual(container["memory"], 1024)

    def test_tf_file_exists(self):
        tf_path = ROOT / "terraform" / "ecs_agent_runner.tf"
        self.assertTrue(tf_path.exists())


if __name__ == "__main__":
    unittest.main()
