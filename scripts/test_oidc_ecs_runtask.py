"""#437: GitLab CI OIDC must allow ecs:RunTask/DescribeTasks without Project tag (task defs)."""
from __future__ import annotations
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OIDC = ROOT / "infra" / "aws" / "oidc.tf"


class OidcRunTaskIamTests(unittest.TestCase):
    def test_untagged_register_allows_run_task(self) -> None:
        text = OIDC.read_text(encoding="utf-8")
        self.assertIn('sid       = "EcsDeployUntaggedRegister"', text)
        start = text.find('sid       = "EcsDeployUntaggedRegister"')
        end = text.find("statement {", start + 10)
        block = text[start:end if end > start else start + 500]
        self.assertIn("ecs:RunTask", block)
        self.assertIn("ecs:DescribeTasks", block)
        self.assertIn("ecs:ListTasks", block)
        self.assertIn("iam:PassRole", block)


if __name__ == "__main__":
    unittest.main()
