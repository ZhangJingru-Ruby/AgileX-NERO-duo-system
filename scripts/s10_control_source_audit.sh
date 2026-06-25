#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

arm_a_can="${NERO_ARM_A_CAN_PORT:-can_arm_a}"
arm_b_can="${NERO_ARM_B_CAN_PORT:-can_arm_b}"

echo "S10.4 control-source audit"
echo "Timestamp: $(date --iso-8601=seconds)"
echo

echo "CAN interfaces:"
for can_if in "$arm_a_can" "$arm_b_can"; do
  if ip -details link show "$can_if" >/dev/null 2>&1; then
    ip -details link show "$can_if" | sed 's/^/  /'
  else
    echo "  $can_if: not visible"
  fi
done
echo

echo "NERO-related Docker containers:"
docker_cmd=()
if command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1; then
  docker_cmd=(docker)
elif command -v sudo >/dev/null 2>&1 && sudo -n docker ps >/dev/null 2>&1; then
  docker_cmd=(sudo docker)
fi

if [ "${#docker_cmd[@]}" -gt 0 ]; then
  "${docker_cmd[@]}" ps --format '  {{.Names}}\t{{.Status}}\t{{.Command}}' | grep -E 'nero|agx|ros|humble' || echo "  none"
else
  echo "  docker ps unavailable without interactive sudo"
fi
echo

echo "NERO-related host processes:"
pgrep -af 'run_humble_container|ros_single_joint_step|nero_sdk_single_joint_step|launch_dual_ros_readonly|agx_arm_ctrl|ros2 launch' | sed 's/^/  /' || echo "  none"
echo

echo "Expected S10.4 handoff state before Arm B motion:"
echo "  - no Arm A ROS control container running"
echo "  - no SDK motion script running"
echo "  - no Web motion command active"
echo "  - CAN interfaces may remain UP"
echo "  - dual read-only driver may run only for monitoring; stop it before Arm B Web/SDK/ROS motion"
