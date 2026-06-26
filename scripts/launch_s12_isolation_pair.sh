#!/usr/bin/env bash
set -euo pipefail

if [ -f /workspace/nero/config/nero.env ]; then
  # shellcheck disable=SC1091
  . /workspace/nero/config/nero.env
elif [ -f config/nero.env ]; then
  # shellcheck disable=SC1091
  . config/nero.env
fi

active_arm="${1:-}"
if [ "$active_arm" != "arm_a" ] && [ "$active_arm" != "arm_b" ]; then
  echo "Usage: $0 arm_a|arm_b" >&2
  exit 2
fi

arm_a_ns="${NERO_ARM_A_ROS_NAMESPACE:-arm_a}"
arm_b_ns="${NERO_ARM_B_ROS_NAMESPACE:-arm_b}"
arm_a_can="${NERO_ARM_A_CAN_PORT:-can_arm_a}"
arm_b_can="${NERO_ARM_B_CAN_PORT:-can_arm_b}"
effector="${NERO_EFFECTOR_TYPE:-none}"
tcp_offset="${NERO_TCP_OFFSET:-[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}"
speed_percent="${NERO_S12_SPEED_PERCENT:-5}"

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 is not available. Run this script inside the Humble container." >&2
  exit 1
fi

if ! ip link show "$arm_a_can" >/dev/null 2>&1; then
  echo "CAN interface $arm_a_can is not visible." >&2
  exit 1
fi

if ! ip link show "$arm_b_can" >/dev/null 2>&1; then
  echo "CAN interface $arm_b_can is not visible." >&2
  exit 1
fi

if [ "$active_arm" = "arm_a" ]; then
  arm_a_auto_enable=true
  arm_a_control_enabled=true
  arm_b_auto_enable=false
  arm_b_control_enabled=false
else
  arm_a_auto_enable=false
  arm_a_control_enabled=false
  arm_b_auto_enable=true
  arm_b_control_enabled=true
fi

echo "Starting S12 control-isolation driver pair."
echo "Active arm: $active_arm"
echo "Arm A: namespace=$arm_a_ns can_port=$arm_a_can auto_enable=$arm_a_auto_enable control_enabled=$arm_a_control_enabled"
echo "Arm B: namespace=$arm_b_ns can_port=$arm_b_can auto_enable=$arm_b_auto_enable control_enabled=$arm_b_control_enabled"
echo "Speed percent for both driver instances: $speed_percent"
echo "This script does not publish motion commands."

cleanup() {
  echo "Stopping S12 control-isolation driver pair..."
  kill "${pid_a:-}" "${pid_b:-}" 2>/dev/null || true
  wait "${pid_a:-}" "${pid_b:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
  namespace:="$arm_a_ns" \
  can_port:="$arm_a_can" \
  arm_type:=nero \
  effector_type:="$effector" \
  auto_enable:="$arm_a_auto_enable" \
  control_enabled:="$arm_a_control_enabled" \
  speed_percent:="$speed_percent" \
  tcp_offset:="$tcp_offset" &
pid_a=$!

ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
  namespace:="$arm_b_ns" \
  can_port:="$arm_b_can" \
  arm_type:=nero \
  effector_type:="$effector" \
  auto_enable:="$arm_b_auto_enable" \
  control_enabled:="$arm_b_control_enabled" \
  speed_percent:="$speed_percent" \
  tcp_offset:="$tcp_offset" &
pid_b=$!

wait -n "$pid_a" "$pid_b"
