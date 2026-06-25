#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

image="${NERO_CONTAINER_IMAGE:-nero-humble:local}"
host_ws="${NERO_ROS_WS:-${HOME}/agx_arm_ws}"
container_ws="${NERO_CONTAINER_WORKSPACE:-/root/agx_arm_ws}"
container_name="${NERO_CONTAINER_NAME:-nero-humble}"

usage() {
  cat <<USAGE
Usage:
  bash scripts/run_humble_container.sh [--allow-xhost] [command...]

Examples:
  bash scripts/run_humble_container.sh
  bash scripts/run_humble_container.sh ros2 --help
  bash scripts/run_humble_container.sh --allow-xhost rviz2

Notes:
  Run this script as the normal desktop user. By default it calls 'sudo docker'
  internally so \$HOME and workspace paths still point to the operator account.

  --allow-xhost runs 'xhost +local:root' on the host so GUI apps such as RViz
  can connect to the current X11 display. This relaxes local X11 access for
  root processes and should only be used during a controlled debug session.
USAGE
}

allow_xhost=0
args=()
for arg in "$@"; do
  case "$arg" in
    --allow-xhost)
      allow_xhost=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      args+=("$arg")
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed. Install Docker before running the ROS2 Humble container." >&2
  exit 1
fi

docker_cmd=(docker)
if [ "${NERO_USE_SUDO_DOCKER:-1}" = "1" ] && [ "$(id -u)" -ne 0 ]; then
  if ! command -v sudo >/dev/null 2>&1; then
    echo "sudo is required because NERO_USE_SUDO_DOCKER=1." >&2
    exit 1
  fi
  docker_cmd=(sudo docker)
fi

mkdir -p "$host_ws/src"

docker_args=(
  run
  --rm
  --name "$container_name"
  --network host
  --ipc host
  --privileged
  -e "DISPLAY=${DISPLAY:-}"
  -e "QT_X11_NO_MITSHM=1"
  -v "$repo_root:/workspace/nero:rw"
  -v "$host_ws:$container_ws:rw"
)

if [ -t 0 ] && [ -t 1 ]; then
  docker_args+=(-it)
else
  docker_args+=(-i)
fi

if [ -n "${DISPLAY:-}" ] && [ -d /tmp/.X11-unix ]; then
  docker_args+=(-v "/tmp/.X11-unix:/tmp/.X11-unix:rw")
  if [ "$allow_xhost" -eq 1 ]; then
    if command -v xhost >/dev/null 2>&1; then
      xhost +local:root
    else
      echo "xhost not found; GUI programs may not be able to connect to DISPLAY." >&2
    fi
  fi
else
  echo "DISPLAY is not set or /tmp/.X11-unix is missing; GUI programs such as RViz may not work." >&2
fi

if [ "${#args[@]}" -eq 0 ]; then
  args=(bash)
fi

"${docker_cmd[@]}" "${docker_args[@]}" "$image" "${args[@]}"
