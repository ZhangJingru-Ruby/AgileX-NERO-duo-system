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

if ! command -v xacro >/dev/null 2>&1; then
  echo "xacro is not available. Check the Humble container image." >&2
  exit 1
fi

pkg_prefix="$(ros2 pkg prefix agx_arm_description)"
model_path="${pkg_prefix}/share/agx_arm_description/agx_arm_urdf/nero/urdf/nero_description.urdf"
rviz_config="/workspace/nero/rviz/s11_dual_arm.rviz"

if [ ! -f "$model_path" ]; then
  echo "NERO model not found: $model_path" >&2
  exit 1
fi

if [ ! -f "$rviz_config" ]; then
  echo "S11 RViz config not found: $rviz_config" >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"

cleanup() {
  echo "Stopping S11 dual model view..."
  kill "${pid_a:-}" "${pid_b:-}" "${pid_rviz:-}" 2>/dev/null || true
  wait "${pid_a:-}" "${pid_b:-}" "${pid_rviz:-}" 2>/dev/null || true
  rm -rf "$tmp_dir"
}
trap cleanup EXIT INT TERM

robot_description="$(xacro "$model_path")"

write_rsp_params() {
  local node_fqn="$1"
  local frame_prefix="$2"
  local out_file="$3"

  {
    echo "${node_fqn}:"
    echo "  ros__parameters:"
    echo "    frame_prefix: \"${frame_prefix}\""
    echo "    robot_description: |"
    printf '%s\n' "$robot_description" | sed 's/^/      /'
  } >"$out_file"
}

params_a="${tmp_dir}/arm_a_rsp.yaml"
params_b="${tmp_dir}/arm_b_rsp.yaml"
write_rsp_params "/arm_a/robot_state_publisher" "arm_a/" "$params_a"
write_rsp_params "/arm_b/robot_state_publisher" "arm_b/" "$params_b"

echo "Starting S11 dual model view."
echo "Subscribing arm_a model to /arm_a/feedback/joint_states"
echo "Subscribing arm_b model to /arm_b/feedback/joint_states"
echo "RViz fixed frame: lab_world"
echo "This script does not publish control commands."
echo "Arm A robot_state_publisher params: $params_a"
echo "Arm B robot_state_publisher params: $params_b"

ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -r __ns:=/arm_a \
  --params-file "$params_a" \
  -r joint_states:=/arm_a/feedback/joint_states &
pid_a=$!

ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -r __ns:=/arm_b \
  --params-file "$params_b" \
  -r joint_states:=/arm_b/feedback/joint_states &
pid_b=$!

rviz2 -d "$rviz_config" &
pid_rviz=$!

wait -n "$pid_a" "$pid_b" "$pid_rviz"
