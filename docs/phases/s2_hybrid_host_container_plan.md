# S2 Hybrid Host And Container Plan

Date: 2026-06-24

Decision: this shared Ubuntu 20.04 computer will not be reinstalled or upgraded.
NERO bring-up will use a split environment:

- Host Ubuntu 20.04: SDK/CAN-only work, SocketCAN activation, low-level read-only
  checks.
- Docker container Ubuntu 22.04 + ROS2 Humble: `agx_arm_ros`, RViz, ROS topics,
  MoveIt-related setup, and later application integration.

Status on 2026-06-24:

- `docker.io`, `ethtool`, and `python3.8-venv` are installed on the host.
- Docker image `nero-humble:local` is built.
- Host SDK venv `.venv/nero-sdk` imports `python-can=4.5.0` and `pyAgxArm`.
- Container reports Ubuntu 22.04.5, `ROS_DISTRO=humble`, `ros2`, `colcon`, and
  `python-can=4.6.1`.
- `~/agx_arm_ws` builds successfully with 5 packages.

## Why This Is The Selected Plan

- The computer is shared with other users, so OS reinstall/upgrade is not
  allowed.
- The current official NERO ROS route in our workspace is ROS2 through
  `agx_arm_ros`.
- Native ROS2 Humble/Jazzy installation on Ubuntu 20.04 is not the supported
  upstream combination.
- Docker keeps ROS2 dependencies isolated while still allowing the container to
  use host SocketCAN through host networking.

## System-Level Changes

Required:

| Package | Necessity | Risk |
| --- | --- | --- |
| `docker.io` | Required to run the Ubuntu 22.04 + ROS2 Humble container on the Ubuntu 20.04 host. | Installs a daemon and service on the shared machine. Users allowed to control Docker effectively gain high system privileges. To reduce risk, initially use `sudo docker` instead of adding the user to the `docker` group. |
| `ethtool` | Required by CAN setup and diagnostics used by AgileX scripts and SocketCAN troubleshooting. | Low risk. It installs a network diagnostic utility; it does not change network configuration by itself. |

Not planned:

- No host OS reinstall.
- No native ROS2 Humble/Jazzy installation on Ubuntu 20.04.
- No Noetic route unless a separate legacy ROS1 validation plan is requested.
- No automatic addition of `lv-robotics` to the `docker` group.

## Files Added For This Plan

| File | Purpose |
| --- | --- |
| `docker/humble/Dockerfile` | Builds the ROS2 Humble image with ROS control, MoveIt, CAN tools, and Python dependencies. |
| `docker/humble/entrypoint.sh` | Sources ROS2 Humble and the workspace overlay inside the container. |
| `scripts/build_humble_container.sh` | Builds the local Docker image. |
| `scripts/run_humble_container.sh` | Runs the image with host networking, workspace mounts, and optional X11 access for RViz. |
| `scripts/setup_host_sdk_venv.sh` | Creates a project-local host SDK venv using `/usr/bin/python3`, then installs `python-can>=3.3.4` and local `pyAgxArm`. |
| `scripts/fix_ros_ws_permissions.sh` | Repairs host ownership of `~/agx_arm_ws/build`, `install`, and `log` after container builds if needed. |
| `.dockerignore` | Keeps `docs/`, `upstream/`, CAD files, and local venv out of Docker build context. |

## Execution Order

1. Install system packages after explicit operator approval:

   ```bash
   sudo apt-get install -y docker.io ethtool
   ```

2. Build the ROS2 Humble image:

   ```bash
   bash scripts/build_humble_container.sh
   ```

3. Prepare the host SDK-only Python environment:

   ```bash
   bash scripts/setup_host_sdk_venv.sh
   ```

4. Start a shell in the ROS2 Humble container:

   ```bash
   bash scripts/run_humble_container.sh
   ```

5. Clone/build the official ROS workspace inside the mounted workspace:

   ```bash
   cd ~/agx_arm_ws/src
   git clone -b ros2 --recurse-submodules https://github.com/agilexrobotics/agx_arm_ros.git
   git clone https://github.com/agilexrobotics/pyAgxArm.git
   cd ~/agx_arm_ws/src/pyAgxArm
   pip3 install .
   cd ~/agx_arm_ws
   colcon build
   ```

6. If the host shows `~/agx_arm_ws/build`, `install`, or `log` owned by a
   container-mapped user, fix ownership:

   ```bash
   bash scripts/fix_ros_ws_permissions.sh
   ```

## GUI Note

RViz requires X11 access. Use this only during controlled debugging:

```bash
sudo bash scripts/run_humble_container.sh --allow-xhost rviz2
```

`--allow-xhost` runs `xhost +local:root`, which relaxes local X11 access for
root processes. Close the debug session when done. If GUI access becomes a
problem, first verify ROS topics without RViz, then debug X11 separately.

## Acceptance Criteria

S2A host SDK/CAN-only is ready when:

- `candump`, `cansend`, and `ethtool` are available.
- The host venv imports `python-can` and `pyAgxArm`.
- No Conda Python is used for the host SDK venv.

S2B container ROS2 is ready when:

- Docker image `nero-humble:local` builds successfully.
- `ros2` and `colcon` work inside the container.
- `~/agx_arm_ws` builds `agx_arm_ros`.
- The container can see host `can0` once the CAN interface exists.
