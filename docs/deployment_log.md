# NERO Deployment Log

This file records actual deployment and debugging steps. It is the durable
history of what was done, what was observed, and what changed.

## 2026-06-24 - S0/S1 Baseline And Agent Rules

Phase: S0 资料基线 / S1 安全与场地

Goal:
Create a working rule set before entering S2 so future setup steps remain
faithful to local documents, verified facts, and observed results.

Action:
Added `agent.md` as the operating rule file for future deployment work.

Commands / evidence:
Local project already contains the user manual text, CAN protocol, CAD assets,
and key manual images under `docs/` and `docs/pics/`.

Result:
S0 is complete. S1 is complete for planning, with final physical checks required
before any power-on or robot motion.

Deployment choices:
Current bring-up remains bare-arm first. Dexterous hand installation is deferred
to S11. Initial ROS `effector_type` remains `none`.

Files changed:
`agent.md`, `docs/deployment_log.md`, `README.md`,
`docs/机器人部署与调试行动路线.md`.

Verification:
Passed lightweight checks:

- `bash -n scripts/check_environment.sh`
- `bash -n scripts/activate_can.sh`
- Python AST parse for `examples/nero_read_state.py`
- `rg` check confirmed `agent.md`, `deployment_log.md`, and route links are present.

Route updates:
The action route now includes the agent operating requirement: after every
deployment step, record evidence and correct the route.

Open risks:
S2 host dependencies are not installed yet: ROS2, colcon, ethtool, python-can,
pyAgxArm, and agx_arm_ros workspace remain pending.

Next:
Enter S2 主机环境 after reviewing this agent rule file.

## 2026-06-24 - S2.1 Host Environment Discovery

Phase: S2 主机环境

Goal:
Check whether the current machine can be used as the ROS2/SDK deployment host
for NERO.

Action:
Ran the local environment check and additional read-only host diagnostics.

Commands / evidence:

- `bash scripts/check_environment.sh`
- `lsb_release -a`
- `python3 --version`
- `pip3 --version`
- `ls /opt/ros`
- `apt-cache policy ros-humble-ros-base ros-jazzy-ros-base ros-foxy-ros-base python3-colcon-common-extensions ethtool python3-can`
- `/usr/bin/python3 --version`
- `which python3`
- `which pip3`
- `printenv PATH`
- ROS REP 2000 was checked as upstream evidence for ROS distribution target
  platforms.

Result:

- OS is Ubuntu 20.04.6 LTS (`focal`).
- No ROS installation exists under `/opt/ros`.
- `ros2` is missing.
- `colcon` is missing.
- `ethtool` is missing.
- `python-can` is not importable.
- `pyAgxArm` is not importable.
- `agx_arm_ros` and `pyAgxArm` are not cloned under `~/agx_arm_ws/src`.
- Current shell `python3` and `pip3` resolve to Miniconda Python 3.13.
- System Python is `/usr/bin/python3`, version 3.8.10.
- Ubuntu apt currently shows packages for `ethtool` and `python3-can`, but no
  visible package candidate for `ros-humble-ros-base`, `ros-jazzy-ros-base`, or
  `python3-colcon-common-extensions`.
- ROS REP 2000 lists Humble as Tier 1 on Ubuntu Jammy 22.04, with Ubuntu Focal
  20.04 only Tier 3/source support.
- ROS REP 2000 lists Jazzy as Tier 1 on Ubuntu Noble 24.04.

Deployment choices:
No install was performed. S2 now needs an explicit ROS host strategy before
installing dependencies or cloning/building the ROS workspace.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`.

Verification:
Read-only diagnostics completed successfully. Environment check correctly
reports S2 blockers.

Route updates:
The route is corrected to mark Ubuntu 20.04 + Conda Python 3.13 as a blocker for
the default Humble/Jazzy path. S2 now requires choosing a supported ROS host
strategy.

Open risks:

- Upstream `agx_arm_ros` route targets Humble/Jazzy, while the current OS is
  Ubuntu 20.04.
- Conda Python 3.13 is first in `PATH`; ROS apt work should use system Python in
  a clean shell.
- Installing packages on this machine may create a partially supported ROS setup
  if the OS strategy is not decided first.

Next:
Choose the S2 host strategy: recommended Ubuntu 22.04 + ROS2 Humble, alternative
Ubuntu 24.04 + ROS2 Jazzy, or an isolated container/VM strategy if the host must
remain Ubuntu 20.04.

## 2026-06-24 - S2.2 Environment Check Script Correction

Phase: S2 主机环境

Goal:
Make the environment checker expose the Python environment risk discovered
during S2.1.

Action:
Updated `scripts/check_environment.sh` to print the active `python3` path, active
`pip3` path, and `/usr/bin/python3` version. It now warns if `python3` resolves
to Conda/Miniconda/Anaconda.

Commands / evidence:

- `bash -n scripts/check_environment.sh`
- `bash scripts/check_environment.sh`

Result:
The script reports:

- active `python3`: `/home/lv-robotics/miniconda3/bin/python3`
- active `pip3`: `/home/lv-robotics/miniconda3/bin/pip3`
- system Python: `Python 3.8.10`
- warning: ROS apt work should use a clean system Python shell

Deployment choices:
No ROS install was performed. The S2 host strategy remains undecided.

Files changed:
`scripts/check_environment.sh`, `docs/deployment_log.md`.

Verification:
`bash -n scripts/check_environment.sh` passed. Running the check reports the
expected S2 blockers and the new Conda Python warning.

Route updates:
No additional route structure change was needed beyond the existing S2 host
strategy blocker. The script now enforces that blocker more visibly.

Open risks:
Same as S2.1.

Next:
Choose the S2 host strategy before installing ROS or cloning/building the ROS
workspace.

## 2026-06-24 - S2.3 Noetic Strategy Evaluation

Phase: S2 主机环境

Goal:
Evaluate whether ROS Noetic can be selected for the NERO bring-up because the
current host is Ubuntu 20.04.

Action:
Checked official ROS distribution metadata and the upstream AgileX ROS package
direction.

Commands / evidence:

- ROS rosdistro index reports `noetic` as `distribution_type: ros1` and
  `distribution_status: end-of-life`.
- ROS REP 3 lists Noetic as May 2020 - May 2025, with required support for
  Ubuntu Focal 20.04 and Python 3.8.
- Upstream `agx_arm_ros` README identifies the current package as an AgileX ROS2
  driver, shows Humble/Jazzy passing, and describes support for Piper/Nero.

Result:
Noetic is technically compatible with the current Ubuntu 20.04 host, but it is
ROS1 and already end-of-life. It is not the recommended NERO bring-up path unless
there is a hard legacy ROS1 integration requirement.

Deployment choices:
No install was performed. Recommended S2 strategy remains Ubuntu 22.04 + ROS2
Humble, unless the project explicitly chooses a legacy ROS1 route.

Files changed:
`docs/deployment_log.md`, `docs/机器人部署与调试行动路线.md`,
`docs/current_bringup_status.md`.

Verification:
Evaluation is documented. No system state was changed.

Route updates:
The S2 route now includes a Noetic decision note: possible for legacy ROS1 only,
not recommended for the default NERO setup.

Open risks:
Choosing Noetic would require finding or maintaining a ROS1-compatible NERO
driver path, remapping expected topics/interfaces, and accepting EOL ROS
infrastructure risk.

Next:
User decision: keep recommended Humble route or intentionally switch to a legacy
Noetic route with a separate validation plan.

## 2026-06-24 - S2.4 Upstream Repository Clone And ROS Strategy Correction

Phase: S2 主机环境

Goal:
Clone the user-specified upstream repositories into the project workspace, read
their current contents, and decide the most reasonable ROS strategy from
repository evidence rather than assumption.

Action:
Created local upstream evidence clones under `upstream/`:

- `agx_arm_ros`
- `pyAgxArm`
- `piper_ros`
- `agx_arm_ros/src/agx_arm_description/agx_arm_urdf` submodule

Commands / evidence:

- `git clone -b humble_beta1 https://github.com/agilexrobotics/piper_ros.git upstream/piper_ros`
- `git clone https://github.com/agilexrobotics/pyAgxArm.git upstream/pyAgxArm`
- `git clone -b ros2 https://github.com/agilexrobotics/agx_arm_ros.git upstream/agx_arm_ros`
- `git -C upstream/agx_arm_ros submodule update --init --recursive`
- `sed` review of upstream README, `package.xml`, `CMakeLists.txt`, launch files,
  install script, SDK setup file, and URDF README.

Observed repository states:

| Repository | Branch | Commit | Key observation |
| --- | --- | --- | --- |
| `agx_arm_ros` | `ros2` | `c73d33f` | README identifies it as the AgileX ROS2 driver, with Humble/Jazzy pass status and NERO support. |
| `pyAgxArm` | `master` | `a226840` | SDK supports Ubuntu 18.04/20.04/22.04/24.04 and Python 3.6+, requires `python-can>=3.3.4`. |
| `piper_ros` | `humble_beta1` | `2dc30fc` | Requested `nero_description` package is `ament_cmake`/`rviz2` model description, not a NERO control driver. |
| `agx_arm_urdf` submodule | submodule | `f6642ce` | Contains current NERO URDF/Xacro assets for bare arm, gripper, and Revo2 variants. |

Result:
The default NERO ROS deployment route should remain ROS2, not Noetic. The most
reasonable ROS host remains Ubuntu 22.04 + ROS2 Humble, with Ubuntu 24.04 +
ROS2 Jazzy as an alternative. The current Ubuntu 20.04 host can still be used
for SDK/CAN-only readout preparation because `pyAgxArm` supports Ubuntu 20.04,
but it should not be treated as a completed ROS environment.

Deployment choices:

- Split S2 into S2A SDK/CAN-only and S2B ROS host preparation.
- Keep initial ROS parameters as `arm_type:=nero`, `effector_type:=none` for
  the bare-arm phase.
- Defer dexterous hand configuration to S11.
- Do not choose Noetic unless there is a hard legacy ROS1 requirement and a
  separate validation plan is created.

Files changed:
`docs/upstream_repo_analysis.md`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/机器人部署与调试行动路线.md`,
`README.md`, `docs/setup_framework.md`, `docs/bringup_checklist.md`,
`config/nero.env`.

Verification:
Repository clones and submodule are present locally. Read-only checks confirmed:

- `agx_arm_ros` is a ROS2/ament/rclpy workspace.
- `piper_ros` NERO path is an ament model package.
- `pyAgxArm` can support SDK-only work on Ubuntu 20.04 if Python dependencies
  meet version requirements.

Route updates:
The action route now records the upstream clone evidence, the ROS2 strategy, the
Noetic correction, and the S2A/S2B split. The checklist S2/S3/S4 numbering was
also corrected to match the main route.

Open risks:

- Current host still lacks `ros2`, `colcon`, `ethtool`, `python-can`, and
  `pyAgxArm` import.
- Current shell still resolves `python3`/`pip3` to Miniconda Python 3.13.
- Ubuntu Focal apt candidate for `python3-can` is `3.3.2`, below the SDK
  requirement, so SDK-only setup needs pip or another isolated dependency path.
- ROS2 workspace build has not been attempted because a supported ROS2 host has
  not yet been selected.

Next:
Choose whether to proceed with S2A on this Ubuntu 20.04 host first, or prepare a
Ubuntu 22.04 + ROS2 Humble host for S2B.

## 2026-06-24 - S2.5 Upstream Repository Role Clarification

Phase: S2 主机环境

Goal:
Before choosing the next S2 track, clarify what the three user-provided GitHub
repositories are, what role each one plays, and how each should be used later.

Action:
Updated `agent.md` and the main action route with explicit repository role
boundaries.

Commands / evidence:

- Re-read `agent.md`.
- Re-read `docs/机器人部署与调试行动路线.md`.
- Re-read `docs/upstream_repo_analysis.md`.
- Used the local upstream clone evidence recorded in S2.4.

Result:
The project now treats the three repositories as distinct layers:

| Repository | Role | Later use |
| --- | --- | --- |
| `agx_arm_ros` | Main ROS2 integration/control workspace for NERO. | Use for S2B ROS host setup, S3 model display, S8 ROS read-only feedback, and later MoveIt/application work. |
| `pyAgxArm` | Python SDK and CAN hardware access layer. | Use for S2A SDK/CAN-only preparation and S7 read-only state checks; no motion before motion gates. |
| `piper_ros` | Reference source for the user-provided NERO URDF path on branch `humble_beta1`. | Use only for model cross-checking and historical comparison, not as the default NERO control workspace. |

Deployment choices:

- `agx_arm_ros` remains the default ROS route.
- `pyAgxArm` remains the SDK-only route for current Ubuntu 20.04 preparation.
- `piper_ros` is demoted from possible runtime route to reference/model evidence
  unless a separate validation plan is written.
- `agx_arm_ros` submodule `agx_arm_urdf` is the preferred runtime model source
  for the ROS2 route.

Files changed:
`agent.md`, `docs/机器人部署与调试行动路线.md`, `docs/deployment_log.md`.

Verification:
Role boundaries are present in both `agent.md` and the main route. No install,
build, hardware connection, or robot command was executed.

Route updates:
The main route now has an "上游仓库职责边界" section and S2 now points back to
that boundary while preserving commit-level evidence.

Open risks:
No new technical risk. S2 environment blockers remain unchanged:
`ros2`, `colcon`, `ethtool`, `python-can`, and `pyAgxArm` import are still not
ready on the current host.

Next:
Choose whether to proceed with S2A SDK/CAN-only preparation on this host, or
prepare the S2B ROS2 Humble/Jazzy host.

## 2026-06-24 - S2.6 Shared Host Hybrid Deployment Plan

Phase: S2 主机环境

Goal:
Adopt a practical deployment plan because this Ubuntu 20.04 computer is the
only NERO deployment machine and cannot be reinstalled or upgraded due to other
users.

Action:
Selected and documented the hybrid host/container plan:

- Host Ubuntu 20.04 remains in place for SDK/CAN-only work.
- Docker runs Ubuntu 22.04 + ROS2 Humble for the official `agx_arm_ros` route.
- The project will use `sudo docker` initially instead of adding the operator to
  the `docker` group.

Commands / evidence:

- `command -v docker` returned missing.
- `command -v podman` returned missing.
- `command -v candump` returned `/usr/bin/candump`.
- `command -v cansend` returned `/usr/bin/cansend`.
- `command -v ethtool` returned missing.
- `/usr/bin/python3 -m venv --help` works.
- `apt-cache policy docker.io ethtool python3-venv python3-pip` showed
  available `docker.io` and `ethtool` packages on Ubuntu Focal.

Result:
The selected S2 strategy is now:

- S2A: host SDK/CAN-only with a project-local venv using `/usr/bin/python3`.
- S2B: Docker image `nero-humble:local` based on ROS2 Humble desktop, used for
  `agx_arm_ros`, RViz, ROS topics, and later MoveIt.

Deployment choices:

- No OS reinstall or in-place upgrade.
- No native ROS2 Humble/Jazzy installation on Ubuntu 20.04.
- No Noetic default route.
- System-level changes are limited to `docker.io` and `ethtool`, with risk and
  necessity to be stated before installation.
- Docker group membership is not changed by default.

Files changed:
`config/nero.env`, `docker/humble/Dockerfile`, `docker/humble/entrypoint.sh`,
`scripts/build_humble_container.sh`, `scripts/run_humble_container.sh`,
`scripts/setup_host_sdk_venv.sh`, `docs/s2_hybrid_host_container_plan.md`,
`docs/机器人部署与调试行动路线.md`, `docs/current_bringup_status.md`,
`docs/bringup_checklist.md`, `docs/setup_framework.md`, `README.md`,
`agent.md`, `docs/deployment_log.md`.

Verification:
Pending after script syntax checks and environment check. No install, Docker
build, ROS build, hardware connection, or robot command has been executed yet.

Route updates:
The main route now treats the hybrid host/container path as the selected S2
strategy. S2 acceptance criteria now separate host SDK/CAN-only readiness from
Docker ROS2 Humble readiness.

Open risks:

- Docker is not installed yet.
- `ethtool` is not installed yet.
- Docker image build requires network and package downloads.
- RViz GUI access through X11 may need separate display permission handling.
- Current shell still resolves `python3` to Conda, so host SDK setup must use
  `/usr/bin/python3`.

Next:
Run syntax checks. Then request approval for the system-level installation of
`docker.io` and `ethtool`, explicitly stating risk and necessity.

## 2026-06-24 - S2.7 System Install Approval Blocked

Phase: S2 主机环境

Goal:
Install the two required system packages for the selected hybrid plan:
`docker.io` and `ethtool`.

Action:
Requested escalated execution of:

```bash
sudo apt-get install -y docker.io ethtool
```

Commands / evidence:

- The request stated the necessity of Docker for Ubuntu 22.04/ROS2 Humble
  container deployment without reinstalling the shared Ubuntu 20.04 host.
- The request stated the risk that Docker installs a persistent high-privilege
  daemon/service and that Docker control is effectively high privilege.
- The request stated the lower risk of `ethtool` as a diagnostic utility.

Result:
The escalation was rejected by safety policy because explicit user approval is
required after stating the concrete risks of installing Docker on a shared
machine. No package was installed.

Deployment choices:
No change. Continue to use the selected hybrid plan, but block system package
installation until the user explicitly approves this exact system-level change.

Files changed:
`docs/deployment_log.md`.

Verification:
No installation occurred. Current S2 failures remain `docker` and `ethtool`
missing.

Route updates:
No route change. The route already records the risk and necessity of Docker and
`ethtool`.

Open risks:
Docker installation remains a shared-host security decision.

Next:
Ask the user for explicit approval to install `docker.io` and `ethtool`.

## 2026-06-24 - S2.8 Hybrid Environment Installation And Build

Phase: S2 主机环境

Goal:
Complete the selected hybrid host/container S2 environment on the shared Ubuntu
20.04 machine.

Action:
After explicit user approval, installed required host packages, prepared the
host SDK venv, built the ROS2 Humble Docker image, cloned the official ROS
workspace, and built `agx_arm_ros` in the container.

Commands / evidence:

- `sudo apt-get update`
- `sudo apt-get install -y docker.io ethtool`
- `sudo docker info`
- `bash scripts/check_environment.sh`
- `sudo apt-get install -y python3.8-venv`
- `bash scripts/setup_host_sdk_venv.sh`
- `bash scripts/build_humble_container.sh`
- `bash scripts/run_humble_container.sh ...`
- `git clone -b ros2 --recurse-submodules https://github.com/agilexrobotics/agx_arm_ros.git /home/lv-robotics/agx_arm_ws/src/agx_arm_ros`
- `git clone https://github.com/agilexrobotics/pyAgxArm.git /home/lv-robotics/agx_arm_ws/src/pyAgxArm`
- Container: `cd /root/agx_arm_ws/src/pyAgxArm && pip3 install .`
- Container: `cd /root/agx_arm_ws && colcon build`
- `sudo chown -R lv-robotics:lv-robotics /home/lv-robotics/agx_arm_ws/build /home/lv-robotics/agx_arm_ws/install /home/lv-robotics/agx_arm_ws/log`

Result:

- Host package install succeeded.
- Docker version: `26.1.3`.
- Docker daemon check passed via `sudo docker info`.
- `ethtool` version: `5.4`.
- Current user groups remain `lv-robotics nogroup`; the user was not added to
  the `docker` group.
- Host SDK venv `.venv/nero-sdk` is ready.
- Host SDK venv imports `python-can=4.5.0` and `pyAgxArm`.
- Docker image `nero-humble:local` exists, image ID `cd76a30091d2`, size about
  `3.65GB`.
- Container reports Ubuntu `22.04.5 LTS`, `ROS_DISTRO=humble`, `ros2`,
  `colcon`, and `python-can=4.6.1`.
- ROS workspace build completed: 5 packages finished.
- Built packages include `agx_arm_msgs`, `agx_arm_description`, `pyAgxArm`,
  `agx_arm_ctrl`, and `agx_arm_moveit`.
- `pyAgxArm` emitted packaging warnings about excluded directories/cache files;
  this did not fail the build.
- Container install-space verification passed:
  `agx_arm_ctrl`, `agx_arm_description`, `agx_arm_moveit`, and `pyAgxArm`
  import are available.

Deployment choices:

- Keep `sudo docker` strategy; do not add `lv-robotics` to the `docker` group.
- Keep host-native ROS2 absent; ROS2/colcon are expected only inside the Humble
  container.
- Use `.venv/nero-sdk` for host SDK/CAN-only checks.
- Use `~/agx_arm_ws` as the mounted ROS workspace for container builds.

Files changed:
`.dockerignore`, `scripts/setup_host_sdk_venv.sh`,
`scripts/fix_ros_ws_permissions.sh`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/机器人部署与调试行动路线.md`,
`docs/s2_hybrid_host_container_plan.md`, `README.md`.

Verification:

- `bash scripts/check_environment.sh` exits with 0 failures.
- Container verification reports:
  - `ROS_DISTRO=humble`
  - `/opt/ros/humble/bin/ros2`
  - `/usr/bin/colcon`
  - `python-can 4.6.1`
  - `Ubuntu 22.04.5 LTS`
- ROS package prefix checks passed for `agx_arm_ctrl`, `agx_arm_description`,
  and `agx_arm_moveit`.

Route updates:
S2 is now marked complete for offline preparation. The next route phase is S3
离线模型. CAN interface detection is deferred to S6 because real hardware was
not connected.

Open risks:

- Docker image is large, about `3.65GB`.
- RViz/X11 GUI has not been tested yet.
- CAN interface is not present because the USB-CAN/robot is not connected.
- Container builds may leave host workspace artifacts with mapped ownership;
  use `bash scripts/fix_ros_ws_permissions.sh` if needed.

Next:
Proceed to S3 离线模型 in the ROS2 Humble container. Do not connect or move real
hardware yet.

## 2026-06-24 - S3.1 Offline NERO Model Validation

Phase: S3 离线模型

Goal:
Validate the NERO runtime model in the Docker ROS2 Humble environment before any
real hardware connection or motion.

Action:
Inspected `agx_arm_description` launch/model files, expanded NERO URDF/Xacro
models, ran `check_urdf`, verified mesh references, and tested
`robot_state_publisher` loading.

Commands / evidence:

- Read `agx_arm_description/launch/display.launch.py`.
- Listed NERO model files under
  `agx_arm_urdf/nero/urdf` and `agx_arm_urdf/nero/meshes`.
- Container: `xacro` expansion for:
  - `nero_description.urdf`
  - `nero_with_gripper_description.xacro`
  - `nero_with_left_revo2_description.xacro`
  - `nero_with_right_revo2_description.xacro`
  - `nero_with_revo2_flange_description.xacro`
- Container: `check_urdf` for the same models.
- Container: XML parse for links, joints, joint origins, axes, limits, and mesh
  references.
- Container: `robot_state_publisher` load test using a temporary parameter file.
- Container: `display.launch.py arm_type:=nero effector_type:=none gui:=false
  control:=true` with `QT_QPA_PLATFORM=offscreen`.

Result:

- Runtime model source is `agx_arm_description` using `agx_arm_urdf` submodule
  commit `f6642ce`.
- Current bare-arm model is `nero/urdf/nero_description.urdf`.
- All checked NERO models expand with `xacro` and pass `check_urdf`.
- Bare-arm model has robot name `nero`, 9 links, 8 joints, and chain:
  `world -> base_link -> link1 -> link2 -> link3 -> link4 -> link5 -> link6 -> link7`.
- Bare-arm model has 16 mesh references and 0 missing mesh files.
- `robot_state_publisher` successfully loaded segments `world`, `base_link`,
  and `link1` through `link7`.
- `display.launch.py` supports `arm_type:=nero`, `effector_type:=none`,
  `gui`, `control`, `follow`, `tcp_offset`, and related topic arguments.
- `display.launch.py` always starts RViz; `gui:=false` disables
  `joint_state_publisher_gui`, not RViz.
- RViz failed in the current shell because X11 display `:1` is not accessible:
  `No protocol specified`, `Unable to open display`, and OGRE
  `RenderingAPIException`.

Deployment choices:

- Keep the active model as bare arm: `arm_type:=nero`, `effector_type:=none`.
- Do not enable gripper/Revo2/dexterous-hand models until S11.
- Treat S3 as non-GUI complete, with RViz GUI verification pending in a real
  desktop session.
- Keep manual joint limits as the safety source until live feedback confirms
  the URDF/mechanical angle mapping.

Files changed:
`docs/s3_model_validation.md`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/机器人部署与调试行动路线.md`,
`docs/bringup_checklist.md`.

Verification:

- `xacro` succeeded for 5 NERO models.
- `check_urdf` succeeded for 5 NERO models.
- Mesh reference check passed: `16` references, `0` missing.
- `robot_state_publisher` loaded the bare-arm model.
- Launch test confirmed model load but RViz failed only at X11 display access.

Route updates:
S3 now records non-GUI model validation, the RViz/X11 blocker, and a joint-limit
mapping finding for J2.

Open risks:

- RViz visual inspection is not complete because the current shell cannot access
  the desktop X11 display.
- URDF `joint2` limit is approximately `-99.69..99.69 deg`, while the local
  manual records J2 as `-15..190 deg`. This likely reflects a zero/mapping
  convention difference, but it must be confirmed later with Web/CAN/SDK/ROS
  feedback on the real arm.

Next:
Retry RViz from a real desktop session, or explicitly accept non-GUI S3
validation as sufficient to prepare S4. Do not connect or move real hardware
until the next phase gate is clear.

## 2026-06-24 - S3.2 Desktop RViz GUI Validation

Phase: S3 离线模型

Goal:
Complete the RViz GUI portion of S3 from a real desktop terminal.

Action:
The operator ran the Docker Humble RViz launch from the desktop session:

```bash
bash scripts/run_humble_container.sh --allow-xhost \
  ros2 launch agx_arm_description display.launch.py \
  arm_type:=nero \
  effector_type:=none \
  gui:=false \
  control:=true
```

Commands / evidence:

- `--allow-xhost` added local root access:
  `non-network local connections being added to access control list`.
- `joint_state_publisher`, `robot_state_publisher`, and `rviz2` started.
- `robot_state_publisher` reported segments:
  `base_link`, `link1`, `link2`, `link3`, `link4`, `link5`, `link6`, `link7`,
  and `world`.
- `rviz2` reported:
  - `Stereo is NOT SUPPORTED`
  - `OpenGl version: 4.5 (GLSL 4.5)`
- The launch was stopped with Ctrl-C.
- `joint_state_publisher`, `robot_state_publisher`, and `rviz2` finished
  cleanly.
- The operator revoked X11 permission:

```bash
xhost -local:root
xhost
```

- Final `xhost` output:
  `access control enabled, only authorized clients can connect` and
  `SI:localuser:lv-robotics`.

Result:
S3 RViz GUI validation is complete. The earlier RViz failure was confirmed to be
a non-desktop X11 authorization issue, not a model/URDF issue.

Deployment choices:

- Keep current active offline model as bare arm:
  `arm_type:=nero`, `effector_type:=none`.
- Proceed to S4 机械与电气连接.
- No real robot was connected and no motion command was issued during S3.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/s3_model_validation.md`, `docs/机器人部署与调试行动路线.md`,
`docs/bringup_checklist.md`.

Verification:
The operator-provided terminal log satisfies the S3 RViz GUI acceptance
criteria: RViz started, OpenGL initialized, robot segments loaded, processes
exited cleanly, and temporary X11 permission was revoked.

Route updates:
S3 is now marked complete. The current route advances to S4 mechanical and
electrical connection.

Open risks:

- J2 URDF/manual angle mapping discrepancy remains open until live feedback
  comparison in S6-S8.
- No hardware connection has been verified yet.

Next:
Begin S4 with physical fixation, cable identification, CAN wiring, power
inspection, and final pre-power safety checks. Do not issue motion commands.

## 2026-06-24 - S4/S5.1 Power-On And Web Read-Only Observation

Phase: S4 机械与电气连接 / S5 Web 验机

Goal:
Record the first successful power-on and determine what the Web page currently
proves before moving to CAN/SDK/ROS hardware checks.

Action:
Reviewed the user-provided Web screenshot saved at
`docs/pics/S4 上电与 S5 Web 只读验机.png`.

Commands / evidence:

- Web URL visible: `http://192.168.31.1/#/welcome`.
- UI title: `松灵机器人`.
- Current account: `admin`.
- Visible joint tabs: `关节1` through `关节7`.
- Footer: version `v1.121`, model `7ax`.
- `关节1` visible values:
  - bus voltage `23.8 V`
  - bus current `0.0 A`
  - driver temperature `29.0 degC`
  - motor temperature `22.0 degC`
  - undervoltage `否`
  - motor overtemperature `否`
  - overcurrent `否`
  - driver overtemperature `否`
  - collision protection `否`
  - driver error `否`
  - driver disabled `是`
  - stall protection `否`

Result:

- Power-on succeeded and the Web UI is reachable.
- The visible UI represents one NERO `7ax` controller/arm with seven joint tabs.
- `驱动失能: 是` is expected before deliberate enable; this is not a fault by
  itself.

Deployment choices:

- Continue S5 as read-only Web validation.
- Do not click `使能`, `清除错误`, motion, zeroing, firmware upgrade, master/slave,
  or dexterous-hand controls yet.
- If a second physical arm is expected, treat it as a separate controller/IP or
  device until documentation or live evidence proves otherwise.

Files changed:
`agent.md`, `docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`, `docs/bringup_checklist.md`.

Verification:
The screenshot contains a live Web session, model `7ax`, and readable joint
status fields for `关节1`.

Route updates:
The route no longer says the robot is unconnected. It now records that power-on
and Web access succeeded, and that S5 requires read-only checks for all seven
joint tabs before S6 CAN read-only capture.

Open risks:

- Final S4 wiring/fixation photo evidence is not fully archived yet.
- Only `关节1` status is visible in the screenshot; `关节2` through `关节7` still
  need read-only Web verification.
- Footer version `v1.121` must be clarified as software, firmware, or both
  before choosing the SDK firmware selector.

Next:
Complete S5 Web read-only validation by checking `关节1` through `关节7`, recording
version/status information, and confirming whether the physical setup is a single
arm or includes another independent controller.

## 2026-06-24 - S5.2 Dual-Arm Network Identity Correction

Phase: S5 Web 验机

Goal:
Correct the bring-up route after confirming that the site has two physical NERO
arms, not one.

Action:
Reviewed the new network configuration screenshot
`docs/pics/网络配置页面截图.png`, checked the local user manual network sections,
and updated the route to treat the system as a two-arm deployment with per-arm
identity checks.

Commands / evidence:

- User report: the site has a second physical arm with independent power.
- User report: the currently connected arm's other seven joint tabs are normal.
- Screenshot: Arm A Web network page at
  `http://192.168.31.1/#/settings/sys`.
- Screenshot: Arm A hotspot name `agx-7ax-xin`.
- Screenshot: Arm A hotspot password `12345678`.
- Screenshot: Arm A hotspot channel `9`.
- Manual section 4.1: default Wi-Fi SSID pattern `agx-7ax-xx`, password
  `12345678`, Web address `192.168.31.1`, login `admin/123456`.
- Manual section 4.2: default wired controller IP `10.90.0.150`; host must use
  the same subnet, example `10.90.0.153/255.255.255.0`.
- Manual section 7.1/7.2: Web supports network-port configuration and hotspot
  configuration.
- Manual warning: do not set two arms as slave simultaneously, and do not enable
  CAN push on two connected arms simultaneously.

Result:

- The project state is now corrected to a two-arm physical setup.
- Arm A is the currently verified Web arm.
- Arm B requires independent S5 Web read-only verification before any S6 CAN
  work.

Deployment choices:

- Continue one-arm-at-a-time bring-up.
- Do not use simultaneous CAN/ROS until both arms have unique network identities
  and independent CAN paths.
- Use labels Arm A and Arm B until physical left/right installation is confirmed.
- Recommended future wired IP plan, if simultaneous wired Web access is needed:
  Arm A `10.90.0.151`, Arm B `10.90.0.152`, host `10.90.0.153`.

Files changed:
`agent.md`, `config/nero.env`, `docs/s5_dual_arm_network_plan.md`,
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`, `docs/bringup_checklist.md`.

Verification:
The new screenshot proves the Arm A hotspot configuration page is accessible and
that Arm A has a unique hotspot name `agx-7ax-xin`. The user report confirms all
Arm A joint tabs are normal.

Route updates:
S5 now includes dual-arm identity management. S6 now requires per-arm Web
verification and unique identity before CAN capture. Dual-arm simultaneous CAN
is deferred until independent CAN interfaces are mapped.

Open risks:

- Arm B has not yet been verified through Web.
- Arm B may still share default Wi-Fi/IP identity with Arm A.
- Arm A wired IP is not proven by the screenshot.
- SDK firmware selector is still not final because footer `v1.121` has not been
  tied to the exact SDK firmware selector.

Next:
Physically label Arm A and Arm B. Then power/connect Arm B by itself, complete
the same S5 Web read-only joint/status checks, and set/record a unique hotspot
name before both arms are used in the same environment.

## 2026-06-25 - S5.3 Dual-Arm Web Complete And S6 Plan

Phase: S5 Web 验机 / S6 CAN 只读

Goal:
Record completion of dual-arm Web identity checks and define the next read-only
CAN/ROS direction for future simultaneous dual-arm control.

Action:
Recorded the operator's confirmation that both arms passed Web checks and that
the Wi-Fi hotspots were changed to unique names. Reviewed the ROS2 launch files
for dual-instance support and safety defaults.

Commands / evidence:

- User report: both NERO arms have no observed Web problems.
- User report: Arm A Wi-Fi hotspot is now `agx-7ax-armA`.
- User report: Arm B Wi-Fi hotspot is now `agx-7ax-armB`.
- Source review:
  `start_single_agx_arm.launch.py` has `namespace` and `can_port` arguments.
- Source review:
  `start_single_agx_arm.launch.py` defaults `auto_enable:=true` and
  `control_enabled:=true`.
- Source review:
  `display.launch.py` applies a namespace frame prefix for RViz/model display.
- Source review:
  upstream CAN documentation supports finding USB bus-info and assigning
  deterministic names to multiple CAN modules.

Result:

- S5 is complete for both arms.
- The next phase is S6 dual-arm CAN read-only.
- The selected dual-arm naming plan is:
  - Arm A: Wi-Fi `agx-7ax-armA`, CAN `can_arm_a`, ROS namespace `arm_a`.
  - Arm B: Wi-Fi `agx-7ax-armB`, CAN `can_arm_b`, ROS namespace `arm_b`.

Deployment choices:

- Use two independent official USB-CAN modules or two independent CAN channels.
- Do not put both arms on one CAN bus.
- Do not enable CAN push on two connected arms simultaneously.
- For S8 ROS read-only, explicitly launch with
  `auto_enable:=false control_enabled:=false`.

Files changed:
`agent.md`, `config/nero.env`, `scripts/find_can_ports.sh`,
`scripts/activate_can.sh`, `docs/s6_dual_arm_can_ros_plan.md`,
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/s5_dual_arm_network_plan.md`, `docs/机器人部署与调试行动路线.md`,
`docs/bringup_checklist.md`.

Verification:
Documentation now records unique Wi-Fi identities for both arms and a read-only
dual-CAN plan. The new `scripts/find_can_ports.sh` wrapper is read-only and
delegates to the upstream CAN discovery script when available.

Route updates:
The route advances from S5 to S6 and replaces single-arm `can0` examples with
`can_arm_a` and `can_arm_b`. S8 examples now use namespaces and disable
auto-enable/control gate for read-only bring-up.

Open risks:

- USB-CAN bus-info for Arm A and Arm B has not been recorded yet.
- CAN feedback has not yet been captured from either arm.
- Footer version `v1.121` still needs to be tied to the SDK firmware selector
  before SDK/ROS conclusions are finalized.

Next:
Connect the two official USB-CAN modules, identify their USB bus-info one at a
time, map them to Arm A/Arm B, activate `can_arm_a` and `can_arm_b`, then run
read-only `candump` on each interface.

## 2026-06-25 - S6.0 Two Official USB-CAN Modules Confirmed

Phase: S6 CAN 只读

Goal:
Record the hardware prerequisite for dual-arm CAN read-only validation.

Action:
Recorded the operator's confirmation that the dual-arm setup uses two official
USB-CAN modules, one module per arm.

Commands / evidence:

- User report: there are two official USB-CAN modules.
- User report: the modules were already used separately while testing each
  arm's Wi-Fi/Web setup.

Result:

- S6 can proceed with the planned dual-interface mapping:
  `can_arm_a` for Arm A and `can_arm_b` for Arm B.

Deployment choices:

- Continue with one CAN bus per physical arm.
- Do not combine both arms on one CAN bus.
- Keep S6 read-only: `find_can_ports`, `activate_can`, `ip link`, and `candump`;
  no `cansend`.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/s6_dual_arm_can_ros_plan.md`.

Verification:
Hardware availability is confirmed by operator report; actual USB bus-info and
feedback frames are still pending.

Route updates:
No phase jump. S6 remains the active phase; the next concrete step is bus-info
mapping and read-only feedback capture.

Open risks:

- USB bus-info for each module has not been recorded yet.
- It is not yet proven that `can_arm_a` feedback stops only when Arm A CAN is
  disconnected and `can_arm_b` feedback stops only when Arm B CAN is disconnected.

Next:
Run read-only CAN discovery, map each USB-CAN module to Arm A/Arm B, activate
the deterministic interface names, then capture `candump` output from each
interface.

## 2026-06-25 - S6.1 USB-CAN Bus-Info Mapping

Phase: S6 CAN 只读

Goal:
Map each official USB-CAN module to the correct physical arm before activating
deterministic CAN interface names.

Action:
Recorded operator-provided output from `bash scripts/find_can_ports.sh` with one
module connected at a time.

Commands / evidence:

Arm B:

```text
Both ethtool and can-utils are installed.
Interface can0 is connected to USB port 1-11:1.0
```

Arm A:

```text
Both ethtool and can-utils are installed.
Interface can0 is connected to USB port 1-5:1.0
```

Result:

- Arm A USB-CAN bus-info: `1-5:1.0`.
- Arm B USB-CAN bus-info: `1-11:1.0`.

Deployment choices:

- Activate Arm A as `can_arm_a` from bus-info `1-5:1.0`.
- Activate Arm B as `can_arm_b` from bus-info `1-11:1.0`.
- Keep the modules in the same physical USB ports unless the mapping is
  rediscovered and updated.

Files changed:
`config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/s6_dual_arm_can_ros_plan.md`.

Verification:
The mapping is verified by read-only `find_can_ports.sh` output. Interface
activation and CAN feedback capture are still pending.

Route updates:
S6 now has concrete USB bus-info values for Arm A and Arm B.

Open risks:

- If a USB-CAN module is moved to a different host USB port, the bus-info mapping
  can change.
- Both modules have not yet been activated simultaneously.
- No `candump` feedback has been captured yet.

Next:
Plug both modules into the mapped USB ports, verify both bus-info values are
visible at the same time, activate `can_arm_a` and `can_arm_b`, and run read-only
`candump`.

## 2026-06-25 - S6.2 CAN Interfaces Up And Frames Reported

Phase: S6 CAN 只读

Goal:
Record the first successful dual USB-CAN interface activation and clarify the
role of Wi-Fi in future dual-arm control.

Action:
Recorded operator-provided `ip -details link show` and
`find_can_ports.sh` output, plus the operator report that CAN capture produced
normal frames.

Commands / evidence:

Arm B:

```text
21: can_arm_b: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UP mode DEFAULT group default qlen 10
    link/can
    can state ERROR-ACTIVE restart-ms 0
      bitrate 1000000 sample-point 0.750
```

Arm A:

```text
20: can_arm_a: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UP mode DEFAULT group default qlen 10
    link/can
    can state ERROR-ACTIVE restart-ms 0
      bitrate 1000000 sample-point 0.750
```

CAN discovery:

```text
Both ethtool and can-utils are installed.
Interface can_arm_a is connected to USB port 1-5:1.0
Interface can_arm_b is connected to USB port 1-11:1.0
```

Operator report:

- CAN capture produced normal frames.
- Arm A uses the vertical USB port.
- Arm B uses the horizontal USB port.

Result:

- `can_arm_a` is UP, ERROR-ACTIVE, bitrate `1000000`.
- `can_arm_b` is UP, ERROR-ACTIVE, bitrate `1000000`.
- USB mapping is stable with both modules visible at the same time.
- Normal CAN frames were observed by the operator.

Deployment choices:

- Continue using USB-CAN as the dual-arm real-time control path.
- Treat Wi-Fi as a Web configuration/status path only.
- The host's single Wi-Fi connection does not block future dual-arm CAN/ROS
  coordination.

Files changed:
`config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/s6_dual_arm_can_ros_plan.md`,
`docs/机器人部署与调试行动路线.md`, `docs/bringup_checklist.md`.

Verification:
Interface-level S6 checks passed. Detailed frame ID evidence should still be
archived before closing S6 completely if not already saved.

Route updates:
The route now records the USB physical orientation, confirms both CAN interfaces
are UP at 1 Mbps, and clarifies that Wi-Fi is not the dual-arm control path.

Open risks:

- The actual `candump` frame lines were not pasted into the log; exact frame IDs
  are based on operator report so far.
- SDK firmware selector is still pending.

Next:
Archive a short `candump` sample from each interface if possible, then proceed
to S7 SDK read-only on `can_arm_a` and `can_arm_b`.

## 2026-06-25 - S7.1 SDK Read-Only Passed And S8 Prepared

Phase: S7 SDK 只读 / S8 ROS 只读

Goal:
Record S7 completion and prepare a safe dual-arm ROS read-only launch path.

Action:
Recorded the operator's confirmation that S7 passed, reviewed the ROS container
entrypoint and launch requirements, and added a project wrapper for dual-arm ROS
read-only startup.

Commands / evidence:

- User report: S7 passed.
- Existing Docker entrypoint sources ROS Humble and
  `/root/agx_arm_ws/install/setup.bash`.
- The new wrapper `scripts/launch_dual_ros_readonly.sh` starts two
  `start_single_agx_arm.launch.py` instances:
  - Arm A: `namespace:=arm_a`, `can_port:=can_arm_a`
  - Arm B: `namespace:=arm_b`, `can_port:=can_arm_b`
  - both: `arm_type:=nero`, `effector_type:=none`,
    `auto_enable:=false`, `control_enabled:=false`

Result:

- S7 is complete by operator report.
- S8 is now the active next phase.
- A safer project command exists for ROS read-only startup.

Deployment choices:

- Continue with bare-arm `effector_type:=none`.
- Do not use MoveIt execute, `/control/*`, `enable_agx_arm`, or `move_home`
  during S8.
- Use Docker Humble for ROS2; host remains SDK/CAN-only.

Files changed:
`scripts/launch_dual_ros_readonly.sh`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/s6_dual_arm_can_ros_plan.md`,
`docs/机器人部署与调试行动路线.md`.

Verification:
The wrapper checks that `ros2`, `can_arm_a`, and `can_arm_b` are visible before
starting the two ROS drivers.

Route updates:
S8 now documents the preferred host command:
`bash scripts/run_humble_container.sh bash /workspace/nero/scripts/launch_dual_ros_readonly.sh`.

Open risks:

- S8 has not yet been run.
- ROS topic frequency and namespace isolation still need verification.

Next:
Run the dual ROS read-only wrapper, then inspect `/arm_a/feedback/*` and
`/arm_b/feedback/*` topics from inside the running container.

## 2026-06-25 - S8.1 Dual ROS Feedback Passed

Phase: S8 ROS 只读

Goal:
Verify that both NERO arms publish isolated ROS feedback topics through the
Humble container with distinct namespaces.

Action:
Recorded operator-provided `ros2 topic list`, `ros2 topic hz`, and
`ros2 topic echo --once` output.

Commands / evidence:

- Topic list contains namespaced feedback topics:
  - `/arm_a/feedback/joint_states`
  - `/arm_a/feedback/tcp_pose`
  - `/arm_a/feedback/arm_status`
  - `/arm_b/feedback/joint_states`
  - `/arm_b/feedback/tcp_pose`
  - `/arm_b/feedback/arm_status`
- Topic list also contains namespaced control subscribers under
  `/arm_a/control/*` and `/arm_b/control/*`; these are expected node interfaces,
  but S8 does not publish to them.
- Arm A `/arm_a/feedback/joint_states` frequency: about `199.8-200.0 Hz` over a
  10 second sample.
- Arm B `/arm_b/feedback/joint_states` frequency: about `199.8-200.0 Hz` over a
  10 second sample.
- Arm A `arm_status`:
  - `ctrl_mode: 1`
  - `arm_status: 6`
  - `mode_feedback: 1`
  - `teach_status: 0`
  - `motion_status: 1`
  - `trajectory_num: 0`
  - `err_status: 0`
  - all `joint_angle_limit` values `false`
  - all `communication_status_joint` values `false`
- Arm B `arm_status` shows the same status pattern, including `err_status: 0`,
  all joint angle limits `false`, and all joint communication statuses `false`.

Result:

- Dual-arm ROS feedback is working.
- ROS namespace isolation is working: Arm A topics are under `/arm_a`, and Arm B
  topics are under `/arm_b`.
- Both arms publish joint feedback at the configured `200 Hz` rate.
- No ROS-level error, joint limit flag, or joint communication error is visible
  in the provided status output.

Deployment choices:

- Keep S8 read-only.
- Do not publish to `/arm_a/control/*` or `/arm_b/control/*`.
- Do not call `enable_agx_arm`, `move_home`, MoveIt execute, or any motion
  command yet.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`.

Verification:
S8 ROS feedback/topic portion passes. RViz follow visual validation remains as
the only S8 item not yet evidenced in this log.

Route updates:
The action route now records the observed 200 Hz dual-arm ROS feedback and clean
arm status.

Open risks:

- RViz has not yet been confirmed to follow the real dual-arm feedback.
- `arm_status` numeric meanings should still be interpreted through vendor docs
  before using them for application logic; the immediately relevant safety
  fields here are `err_status: 0`, no joint limits, and no joint communication
  errors.

Next:
Run RViz follow validation without publishing control topics. If the displayed
pose matches the real arms, close S8 and move to S9 configuration review.

## 2026-06-25 - S8.2 RViz RobotModel TF Issue

Phase: S8 ROS 只读

Goal:
Evaluate the operator-provided RViz screenshot after visual pose confirmation.

Action:
Reviewed `docs/pics/Riz 姿态确认关节未识别.png` and compared it with the
`display.launch.py` namespace/frame-prefix behavior.

Commands / evidence:

- User report: RViz pose matches the real arm.
- Screenshot: RViz Fixed Frame is `arm_a/base_link`.
- Screenshot: RobotModel has Description Source `Topic`, Description Topic
  `robot_description`, and TF Prefix `arm_a`.
- Screenshot: RobotModel status is `Error`.
- Screenshot: `arm_a/base_link` and `arm_a/world` are `Transform OK`.
- Screenshot: `arm_a/link1` through `arm_a/link7` report:
  `No transform from [arm_a/linkN] to [arm_a/base_link]`.
- Source review: `display.launch.py` sets `frame_prefix` from namespace and
  remaps `joint_states` to the selected `feedback_topic` when `follow:=true`.

Result:

- S8 ROS feedback remains passed from prior topic evidence.
- RViz visual follow is not fully accepted yet because the RobotModel plugin
  reports missing dynamic link transforms.
- The failure surface is likely between `/arm_a/feedback/joint_states` and
  `/arm_a/robot_state_publisher` dynamic TF output, or a joint-name mismatch
  between feedback and URDF.

Deployment choices:

- Keep S8 open until RViz RobotModel reports transforms for `link1` through
  `link7`.
- Continue read-only. Do not publish to `/control/*`.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`.

Verification:
Screenshot evidence confirms the RViz issue is not mesh loading or base frame
selection; it is missing dynamic TF for joint links.

Route updates:
S8 now requires both subjective visual pose match and RobotModel transform OK
for `link1` through `link7`.

Open risks:

- The exact cause is not yet proven. Need to inspect joint state names and
  robot_state_publisher subscription/TF output while RViz/RSP is running.

Next:
Re-run RViz with explicit absolute `feedback_topic:=/arm_a/feedback/joint_states`.
If RobotModel still reports missing link transforms, run ROS diagnostics for
joint state names, robot_state_publisher subscriptions, and TF echo.

## 2026-06-25 - S8.3 RViz Diagnosis Corrected And S8 Accepted

Phase: S8 ROS 只读

Goal:
Correct the previous RViz TF diagnosis using operator follow-up evidence.

Action:
The operator restarted the RViz validation with the first terminal running the
dual ROS read-only driver. RViz then recognized the joints and displayed the arm
pose correctly.

Commands / evidence:

- Prior screenshot showed `link1` through `link7` missing transforms while RViz
  was open.
- Operator confirmed the first terminal, which should run the ROS read-only
  driver and publish `/arm_a/feedback/joint_states` and
  `/arm_b/feedback/joint_states`, had not been started at that time.
- After starting that terminal, RViz behaved normally.
- Operator confirmed the RViz arm posture matches the real robot feedback.
- Remaining visual difference: the RViz model appears horizontal while the real
  table-upright arm hangs vertically. This is treated as coordinate frame /
  installation-pose alignment for S9, not as an S8 driver or URDF failure.

Result:

- Corrected diagnosis: the previous RobotModel TF error was caused by missing
  runtime feedback source due to launch order / prerequisite terminal omission.
- There is no current evidence of a joint-name mismatch or URDF joint-loading
  failure.
- S8 read-only ROS feedback and RViz follow are accepted.

Deployment choices:

- RViz follow validation requires the dual ROS read-only driver terminal to be
  running first.
- Keep `auto_enable:=false control_enabled:=false` for all read-only launches.
- Defer world/base frame alignment, Web installation-pose review, and external
  frame documentation to S9.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`, `docs/bringup_checklist.md`.

Verification:
Operator field report confirms RViz joint recognition and pose following work
after the driver terminal is active.

Route updates:
S8 is marked complete. The action route now says that missing `link1-link7` TF
in RViz should first trigger a check that the ROS feedback driver is running.

Next:
Proceed to S9 configuration review: installation posture, coordinate frames,
zero/TCP/tool settings, conservative limits, and documentation of the dual-arm
base frames.

## 2026-06-25 - S9.1 Read-Only Configuration Inventory Prepared

Phase: S9 标定与参数配置

Goal:
Start S9 without changing robot settings or sending motion commands.

Action:
Created a S9 worksheet and a read-only ROS snapshot helper. Updated the current
phase state and action route so S9 begins with Web/ROS evidence capture before
any configuration write.

Commands / evidence:

- Read `agent.md`, `docs/机器人部署与调试行动路线.md`, and the user manual sections
  for zero setting and system settings.
- User manual section `6.7 设置零点` states zero setting should be done at the
  default upright position and that automatic zero setting moves the motor to
  the mechanical limit before returning.
- User manual section `6.8.4 安装位置设置` states installation posture affects
  robot coordinate calibration and spatial calculation.
- Added `docs/s9_configuration_review.md`.
- Added executable script `scripts/snapshot_ros_readonly_state.sh`.

Result:

- S9 is active as `S9.1 read-only inventory`.
- The first S9 task is to capture Arm A and Arm B Web screenshots and one ROS
  read-only snapshot.
- Zero calibration, joint-limit changes, collision-level changes, and speed
  changes remain blocked until reviewed separately.

Deployment choices:

- S9.1 is read-only.
- Use current bare-arm configuration: `effector_type:=none`,
  `tcp_offset:=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`.
- Treat the RViz horizontal-versus-real vertical visual difference as an S9
  coordinate/installation-pose alignment item.

Files changed:
`agent.md`, `docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s9_configuration_review.md`,
`scripts/snapshot_ros_readonly_state.sh`.

Verification:
`scripts/snapshot_ros_readonly_state.sh` was created and marked executable.
Route/status files now identify S9.1 as the active next step.

Route updates:
The S9 section now explicitly starts with a read-only inventory and requires a
ROS snapshot under `docs/s9_ros_snapshots/`.

Open risks:

- Arm A and Arm B Web configuration screenshots have not yet been captured.
- The exact Web installation-position option corresponding to the physical
  table-upright installation still needs operator confirmation.
- No zero calibration decision has been made.

Next:
Operator captures S9 Web screenshots for both arms and runs the ROS read-only
snapshot command while the dual ROS read-only driver is running.

## 2026-06-25 - S9.2 Web Screenshots Read And Snapshot Script Corrected

Phase: S9 标定与参数配置

Goal:
Read the operator-provided S9 Web screenshots and identify whether S9.1 can be
accepted.

Action:
Inspected `docs/pics/S9.1/A01.png` through `A04.png` and
`docs/pics/S9.1/B01.png` through `B03.png`. Inspected the ROS snapshot directory
`docs/s9_ros_snapshots/20260625_035128/`. Corrected the snapshot helper so a
timed `ros2 topic hz` sample does not abort the remaining captures.

Commands / evidence:

- Screenshot files:
  - Arm A: `A01.png`, `A02.png`, `A03.png`, `A04.png`.
  - Arm B: `B01.png`, `B02.png`, `B03.png`.
- Arm A and Arm B Web installation position: `1-水平正装`.
- Arm A and Arm B end effector: `默认（无加载）`.
- Arm A and Arm B load mode: `满载`.
- Arm A and Arm B visible tool mass: `0.00000 kg`.
- Arm A and Arm B visible collision protection evidence: J1 level `1`.
- Arm A zero-setting dialog was captured; Arm B zero-setting dialog was not
  captured.
- Arm A and Arm B joint limits/speeds shown by Web:
  - J1 `-155..155 deg`, max speed `179.9 deg/s`.
  - J2 `-100..100 deg`, max speed `179.9 deg/s`.
  - J3 `-158..158 deg`, max speed `179.9 deg/s`.
  - J4 `-58..123 deg`, max speed `179.9 deg/s`.
  - J5 `-158..158 deg`, max speed `224.6 deg/s`.
  - J6 `-42..55 deg`, max speed `224.6 deg/s`.
  - J7 `-90..90 deg`, max speed `224.6 deg/s`.
- End-speed settings shown by Web:
  - Linear velocity `1000.0 mm/s`.
  - Angular velocity `34.4 deg/s`.
  - Linear acceleration `1500.0 mm/s^2`.
  - Angular acceleration `286.5 deg/s^2`.
- Existing ROS snapshot only contains Arm A files because `timeout 5s ros2
  topic hz` returned a timeout code and the script stopped before Arm B capture.

Result:

- S9.1 is partially complete, but not accepted yet.
- A/B installation, default end-effector, load mode, joint limits, and end-speed
  values are recorded.
- J2 Web limit `-100..100 deg` conflicts with the manual route value
  `-15..190 deg`. This is consistent with the earlier URDF/Web/manual angle
  convention concern and must be resolved before any limit expansion or larger
  motion.
- Collision protection is not fully recorded because only J1 level is visible.
- Arm B zero-setting page is missing.
- Full A/B ROS snapshot is missing.

Deployment choices:

- Do not change Web settings yet.
- Do not perform zero calibration.
- Treat Web option `1-水平正装` as the currently observed installation setting
  for both arms.
- Treat `满载` as observed, not yet approved as the final operating load mode.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/机器人部署与调试行动路线.md`, `docs/bringup_checklist.md`,
`docs/s9_configuration_review.md`, `scripts/snapshot_ros_readonly_state.sh`.

Verification:
The snapshot helper now allows timeout exit code `124` for the intended short
frequency sample. Screenshot-derived values are recorded in the S9 worksheet.

Route updates:
S9 now records the observed Web configuration and explicitly calls out the
remaining S9.1 evidence gaps.

Open risks:

- Need Arm B zero-setting page screenshot.
- Need collision protection levels for J2-J7 on both arms.
- Need a corrected full A/B ROS snapshot.
- Need a decision on whether `满载` is an appropriate conservative load mode for
  the current bare-arm state.
- Need to reconcile Web J2 `-100..100 deg` with the manual `-15..190 deg`
  representation before S10.

Next:
Capture the missing Web evidence and rerun the S9 ROS read-only snapshot with
the corrected script.

## 2026-06-25 - S9.3 Read-Only Inventory Accepted

Phase: S9 标定与参数配置

Goal:
Close S9.1 inventory after the remaining operator confirmations and corrected
ROS snapshot.

Action:
Read the new ROS snapshot and recorded operator field confirmations for Arm B
zero page and collision protection levels.

Commands / evidence:

- Operator ran:
  `NERO_CONTAINER_NAME=nero-humble-s9-snapshot2 bash scripts/run_humble_container.sh bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh`
- Snapshot path:
  `docs/s9_ros_snapshots/20260625_044256/`.
- Snapshot contains Arm A and Arm B files for:
  - topic list
  - `joint_states`
  - `tcp_pose`
  - `arm_status`
  - short `joint_states` frequency samples
- Arm A `joint_states` names: `joint1` through `joint7`.
- Arm B `joint_states` names: `joint1` through `joint7`.
- Arm A frequency sample: about `199.98-200.00 Hz`.
- Arm B frequency sample: about `200.00-200.02 Hz`.
- Arm A and Arm B `arm_status`: `err_status: 0`, all joint angle limits
  `false`, all joint communication statuses `false`.
- Operator confirmed Arm B zero-setting page joint sequence is also `1`.
- Operator confirmed both arms have collision protection level `1` for all
  joints J1-J7.

Result:

- S9.1 read-only inventory is accepted.
- S9 remains active because configuration decisions are still pending before
  S10.
- The `ros2 topic hz` timeout files include a shutdown message after the sample
  window, but the frequency samples are valid. The helper script was updated to
  use SIGINT for cleaner future timeout shutdown.

Deployment choices:

- Current Web installation position for both arms: `1-水平正装`.
- Current Web end effector for both arms: `默认（无加载）`.
- Current Web load mode for both arms: `满载`.
- Current Web collision levels for both arms: J1-J7 all `1`.
- Current ROS runtime remains bare arm:
  `effector_type:=none`, `tcp_offset:=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/机器人部署与调试行动路线.md`,
`docs/bringup_checklist.md`, `docs/s9_configuration_review.md`,
`scripts/snapshot_ros_readonly_state.sh`.

Verification:
The corrected snapshot directory contains both Arm A and Arm B data and both
arms report clean read-only ROS status.

Route updates:
S9.1 is now accepted. S9.2 is the active next step.

Open risks:

- Decide whether `满载` should be kept or changed before first motion.
- Reconcile Web/URDF/manual J2 angle conventions before any limit expansion or
  larger motion.
- Decide how to document/transform the horizontal RViz/world representation
  relative to the real table-upright hanging posture.
- Decide whether zero calibration is needed; if yes, write a dedicated procedure
  before doing it.

Next:
Proceed to S9.2 configuration decisions. Do not enter S10 motion until S9.2
decisions are documented.

## 2026-06-25 - S9.4 Configuration Decisions Made

Phase: S9 标定与参数配置

Goal:
Resolve the remaining S9.2 decisions using current evidence and define the next
safe action before S10.

Action:
Reviewed the S9.1 Web/ROS evidence, user note that Web joint limits are
editable, local manual sections, and upstream ROS/SDK source behavior.

Commands / evidence:

- Manual section `6.8.5` says end-effector physical properties are used for
  motion control and torque compensation.
- Manual-derived S9 route says load mode must match the actual end effector.
- Current physical end effector is bare arm.
- Current Web end effector is `默认（无加载）`; visible tool mass is `0.00000 kg`.
- Current Web load mode is `满载`.
- Web J2 limit is `-100..100 deg`.
- URDF J2 limit found in S3 is about `-99.69..99.69 deg`.
- Manual J2 mechanical range is `-15..190 deg`.
- User confirmed Web joint limits are adjustable.
- Upstream `pyAgxArm` NERO `arm_mode_ctrl.py` defines installation position
  `0x01` as `Horizontal upright`.
- Upstream ROS launch/config review did not identify a ROS launch argument for
  Web installation pose; ROS exposes namespace, end-effector type, and TCP
  offset.

Result:

1. Load-mode decision:
   Change both arms from observed `满载` to the Web empty/no-load option before
   S10. Keep end effector `默认（无加载）`, tool mass `0.00000 kg`, ROS
   `effector_type:=none`, and TCP offset zero.

2. J2 limit decision:
   Do not edit or expand J2 Web limits before S10. Keep Web `-100..100 deg`.
   Treat manual `-15..190 deg` as a different angle convention, with current
   working inference `manual_J2_angle ≈ web_or_urdf_J2_angle + 90 deg`. This
   inference is only for avoiding unsafe edits, not for extending the allowed
   range.

3. Coordinate-frame decision:
   Keep Web installation position `1-水平正装`. Do not rotate URDF or change Web
   installation position to make RViz visually match the real hanging posture.
   Treat `arm_a/base_link` and `arm_b/base_link` as robot-local frames; future
   dual-arm coordination must add measured static transforms:
   `lab_world -> arm_a/base_link` and `lab_world -> arm_b/base_link`.

Deployment choices:

- S9.3 must perform only the load-mode correction and read-only revalidation.
- No joint limit edits before first motion.
- No Web installation-position change.
- No zero calibration.
- No Cartesian, MoveIt execute, or dual-arm coordinated motion before external
  base-frame calibration.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/机器人部署与调试行动路线.md`,
`docs/bringup_checklist.md`, `docs/s9_configuration_review.md`.

Verification:
Documents and config now distinguish observed current load mode `满载` from the
target before S10: empty/no-load.

Route updates:
S9.2 decisions are recorded. The active next step is S9.3 load-mode correction
and ROS read-only revalidation.

Open risks:

- Need to identify the exact Web label for empty/no-load on the live UI before
  applying it.
- Changing load mode is a controller configuration write and must be done while
  disabled and without motion.
- J2 angle convention remains an inference until validated through controlled
  first-motion observations.
- Lab/world base-frame calibration is still missing for dual-arm coordination.

Next:
Perform S9.3: change both arms' load mode to the Web empty/no-load option,
record screenshots, and rerun the ROS read-only snapshot.

## 2026-06-25 - S9.5 Load-Mode Change Procedure Prepared

Phase: S9 标定与参数配置

Goal:
Prepare the controlled S9.3 load-mode correction before the operator changes Web
settings.

Action:
Expanded `docs/s9_configuration_review.md` with a load-mode-only execution
procedure, acceptance criteria, and stop conditions.

Commands / evidence:

- Current observed load mode remains `满载`.
- Current target before S10 is empty/no-load, expected Web label `空载`.
- Current Web end effector remains `默认（无加载）` and tool mass is
  `0.00000 kg`.

Result:

- S9.3 can proceed as a single controlled Web configuration write on each arm.
- The action is limited to load mode only.

Deployment choices:

- Change Arm A and Arm B consistently.
- Capture after-change screenshots under `docs/pics/S9.3/`.
- Re-run ROS read-only snapshot after the Web write.

Files changed:
`docs/deployment_log.md`, `docs/s9_configuration_review.md`.

Verification:
Procedure now specifies acceptance criteria and stop/rollback conditions.

Route updates:
No phase gate changed. S9.3 remains the active next step.

Open risks:

- The exact Web label for empty/no-load must be verified on the live UI.
- Any Web submit is a controller configuration write, so the operator must avoid
  changing adjacent settings.

Next:
Operator performs S9.3 in Web UI, then provides screenshots and ROS snapshot
path/output.

## 2026-06-25 - S9.6 Web Mode And CAN Revalidation Issue

Phase: S9 标定与参数配置

Goal:
Record the S9.3 recovery state after Web load-mode change and failed ROS
revalidation.

Action:
The operator reported that the load setting was successfully changed, but Web
could not switch back through the top CAN button. The CAN button tooltip says
`关闭外网CAN推送`. The operator also reported ROS launch failure:
`CAN interface can_arm_a is not visible`.

Commands / evidence:

- User report: load setting changed successfully.
- User report: top CAN button tooltip is `关闭外网CAN推送`.
- User report: clicking it fails.
- User command/output:
  `bash scripts/run_humble_container.sh >     bash /workspace/nero/scripts/launch_dual_ros_readonly.sh`
  then `CAN interface can_arm_a is not visible.`
- Local repository root contains a new zero-byte file named `bash`, consistent
  with a literal shell redirection character `>` being used accidentally.
- Attempting to inspect netlink interfaces from the assistant sandbox failed
  with `Operation not permitted`, so host CAN state must be checked in the real
  desktop terminal.

Result:

- S9.3 is not accepted yet.
- The Web CAN button may be CAN push rather than the SocketCAN host interface.
  Tooltip `关闭外网CAN推送` means CAN push appears already enabled.
- ROS failure now needs host SocketCAN interface recovery or command syntax
  correction.

Deployment choices:

- Do not repeatedly click the Web CAN push button during recovery.
- Verify host `can_arm_a` and `can_arm_b` visibility first.
- If deterministic names are missing, reactivate with the recorded USB bus-info:
  Arm A `1-5:1.0`, Arm B `1-11:1.0`.
- Use the correct read-only launch command without a literal `>`.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/s9_configuration_review.md`.

Verification:
No ROS revalidation accepted yet.

Route updates:
S9.3 troubleshooting now documents Web mode, CAN push, SocketCAN checks, and the
correct launch command.

Open risks:

- Unknown whether both host CAN interfaces are currently up and named.
- Unknown whether both arms' load mode was changed and screenshotted.

Next:
Operator checks host CAN interfaces, reactivates names if needed, then reruns
read-only ROS and S9 snapshot.

## 2026-06-25 - S9.7 Load-Mode Snapshot Attempt Missing ROS Topics

Phase: S9 标定与参数配置

Goal:
Evaluate the operator's S9.3 snapshot attempt.

Action:
Inspected the latest snapshot directories:
`docs/s9_ros_snapshots/20260625_051838/` and
`docs/s9_ros_snapshots/20260625_051844/`.

Commands / evidence:

- Both latest `topic_list.txt` files contain only:
  - `/parameter_events`
  - `/rosout`
- Both attempts fail at `/arm_a/feedback/joint_states`:
  `topic [/arm_a/feedback/joint_states] does not appear to be published yet`.
- No Arm B files were created by the old script because it stopped on the first
  failed Arm A capture.

Result:

- These S9.3 snapshots do not validate the load-mode change.
- The likely cause is that the dual ROS read-only driver was not running, or had
  already exited, when the snapshot was taken.

Deployment choices:

- S9.3 remains open.
- Snapshot helper was made more diagnostic: it now continues through both arms
  and reports failed capture commands instead of leaving a partial directory.

Files changed:
`docs/deployment_log.md`, `scripts/snapshot_ros_readonly_state.sh`.

Verification:
Latest snapshot topic lists prove the expected `/arm_a/...` and `/arm_b/...`
feedback topics were absent during the attempt.

Route updates:
No phase gate changed.

Open risks:

- Need to confirm the dual ROS read-only driver can stay running after the Web
  load-mode change.
- Need after-change Web screenshots if not already saved.

Next:
Start the dual ROS read-only driver in one terminal, confirm feedback topics in
a second terminal, then rerun the S9 snapshot.

## 2026-06-25 - S9.8 Arm A Firmware Read Failure

Phase: S9 标定与参数配置

Goal:
Diagnose why S9.3 ROS revalidation topics were absent.

Action:
Reviewed the operator-provided dual ROS read-only launch log and upstream driver
code around firmware detection.

Commands / evidence:

- Launch command:
  `bash scripts/run_humble_container.sh bash /workspace/nero/scripts/launch_dual_ros_readonly.sh`
- Both arm nodes started with:
  `auto_enable: False`, `control_enabled: False`, `pub_rate: 200`,
  `effector_type: none`.
- Arm B:
  - `firmware version: 1.121`
  - `Agx_arm feedback is ready`
- Arm A:
  - `Failed to get firmware version`
  - process exited with code `1`
- `launch_dual_ros_readonly.sh` exits when one child exits, so Arm B is also
  stopped after Arm A fails.
- Upstream `agx_arm_ctrl_single_node.py` calls `get_firmware()` during node
  initialization and exits if firmware is not returned within
  `enable_timeout`.
- Upstream NERO driver `get_firmware()` sends a firmware request and waits for
  an 8-byte firmware feedback message.

Result:

- The failure is isolated to Arm A / `can_arm_a` CAN request-response path.
- Arm B / `can_arm_b` is proven healthy in the same launch attempt.
- S9.3 remains open.

Deployment choices:

- Do not proceed to S10.
- Do not keep repeatedly clicking the Web CAN push button.
- First verify host `can_arm_a` visibility and passive CAN frames, then test
  Arm A SDK read-only.

Files changed:
`docs/deployment_log.md`.

Verification:
Driver source confirms the ROS failure happens before any control topic
operation; it is a firmware query failure.

Route updates:
No phase gate changed.

Open risks:

- Arm A may still be in a Web/control state that blocks external CAN
  request-response.
- Arm A external CAN push may be off despite Web tooltip ambiguity.
- Arm A USB-CAN mapping or physical CAN connection may have changed.

Next:
Run host CAN visibility checks, passive `candump`, and Arm A SDK read-only
firmware/state checks before retrying dual ROS.

## 2026-06-25 - S9.9 Arm A Passive CAN Frames Missing

Phase: S9 标定与参数配置

Goal:
Record the result of host-side CAN isolation after Arm A firmware read failure.

Action:
The operator ran the second diagnostic step and compared passive CAN capture on
Arm A and Arm B.

Commands / evidence:

- Operator report: Arm A has no passive CAN frames.
- Operator report: Arm B has passive CAN frames and is normal.
- Operator attempted SDK read-only commands from the Conda/base environment:
  `python examples/nero_read_state.py --connect --channel can_arm_a --firmware v112 --duration 3`
  and the same command for `can_arm_b`.
- Both SDK attempts failed before connecting:
  `No module named 'pyAgxArm'`.
- This SDK result is an environment activation issue, not a robot communication
  result.
- Manual section `5.1.3` identifies the top `can通讯` button as toggling CAN
  communication on/off.
- Manual notes the controller uses independent state-machine modes and Web mode
  is required for Web operations.

Result:

- Current fault is isolated to Arm A CAN publishing/communication availability.
- Arm B remains healthy.
- The most likely explanation is that Arm A's CAN communication / external CAN
  push was disabled or not restored during the Web mode/configuration sequence.

Deployment choices:

- Do not proceed to S10.
- Recover Arm A CAN communication through the Web CAN communication toggle or a
  controlled reboot if Web recovery fails.
- SDK tests must be run from `.venv/nero-sdk`, not the Conda/base environment.

Files changed:
`docs/deployment_log.md`.

Verification:
Passive `candump` comparison distinguishes Arm A from Arm B and points below ROS
to the arm/controller CAN communication state.

Route updates:
No phase gate changed.

Open risks:

- It is not yet verified whether Arm A Web CAN button state says enable or
  disable after refreshing/relogging.
- It is not yet verified whether Arm A reboot restores CAN push.

Next:
Refresh/relogin Arm A Web, ensure CAN communication is enabled, verify passive
`candump -tz can_arm_a`, then rerun dual ROS read-only.

## 2026-06-25 - S9.10 Arm A Still Has No Passive CAN Frames After Reboot

Phase: S9 标定与参数配置

Goal:
Record Arm A recovery attempt after Web load-mode change and CAN frame loss.

Action:
The operator rebooted Arm A and reran passive CAN capture on `can_arm_a`.

Commands / evidence:

- Operator report: after reboot, `timeout 5s candump -tz can_arm_a` still shows
  no frames.
- Prior comparison remains: Arm B has frames and is normal.

Result:

- S9.3 remains blocked.
- The problem is below ROS topics and below the previous SDK import issue.
- Candidate causes are now:
  - Arm A Web CAN communication / external CAN push is still off or stuck.
  - `can_arm_a` is not actually mapped to the Arm A USB-CAN path after recovery.
  - Arm A CAN interface is not UP / not ERROR-ACTIVE / bus-off.
  - Arm A physical CAN wiring or USB-CAN module path has a fault.

Deployment choices:

- Do not proceed to S10.
- First collect host CAN interface state and mapping before changing more Web
  settings.
- If host interface/mapping is healthy, isolate by known-good module/cable or
  Arm A Web CAN state.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`.

Verification:
No passive Arm A CAN frames are present after reboot.

Route updates:
No phase gate changed.

Open risks:

- Unknown exact Arm A Web CAN button state after reboot.
- Unknown current `ip -details` state for `can_arm_a`.
- Unknown whether Arm A physical CAN path is healthy.

Next:
Run host CAN interface/mapping checks, then run SDK read-only from the correct
venv if any Arm A frames or request-response path is restored.

## 2026-06-25 - S9.11 Arm A CAN Recovered By USB Replug

Phase: S9 标定与配置

Goal:
Record the recovery that restored Arm A CAN communication after the S9.3 Web
load-mode change.

Action:
The operator unplugged/replugged the Arm A USB-CAN path and reactivated the
interface.

Commands / evidence:

- Operator report: the issue was resolved by replugging the USB port and then
  setting/activating the interface again.
- Operator report: the dual ROS read-only launch now runs successfully:
  `bash scripts/run_humble_container.sh bash /workspace/nero/scripts/launch_dual_ros_readonly.sh`

Result:

- Arm A CAN request/response path is recovered by operator report.
- S9.3 still needs final ROS snapshot after the load-mode change.

Deployment choices:

- If a CAN interface is mapped but produces no passive frames after Web mode or
  configuration changes, use USB-CAN replug plus deterministic reactivation as a
  recovery step before deeper robot-side debugging.
- Preserve Arm A mapping as `1-5:1.0` and Arm B mapping as `1-11:1.0`.

Files changed:
`docs/deployment_log.md`, `docs/current_bringup_status.md`,
`docs/s9_configuration_review.md`.

Verification:
No new S9.3 snapshot has been recorded yet in `docs/s9_ros_snapshots/`.

Route updates:
S9.3 moves from CAN recovery to ROS read-only revalidation pending.

Open risks:

- Need to confirm the post-load-mode ROS snapshot shows clean A/B status.
- Need screenshots or field confirmation that both arms show the new no-load
  mode.

Next:
Run S9.3 snapshot while the dual ROS read-only driver remains running.

## 2026-06-25 - S9.12 S9 Accepted After Load-Mode Revalidation

Phase: S9 标定与配置

Goal:
Evaluate the final S9.3 ROS snapshot after load-mode correction and Arm A CAN
recovery.

Action:
Read `docs/s9_ros_snapshots/20260625_054435/`.

Commands / evidence:

- Operator confirmed topic list includes complete Arm A and Arm B feedback
  topics.
- Snapshot path: `docs/s9_ros_snapshots/20260625_054435/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Arm A `arm_status`:
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm B `arm_status`:
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm A joint-state frequency: about `199.9 Hz`.
- Arm B joint-state frequency: about `199.7-199.9 Hz`.
- Arm A and Arm B joint-state names are `joint1` through `joint7`.
- Operator previously reported both arms' load settings were changed
  successfully to the bare-arm empty/no-load option.
- No after-change Web screenshots were found under `docs/pics/`; acceptance uses
  operator field confirmation plus clean ROS revalidation.

Result:

- S9 is accepted.
- S10 can be prepared, but no motion is approved until the S10 first-motion
  checklist is explicitly followed.

Deployment choices:

- Current Web load mode is treated as empty/no-load by operator confirmation.
- Keep Web installation position `1-水平正装`.
- Keep J2 Web limits `-100..100 deg`; do not expand before first motion.
- Keep ROS runtime as bare arm:
  `effector_type:=none`, `tcp_offset:=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`.
- Record Arm A USB-CAN replug plus deterministic activation as a valid recovery
  path for a mapped interface with no passive frames.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/机器人部署与调试行动路线.md`,
`docs/bringup_checklist.md`, `docs/s9_configuration_review.md`.

Verification:
Final S9.3 ROS snapshot is complete and clean for both arms.

Route updates:
S9 is complete. The active next phase is S10 first low-speed motion planning.

Open risks:

- No measured `lab_world -> arm_a/base_link` or `lab_world -> arm_b/base_link`
  transforms yet; do not do dual-arm coordinated or Cartesian motion.
- First motion still requires human safety checks and one active control source.
- J2 angle convention remains inferred and must be watched during small
  joint-space tests.

Next:
Prepare S10 first low-speed single-arm joint-space motion checklist and command
selection.

## 2026-06-25 - S10.0 First-Motion Plan Prepared

Phase: S10 首次低速运动

Goal:
Prepare the first real NERO motion as a bounded, documented, operator-confirmed
procedure.

Action:
Created a dedicated first-motion plan and updated the route, status page,
checklist, agent rules, and environment defaults.

Commands / evidence:

- Manual section `6.1 运动控制`: Web operation requires switching to `WEB`
  mode and enabling before joint motion; joint motion applies after clicking
  apply.
- Manual section `6.5 速度调节`: Web has an overall speed percentage slider.
- S9 accepted snapshot: `docs/s9_ros_snapshots/20260625_054435/`.
- S9 accepted configuration: bare arm, no-load, Web `1-水平正装`, collision
  levels J1-J7 all `1`, no ROS status errors.

Result:

- S10 is active but no motion has been executed.
- First motion is constrained to one arm, Web control only, low speed, single
  joint J7, `+2 deg` then return to the original angle.

Deployment choices:

- Prefer Arm B only if physical clearance is no worse than Arm A, because Arm B
  had the more stable CAN path during S9 recovery.
- Use J7 first because the bare-arm swept volume is expected to be smallest and
  it avoids J2/J4 and J1 for the initial motion.
- Stop ROS before Web motion so there is only one active control source.
- Use the Web speed percentage slider at the lowest available value, preferably
  `5%` or lower.
- After Web motion, return to dual-arm ROS read-only validation and save a
  snapshot before any SDK or ROS motion.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_first_motion_plan.md`.

Follow-up correction:
Updated the current SDK selector note to `v112`, fixed the `agent.md`
read-only launch sentence, and changed `NERO_DUAL_ARM_INITIAL_MODE` from the
stale S6 value to `s10_web_first_motion_next`.

Verification:
Documentation update only. No robot motion or control command was sent.

Route updates:
S10.0 is prepared. S10.1 Web first motion is pending operator safety
confirmation.

Open risks:

- The Web speed UI must be physically confirmed before clicking apply.
- J7 can twist a cable if the cable path is poor; confirm J6/J7 clearance before
  using the default J7 motion.
- Web mode may again disturb passive CAN frames; use the S9 USB-CAN replug and
  deterministic activation recovery if needed.

Next:
Operator confirms the S10 Pre-Motion Gate, then executes the Web J7 `+2 deg`
and return test on the selected single arm.

## 2026-06-25 - S10.1 Arm A Selected For First Motion

Phase: S10 首次低速运动

Goal:
Record operator selection and safety confirmation before the first real motion.

Action:
The operator selected Arm A for S10.1 and confirmed the remaining pre-motion
requirements.

Commands / evidence:

- Operator statement: "就用 arm A 吧，其余内容已确认。"
- Planned action remains Web-only, low-speed, single-joint J7, `+2 deg` then
  return to the original J7 angle.

Result:

- Arm A is the selected S10.1 execution arm.
- First motion has not yet been reported executed.

Deployment choices:

- Use Arm A despite the default Arm B recommendation because the operator chose
  Arm A after confirming the safety conditions.
- Keep the Web first-motion procedure unchanged: stop ROS first, Web is the
  only control source, use lowest speed percentage, command only J7.

Files changed:
`config/nero.env`, `docs/current_bringup_status.md`,
`docs/deployment_log.md`, `docs/s10_first_motion_plan.md`.

Verification:
Documentation update only. No robot motion or control command was sent by this
agent.

Route updates:
S10.1 may now proceed on Arm A under the documented Web first-motion procedure.

Open risks:

- Motion result and post-motion ROS snapshot are still pending.
- If Arm A CAN feedback disappears after Web mode, use the documented USB-CAN
  replug and deterministic reactivation recovery path.

Next:
Execute Arm A Web J7 `+2 deg`, return to original angle, then run post-motion
ROS read-only validation.

## 2026-06-25 - S10.1 Web First Motion Passed On Arm A

Phase: S10 首次低速运动

Goal:
Record and evaluate the first real NERO motion result.

Action:
The operator executed Web control on Arm A.

Commands / evidence:

- Operator report: Web enable succeeded.
- Operator report: Web joint control succeeded.
- Operator report: all 7 Arm A degrees of freedom moved successfully.
- Post-motion ROS read-only snapshot:
  `docs/s9_ros_snapshots/20260625_060810/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Arm A joint-state frequency: about `200.0 Hz`.
- Arm B joint-state frequency: about `200.0 Hz`.
- Arm A `arm_status`:
  - `arm_status: 0`
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm B `arm_status`:
  - `arm_status: 6`
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm A after-motion joint positions in radians:
  `J1=0.9686577348568529`,
  `J2=1.2356931104119853`,
  `J3=-0.5166174585903216`,
  `J4=0.7260569688296411`,
  `J5=0.3769911184307752`,
  `J6=-0.6981317007977318`,
  `J7=-0.6195220712879073`.

Result:

- S10.1 Web first motion is accepted for Arm A.
- Actual field motion exceeded the original J7-only recommendation because all
  7 degrees of freedom were moved. It succeeded and post-motion ROS feedback is
  healthy, but it does not remove the need for separate SDK/ROS motion gates.

Deployment choices:

- Hold further motion after the successful Web test.
- Treat the current Arm A pose as the latest observed post-motion pose; do not
  command return/home/park unless a separate procedure is written.
- Keep SDK motion, ROS `/control/*`, raw CAN motion, Cartesian motion, MoveIt
  execute, MIT mode, master-slave mode, dexterous-hand actuation, and dual-arm
  motion disabled until separately planned.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_first_motion_plan.md`.

Verification:
Post-motion ROS read-only snapshot is complete and clean for both arms.

Route updates:
S10.1 Web first motion has passed. S10 remains active for SDK/ROS low-speed
motion planning.

Open risks:

- Arm A `arm_status` changed from previous snapshot value `6` to `0`; no error
  flags are set, but monitor this state-machine difference in the next step.
- Intentional emergency-stop recovery has not been triggered and verified.
- The final Arm A pose may need a future controlled park/home decision.

Next:
Prepare S10.2: a single-arm, single-joint, low-speed SDK or ROS motion test
with explicit command limits and post-motion read-only validation.

## 2026-06-25 - S10.2 SDK Single-Joint Test Prepared

Phase: S10 首次低速运动

Goal:
Prepare the next control path after Web: direct `pyAgxArm` SDK joint-space
control over SocketCAN.

Action:
Read the local SDK and ROS driver sources, then created a bounded SDK motion
script and S10.2 procedure.

Commands / evidence:

- Local SDK documentation `pyAgxArm/docs/nero/nero_api.md`:
  NERO joint angles are 7-element lists in radians; `move_j()` commands
  joint-space targets; `set_speed_percent()` sets relative speed.
- Local SDK v112 driver:
  `enable(joint_index=255, timeout=...)` is supported for all-joint enable.
- Local ROS driver:
  `/control/move_j` ultimately calls SDK `move_j()` and is additionally gated
  by ROS `auto_enable`, `control_enabled`, and feedback readiness.
- New script:
  `examples/nero_sdk_single_joint_step.py`.
- New procedure:
  `docs/s10_2_sdk_motion_plan.md`.
- Verification commands:
  `python3 -m py_compile examples/nero_sdk_single_joint_step.py`
  and
  `.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py --help`
  both passed.

Result:

- S10.2 is prepared but not executed.
- The script defaults to dry-run and requires `--execute` to send any motion.

Deployment choices:

- Test SDK before ROS because SDK is the direct control layer underneath the ROS
  driver and avoids ROS launch/topic gate variables for this step.
- Scope is Arm A, `can_arm_a`, J7, `+1 deg`, speed `5%`, then return to the
  original angle.
- The script reads current 7-joint feedback, modifies only J7, verifies SDK
  joint limits, refuses speed above `10%`, and refuses delta above `2 deg` by
  default.
- Do not disable the arm at script end because disabling can allow gravity
  motion depending on posture and brake state.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_2_sdk_motion_plan.md`,
`examples/nero_sdk_single_joint_step.py`.

Verification:
Static Python compilation and `--help` passed. No robot motion command was sent
by this agent.

Route updates:
S10.2 SDK dry-run is next. SDK execution requires operator safety confirmation
after dry-run output is checked.

Open risks:

- SDK execution still enables all joints and sends real CAN motion; keep one
  active control source and a human emergency-stop/power-cutoff assignment.
- Arm A `arm_status` state-machine value should continue to be monitored.
- ROS motion remains pending until S10.2 SDK motion is accepted.

Next:
Run the SDK dry-run command from `docs/s10_2_sdk_motion_plan.md`. If the target
is correct and safety gate remains true, run the `--execute` command and then
capture a ROS read-only snapshot.

## 2026-06-25 - S10.2 SDK J7 Dry-Run Passed, Execution Candidate Revised To J1

Phase: S10 首次低速运动

Goal:
Evaluate SDK dry-run output and decide the execution joint for observability.

Action:
Operator ran the SDK dry-run for Arm A J7 without `--execute`.

Commands / evidence:

- Command:
  `.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py --channel can_arm_a --firmware v112 --joint 7 --delta-deg 1 --speed-percent 5`
- Output reported firmware: `{'software_version': '1.121'}`.
- Current Arm A joint angles in degrees:
  `[55.5, 70.798, -29.599, 41.602000000000004, 21.6, -39.999, -35.5]`.
- Target Arm A joint angles in degrees:
  `[55.5, 70.798, -29.599, 41.602000000000004, 21.6, -39.999, -34.5]`.
- Pre-status:
  `ctrl_mode=CAN_CTRL(0x1)`,
  `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- Script ended in dry-run mode; no motion was sent.
- Operator proposed using J1 instead of J7 because J7 rotation is hard to
  observe visually.

Result:

- SDK dry-run path is healthy.
- J7 dry-run target was correct and changed only J7 by `+1 deg`.
- No SDK motion has been executed.
- Execution candidate is revised from J7 to J1, pending a new J1 dry-run.

Deployment choices:

- Accept J1 as the next dry-run/execution candidate because `1 deg` J1 motion
  is more observable than J7 wrist rotation.
- Recognize the added risk: J1 moves the whole arm around the base. Before
  execution, the entire small J1 swept area must be clear.
- Keep all other constraints unchanged: Arm A only, `can_arm_a`, `+1 deg`,
  speed `5%`, SDK only, then return to the original angle.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_2_sdk_motion_plan.md`.

Verification:
Dry-run output is consistent with a J7-only target change and healthy status.

Route updates:
S10.2 remains active. Run a new J1 dry-run before considering SDK execution.

Open risks:

- J1 has larger workspace sweep than J7 even at `1 deg`.
- No SDK motion has been accepted yet.

Next:
Run the SDK J1 dry-run command. If it changes only J1 by `+1 deg`, and the J1
swept area is confirmed clear, proceed to the SDK `--execute` command.

## 2026-06-25 - S10.2 SDK J1 Dry-Run Passed, Delta Revised To 2 Degrees

Phase: S10 首次低速运动

Goal:
Evaluate the revised J1 dry-run and decide whether the execution delta should
remain `1 deg` or increase slightly for observability.

Action:
Operator ran the SDK dry-run for Arm A J1 without `--execute`.

Commands / evidence:

- Command:
  `.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py --channel can_arm_a --firmware v112 --joint 1 --delta-deg 1 --speed-percent 5`
- Output reported firmware: `{'software_version': '1.121'}`.
- Current Arm A joint angles in degrees:
  `[55.498000000000005, 70.796, -29.599, 41.599000000000004, 21.599, -40.0, -35.499]`.
- Target Arm A joint angles in degrees:
  `[56.49800000000001, 70.796, -29.599, 41.599000000000004, 21.599, -40.0, -35.499]`.
- Pre-status:
  `ctrl_mode=CAN_CTRL(0x1)`,
  `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- Script ended in dry-run mode; no motion was sent.
- Operator confirmed the J1 swept area is clear and requested a slightly larger
  J1 angle for easier observation.

Result:

- J1 `+1 deg` dry-run is accepted.
- No SDK motion has been executed.
- Execution delta is revised to J1 `+2 deg`, pending a new `+2 deg` dry-run.

Deployment choices:

- Keep the delta at the script's default safety ceiling of `2 deg`; do not
  increase above this for first SDK motion.
- At the manual working radius of about `580 mm`, `2 deg` corresponds to about
  `20 mm` arc displacement at the outer radius, which should be observable
  while still being a small joint-space command.
- Preserve all other constraints: Arm A only, `can_arm_a`, speed `5%`, SDK only,
  then return to the original angle.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_2_sdk_motion_plan.md`.

Verification:
Dry-run output is consistent with a J1-only `+1 deg` target change and healthy
status.

Route updates:
S10.2 remains active. Run a new J1 `+2 deg` dry-run before SDK execution.

Open risks:

- J1 moves the full arm around the base; swept area must remain clear during
  execution.
- No SDK motion has been accepted yet.

Next:
Run the SDK J1 `+2 deg` dry-run command. If it changes only J1 by `+2 deg`, and
the safety gate remains true, proceed to the SDK `--execute` command.

## 2026-06-25 - S10.2 SDK J1 Motion Passed

Phase: S10 首次低速运动

Goal:
Record and evaluate the first SDK-controlled real motion.

Action:
Operator executed the SDK single-joint step on Arm A J1.

Commands / evidence:

- Command:
  `.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py --execute --channel can_arm_a --firmware v112 --joint 1 --delta-deg 2 --speed-percent 10`
- Operator report: J1 visibly moved upward a small amount and then returned to
  the original position.
- Firmware: `{'software_version': '1.121'}`.
- Current Arm A joint angles in degrees:
  `[55.499, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.502]`.
- Target Arm A joint angles in degrees:
  `[57.499, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.502]`.
- After-step angles:
  `[57.503, 70.8, -29.625000000000004, 41.598, 21.6, -39.999, -35.502]`.
- After-return angles:
  `[55.49500000000001, 70.8, -29.619, 41.597, 21.6, -40.005, -35.502]`.
- Pre, enabled, and final statuses were all:
  `ctrl_mode=CAN_CTRL(0x1)`,
  `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- Script printed:
  `S10.2 SDK single-joint step completed.`

Result:

- S10.2 SDK single-joint motion is accepted for Arm A.
- J1 moved by about `+2 deg` and returned to the original angle within normal
  feedback tolerance.
- Actual speed percent was `10`, not the planned `5`; this is accepted because
  it stayed within the script's S10.2 hard limit of `0..10`.

Deployment choices:

- Keep future first-time control-path motions at or below `10%`; prefer `5%`
  unless observability requires otherwise.
- Do not proceed to ROS motion until the post-SDK ROS read-only snapshot is
  captured and accepted.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_2_sdk_motion_plan.md`.

Verification:
SDK script output and operator visual observation indicate successful motion and
return. ROS post-motion validation is still pending.

Route updates:
S10.2 SDK motion has passed. S10.2 post-SDK ROS read-only validation is next.

Open risks:

- Need post-SDK ROS snapshot to confirm both arms still have clean feedback.
- Intentional emergency-stop recovery remains untested.

Next:
Start dual-arm ROS read-only validation and capture a post-SDK snapshot.

## 2026-06-25 - S10.2 Post-SDK ROS Snapshot Accepted And S10.3 Prepared

Phase: S10 首次低速运动

Goal:
Accept the post-SDK read-only validation and prepare the ROS control-layer test.

Action:
Read `docs/s9_ros_snapshots/20260625_062910/`, then created the S10.3 ROS
single-joint procedure and helper script.

Commands / evidence:

- Snapshot: `docs/s9_ros_snapshots/20260625_062910/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback and
  control topics.
- Arm A joint-state frequency: about `200.0 Hz`.
- Arm B joint-state frequency: about `200.0 Hz`.
- Arm A `arm_status`:
  - `ctrl_mode: 1`
  - `arm_status: 0`
  - `mode_feedback: 1`
  - `motion_status: 0`
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm B `arm_status`:
  - `ctrl_mode: 1`
  - `arm_status: 6`
  - `mode_feedback: 1`
  - `motion_status: 1`
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- New script:
  `scripts/ros_single_joint_step.py`.
- New procedure:
  `docs/s10_3_ros_motion_plan.md`.
- Verification:
  `python3 -m py_compile scripts/ros_single_joint_step.py` passed.

Result:

- S10.2 SDK motion is fully accepted, including post-SDK ROS read-only
  validation.
- S10.3 ROS single-joint test is prepared but not executed.

Deployment choices:

- S10.3 will test ROS after SDK because ROS wraps the SDK and adds launch
  parameters, enable behavior, control gate, and topic delivery.
- Scope remains Arm A only: ROS namespace `/arm_a`, `can_arm_a`, `joint1 +2 deg`,
  then return to original angle.
- ROS driver speed is planned at `5%`; `10%` remains the maximum for first
  control-path tests.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_2_sdk_motion_plan.md`,
`docs/s10_3_ros_motion_plan.md`, `scripts/ros_single_joint_step.py`.

Verification:
Post-SDK ROS snapshot is clean. S10.3 script static compilation passed. No ROS
motion was sent by this agent.

Route updates:
S10.3 ROS dry-run is next.

Open risks:

- S10.3 requires an Arm A ROS control driver with `auto_enable:=true` and
  `control_enabled:=true`; do not leave the dual read-only driver running.
- Intentional emergency-stop recovery remains untested.
- No Cartesian, MoveIt, MIT/JS, raw CAN, dual-arm, or dexterous-hand motion is
  allowed in S10.3.

Next:
Start the Arm A ROS control driver, run the S10.3 dry-run, verify only
`joint1 +2 deg`, then decide whether to execute.

## 2026-06-25 - S10.3 ROS Dry-Run Passed

Phase: S10 首次低速运动

Goal:
Verify the ROS command target before sending a real ROS motion command.

Action:
Operator ran `scripts/ros_single_joint_step.py` in dry-run mode inside the
Humble container.

Commands / evidence:

- Command:
  `NERO_CONTAINER_NAME=nero-humble-s10-ros-tool bash scripts/run_humble_container.sh python3 /workspace/nero/scripts/ros_single_joint_step.py --namespace arm_a --joint joint1 --delta-deg 2`
- Feedback topic: `/arm_a/feedback/joint_states`.
- Command topic: `/arm_a/control/move_j`.
- Current degrees:
  `[55.498000000000005, 70.797, -29.62, 41.599000000000004, 21.6, -39.998, -35.505]`.
- Target degrees:
  `[57.498000000000005, 70.797, -29.62, 41.599000000000004, 21.6, -39.998, -35.505]`.
- Pre-status:
  `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`, `motion_status=0`.
- Script ended with:
  `Dry run only. Add --execute after the S10.3 safety gate is confirmed.`

Result:

- S10.3 ROS dry-run is accepted.
- No ROS motion has been executed yet.

Deployment choices:

- Proceed to S10.3 ROS execution only if the Arm A ROS control driver remains
  running, the J1 swept area remains clear, and no Web/SDK command is active.
- Keep the command as Arm A only, `joint1 +2 deg`, then return to original
  angle.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_3_ros_motion_plan.md`.

Verification:
Dry-run target changes only `joint1` by `+2 deg`; pre-status is healthy.

Route updates:
S10.3 ROS execution is pending.

Open risks:

- ROS control driver uses `auto_enable:=true control_enabled:=true`; keep only
  the Arm A control driver active.
- Intentional emergency-stop recovery remains untested.

Next:
Run the S10.3 `--execute` command if the safety gate remains true.

## 2026-06-25 - S10.3 ROS J1 Motion Passed, Post-Snapshot Pending

Phase: S10 首次低速运动

Goal:
Record the first ROS-controlled real motion result.

Action:
Operator executed the S10.3 ROS single-joint step on Arm A.

Commands / evidence:

- Command:
  `NERO_CONTAINER_NAME=nero-humble-s10-ros-tool bash scripts/run_humble_container.sh python3 /workspace/nero/scripts/ros_single_joint_step.py --execute --namespace arm_a --joint joint1 --delta-deg 2`
- Operator report: J1 angle change was visually observable and returned to the
  original position.
- Feedback topic: `/arm_a/feedback/joint_states`.
- Command topic: `/arm_a/control/move_j`.
- Current degrees:
  `[55.498000000000005, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.505]`.
- Target degrees:
  `[57.498000000000005, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.505]`.
- After-step degrees:
  `[57.294000000000004, 70.801, -29.615000000000002, 41.595, 21.6, -39.999, -35.505]`.
- After-return degrees:
  `[55.743, 70.798, -29.613999999999997, 41.598, 21.6, -39.999, -35.505]`.
- Final status:
  `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`, `motion_status=1`.
- Script completed with:
  `S10.3 ROS single-joint step completed.`

Result:

- S10.3 ROS motion is accepted by operator observation and script target
  tolerance.
- J1 return error was about `0.245 deg`, within script tolerance `0.3 deg`.
- Final printed `motion_status=1` is an observation item, so S10.3 still needs
  a post-motion dual-arm ROS read-only snapshot before full acceptance.

Deployment choices:

- Stop the Arm A ROS control driver before starting the dual-arm read-only
  validation driver.
- Do not proceed to Cartesian, MoveIt, MIT/JS, dual-arm, raw CAN, or dexterous
  hand motion until S10.3 post-motion validation is accepted.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_3_ros_motion_plan.md`.

Verification:
Script output and operator observation indicate successful ROS motion and
return. Post-motion ROS read-only snapshot is still pending.

Route updates:
S10.3 post-motion ROS read-only validation is next.

Open risks:

- Final printed `motion_status=1` needs interpretation through the next
  read-only snapshot.
- Intentional emergency-stop recovery remains untested.

Next:
Stop the Arm A ROS control driver, start dual-arm read-only validation, and
capture a post-ROS snapshot.

## 2026-06-25 - S10.3 Post-ROS Snapshot Accepted

Phase: S10 首次低速运动

Goal:
Accept the post-ROS read-only validation and close the Arm A Web/SDK/ROS
single-joint motion ladder.

Action:
Read `docs/s9_ros_snapshots/20260625_064243/`.

Commands / evidence:

- Snapshot: `docs/s9_ros_snapshots/20260625_064243/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback and
  control topics.
- Arm A joint-state frequency: about `200.0 Hz`.
- Arm B joint-state frequency: about `200.0 Hz`.
- Arm A `arm_status`:
  - `ctrl_mode: 1`
  - `arm_status: 0`
  - `mode_feedback: 1`
  - `motion_status: 0`
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm B `arm_status`:
  - `ctrl_mode: 1`
  - `arm_status: 6`
  - `mode_feedback: 1`
  - `motion_status: 1`
  - `err_status: 0`
  - all joint angle limits `false`
  - all joint communication statuses `false`
- Arm A post-ROS joint positions in radians:
  `[0.9686228282718131, 1.2356756571194656, -0.5170188843182802,
  0.7260569688296411, 0.3769911184307752, -0.6981142475052119,
  -0.6197140575056266]`.

Result:

- S10.3 ROS single-joint motion is fully accepted.
- The final printed `motion_status=1` from the execution script is resolved by
  the post-motion snapshot showing Arm A `motion_status=0`.
- Arm A has now passed Web, SDK, and ROS single-joint low-speed motion with
  post-motion ROS read-only validation.

Deployment choices:

- Do not broaden immediately to Cartesian, MoveIt, MIT/JS, raw CAN, dual-arm,
  or dexterous-hand motion.
- Next preferred step is S10.4 stop/recovery and control-source closure.
- If Arm B motion parity is required before S11/S12, repeat the same minimal
  Web/SDK/ROS ladder on Arm B with separate post-motion snapshots.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`, `docs/s10_3_ros_motion_plan.md`.

Verification:
Post-ROS snapshot is complete and clean for both arms.

Route updates:
S10.3 accepted. S10.4 stop/recovery and safe control-source closure is next.

Open risks:

- Intentional emergency-stop recovery remains untested.
- Arm B has not yet gone through the same motion ladder.
- External lab-frame transforms for dual-arm coordination remain unmeasured.

Next:
Prepare S10.4 stop/recovery and control-source closure, then decide whether to
repeat minimal motion on Arm B or defer to later dual-arm planning.

## 2026-06-25 - S10.4 Closure Plan Prepared

Phase: S10 首次低速运动

Goal:
Prepare a no-motion stop/recovery and control-source closure step before
replicating the first-motion ladder on Arm B.

Action:
Created the S10.4 closure document and a read-only control-source audit script.
No emergency stop, power cut, Web motion, SDK motion, ROS motion, raw CAN
command, Cartesian command, or dual-arm command was sent by the agent.

Commands / evidence:

- New procedure: `docs/s10_4_stop_recovery_closure.md`.
- New audit helper: `scripts/s10_control_source_audit.sh`.
- Codex-session audit output:
  `docs/s10_4_control_source_audit_codex_20260625_150052.txt`.
- Last accepted motion evidence remains
  `docs/s9_ros_snapshots/20260625_064243/`.

Result:

- S10.4 is prepared. A Codex-session audit was saved, but live
  desktop-terminal audit is still pending because the Codex session could not
  see the CAN interfaces.
- Recommended handoff state before Arm B motion is `handoff_to_arm_b`.
- Intentional emergency-stop recovery and power-cut recovery remain deferred.

Deployment choices:

- Stop or account for any Arm A ROS control driver before Arm B motion.
- Dual-arm read-only monitoring may be used for observation, but should be
  stopped before Arm B Web/SDK/ROS motion so only one deliberate control source
  remains.
- Arm B should repeat the same minimal ladder as Arm A: Web single-joint,
  SDK single-joint, ROS single-joint, each followed by read-only validation.

Files changed:
`agent.md`, `config/nero.env`, `docs/deployment_log.md`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/机器人部署与调试行动路线.md`,
`docs/s10_4_stop_recovery_closure.md`,
`docs/s10_4_control_source_audit_codex_20260625_150052.txt`,
`scripts/s10_control_source_audit.sh`.

Verification:
`bash -n scripts/s10_control_source_audit.sh` passed. The script was also run
once from the Codex session and reported `can_arm_a` and `can_arm_b` as not
visible, Docker status unavailable without interactive sudo, and no
NERO-related host process. Because the CAN interfaces were not visible from
that session, this does not replace live desktop-terminal audit.

Route updates:
S10.4 is now the active immediate step. Arm B replication starts only after
S10.4 closure is accepted.

Open risks:

- Intentional emergency-stop recovery remains untested.
- Arm B has not yet gone through motion parity.
- Active control sources must be confirmed from the live machine before any
  further motion.

Next:
Run the S10.4 audit from the real desktop terminal, record the handoff state,
then start Arm B first-motion replication if the audit is clean.

## 2026-06-25 - S10.4 Live Audit Accepted And Git Boundary Defined

Phase: S10 首次低速运动 / repository baseline

Goal:
Accept the live S10.4 closure and prepare the project for the first git commit.

Action:
Recorded the operator's real desktop-terminal S10.4 audit and defined which
workspace contents belong in the baseline repository.

Commands / evidence:

- Live audit output saved to
  `docs/s10_4_control_source_audit_live_20260625_150438.txt`.
- `can_arm_a`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- `can_arm_b`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- NERO-related Docker containers: none.
- NERO-related host processes: none.
- Upstream repo status checks were clean:
  - `upstream/agx_arm_ros`
  - `upstream/pyAgxArm`
  - `upstream/piper_ros`
- Upstream commits recorded in `README.md`:
  - `agx_arm_ros`: `c73d33f2ab377447261423f1b881bd89c6663627`
  - `pyAgxArm`: `a226840db0c3d5c5dc7f3ec78d6cef1a6800f9e6`
  - `piper_ros`: `2dc30fca68cbf4e04d1d0bc15c123d026380ece7`

Result:

- S10.4 no-motion control-source closure is accepted.
- Handoff state is `handoff_to_arm_b`.
- The next operational step is Arm B Web/SDK/ROS first-motion replication.
- Before that, create the first repository baseline commit.

Deployment choices:

- Track `docs/`, `scripts/`, `examples/`, `config/`, `docker/`, `README.md`,
  and `agent.md`.
- Do not track `upstream/`, because the repos are clean and reproducible from
  URL plus commit.
- Do not track `.venv/`, local agent metadata, Python caches, or ROS build
  outputs.
- Keep `docs/` tracked even though it contains large CAD and evidence files;
  it is part of this deployment package.

Files changed:
`.gitignore`, `README.md`, `agent.md`, `config/nero.env`,
`docs/current_bringup_status.md`, `docs/bringup_checklist.md`,
`docs/deployment_log.md`, `docs/机器人部署与调试行动路线.md`,
`docs/s10_4_stop_recovery_closure.md`,
`docs/s10_4_control_source_audit_live_20260625_150438.txt`.

Verification:
S10.4 live audit is clean. Upstream working trees are clean. Git is installed
but the root `.git/` directory is currently an empty invalid repository
directory and must be converted into a valid git repository before committing.

Route updates:
S10.4 accepted. First git baseline commit is next; Arm B replication follows.

Open risks:

- First commit will include large `docs/` assets, about `434 MB`.
- Remote hosting may later require Git LFS or a different artifact policy, but
  local baseline commit can proceed now.

Next:
Initialize git, stage the project package according to `.gitignore`, review the
staged set, and create the first commit.

## 2026-06-25 - Git Repository Initialized And Baseline Staged

Phase: repository baseline

Goal:
Create the first git baseline for the NERO deployment package before Arm B
motion replication.

Action:
Converted the project root into a valid git repository and staged the baseline
package according to `.gitignore`.

Commands / evidence:

- `git init` succeeded after removing the previous empty invalid `.git/`
  directory.
- Default branch HEAD was set to `main`.
- `git add .` staged the project package.
- `git diff --cached --name-only` showed no staged `upstream/`, `.venv/`,
  `.agents/`, `.codex/`, root `bash`, Python cache, `__MACOSX/`, or `._*`
  paths.
- Staged file count before commit: `126`.

Result:

- The repository baseline is ready for the first commit.
- `upstream/` remains present locally but ignored because the three upstream
  working trees are clean and reproducible from `README.md`.
- `docs/` remains tracked as part of the deployment evidence package.

Deployment choices:

- Commit on branch `main`.
- Commit message: `Initial NERO bring-up baseline`.

Verification:
Shell scripts passed `bash -n`. Python helper scripts passed `py_compile`.

Route updates:
After the baseline commit, proceed to Arm B Web/SDK/ROS first-motion
replication using the same staged procedure that passed on Arm A.

Open risks:

- The baseline contains large CAD/evidence assets in `docs/`; this is accepted
  for local traceability. Remote publishing may need a separate artifact or LFS
  policy.

Next:
Run the first commit.

## 2026-06-25 - Arm B First-Motion Replication Prepared

Phase: S10 首次低速运动

Goal:
Start Arm B motion validation after Arm A Web/SDK/ROS ladder, S10.4 closure,
and the first git baseline commit.

Action:
Created the Arm B first-motion replication plan and updated project status,
checklist, route, and environment defaults.

Commands / evidence:

- New procedure: `docs/s10_5_arm_b_first_motion_plan.md`.
- Current accepted handoff state from S10.4: `handoff_to_arm_b`.
- Arm B identity:
  - Web SSID: `agx-7ax-armB`
  - CAN: `can_arm_b`
  - ROS namespace: `arm_b`
  - USB bus: `1-11:1.0`
- Baseline git commit exists:
  `fb8a262 Initial NERO bring-up baseline`.

Result:

- S10.5 is prepared but not executed.
- The next real motion is Arm B Web-only J1 `+2 deg`, then return to the
  original angle.
- SDK and ROS Arm B motion remain pending until S10.5 Web motion and post-Web
  read-only snapshot pass.

Deployment choices:

- Use J1 again because Arm A showed J7 is hard to observe visually and J1
  `+2 deg` is observable.
- Keep the Arm B Web first step narrower than Arm A's actual Web result: one
  joint only, not all 7 degrees of freedom.
- Require a fresh control-source audit before touching Arm B Web motion.
- Require a post-Web dual-arm ROS read-only snapshot before SDK or ROS motion
  on Arm B.

Files changed:
`agent.md`, `config/nero.env`, `docs/current_bringup_status.md`,
`docs/bringup_checklist.md`, `docs/deployment_log.md`,
`docs/机器人部署与调试行动路线.md`,
`docs/s10_5_arm_b_first_motion_plan.md`.

Verification:
`bash -n scripts/*.sh` passed. Python helper scripts passed `py_compile`.
S10.5 references were checked across status, checklist, route, agent rules, and
environment defaults. No Arm B motion has been sent.

Route updates:
Immediate next step is S10.5 Arm B Web first motion.

Open risks:

- Arm B J1 swept area must be checked independently; do not assume Arm A
  clearance applies to Arm B.
- Operator must verify Web is connected to Arm B, not Arm A.
- Intentional emergency-stop recovery remains deferred.

Next:
Run the S10.5 pre-motion gate and Web J1 `+2 deg` return test on Arm B.

## 2026-06-25 - S10.5 Arm B Audit And Snapshot Clean

Phase: S10 首次低速运动

Goal:
Record the Arm B S10.5 pre-motion audit and the following read-only validation
snapshot.

Action:
Read the operator-provided audit output and ROS read-only snapshot
`docs/s9_ros_snapshots/20260625_072129/`.

Commands / evidence:

- Pre-motion audit saved to:
  `docs/s10_5_control_source_audit_live_20260625_152039.txt`.
- Audit result:
  - `can_arm_a`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
  - `can_arm_b`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
  - NERO-related Docker containers: none.
  - NERO-related host processes: none.
- Snapshot:
  `docs/s9_ros_snapshots/20260625_072129/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback and
  control topics.
- Arm A joint-state frequency: about `200 Hz`.
- Arm B joint-state frequency: about `200 Hz`.
- Arm A `arm_status`: `err_status: 0`, all joint angle limits `false`, all
  joint communication statuses `false`.
- Arm B `arm_status`: `err_status: 0`, all joint angle limits `false`, all
  joint communication statuses `false`.
- Arm B sampled joint positions in radians:
  `[0.5724505413616201, 1.3979912775549381, -0.3002140846355446,
  0.3630110311223006, -1.2374035330789397, 0.37346555334174664,
  0.16057029118347835]`.

Result:

- S10.5 audit and read-only validation are clean.
- S10.5 is not fully accepted yet because the chat log has not explicitly
  recorded whether Arm B Web J1 `+2 deg` actually moved normally and returned
  to the original angle.

Deployment choices:

- Do not skip the SDK dry-run just because Arm A passed.
- It is acceptable to streamline S10.6 by running dry-run and, if the printed
  target/status are correct, immediately running the execute command manually.
- Keep post-motion ROS read-only snapshots after each control layer.

Files changed:
`agent.md`, `config/nero.env`, `docs/current_bringup_status.md`,
`docs/bringup_checklist.md`, `docs/deployment_log.md`,
`docs/机器人部署与调试行动路线.md`,
`docs/s10_5_arm_b_first_motion_plan.md`,
`docs/s10_5_control_source_audit_live_20260625_152039.txt`,
`docs/s9_ros_snapshots/20260625_072129/`.

Verification:
Snapshot is complete and clean for both arms. Web motion outcome needs one
operator confirmation before S10.6.

Route updates:
S10.6 SDK can start after the operator confirms Arm B Web J1 motion and return.

Open risks:

- Moving faster is acceptable only by reducing waiting between gates, not by
  removing gates.
- Intentional emergency-stop recovery remains deferred.

Next:
Confirm Arm B Web J1 `+2 deg` motion and return, then run S10.6 SDK dry-run on
`can_arm_b`.

## 2026-06-25 - S10.5 Accepted And S10.6 SDK Dry-Run Accepted

Phase: S10 首次低速运动

Goal:
Close Arm B Web first motion and accept the Arm B SDK dry-run before SDK
execution.

Action:
Recorded operator confirmation that Arm B Web motion was normal, then recorded
the SDK dry-run output and read-only snapshot `20260625_072742`.

Commands / evidence:

- Operator statement: Arm B Web side was normal.
- SDK dry-run command:
  `.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py --channel can_arm_b --firmware v112 --joint 1 --delta-deg 2 --speed-percent 5`
- SDK dry-run output:
  - firmware: `{'software_version': '1.121'}`
  - current degrees:
    `[32.799, 80.10000000000001, -17.199, 20.799, -70.9, 21.398,
    9.200000000000001]`
  - target degrees:
    `[34.799, 80.10000000000001, -17.199, 20.799, -70.9, 21.398,
    9.200000000000001]`
  - `pre_status`: `CAN_CTRL`, `NORMAL`, `MOVE_J`,
    `REACH_TARGET_POS_SUCCESSFULLY`
  - dry run only; no SDK motion occurred
- Read-only snapshot:
  `docs/s9_ros_snapshots/20260625_072742/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Arm A joint-state frequency: about `200 Hz`.
- Arm B joint-state frequency: about `200 Hz`.
- Arm A and Arm B `err_status: 0`.
- Arm A and Arm B joint angle limits and joint communication statuses: all
  `false`.

Result:

- S10.5 Arm B Web first motion is accepted.
- S10.6 Arm B SDK dry-run is accepted.
- S10.6 SDK execution is pending.

Deployment choices:

- Proceed faster by chaining the next commands manually, but do not skip gates.
- Before SDK `--execute`, stop the dual-arm read-only driver that was launched
  for the snapshot.
- Keep SDK execution at J1 `+2 deg`, speed `5%`, then return to the original
  angle.

Files changed:
`agent.md`, `config/nero.env`, `docs/current_bringup_status.md`,
`docs/bringup_checklist.md`, `docs/deployment_log.md`,
`docs/机器人部署与调试行动路线.md`,
`docs/s10_5_arm_b_first_motion_plan.md`,
`docs/s10_6_arm_b_sdk_motion_plan.md`,
`docs/s9_ros_snapshots/20260625_072742/`.

Verification:
SDK dry-run target changes only Arm B J1 by `+2 deg`. Read-only snapshot is
complete and clean for both arms.

Route updates:
Immediate next step is S10.6 SDK execution on `can_arm_b`.

Open risks:

- Running SDK execute while the dual-arm read-only driver is still active would
  violate the one-motion-control-source rule. Stop the driver first.
- Intentional emergency-stop recovery remains deferred.

Next:
Stop dual-arm read-only, run the S10.6 SDK execute command, then capture a
post-execute read-only snapshot.

## 2026-06-25 - S10.6 Arm B SDK Motion Accepted And S10.7 Prepared

Phase: S10 首次低速运动

Goal:
Accept Arm B SDK execution and prepare the Arm B ROS single-joint replication
step.

Action:
Recorded the operator's SDK execution result, read post-SDK snapshot
`docs/s9_ros_snapshots/20260625_074048/`, and created the S10.7 ROS plan.

Commands / evidence:

- Operator report: Arm B SDK real motion was observed successfully and execution
  was smooth.
- Full SDK execute terminal output was not pasted, so exact `after_step_deg`
  and `after_return_deg` values are not recorded.
- Post-SDK snapshot:
  `docs/s9_ros_snapshots/20260625_074048/`.
- Snapshot `README.md`: `Failed capture commands: 0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback and
  control topics.
- Arm A joint-state frequency: about `200 Hz`.
- Arm B joint-state frequency: about `200 Hz`.
- Arm A `arm_status`: `err_status: 0`, all joint angle limits `false`, all
  joint communication statuses `false`.
- Arm B `arm_status`: `err_status: 0`, all joint angle limits `false`, all
  joint communication statuses `false`.
- Arm B sampled joint positions in radians:
  `[0.57246799465414, 1.3979563709698983, -0.30017917805050476,
  0.36302848441482055, -1.2374035330789397, 0.37355281980434635,
  0.16053538459843844]`.
- New ROS plan:
  `docs/s10_7_arm_b_ros_motion_plan.md`.

Result:

- S10.6 Arm B SDK execution is accepted.
- S10.7 Arm B ROS motion is prepared but not executed.

Deployment choices:

- S10.7 must start with dry-run, not execute.
- Stop the dual-arm read-only driver before starting the Arm B ROS control
  driver.
- Start only the Arm B ROS control driver for S10.7:
  `namespace:=arm_b`, `can_port:=can_arm_b`, `auto_enable:=true`,
  `control_enabled:=true`, `speed_percent:=5`.
- Keep the motion target as `joint1 +2 deg`, then return to original angle.

Files changed:
`agent.md`, `config/nero.env`, `docs/current_bringup_status.md`,
`docs/bringup_checklist.md`, `docs/deployment_log.md`,
`docs/机器人部署与调试行动路线.md`,
`docs/s10_6_arm_b_sdk_motion_plan.md`,
`docs/s10_7_arm_b_ros_motion_plan.md`,
`docs/s9_ros_snapshots/20260625_074048/`.

Verification:
Post-SDK snapshot is complete and clean for both arms.

Route updates:
Immediate next step is S10.7 ROS dry-run on `/arm_b`.

Open risks:

- ROS control driver uses `auto_enable:=true` and `control_enabled:=true`; keep
  only Arm B control active.
- Intentional emergency-stop recovery remains deferred.

Next:
Stop dual-arm read-only, start the Arm B ROS control driver, and run S10.7
dry-run.
