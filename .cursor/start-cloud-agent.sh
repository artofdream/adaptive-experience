#!/usr/bin/env bash
# Per-boot startup for a Cursor Cloud Agent working this repo.
# Runs every time the environment starts. Must tolerate restarts and be
# idempotent (an already-running daemon / already-up stack is fine).
set -euo pipefail

cd "$(dirname "$0")/.."

# 1. Ensure the Docker daemon is running.
if ! sudo docker info >/dev/null 2>&1; then
  echo "[start] Starting Docker daemon ..."
  sudo service docker start || sudo nohup dockerd >/tmp/dockerd.log 2>&1 &
  for _ in $(seq 1 30); do
    sudo docker info >/dev/null 2>&1 && break
    sleep 1
  done
fi
sudo docker info >/dev/null 2>&1 || { echo "[start] Docker daemon failed to start" >&2; exit 1; }

# 2. Nested-VM bridge networking fix.
#    With bridge-nf-call-iptables=1, same-network container-to-container TCP
#    is evaluated by nftables and silently dropped in this nested VM (Postgres
#    is reachable by DNS but connections time out). Letting intra-bridge
#    traffic bypass netfilter restores service-to-service connectivity.
sudo modprobe br_netfilter 2>/dev/null || true
if [ -e /proc/sys/net/bridge/bridge-nf-call-iptables ]; then
  sudo sysctl -w net.bridge.bridge-nf-call-iptables=0 >/dev/null
  sudo sysctl -w net.bridge.bridge-nf-call-ip6tables=0 >/dev/null || true
fi

# 3. Bring up the edge stack: browser Adaptive Workspace UI + nginx TLS
#    gateway (https://localhost:8443) + BFF + orchestration + Postgres
#    (pgvector) + local inventory seeder + Grafana. --wait blocks until all
#    health checks pass, then returns so startup completes.
echo "[start] Bringing up edge Docker Compose stack ..."
sudo docker compose -f edge/docker-compose.yml up --build --wait

echo "[start] Edge stack healthy. UI: https://localhost:8443  Grafana: http://localhost:3000"
