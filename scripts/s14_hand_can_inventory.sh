#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  bash scripts/s14_hand_can_inventory.sh

Purpose:
  Read-only inventory of candidate LinkerHand CAN interfaces.

Safety:
  This script does not send CAN frames. It only lists SocketCAN interfaces,
  driver names, USB bus-info, and link state. It marks NERO arm CAN interfaces
  so they are not confused with standalone hand CAN adapters.
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

arm_a_can="${NERO_ARM_A_CAN_PORT:-can_arm_a}"
arm_b_can="${NERO_ARM_B_CAN_PORT:-can_arm_b}"

for cmd in ip ethtool awk sed; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

echo "S14 LinkerHand CAN interface inventory"
echo "arm_can_guard=$arm_a_can,$arm_b_can"
echo "safety=read_only_no_can_frames"
echo

interfaces="$(ip -br link show type can | awk '{print $1}')"
if [ -z "$interfaces" ]; then
  echo "No SocketCAN interfaces found."
  exit 0
fi

for iface in $interfaces; do
  role="candidate_hand_can"
  if [ "$iface" = "$arm_a_can" ] || [ "$iface" = "$arm_b_can" ]; then
    role="nero_arm_can_do_not_use_for_hand"
  fi

  state="$(ip -br link show "$iface" | awk '{print $2}')"
  details="$(ip -details link show "$iface" | sed 's/^/    /')"
  driver="$(ethtool -i "$iface" 2>/dev/null | awk -F': ' '/^driver:/ {print $2}')"
  bus_info="$(ethtool -i "$iface" 2>/dev/null | awk -F': ' '/^bus-info:/ {print $2}')"

  echo "interface=$iface role=$role state=$state driver=${driver:-unknown} bus_info=${bus_info:-unknown}"
  echo "$details"
  echo
done
