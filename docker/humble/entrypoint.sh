#!/usr/bin/env bash
set -e

source /opt/ros/humble/setup.bash

if [ -f /root/agx_arm_ws/install/setup.bash ]; then
  source /root/agx_arm_ws/install/setup.bash
fi

exec "$@"
