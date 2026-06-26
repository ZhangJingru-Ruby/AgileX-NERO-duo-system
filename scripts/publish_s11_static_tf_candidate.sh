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

arm_a_tf="${NERO_S11_ARM_A_BASE_TF_CANDIDATE:-0.000,0.000,0.000,0,0,0}"
arm_b_tf="${NERO_S11_ARM_B_BASE_TF_CANDIDATE:-0.260,0.000,0.000,0,0,3.1415926}"

parse_tf() {
  local raw="$1"
  local -n out="$2"
  IFS=',' read -r out[0] out[1] out[2] out[3] out[4] out[5] <<<"$raw"
  if [ "${#out[@]}" -ne 6 ]; then
    echo "Invalid TF tuple: $raw" >&2
    exit 1
  fi
}

declare -a arm_a
declare -a arm_b
parse_tf "$arm_a_tf" arm_a
parse_tf "$arm_b_tf" arm_b

echo "Publishing S11 static TF candidates."
echo "lab_world -> arm_a/base_link: ${arm_a[*]}"
echo "lab_world -> arm_b/base_link: ${arm_b[*]}"
echo "Press Ctrl-C to stop the static TF publishers."

cleanup() {
  echo "Stopping S11 static TF publishers..."
  kill "${pid_a:-}" "${pid_b:-}" 2>/dev/null || true
  wait "${pid_a:-}" "${pid_b:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ros2 run tf2_ros static_transform_publisher \
  --x "${arm_a[0]}" --y "${arm_a[1]}" --z "${arm_a[2]}" \
  --roll "${arm_a[3]}" --pitch "${arm_a[4]}" --yaw "${arm_a[5]}" \
  --frame-id lab_world \
  --child-frame-id arm_a/base_link &
pid_a=$!

ros2 run tf2_ros static_transform_publisher \
  --x "${arm_b[0]}" --y "${arm_b[1]}" --z "${arm_b[2]}" \
  --roll "${arm_b[3]}" --pitch "${arm_b[4]}" --yaw "${arm_b[5]}" \
  --frame-id lab_world \
  --child-frame-id arm_b/base_link &
pid_b=$!

wait -n "$pid_a" "$pid_b"
