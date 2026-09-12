"""Guards: deploy-ecs must fail-closed apply migrations (#436)."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".gitlab-ci.yml"
SCRIPT = ROOT / "scripts" / "ecs_apply_migrations.sh"


def job_block(name: str) -> str:
    lines = CI.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f"{name}:"):
            start = i
            break
    if start is None:
        raise AssertionError(f"missing job {name}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j] and lines[j][0] not in (" ", "\t", "#"):
            end = j
            break
    return "\n".join(lines[start:end])


class EcsApplyMigrationsDeployGuard(unittest.TestCase):
    def test_helper_script_exists_and_is_fail_closed(self) -> None:
        self.assertTrue(SCRIPT.is_file(), str(SCRIPT))
        body = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("apply_migrations.py", body)
        self.assertIn("aws ecs run-task", body)
        self.assertIn("wait tasks-stopped", body)
        self.assertIn("exitCode", body)
        self.assertIn("exit 1", body)
        self.assertIn("assignPublicIp=DISABLED", body)

    def test_deploy_ecs_invokes_helper_before_healthz(self) -> None:
        deploy = job_block("deploy-ecs")
        self.assertIn("scripts/ecs_apply_migrations.sh", deploy)
        health = deploy.find("/healthz")
        migrate = deploy.find("ecs_apply_migrations.sh")
        self.assertGreaterEqual(migrate, 0)
        self.assertGreaterEqual(health, 0)
        self.assertLess(migrate, health, "migrate must run before public healthz gate")


if __name__ == "__main__":
    unittest.main()
