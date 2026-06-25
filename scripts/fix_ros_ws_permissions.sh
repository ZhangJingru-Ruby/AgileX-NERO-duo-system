#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

workspace="${NERO_ROS_WS:-${HOME}/agx_arm_ws}"
owner="${SUDO_USER:-$(id -un)}"
group="$(id -gn "$owner" 2>/dev/null || id -gn)"

if [ ! -d "$workspace" ]; then
  echo "Workspace not found: $workspace" >&2
  exit 1
fi

sudo chown -R "$owner:$group" \
  "$workspace/build" \
  "$workspace/install" \
  "$workspace/log" 2>/dev/null || true

echo "Fixed ROS workspace permissions under: $workspace"
