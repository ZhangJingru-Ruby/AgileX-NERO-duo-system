#!/usr/bin/env bash
set -euo pipefail

if [ -f /workspace/nero/config/nero.env ]; then
  # shellcheck disable=SC1091
  . /workspace/nero/config/nero.env
elif [ -f config/nero.env ]; then
  # shellcheck disable=SC1091
  . config/nero.env
fi

arm_a_ns="${NERO_ARM_A_ROS_NAMESPACE:-arm_a}"
arm_b_ns="${NERO_ARM_B_ROS_NAMESPACE:-arm_b}"
arm_a_can="${NERO_ARM_A_CAN_PORT:-can_arm_a}"
arm_b_can="${NERO_ARM_B_CAN_PORT:-can_arm_b}"
effector="${NERO_EFFECTOR_TYPE:-none}"
tcp_offset="${NERO_TCP_OFFSET:-[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}"
speed_percent="${NERO_S13_SPEED_PERCENT:-5}"
enable_timeout="${NERO_S13_ENABLE_TIMEOUT:-5.0}"

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

echo "Starting S13 dual-active driver pair."
echo "Arm A: namespace=$arm_a_ns can_port=$arm_a_can auto_enable=true control_enabled=true"
echo "Arm B: namespace=$arm_b_ns can_port=$arm_b_can auto_enable=true control_enabled=true"
echo "Speed percent for both driver instances: $speed_percent"
echo "Enable timeout for both driver instances: $enable_timeout"
echo "This script does not publish motion commands."

cleanup() {
  echo "Stopping S13 dual-active driver pair..."
  kill "${pid_a:-}" "${pid_b:-}" 2>/dev/null || true
  wait "${pid_a:-}" "${pid_b:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
  namespace:="$arm_a_ns" \
  can_port:="$arm_a_can" \
  arm_type:=nero \
  effector_type:="$effector" \
  auto_enable:=true \
  control_enabled:=true \
  enable_timeout:="$enable_timeout" \
  speed_percent:="$speed_percent" \
  tcp_offset:="$tcp_offset" &
pid_a=$!

ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
  namespace:="$arm_b_ns" \
  can_port:="$arm_b_can" \
  arm_type:=nero \
  effector_type:="$effector" \
  auto_enable:=true \
  control_enabled:=true \
  enable_timeout:="$enable_timeout" \
  speed_percent:="$speed_percent" \
  tcp_offset:="$tcp_offset" &
pid_b=$!

wait -n "$pid_a" "$pid_b"
