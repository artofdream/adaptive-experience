from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    compose = str(ROOT / "platform" / "docker-compose.yml")
    run("docker", "compose", "-f", compose, "up", "-d", "--wait")
    try:
        run(sys.executable, "platform/scripts/wait_for_services.py")
        run(sys.executable, "platform/scripts/apply_migrations.py")
        run(sys.executable, "platform/scripts/apply_migrations.py")
        run(sys.executable, "platform/scripts/provision_kafka.py")
        environment = dict(
            os.environ,
            AEA_INTEGRATION="1",
            AEA_POSTGRES_DSN=os.environ.get(
                "AEA_POSTGRES_DSN",
                "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
            ),
            AEA_KAFKA_BOOTSTRAP=os.environ.get("AEA_KAFKA_BOOTSTRAP", "localhost:9092"),
        )
        subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "platform/tests", "-v"],
            cwd=ROOT, check=True, env=environment,
        )
        run(sys.executable, "platform/scripts/diagnose.py")
    finally:
        run("docker", "compose", "-f", compose, "down", "-v")


if __name__ == "__main__":
    main()
