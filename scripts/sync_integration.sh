#!/usr/bin/env bash
set -euo pipefail

# Sync custom component into Home Assistant's config directory in the Supervisor devcontainer.

WS_DIR="${WORKSPACE_DIRECTORY:-${containerWorkspaceFolder:-/workspaces}}"
COMPONENT_DOMAIN="noaa_space_weather"

# Resolve repository root relative to this script to avoid relying on env when run via sudo
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
SRC_COMPONENT_DIR="${REPO_ROOT}/custom_components/${COMPONENT_DOMAIN}"

if [[ ! -d "${SRC_COMPONENT_DIR}" ]]; then
  echo "[sync] Source component not found: ${SRC_COMPONENT_DIR}" >&2
  echo "[sync] Script dir: ${SCRIPT_DIR} | Repo root: ${REPO_ROOT}" >&2
  exit 1
fi

detect_config_dir() {
  # Prefer resolved /config when available, else fall back to Supervisor data path.
  if [[ -e "/config" ]]; then
    local resolved
    resolved="$(readlink -f /config || echo /config)"
    echo "${resolved}"
    return 0
  fi
  if [[ -d "/mnt/supervisor/homeassistant" ]]; then
    echo "/mnt/supervisor/homeassistant"
    return 0
  fi
  return 1
}

HA_CONFIG_DIR="$(detect_config_dir || true)"
if [[ -z "${HA_CONFIG_DIR}" ]]; then
  echo "[sync] Could not detect Home Assistant config directory. Is Supervisor running?" >&2
  echo "[sync] Try starting it first (task: Start Home Assistant - Supervisor) and re-run sync." >&2
  exit 2
fi

TARGET_CC_DIR="${HA_CONFIG_DIR}/custom_components"
TARGET_COMPONENT_DIR="${TARGET_CC_DIR}/${COMPONENT_DOMAIN}"

echo "[sync] Workspace: ${WS_DIR}"
echo "[sync] Repo root: ${REPO_ROOT}"
echo "[sync] Detected HA config: ${HA_CONFIG_DIR}"
echo "[sync] Syncing ${SRC_COMPONENT_DIR} -> ${TARGET_COMPONENT_DIR}"

# Elevate if needed for writes into Supervisor-managed paths
SUDO_CMD=""
if [[ "$(id -u)" != "0" ]]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO_CMD="sudo -E"
  fi
fi

${SUDO_CMD} mkdir -p "${TARGET_CC_DIR}"

# Use rsync if available for faster incremental copies, else fall back to cp -a
if command -v rsync >/dev/null 2>&1; then
  ${SUDO_CMD} rsync -a --delete "${SRC_COMPONENT_DIR}/" "${TARGET_COMPONENT_DIR}/"
else
  # Remove stale dest then copy fresh to simulate --delete
  ${SUDO_CMD} rm -rf "${TARGET_COMPONENT_DIR}"
  ${SUDO_CMD} cp -a "${SRC_COMPONENT_DIR}" "${TARGET_COMPONENT_DIR}"
fi

# Best-effort: fix permissions to match parent directory
PARENT_UID="$(stat -c %u "${HA_CONFIG_DIR}" 2>/dev/null || echo "")"
PARENT_GID="$(stat -c %g "${HA_CONFIG_DIR}" 2>/dev/null || echo "")"
if [[ -n "${PARENT_UID}" && -n "${PARENT_GID}" ]]; then
  ${SUDO_CMD} chown -R "${PARENT_UID}:${PARENT_GID}" "${TARGET_COMPONENT_DIR}" || true
fi

echo "[sync] Done. You may need to restart Home Assistant to load changes (task: Restart Home Assistant Core)."
