# NERO Current Bring-Up Status

Last updated: 2026-06-30

## Confirmed Configuration

| Item | Current value |
| --- | --- |
| Current end effector | Dual LinkerHand L6 dexterous hands installed mechanically; Arm A right hand, Arm B left hand |
| Planned end effector state | S14.3L LinkerHand read-only identification pending; no finger actuation accepted yet |
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
| S10 首次低速运动 | Complete for both arms | Web, SDK, and ROS J1 motion passed on Arm A and Arm B. Final S10.8 audit `20260625_155538` shows both CAN interfaces UP/ERROR-ACTIVE at 1 Mbps, no NERO Docker container, and no NERO host process. |
| S11 双臂实验基线 | Complete / accepted | `lab_world` is defined with Arm A center as origin and `+X` from Arm A to Arm B. Accepted static TF values are `lab_world -> arm_a/world: x=0, y=0, z=0, roll=0, pitch=-1.5707963, yaw=0` and `lab_world -> arm_b/world: x=0.260, y=0, z=0, roll=3.1415926, pitch=-1.5707963, yaw=0`. Operator reports RViz matches the physical layout and follows both arms when they move. Post-TF snapshot `20260626_055339` is clean, and X11 access was restored to local-user only. |
| S12 控制隔离与日志闭环 | Complete / accepted | Arm A `joint1 +30 deg` and Arm B `joint1 -30 deg` isolation tests both passed and returned. Passive-arm deviations were `0.005 deg` for Arm B during Arm A motion and `0.008 deg` for Arm A during Arm B motion. Post-motion snapshots `20260626_080809` and `20260626_083210` are clean: failed captures `0`, A/B about `200 Hz`, A/B `err_status: 0`, no joint-limit flags, and no joint-communication flags. |
| S13 低风险双臂协同原语 | Complete / accepted | Corrected Arm A `joint1 +30 deg` / Arm B `joint1 +30 deg` execution passed and operator confirmed visible direction matched expectation. Earlier final-snapshot attempts `20260626_093414` and `20260629_043358` were not accepted because duplicate publishers produced about `400 Hz` feedback. After cleanup, publisher count was `1` for both A/B joint-state topics, and final snapshot `20260629_043441` is clean: failed captures `0`, A/B about `200 Hz`, A/B `err_status: 0`, no joint-limit flags, and no joint-communication flags. |
| S14 末端执行器 | Active; left-hand CAN identity confirmed, motion-risk review required | Both dexterous hands are mechanically installed and stable. Arm A = right hand, Arm B = left hand. S14.1 no-motion snapshot `20260629_074337` is accepted for communication/read-only health. Web screenshots show current end-effector config `强脑灵巧手`, hand page `普通灵巧手`, model `revo2`, mode `位置控制`, and enable without error, but Web single-finger send produced no hand motion. New Drive docs reviewed in `docs/s14_linker_drive_review.md` confirm LinkerHand L6 and introduce a Linker/LBOT controller stack at `192.168.10.21`; the live network probe did not reach that IP. Photos under `docs/pics/灵巧手连接设备/` show a bench DC supply plus USB-CAN debug hardware, not an IP controller. The left hand is disconnected from arm/J6 and powered independently; `灵巧手左手上电操控示意图.jpeg` shows about `24.00 V` and `0.122 A`. Live host checks found PEAK-System `XCAN-USB` on SocketCAN `can1`, USB path `1-3.4.4:1.0`; `can1` is UP/ERROR-ACTIVE at `1000000`. The original probe confirmed left serial `LHL6-03-253-L-B-1-C`, plausible temperatures `[33,35,35,35,35,35]`, and all-zero faults, but the operator observed physical hand opening during the probe. Therefore `0x01` is no longer accepted as safe read-only. Next gate: do not rerun the old probe or any GUI/demo; observe stability, optionally run passive `timeout 5s candump -tz can1`, then use only the revised identity/health probe before replanning first micro motion. |

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
| Dexterous hand size | `docs/pics/4 灵巧手示意图.png` | Hand clearance and flange dimensions are available for S14. |
| Dexterous hand flange | `docs/pics/5 灵巧手法兰安装示意图.png` | Dexterous hand flange mounting details are available for S14. |

S0 result:

- No manual-image blocker remains for S2-S4.
- Dexterous hand images are available and were used as S14 installation
  references.
- Global arm-only ROS default `effector_type` remains `none`; S14 hand read-only
  uses a dedicated `revo2` launch script.
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

S13 is complete. S14 is active. S14.0 mechanical/cable review, S14.1
no-motion arm read-only verification, and S14.2 model/parameter decision are
recorded. The local LinkerHand SDK review is in
`docs/s14_linkerhand_sdk_review.md`, and the newer Drive document review is in
`docs/s14_linker_drive_review.md`. The current installation routes the hand
through the NERO J6 end-effector port, so direct LinkerHand PCAN assumptions do
not apply unless the hand is moved back to a bench-test adapter. The immediate
next step is to close S14.3K with the current evidence: `192.168.10.21` is not
reachable from the current network, and the photographed equipment is a bench DC
supply plus USB-CAN kit, not an IP controller. Do not actuate the hand until S14
records:

- which arm J6 hand cable is connected to;
- Web `6.8.5 末端执行器配置` evidence showing `强脑灵巧手`;
- vendor guidance on whether NERO J6 supports LinkerHand L6 directly, and which
  Web/firmware option should be selected;
- if direct bench-test is selected, a separate wiring checklist for one-hand
  power/CAN identity/status read-only checks;
- passive arm-CAN evidence around a small Web hand send, especially Revo2
  `0x1B*` command and `0x1C*` feedback frames;
- Web log evidence around the same send;
- no hand error, over-current, over-temperature, or blocked motor status if the
  Web/controller exposes those fields;
- A temporary J6/J7 wrist envelope that respects the observed cable limit.
- How to handle the current A/B `arm_status=3` singularity observation before
  any arm, wrist, or Cartesian motion.

Until S14 has its own gates accepted, do not run Cartesian, MoveIt execute,
contact, handoff, dexterous-hand actuation, or close-proximity manipulation.

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
- S3 arm-only model setup remains `arm_type:=nero`, `effector_type:=none` for
  regression checks.
- Bare-arm model passes `xacro`, `check_urdf`, mesh existence checks, and
  `robot_state_publisher` loading.
- Bare-arm model structure: robot `nero`, 9 links, 8 joints, chain
  `world -> base_link -> link1 -> ... -> link7`.
- Gripper and Revo2/dexterous-hand model variants also pass `xacro` and
  `check_urdf`; Revo2 is now active only in S14-specific read-only checks.
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
