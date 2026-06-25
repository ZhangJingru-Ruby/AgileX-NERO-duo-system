#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

workspace="${NERO_ROS_WS:-${HOME}/agx_arm_ws}"
vendor_script="$workspace/src/agx_arm_ros/scripts/find_all_can_port.sh"

if [ -f "$vendor_script" ]; then
  bash "$vendor_script"
  exit 0
fi

echo "Vendor find_all_can_port.sh not found. Falling back to local read-only scan."

if ! command -v ethtool >/dev/null 2>&1; then
  echo "Error: ethtool is not installed." >&2
  exit 1
fi

if ! command -v ip >/dev/null 2>&1; then
  echo "Error: ip command is not installed." >&2
  exit 1
fi

for iface in $(ip -br link show type can | awk '{print $1}'); do
  bus_info="$(sudo ethtool -i "$iface" | awk '/bus-info/ {print $2}')"
  if [ -n "$bus_info" ]; then
    echo "Interface $iface is connected to USB port $bus_info"
  else
    echo "Interface $iface bus-info unknown"
  fi
done
