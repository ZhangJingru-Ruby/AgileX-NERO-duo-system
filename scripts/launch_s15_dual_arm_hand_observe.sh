#!/usr/bin/env bash
set -euo pipefail

if [ -f /workspace/nero/config/nero.env ]; then
  # shellcheck disable=SC1091
  . /workspace/nero/config/nero.env
elif [ -f config/nero.env ]; then
  # shellcheck disable=SC1091
  . config/nero.env
fi

arm_a_can="${NERO_ARM_A_CAN_PORT:-can_arm_a}"
arm_b_can="${NERO_ARM_B_CAN_PORT:-can_arm_b}"

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

echo "Starting S15 dual arm + hand observation session."
echo "This launches:"
echo "  - S13 dual-active arm drivers"
echo "  - S11 accepted static TF publishers"
echo "  - S11 dual model RobotStatePublisher instances and RViz"
echo "It does not send arm or hand motion commands."

cleanup() {
  echo "Stopping S15 observation session..."
  kill "${pid_driver:-}" "${pid_tf:-}" "${pid_view:-}" 2>/dev/null || true
  wait "${pid_driver:-}" "${pid_tf:-}" "${pid_view:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

bash /workspace/nero/scripts/launch_s13_dual_active_pair.sh &
pid_driver=$!

sleep 2

bash /workspace/nero/scripts/publish_s11_static_tf_candidate.sh &
pid_tf=$!

sleep 1

bash /workspace/nero/scripts/launch_s11_dual_model_view.sh &
pid_view=$!

wait -n "$pid_driver" "$pid_tf" "$pid_view"
