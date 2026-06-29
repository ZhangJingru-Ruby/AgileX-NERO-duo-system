#!/usr/bin/env bash
set -euo pipefail

namespace="${1:-}"
timeout_seconds="${2:-10}"

if [ -z "$namespace" ]; then
  echo "Usage: $0 arm_a|arm_b [timeout_seconds]" >&2
  exit 2
fi

topic="/${namespace}/feedback/hand_status"

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 is not available. Run this script inside the Humble container." >&2
  exit 1
fi

echo "S14 Revo2 hand-status read-only probe"
echo "namespace=$namespace"
echo "topic=$topic"
echo "timeout_seconds=$timeout_seconds"
echo "This script only reads ROS graph/topic data and publishes no commands."
echo

echo "Topic info:"
if ! ros2 topic info -v "$topic"; then
  echo "Result: topic_not_found_or_ros_graph_unavailable"
  exit 3
fi

echo
echo "Waiting for one hand_status message..."
set +e
timeout "${timeout_seconds}s" ros2 topic echo --once "$topic"
rc=$?
set -e

if [ "$rc" -eq 0 ]; then
  echo "Result: hand_status_message_received"
  exit 0
fi

if [ "$rc" -eq 124 ]; then
  echo "Result: no_hand_status_message_within_${timeout_seconds}s"
  exit 124
fi

echo "Result: ros2_topic_echo_failed_exit_${rc}"
exit "$rc"
