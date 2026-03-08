#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$HOME/sensor-agent"
SERVICE_NAME="beatmap-sensor.service"
BRANCH="main"

echo "==> Going to repo: $REPO_DIR"
cd "$REPO_DIR"

echo "==> Pulling latest code from origin/$BRANCH"
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"

echo "==> Reloading systemd units"
sudo systemctl daemon-reload

echo "==> Restarting $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "==> Service status"
sudo systemctl --no-pager --full status "$SERVICE_NAME" || true

echo "==> Last 30 log lines"
journalctl -u "$SERVICE_NAME" -n 30 --no-pager || true

echo "==> Done"