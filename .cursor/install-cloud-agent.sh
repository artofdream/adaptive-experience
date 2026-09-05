#!/usr/bin/env bash
# Durable, idempotent setup for a Cursor Cloud Agent working this repo.
# Runs after the repository is checked out. Keep everything here repeatable:
# it may run against a clean image or a partially prepared / cached state.
set -euo pipefail

cd "$(dirname "$0")/.."

# 1. Docker Engine + Compose plugin.
#    The edge and platform stacks are exercised through Docker Compose
#    (see edge/README.md, platform/README.md), so Docker is a hard dependency.
if ! command -v docker >/dev/null 2>&1; then
  echo "[install] Installing Docker Engine via get.docker.com ..."
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sudo sh /tmp/get-docker.sh
else
  echo "[install] Docker already present: $(docker --version)"
fi

# 2. Docker storage driver.
#    This VM runs Docker nested inside a container, where the default
#    overlayfs snapshotter cannot extract image whiteout files
#    ("failed to convert whiteout file ...: operation not permitted").
#    The classic vfs storage driver has no such requirement. It is slower
#    but always works; disable the containerd image store to use it.
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json >/dev/null <<'JSON'
{
  "features": { "containerd-snapshotter": false },
  "storage-driver": "vfs"
}
JSON

# 3. Host-side Python runtime dependencies for scripts and unit tests
#    (platform migrations/diagnostics, edge integration runner, etc.).
python3 -m pip install --user \
  -r platform/requirements.txt -c platform/requirements.lock \
  -r edge/requirements.txt -c edge/requirements.lock

echo "[install] Done. Per-boot startup (daemon + bridge fix + compose up) runs in start-cloud-agent.sh."
