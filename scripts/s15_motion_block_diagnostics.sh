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

echo "3) feedback topic topology:"
ros2 topic info -v /arm_a/feedback/joint_states || true
echo
ros2 topic info -v /arm_b/feedback/joint_states || true
echo

echo "4) current arm status:"
timeout 5s ros2 topic echo --once /arm_a/feedback/arm_status || true
echo
timeout 5s ros2 topic echo --once /arm_b/feedback/arm_status || true
echo

echo "5) current joint feedback:"
timeout 5s ros2 topic echo --once /arm_a/feedback/joint_states || true
echo
timeout 5s ros2 topic echo --once /arm_b/feedback/joint_states || true
echo

echo "6) expected interpretation:"
echo "- For execute mode, the active arm's /control/move_j topic must have at least one subscriber."
echo "- If feedback exists but /control/move_j has no subscriber, the active driver is not the process receiving commands."
echo "- If a previous timeout called emergency_stop, stop/restart the S15 active observation session before retrying execute."
echo "- If command subscribers exist and the arm still does not move, inspect the active-driver terminal for rejection/error logs."
