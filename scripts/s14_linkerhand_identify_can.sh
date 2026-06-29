#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  bash scripts/s14_linkerhand_identify_can.sh <can_iface> [--allow-arm-can]

Purpose:
  S14.3L targeted LinkerHand L6 CAN identification for one selected interface.

Safety:
  This script sends LinkerHand identify/read request frames only to <can_iface>.
  It refuses to run on configured NERO arm CAN interfaces unless
  --allow-arm-can is explicitly supplied.

Frames:
  0FF#C0   primary serial request used by the LinkerHand SDK helper
  0FF#01   fallback hand-side probe used by the LinkerHand SDK helper
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

iface="${1:-}"
allow_arm_can="${2:-}"

if [ -z "$iface" ]; then
  usage >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

arm_a_can="${NERO_ARM_A_CAN_PORT:-can_arm_a}"
arm_b_can="${NERO_ARM_B_CAN_PORT:-can_arm_b}"

if { [ "$iface" = "$arm_a_can" ] || [ "$iface" = "$arm_b_can" ]; } && [ "$allow_arm_can" != "--allow-arm-can" ]; then
  echo "Refusing to send LinkerHand identify frames to arm CAN interface: $iface" >&2
  echo "Arm CAN interfaces are $arm_a_can and $arm_b_can." >&2
  echo "Use a dedicated hand CAN interface, or rerun with --allow-arm-can only after a documented bus review." >&2
  exit 3
fi

for cmd in ip cansend candump timeout; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

if ! ip link show "$iface" >/dev/null 2>&1; then
  echo "CAN interface not found: $iface" >&2
  exit 1
fi

if ! ip -details link show "$iface" | grep -q "state UP"; then
  echo "CAN interface $iface is not UP. Activate it first at 1000000 bitrate." >&2
  echo "Example: bash scripts/activate_can.sh $iface 1000000" >&2
  exit 4
fi

tmp_file="$(mktemp)"
cleanup() {
  rm -f "$tmp_file"
}
trap cleanup EXIT

echo "S14.3L LinkerHand targeted CAN identification"
echo "interface=$iface"
echo "arm_can_guard=$arm_a_can,$arm_b_can"
echo "This script sends identify/read request frames only; it does not send finger motion commands."
echo

echo "Sending primary identify request: ${iface} 0FF#C0"
timeout 2s candump "$iface" >"$tmp_file" 2>&1 &
dump_pid=$!
sleep 0.1
cansend "$iface" "0FF#C0"
sleep 1
kill "$dump_pid" 2>/dev/null || true
wait "$dump_pid" 2>/dev/null || true

if [ -s "$tmp_file" ]; then
  echo "Primary response frames:"
  cat "$tmp_file"
else
  echo "No primary response frames captured."
fi

echo
echo "Sending fallback identify request: ${iface} 0FF#01"
: >"$tmp_file"
timeout 2s candump "$iface" >"$tmp_file" 2>&1 &
dump_pid=$!
sleep 0.1
cansend "$iface" "0FF#01"
sleep 1
kill "$dump_pid" 2>/dev/null || true
wait "$dump_pid" 2>/dev/null || true

if [ -s "$tmp_file" ]; then
  echo "Fallback response frames:"
  cat "$tmp_file"
else
  echo "No fallback response frames captured."
fi

response_id="$(awk '
  NF >= 2 {
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^[0-9A-Fa-f]+$/) {
        id = toupper($i)
        sub(/^0X/, "", id)
        if (id != "0FF") {
          print id
          exit
        }
      }
    }
  }
' "$tmp_file")"

case "$response_id" in
  28)
    echo "Result: linkerhand_left_detected"
    ;;
  27)
    echo "Result: linkerhand_right_detected"
    ;;
  "")
    echo "Result: no_linkerhand_identity_response"
    ;;
  *)
    echo "Result: unknown_response_id_$response_id"
    ;;
esac
