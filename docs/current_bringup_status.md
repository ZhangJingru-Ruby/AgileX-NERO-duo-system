# NERO Current Bring-Up Status

Last updated: 2026-06-25

## Confirmed Configuration

| Item | Current value |
| --- | --- |
| Current end effector | Bare arm |
| Planned end effector | Dexterous hand, to be installed later |
| Physical arm count | Two NERO arms, independently powered |
| Arm A | Web verified; hotspot `agx-7ax-armA`; planned CAN `can_arm_a`; ROS namespace `arm_a` |
| Arm B | Web verified; hotspot `agx-7ax-armB`; planned CAN `can_arm_b`; ROS namespace `arm_b` |
| USB-CAN modules | Two official modules confirmed; one per arm |
| Arm A USB-CAN bus-info | `1-5:1.0` |
| Arm B USB-CAN bus-info | `1-11:1.0` |
| Arm A USB physical port | Vertical USB port |
| Arm B USB physical port | Horizontal USB port |
| Installation pose | Table upright / horizontal upright |
| Power supply | Original factory adapter |
| Web UI | Reachable at `http://192.168.31.1/#/welcome` |
| Observed Web model | `7ax`, one NERO 7-axis controller/arm per physical arm |
| Observed Web footer version | `v1.121`; current SDK firmware selector is `v112` |
| Workspace | Clear enough for bring-up |
| Power cutoff path | Known and reachable |
| Manual key images | Present under `docs/pics/` |

## Current Phase

| Phase | Status | Notes |
| --- | --- | --- |
| S0 资料基线 | Complete | Manual text, CAN protocol, CAD files, and key manual images are present. |
| S1 安全与场地 | Complete for planning | Before power-on, perform the final physical checklist again on site. |
| S2 主机环境 | Complete for offline bring-up | Shared Ubuntu 20.04 host has SDK/CAN-only tools; Docker ROS2 Humble image and `agx_arm_ros` workspace build are complete. |
| S3 离线模型 | Complete | NERO URDF/xacro/check_urdf/robot_state_publisher checks pass; desktop RViz GUI verification succeeded. |
| S4 机械与电气连接 | Power-on successful, final wiring evidence pending | Robot powered on through the factory adapter; Web page is reachable. |
| S5 Web 验机 | Complete for both arms | Arm A and Arm B Web checks passed; Wi-Fi hotspots are unique. |
| S6 CAN 只读 | Interface activation passed, feedback capture reported normal | `can_arm_a` and `can_arm_b` are UP, ERROR-ACTIVE, bitrate `1000000`; operator reports normal CAN frames. |
| S7 SDK 只读 | Complete by operator report | SDK read-only checks passed on `can_arm_a` and `can_arm_b`. |
| S8 ROS 只读 | Complete; coordinate alignment deferred to S9 | `/arm_a` and `/arm_b` feedback topics publish at about 200 Hz; arm status has `err_status: 0`; RViz follow is normal after the dual ROS read-only driver terminal is started first. |
| S9 标定与配置 | Complete by operator confirmation and ROS revalidation | Load mode was changed by operator report; Arm A CAN recovered after USB-CAN replug/reactivation; S9.3 snapshot `20260625_054435` has complete A/B feedback, `err_status: 0`, no joint limits, no joint communication errors, and about 200 Hz joint-state feedback. |
| S10 首次低速运动 | Arm A Web/SDK/ROS ladder and S10.4 closure accepted; Arm B S10.5 prepared | Web first motion, SDK J1 motion, and ROS J1 motion passed on Arm A. Post-ROS snapshot `20260625_064243` is clean for A/B with about 200 Hz feedback, `err_status: 0`, no joint limits, and no joint communication errors. Live S10.4 audit `20260625_150438` is clean. Arm B Web first-motion replication is prepared in `docs/s10_5_arm_b_first_motion_plan.md`. |

## S0 Evidence

Confirmed:

- User manual text: `docs/nero 用户手册.md`
- CAN protocol: `docs/机械臂通信协议V1.2.1.xlsx`
- Base model: `docs/nero3d.stp`
- Gripper and dexterous hand models: `docs/nero带夹爪以及带灵巧手模型/`
- Key manual images: `docs/pics/`

Manual image index:

| Purpose | File | Confirmed information |
| --- | --- | --- |
| Control panel | `docs/pics/2.1.1控制面板说明.png` | Wi-Fi antenna, aviation connector, status indicator, network port, internal-service port positions. |
| Aviation connector | `docs/pics/航插接口示意图.jpg` | Connector red dot must align with panel red dot before insertion. |
| End connector | `docs/pics/2.1.2末端连接电器说明.png` | End XT30 2+2 pinout: upper power `+/-`, lower CAN `H/L`. |
| Base mounting | `docs/pics/2.3.1 底座安装说明.png` | Base mounting pattern includes 4 x Ø5.4 through holes on a 70 mm x 70 mm pattern, compatible with M5 fastening. |
| CAN wiring | `docs/pics/3.1can线链接.jpg` | Red/black go to power adapter branch; yellow/blue go to USB-CAN branch. |
| CAN terminal | `docs/pics/3.1can线链接1.png` | Wire cores must be clamped at the terminal center; yellow is CAN_H, blue is CAN_L, final check follows terminal labels. |
| Power sequence | `docs/pics/3.2上电使用说明.png` | Physical harness/power connection is completed before USB-CAN host-side setup. |
| Dexterous hand size | `docs/pics/4 灵巧手示意图.png` | Hand clearance and flange dimensions are available for S11. |
| Dexterous hand flange | `docs/pics/5 灵巧手法兰安装示意图.png` | Dexterous hand flange mounting details are available for S11. |

S0 result:

- No manual-image blocker remains for S2-S4.
- Dexterous hand images are available, but dexterous hand installation remains deferred to S11.
- Initial ROS `effector_type` remains `none`.
- Initial TCP offset remains zero until a tool is installed and measured.

## S1 Result

Confirmed:

- Table upright installation is planned.
- Original factory adapter will be used.
- Workspace is clear enough.
- Power cutoff path is clear.

Final on-site checks before any power-on or motion:

- Confirm base is physically fixed using the 70 mm x 70 mm M5-compatible pattern.
- Confirm factory adapter label and cable are intact.
- Confirm no person, laptop, tool, or fragile object is under the arm where it can drop if disabled.
- Confirm no cable will be pulled by J6/J7 motion.
- Confirm one person is assigned to power cutoff or emergency stop during first tests.

## S2 Offline Result

S2 offline environment result:

1. S2A host SDK/CAN-only:
   `docker`, `candump`, `cansend`, and `ethtool` are installed; project host venv
   `.venv/nero-sdk` imports `python-can=4.5.0` and `pyAgxArm`.
2. S2B Docker ROS2 Humble:
   Docker image `nero-humble:local` exists; container reports Ubuntu 22.04.5,
   `ROS_DISTRO=humble`, `ros2`, `colcon`, and `python-can=4.6.1`.
3. ROS workspace:
   `~/agx_arm_ws` contains `agx_arm_ros` commit `c73d33f`, `pyAgxArm` commit
   `a226840`, and `agx_arm_urdf` submodule commit `f6642ce`; `colcon build`
   completed with 5 packages.
4. Docker build may leave workspace build artifacts with container-mapped
   ownership. Use `bash scripts/fix_ros_ws_permissions.sh` after container builds
   if host-side file permissions are wrong.
5. Do not choose Noetic as the default route. The cloned current AgileX control
   package is ROS2; Noetic would require a separate legacy ROS1 validation and
   maintenance plan.

## Immediate Next Step

S10.1 Web first motion, S10.2 SDK motion, S10.3 ROS motion, and S10.4
no-motion control-source closure have passed for Arm A. S10.3 post-ROS snapshot
`20260625_064243` is clean, and live S10.4 audit `20260625_150438` is clean.
The git baseline commit `fb8a262` exists. The immediate next step is S10.5 Arm B
Web first-motion replication.

Next checks:

- Do not send more Arm A Web motion just to "try more"; preserve the successful
  state and avoid unnecessary accumulated risk.
- Record whether the final Arm A pose is intentionally acceptable or whether it
  should later be returned to a known home/park pose under a separate command.
- Keep the system in dual-arm read-only validation state unless deliberately
  starting the next controlled test.
- Do not expand to Cartesian, MoveIt, MIT/JS, dual-arm coordinated motion, or
  dexterous-hand actuation yet.
- Next recommended action: run S10.5 Arm B Web first motion using J1 `+2 deg`
  and return, then capture a dual-arm ROS read-only snapshot.
- Actual SDK speed was `10%`, not the planned `5%`; keep future first tests at
  or below `10%`, and prefer `5%` unless observability requires otherwise.
- Do not use SDK motion, ROS `/control/*`, raw CAN motion, MoveIt execute,
  Cartesian point/linear/circular motion, MIT mode, master-slave mode, or
  dexterous-hand actuation outside the documented S10.3 ROS procedure.
- Monitor the state-machine difference: Arm A `arm_status` is now `0` instead
  of the earlier `6`, while `err_status` and all flags remain healthy.
- S10.4 accepted handoff state is `handoff_to_arm_b`.
- Read `docs/s10_5_arm_b_first_motion_plan.md` before touching Arm B Web
  motion controls.

## S2 Discovery Result

Observed on 2026-06-24:

- OS: Ubuntu 20.04.6 LTS (`focal`).
- `/opt/ros` does not exist.
- Host-native `ros2` and `colcon` are intentionally absent; they are available
  inside the Docker ROS2 Humble container.
- Python in current shell: Miniconda Python 3.13.
- System Python: `/usr/bin/python3`, version 3.8.10.
- Host default Conda `python3` does not import `python-can` or `pyAgxArm`; the
  project venv `.venv/nero-sdk` does import them.
- `~/agx_arm_ws/src/agx_arm_ros` and `~/agx_arm_ws/src/pyAgxArm` exist and build
  in the container.
- Noetic evaluation: compatible with Ubuntu 20.04 as ROS1, but not recommended
  for the default NERO route because the current AgileX package path is ROS2
  Humble/Jazzy-oriented.
- `can-utils` is installed.
- `ethtool` is installed.
- `docker` is installed; current user was not added to the `docker` group.
- Ubuntu Focal apt candidate for `python3-can` is `3.3.2`, below the
  `pyAgxArm` requirement `python-can>=3.3.4`.

## Upstream Repository Evidence

Cloned and reviewed on 2026-06-24:

| Repository | Local path | Branch | Commit | Finding |
| --- | --- | --- | --- | --- |
| `agx_arm_ros` | `upstream/agx_arm_ros` | `ros2` | `c73d33f` | Current ROS control route is ROS2; README shows Humble/Jazzy and NERO support. |
| `pyAgxArm` | `upstream/pyAgxArm` | `master` | `a226840` | SDK supports Ubuntu 20.04 and Python 3.6+, usable standalone over SocketCAN. |
| `piper_ros` | `upstream/piper_ros` | `humble_beta1` | `2dc30fc` | Requested NERO path is a Humble/ament model description package. |
| `agx_arm_urdf` submodule | `upstream/agx_arm_ros/src/agx_arm_description/agx_arm_urdf` | submodule | `f6642ce` | Current NERO URDF/Xacro model set includes bare arm, gripper, and Revo2 variants. |

Detailed analysis: `docs/upstream_repo_analysis.md`.

S2 completion is now tracked at two levels:

- S2A host SDK/CAN-only is complete for offline preparation.
- S2B Docker ROS2 Humble is complete for offline preparation.
- CAN interface detection remains deferred to S6 because the real USB-CAN/robot
  is not connected in this session.

Hybrid plan details: `docs/s2_hybrid_host_container_plan.md`.

## S3 Discovery Result

Observed on 2026-06-24:

- Runtime model package: `agx_arm_description`.
- Runtime URDF source: `agx_arm_urdf` submodule commit `f6642ce`.
- Current bare-arm model: `nero/urdf/nero_description.urdf`.
- Current active setup remains `arm_type:=nero`, `effector_type:=none`.
- Bare-arm model passes `xacro`, `check_urdf`, mesh existence checks, and
  `robot_state_publisher` loading.
- Bare-arm model structure: robot `nero`, 9 links, 8 joints, chain
  `world -> base_link -> link1 -> ... -> link7`.
- Gripper and Revo2/dexterous-hand model variants also pass `xacro` and
  `check_urdf`, but they remain deferred to S11.
- RViz GUI verification succeeded from the real desktop terminal:
  `rviz2` started, OpenGL `4.5` was reported, and the model segments
  `base_link`, `link1` through `link7`, and `world` were loaded.
- The launch was stopped with Ctrl-C, and `joint_state_publisher`,
  `robot_state_publisher`, and `rviz2` all exited cleanly.
- Temporary X11 permission was revoked with `xhost -local:root`; final `xhost`
  output allowed only `SI:localuser:lv-robotics`.
- URDF `joint2` limit is `-99.69..99.69 deg`, while the manual records J2 as
  `-15..190 deg`. Treat this as a zero/mapping discrepancy to verify with real
  Web/CAN/SDK/ROS feedback before relying on ROS limits for safety.

Detailed analysis: `docs/s3_model_validation.md`.

## S4/S5 Initial Power-On And Web Evidence

Observed from `docs/pics/S4 上电与 S5 Web 只读验机.png` on 2026-06-24:

- Web page reachable at `http://192.168.31.1/#/welcome`.
- UI title: `松灵机器人`.
- Visible joint tabs: `关节1` through `关节7`.
- Footer shows version `v1.121` and model `7ax`.
- `关节1` page basic information:
  - bus voltage: `23.8 V`
  - bus current: `0.0 A`
  - driver temperature: `29.0 degC`
  - motor temperature: `22.0 degC`
- `关节1` status fields visible:
  - undervoltage: `否`
  - motor overtemperature: `否`
  - overcurrent: `否`
  - driver overtemperature: `否`
  - collision protection: `否`
  - driver error: `否`
  - driver disabled: `是`
  - stall protection: `否`

Interpretation:

- `7ax` and tabs `关节1` through `关节7` match one NERO 7-axis arm.
- `驱动失能: 是` is expected before deliberate enable; do not click `使能` yet.
- The site has a second physical arm, so it must be treated as a separate
  controller/IP/device.

## S5 Dual-Arm Network Evidence

Observed from `docs/pics/网络配置页面截图.png`, user report on 2026-06-24, and user
update on 2026-06-25:

- The site has two NERO arms with independent power.
- Arm A and Arm B both passed Web read-only checks.
- Arm A network configuration page is reachable at
  `http://192.168.31.1/#/settings/sys`.
- Earlier Arm A hotspot name visible in the screenshot: `agx-7ax-xin`.
- Arm A hotspot password visible in the screenshot: `12345678`.
- Arm A hotspot channel visible in the screenshot: `9`.
- Current Arm A hotspot: `agx-7ax-armA`.
- Current Arm B hotspot: `agx-7ax-armB`.
- The host can connect to only one arm Wi-Fi hotspot at a time with its built-in
  Wi-Fi adapter. This does not block dual-arm CAN/ROS control because the
  planned control path is two independent USB-CAN interfaces, not Wi-Fi.
- The network-port configuration form is visible, but no committed wired IP
  value is proven by the screenshot.

Current dual-arm decision:

- S5 is complete for both arms.
- Continue to S6 dual-arm CAN read-only.
- Do not use simultaneous ROS control until both arms have independent CAN,
  SDK, and ROS feedback paths.
- Detailed plan: `docs/s5_dual_arm_network_plan.md`.
  Next CAN/ROS plan: `docs/s6_dual_arm_can_ros_plan.md`.
