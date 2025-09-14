#!/usr/bin/env bash
set -euo pipefail

# This script runs on devcontainer creation to prepare and auto-sync the integration.
# It will:
# 1) Ensure Supervisor is started
# 2) Wait until HA config dir is available
# 3) Run one-time sync of the integration into HA's config/custom_components
# It is idempotent and guarded by a marker file kept in the workspace.

WS_DIR="${WORKSPACE_DIRECTORY:-${containerWorkspaceFolder:-/workspaces}}"
REPO_ROOT="${WS_DIR}"
MARKER_DIR="${WS_DIR}/.devcontainer/.cache"
MARKER_FILE="${MARKER_DIR}/first-sync.done"

mkdir -p "${MARKER_DIR}"

if [[ -f "${MARKER_FILE}" ]]; then
  echo "[first-start] First sync already completed (marker present). Skipping."
  exit 0
fi

# Try to start Supervisor if not already running
if ! ha core info >/dev/null 2>&1; then
  echo "[first-start] Home Assistant Core not reachable yet. Starting Supervisor..."
  if command -v supervisor_run >/dev/null 2>&1; then
    supervisor_run || true
  else
    echo "[first-start] supervisor_run command not found; this image may auto-start Supervisor."
  fi
fi

# Wait for HA config directory to appear
resolve_config_dir() {
  if [[ -e "/config" ]]; then
    readlink -f /config || echo /config
    return 0
  fi
  if [[ -d "/mnt/supervisor/homeassistant" ]]; then
    echo "/mnt/supervisor/homeassistant"
    return 0
  fi
  return 1
}

TRIES=60
SLEEP=2
CONFIG_DIR=""
for ((i=1; i<=TRIES; i++)); do
  if CONFIG_DIR="$(resolve_config_dir)"; then
    if [[ -d "${CONFIG_DIR}" ]]; then
      echo "[first-start] Detected HA config at ${CONFIG_DIR}"
      break
    fi
  fi
  echo "[first-start] Waiting for HA config directory... (${i}/${TRIES})"
  sleep "${SLEEP}"
  CONFIG_DIR=""

done

if [[ -z "${CONFIG_DIR}" ]]; then
  echo "[first-start] Failed to detect HA config directory; skipping auto-sync."
  exit 0
fi

# Run sync script
if [[ -x "${REPO_ROOT}/scripts/sync_integration.sh" ]]; then
  echo "[first-start] Running initial sync..."
  bash "${REPO_ROOT}/scripts/sync_integration.sh" || true
  echo "[first-start] Initial sync attempted."
else
  echo "[first-start] Sync script not found; skipping."
fi

# Mark completion
date -Iseconds > "${MARKER_FILE}"
echo "[first-start] Done. Marker written to ${MARKER_FILE}"
