#!/usr/bin/env bash
set -euo pipefail

if [ -f /workspace/nero/config/nero.env ]; then
  # shellcheck disable=SC1091
  . /workspace/nero/config/nero.env
elif [ -f config/nero.env ]; then
  # shellcheck disable=SC1091
  . config/nero.env
fi

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 is not available. Run this script inside the Humble container." >&2
  exit 1
fi

echo "S15 motion-block diagnostics"
echo "Purpose: inspect why a move_j command did not produce motion."
echo "Safety: read-only ROS graph/status inspection; publishes no motion commands."
echo

echo "1) ROS nodes:"
ros2 node list || true
echo

echo "2) move_j command topic topology:"
ros2 topic info -v /arm_a/control/move_j || true
echo
ros2 topic info -v /arm_b/control/move_j || true
echo

echo "3) driver launch/control parameters:"
for node in /arm_a/agx_arm_ctrl_single_node /arm_b/agx_arm_ctrl_single_node; do
  echo "$node"
  for param in can_port arm_type auto_enable control_enabled speed_percent enable_timeout; do
    printf '  %s: ' "$param"
    ros2 param get "$node" "$param" 2>/dev/null || echo "unavailable"
  done
done
echo

echo "4) feedback topic topology:"
ros2 topic info -v /arm_a/feedback/joint_states || true
echo
ros2 topic info -v /arm_b/feedback/joint_states || true
echo

echo "5) current arm status:"
timeout 5s ros2 topic echo --once /arm_a/feedback/arm_status || true
echo
timeout 5s ros2 topic echo --once /arm_b/feedback/arm_status || true
echo

echo "6) current joint feedback:"
timeout 5s ros2 topic echo --once /arm_a/feedback/joint_states || true
echo
timeout 5s ros2 topic echo --once /arm_b/feedback/joint_states || true
echo

echo "7) expected interpretation:"
echo "- For execute mode, the active arm's /control/move_j topic must have at least one subscriber."
echo "- A subscriber alone is not enough: the driver parameters must show control_enabled=true for execute."
echo "- If feedback exists but /control/move_j has no subscriber, the active driver is not the process receiving commands."
echo "- If a previous timeout called emergency_stop, stop/restart the S15 active observation session before retrying execute."
echo "- If command subscribers exist and the arm still does not move, inspect the active-driver terminal for rejection/error logs."
