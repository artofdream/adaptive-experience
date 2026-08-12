import pathlib
import subprocess
import sys


root = pathlib.Path(__file__).resolve().parents[2]
compose = ["docker", "compose", "-f", str(root / "edge" / "docker-compose.yml")]
try:
    subprocess.run(compose + ["up", "--build", "--wait"], cwd=root, check=True)
    subprocess.run([sys.executable, str(root / "edge" / "scripts" / "diagnose.py")], cwd=root, check=True)
    subprocess.run([sys.executable, str(root / "edge" / "scripts" / "check_assistant_slo.py")],
                   cwd=root, check=True)
finally:
    subprocess.run(compose + ["down", "--volumes"], cwd=root, check=False)
