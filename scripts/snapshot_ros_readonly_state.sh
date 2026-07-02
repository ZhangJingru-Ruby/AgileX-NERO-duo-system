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

repo_root="/workspace/nero"
if [ ! -d "$repo_root" ]; then
  repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

arm_a_ns="${NERO_ARM_A_ROS_NAMESPACE:-arm_a}"
arm_b_ns="${NERO_ARM_B_ROS_NAMESPACE:-arm_b}"
stamp="$(date +%Y%m%d_%H%M%S)"
out_dir="$repo_root/docs/evidence/ros_snapshots/$stamp"
mkdir -p "$out_dir"
failures=0

run_capture() {
  local label="$1"
  shift
  {
    echo "$ $*"
    "$@"
  } >"$out_dir/$label.txt" 2>&1 || {
    echo "Command failed: $*" >>"$out_dir/$label.txt"
    failures=$((failures + 1))
    return 1
  }
}

run_capture_allow_timeout() {
  local label="$1"
  shift
  {
    echo "$ $*"
    set +e
    "$@"
    local rc=$?
    set -e
    if [ "$rc" -eq 124 ]; then
      echo "Command ended by timeout after the requested sample window."
      return 0
    fi
    return "$rc"
  } >"$out_dir/$label.txt" 2>&1 || {
    echo "Command failed: $*" >>"$out_dir/$label.txt"
    failures=$((failures + 1))
    return 1
  }
}

run_capture "topic_list" ros2 topic list || true

for ns in "$arm_a_ns" "$arm_b_ns"; do
  run_capture "${ns}_joint_states_once" \
    ros2 topic echo --once "/${ns}/feedback/joint_states" || true
  run_capture "${ns}_tcp_pose_once" \
    ros2 topic echo --once "/${ns}/feedback/tcp_pose" || true
  run_capture "${ns}_arm_status_once" \
    ros2 topic echo --once "/${ns}/feedback/arm_status" || true
  run_capture_allow_timeout "${ns}_joint_states_hz_5s" \
    timeout --signal=INT 5s ros2 topic hz "/${ns}/feedback/joint_states" || true
done

cat >"$out_dir/README.md" <<EOF
# S9 ROS Read-Only Snapshot

Timestamp: $stamp

Arm A namespace: $arm_a_ns
Arm B namespace: $arm_b_ns

This snapshot is read-only. It records topic list, one message from joint
states, TCP pose, arm status, and a short joint-state frequency sample for both
arms.

Failed capture commands: $failures
EOF

echo "S9 ROS read-only snapshot written to $out_dir"
if [ "$failures" -ne 0 ]; then
  echo "WARNING: $failures capture command(s) failed. Check files in $out_dir." >&2
  exit 1
fi
