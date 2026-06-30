#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  bash scripts/s14_linkerhand_l6_can_readonly_probe.sh [can_iface] [left|right] [--allow-arm-can]

Examples:
  bash scripts/s14_linkerhand_l6_can_readonly_probe.sh can1 left
  bash scripts/s14_linkerhand_l6_can_readonly_probe.sh can_hand_left left

This probe sends LinkerHand L6 read-only request frames only:
  0x64 version, 0xC0 serial, 0x33 temperature,
  0x35 fault, 0x36 current.

It does not send position/speed/torque setting payloads.
It also avoids 0x01 and 0x02 because a live S14.6C run observed physical
hand opening after the original probe included 0x01.
USAGE
}

iface="${1:-can1}"
side="${2:-left}"
allow_arm_can="${3:-}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

case "$side" in
  left)
    hand_id="028"
    response_ids="0x028 or 0x030"
    ;;
  right)
    hand_id="027"
    response_ids="0x027 or 0x02F"
    ;;
  *)
    echo "Error: side must be left or right, got '$side'." >&2
    usage
    exit 2
    ;;
esac

if [[ "$iface" == can_arm_* && "$allow_arm_can" != "--allow-arm-can" ]]; then
  cat >&2 <<EOF
Refusing to probe $iface.
This script is for a hand-only CAN bus. Do not run it on NERO arm CAN
interfaces unless a separate bus review explicitly allows it.
EOF
  exit 3
fi

for tool in ip candump cansend; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Error: required tool '$tool' is not installed." >&2
    exit 4
  fi
done

if ! ip link show "$iface" >/dev/null 2>&1; then
  echo "Error: CAN interface '$iface' does not exist." >&2
  echo "Available CAN interfaces:"
  ip -br link show type can || true
  exit 5
fi

if ! ip link show "$iface" | grep -q "UP"; then
  cat >&2 <<EOF
Error: CAN interface '$iface' is not UP.
Activate it first, for example:
  sudo ip link set "$iface" up type can bitrate 1000000
EOF
  exit 6
fi

echo "S14 LinkerHand L6 CAN read-only probe"
echo "interface=$iface side=$side request_id=0x$hand_id expected_response=$response_ids"
echo "safety=identity_and_health_only no_state_or_torque_query"
echo

ip -details link show "$iface" | sed 's/^/  /'
echo

if command -v ethtool >/dev/null 2>&1; then
  echo "Driver information:"
  ethtool -i "$iface" 2>/dev/null | sed 's/^/  /' || true
  echo
fi

tmp_file="$(mktemp)"
cleanup() {
  if [ -n "${candump_pid:-}" ]; then
    kill "$candump_pid" 2>/dev/null || true
    wait "$candump_pid" 2>/dev/null || true
  fi
  rm -f "$tmp_file"
}
trap cleanup EXIT

candump -tz "$iface" >"$tmp_file" 2>&1 &
candump_pid=$!
sleep 0.2

send_read() {
  local code="$1"
  local label="$2"
  echo "request $label: ${hand_id}#${code}"
  cansend "$iface" "${hand_id}#${code}"
  sleep 0.12
}

send_read "64" "version"
send_read "C0" "serial"
send_read "33" "temperature"
send_read "35" "fault"
send_read "36" "current"

sleep 0.8
kill "$candump_pid" 2>/dev/null || true
wait "$candump_pid" 2>/dev/null || true
candump_pid=""

echo
echo "Raw CAN capture:"
if [ -s "$tmp_file" ]; then
  cat "$tmp_file"
else
  echo "  <no frames captured>"
fi

echo
echo "Acceptance hints:"
echo "  - Expected response arbitration IDs: $response_ids."
echo "  - Response byte0 should include some of: 0x64/0xC2, 0xC0, 0x33, 0x35, 0x36."
echo "  - Fault response 0x35 should report all-zero joint fault values before motion."
echo "  - This script intentionally does not query 0x01 state or 0x02 torque/status."
