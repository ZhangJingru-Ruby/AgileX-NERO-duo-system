#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [ -f "$repo_root/config/nero.env" ]; then
  # shellcheck disable=SC1091
  . "$repo_root/config/nero.env"
fi

image="${NERO_CONTAINER_IMAGE:-nero-humble:local}"
dockerfile="$repo_root/docker/humble/Dockerfile"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed. Install Docker before building the ROS2 Humble image." >&2
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

"${docker_cmd[@]}" build \
  -t "$image" \
  -f "$dockerfile" \
  "$repo_root"

echo "Built Docker image: $image"
