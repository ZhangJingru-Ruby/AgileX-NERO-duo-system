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

echo "S15 RViz pose diagnostics"
echo "Purpose: diagnose horizontal/zero-pose RViz models."
echo
echo "Expected S11 static TF values:"
echo "  lab_world -> ${NERO_S11_ARM_A_STATIC_TF_CHILD_FRAME:-arm_a/world}: ${NERO_S11_ARM_A_BASE_TF_CANDIDATE:-unset}"
echo "  lab_world -> ${NERO_S11_ARM_B_STATIC_TF_CHILD_FRAME:-arm_b/world}: ${NERO_S11_ARM_B_BASE_TF_CANDIDATE:-unset}"
echo

echo "1) Raw feedback topic publishers/subscribers:"
ros2 topic info -v /arm_a/feedback/joint_states || true
echo
ros2 topic info -v /arm_b/feedback/joint_states || true
echo

echo "2) One feedback sample from each arm:"
if ! timeout 5s ros2 topic echo --once /arm_a/feedback/joint_states; then
  echo "FAILED: no /arm_a/feedback/joint_states sample within 5s." >&2
fi
echo
if ! timeout 5s ros2 topic echo --once /arm_b/feedback/joint_states; then
  echo "FAILED: no /arm_b/feedback/joint_states sample within 5s." >&2
fi
echo

echo "3) Static root TF checks:"
timeout 3s ros2 run tf2_ros tf2_echo lab_world arm_a/world || true
echo
timeout 3s ros2 run tf2_ros tf2_echo lab_world arm_b/world || true
echo

echo "4) End-link TF checks. These should reflect live joint feedback, not URDF zero pose:"
timeout 3s ros2 run tf2_ros tf2_echo lab_world arm_a/link7 || true
echo
timeout 3s ros2 run tf2_ros tf2_echo lab_world arm_b/link7 || true
echo

echo "5) Optional S15 visual-anchor topics:"
ros2 topic info -v /arm_a/visual/joint_states || true
echo
ros2 topic info -v /arm_b/visual/joint_states || true
echo

echo "Interpretation:"
echo "- In raw RViz mode, robot_state_publisher subscribes directly to /arm_*/feedback/joint_states."
echo "- In anchored RViz mode, s15_joint_state_visual_anchor subscribes to /arm_*/feedback/joint_states,"
echo "  and robot_state_publisher subscribes to /arm_*/visual/joint_states."
echo "- If lab_world -> arm_*/world is wrong or missing, the accepted S11 root rotation is not active."
echo "- If neither raw nor anchored subscription topology is present, inspect robot_state_publisher remapping."
echo "- If feedback subscribers and S11 root TF are present but the model is still horizontal, the current raw joint feedback"
echo "  is not in the same visual convention as the S11 accepted RViz posture. Use the S15 visual-anchor path for RViz"
echo "  observation only, and do not use /arm_*/visual/joint_states for control or planning."
