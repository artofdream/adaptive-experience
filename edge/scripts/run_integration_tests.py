import pathlib
import subprocess
import sys


root = pathlib.Path(__file__).resolve().parents[2]
compose = ["docker", "compose", "-f", str(root / "edge" / "docker-compose.yml")]


def main(run=subprocess.run):
    try:
        run(compose + ["up", "--build", "--wait"], cwd=root, check=True)
        run([sys.executable, str(root / "edge" / "scripts" / "diagnose.py")],
            cwd=root, check=True)
        run([sys.executable, str(root / "edge" / "scripts" / "check_assistant_slo.py")],
            cwd=root, check=True)
    finally:
        run(compose + ["down", "--volumes"], cwd=root, check=False)


if __name__ == "__main__":
    main()
