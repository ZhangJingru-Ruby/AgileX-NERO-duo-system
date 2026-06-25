# S9 Configuration Review

Date started: 2026-06-25

Phase: S9 标定与参数配置

## Goal

Turn the live dual-arm setup into reproducible configuration records before any
motion command is attempted.

S9 is not a motion phase. It records and reviews installation posture,
coordinate frames, zero/TCP/tool settings, payload, limits, speeds, collision
protection, and dual-arm base-frame assumptions.

## Safety Boundary

- Do not click `使能`.
- Do not publish to `/arm_a/control/*` or `/arm_b/control/*`.
- Do not run MoveIt execute.
- Do not use SDK motion APIs.
- Do not perform zero calibration during S9.1.
- Treat zero calibration as a separate high-risk action because the manual says
  automatic zero setting moves the motor to the mechanical limit and then back,
  and J6 may move during calibration.

## Source Documents

- User manual section `6.7 设置零点`.
- User manual section `6.8.1 关节限制设置`.
- User manual section `6.8.2 末端速度设置`.
- User manual section `6.8.3 碰撞保护设置`.
- User manual section `6.8.4 安装位置设置`.
- User manual section `6.8.5 末端执行器配置`.
- Runtime ROS evidence from S8.

## Current Known Configuration

| Item | Current value |
| --- | --- |
| Physical arms | Arm A and Arm B, independent power |
| Arm A CAN | `can_arm_a`, USB bus `1-5:1.0`, vertical USB port |
| Arm B CAN | `can_arm_b`, USB bus `1-11:1.0`, horizontal USB port |
| Arm A ROS namespace | `arm_a` |
| Arm B ROS namespace | `arm_b` |
| Current end effector | Bare arm |
| Planned end effector | Dexterous hand, deferred |
| ROS `effector_type` | `none` |
| ROS TCP offset | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| Physical installation | Table upright |
| S8 ROS feedback | Arm A and Arm B joint states about `200 Hz`, `err_status: 0` |
| RViz follow | Accepted after the dual ROS read-only driver terminal is running |

## S9.1 Read-Only Inventory

S9.1 only captures configuration. Do not change settings yet.

For each arm, connect to its Web UI and capture:

| Area | Arm A evidence | Arm B evidence | Required decision |
| --- | --- | --- | --- |
| 安装位置设置 | `docs/pics/S9.1/A02.png`, `A04.png`: `1-水平正装` | `docs/pics/S9.1/B02.png`, `B03.png`: `1-水平正装` | Confirm table-upright corresponds to Web option `1-水平正装`. |
| 末端执行器配置 | `A04.png`: `默认（无加载）`, current config | `B02.png`: `默认（无加载）`, current config | Bare arm now; dexterous hand later. |
| 负载/工具配置 | `A04.png`: load mode `满载`; tool mass `0.00000 kg` | `B02.png`: load mode `满载`; tool mass `0.00000 kg` | Decide whether to keep full-load mode as conservative before S10. |
| 关节限制设置 | `A03.png`: values recorded below | `B01.png`: values recorded below | Must not exceed manual joint ranges. |
| 末端速度设置 | `A03.png`: values recorded below | `B01.png`: values recorded below | Use conservative values before first motion. |
| 碰撞保护设置 | `A04.png`: J1 level `1` shown; operator confirms J1-J7 all level `1` | `B02.png`: J1 level `1` shown; operator confirms J1-J7 all level `1` | Recorded by screenshot plus operator field confirmation. |
| 零点页面 | `A01.png`: zero-setting dialog shown, joint sequence `1` | Operator confirms B zero-setting page also shows joint sequence `1` | Read-only only; zero calibration was not performed. |
| 网络/热点 | Arm A SSID `agx-7ax-armA` | Arm B SSID `agx-7ax-armB` | Already unique; record screenshots if convenient. |

## S9.1 Evidence Readout On 2026-06-25

Operator screenshots are stored in `docs/pics/S9.1/`. The file names are not the
recommended names, but the `A*` and `B*` prefixes are treated as operator labels
for Arm A and Arm B.

Arm A Web readout:

- Status/control page: `docs/pics/S9.1/A02.png`.
- Zero-setting dialog: `docs/pics/S9.1/A01.png`.
- Joint limit / end-speed page: `docs/pics/S9.1/A03.png`.
- Collision / load / installation / end-effector page:
  `docs/pics/S9.1/A04.png`.
- Control mode: `CAN`.
- Installation position: `1-水平正装`.
- End effector: `默认（无加载）`.
- Load mode: `满载`.
- Tool mass: `0.00000 kg`.
- Visible tool center: `x=-0.00014 m`, `y=-0.00010 m`, `z=-0.00275 m`.
- Collision protection evidence: J1 level `1` in screenshot; operator confirms
  J1-J7 are all level `1`.

Arm B Web readout:

- Joint limit / end-speed page: `docs/pics/S9.1/B01.png`.
- Collision / load / installation / end-effector page:
  `docs/pics/S9.1/B02.png`.
- Status/control page: `docs/pics/S9.1/B03.png`.
- Control mode: `CAN`.
- Installation position: `1-水平正装`.
- End effector: `默认（无加载）`.
- Load mode: `满载`.
- Tool mass: `0.00000 kg`.
- Visible tool center: `x=-0.00014 m`, `y=-0.00010 m`, `z=-0.00275 m`.
- Collision protection evidence: J1 level `1` in screenshot; operator confirms
  J1-J7 are all level `1`.
- Zero-setting page screenshot was not added, but operator confirms B zero
  joint sequence is also `1`.

Joint limits and speeds shown for both arms:

| Joint | Min deg | Max deg | Max speed deg/s | Accel rad/s^2 | Decel rad/s^2 | Manual range check |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| J1 | `-155.0` | `155.0` | `179.9` | `2.0` | `2.0` | Within `-157..157`; speed within `180`. |
| J2 | `-100.0` | `100.0` | `179.9` | `2.0` | `2.0` | Conflicts with manual `-15..190`; likely Web/URDF zero convention difference, must resolve before expanding motion. |
| J3 | `-158.0` | `158.0` | `179.9` | `2.5` | `2.5` | Within `-160..160`; speed within `180`. |
| J4 | `-58.0` | `123.0` | `179.9` | `2.5` | `2.5` | Within `-60..125`; speed below `225`. |
| J5 | `-158.0` | `158.0` | `224.6` | `2.5` | `2.5` | Within `-160..160`; speed below `225`. |
| J6 | `-42.0` | `55.0` | `224.6` | `2.5` | `2.5` | Within `-43..58`; speed below `225`. |
| J7 | `-90.0` | `90.0` | `224.6` | `2.5` | `2.5` | Within `-90..90`; speed below `225`. |

End-speed settings shown for both arms:

| Field | Value |
| --- | ---: |
| Linear velocity | `1000.0 mm/s` |
| Angular velocity | `34.4 deg/s` |
| Linear acceleration | `1500.0 mm/s^2` |
| Angular acceleration | `286.5 deg/s^2` |

S9.1 supplemental operator confirmation on 2026-06-25:

- Arm B zero-setting page also shows joint sequence `1`.
- Arm A and Arm B collision protection levels are all `1` for J1-J7.
- No zero calibration was performed.
- No collision setting was changed.

S9.1 ROS snapshot:

- Complete snapshot path: `docs/s9_ros_snapshots/20260625_044256/`.
- Topic list includes both `/arm_a/...` and `/arm_b/...` feedback topics.
- Arm A and Arm B `joint_states` names are `joint1` through `joint7`.
- Arm A joint-state frequency sample: about `199.98-200.00 Hz`.
- Arm B joint-state frequency sample: about `200.00-200.02 Hz`.
- Arm A and Arm B `arm_status` both show `err_status: 0`, no joint angle
  limits, and no joint communication errors.
- The `ros2 topic hz` files contain a shutdown message after timeout, but the
  frequency samples were recorded. The helper script was updated to use SIGINT
  for cleaner future timeout shutdown.

S9.1 result:

- Read-only inventory is accepted.
- S9 is not complete yet. S9.2 must resolve deployment decisions before S10.

Recommended screenshot names:

- `docs/pics/s9_arm_a_install_pose.png`
- `docs/pics/s9_arm_a_end_effector.png`
- `docs/pics/s9_arm_a_joint_limits.png`
- `docs/pics/s9_arm_a_tcp_speed.png`
- `docs/pics/s9_arm_a_collision.png`
- `docs/pics/s9_arm_a_zero_page.png`
- `docs/pics/s9_arm_b_install_pose.png`
- `docs/pics/s9_arm_b_end_effector.png`
- `docs/pics/s9_arm_b_joint_limits.png`
- `docs/pics/s9_arm_b_tcp_speed.png`
- `docs/pics/s9_arm_b_collision.png`
- `docs/pics/s9_arm_b_zero_page.png`

## ROS Snapshot

With the dual ROS read-only driver terminal already running, collect a snapshot:

```bash
NERO_CONTAINER_NAME=nero-humble-s9-snapshot \
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

This script records only read-only ROS topic data. It does not publish control
messages.

## S9.1 Acceptance

- Both arms have Web screenshots for installation posture, end-effector/tool,
  joint limits, end speed, collision protection, and zero page.
- A ROS read-only snapshot exists under `docs/s9_ros_snapshots/`.
- Any mismatch between Web installation posture and RViz/world orientation is
  recorded as a coordinate-frame issue, not silently ignored.
- No settings have been changed unless separately documented.
- No motion command has been sent.

## S9.2 Decisions To Make After Inventory

- Which Web installation-position option exactly represents the current table
  upright mounting. Current observed option on both arms is `1-水平正装`.
- Whether the horizontal RViz/world appearance requires an application-level
  static transform, a Web installation-pose correction, or only a documented
  base-frame convention.
- Whether any joint limits or speed values must be reduced before S10.
- Whether `满载` should be kept as the first-motion load mode despite the current
  bare-arm/no-tool state, or changed to a more accurate empty-load mode.
- Whether zero calibration is needed at all. If needed, it must get a dedicated
  procedure and operator confirmation before execution.
- How the future dexterous hand changes TCP, mass, center of gravity, collision
  envelope, and first-actuation procedure.

## S9.2 Decisions On 2026-06-25

Priority order for these decisions:

1. Avoid unexpected motion, incorrect compensation, and accidental limit
   expansion.
2. Preserve observed good Web/CAN/SDK/ROS feedback.
3. Make the smallest reversible configuration changes needed before S10.
4. Keep all facts traceable to manual text, Web screenshots, ROS snapshots, or
   upstream source code.

### Decision 1: Load Mode

Decision:
Change both arms from observed Web load mode `满载` to the Web option that
corresponds to empty/no-load operation, normally `空载`, before S10 first motion.

Do not change the end-effector selection yet. Keep `默认（无加载）`, tool mass
`0.00000 kg`, and ROS `effector_type:=none`.

Basis:

- Current physical end effector is bare arm.
- Web end-effector configuration is `默认（无加载）`.
- Visible tool mass is `0.00000 kg`.
- The route and manual-derived S9 rule require load setting to match the actual
  end effector.
- Manual section `6.8.5` says end-effector physical properties are used for
  motion control and torque compensation.

Benefits:

- Compensation model better matches the real current hardware.
- Avoids carrying a hidden "full payload" assumption into first motion.
- Creates a clean baseline before the future dexterous hand installation changes
  mass, center of gravity, TCP, and collision envelope.

Potential danger:

- Any Web write is a controller configuration change. A wrong option could
  change gravity compensation or protection behavior.
- Mitigation: change only while disabled/no motion; change Arm A and Arm B the
  same way; screenshot before/after; rerun ROS read-only snapshot; do not change
  zero, limits, or collision level in the same step.

### Decision 2: J2 Angle Limits

Decision:
Do not edit or expand J2 Web limits before S10. Keep the current Web limit
`-100..100 deg` for both arms.

Treat the manual J2 range `-15..190 deg` as a different mechanical/spec angle
convention relative to the Web/URDF/runtime joint convention. The current
working inference is:

`manual_J2_angle ≈ web_or_urdf_J2_angle + 90 deg`

This inference explains why Web/URDF `-100..100 deg` approximately corresponds
to manual `-10..190 deg`, close to the manual `-15..190 deg` range while staying
slightly conservative on one side.

Basis:

- Web current J2 limit is `-100..100 deg`.
- Runtime ROS `joint_states` are accepted by the current model and RViz follows.
- URDF J2 limit observed in S3 is about `-99.69..99.69 deg`, matching the Web
  convention.
- Current S8/S9 status shows no joint angle-limit error.
- User confirms Web limits are editable, so accidental manual-range entry would
  be possible; this increases the need to avoid unsupported edits.

Benefits:

- Avoids expanding the active controller limit based on a likely different zero
  convention.
- Keeps Web, URDF, ROS, and RViz consistent for first motion.
- Preserves the safety behavior already verified by ROS read-only feedback.

Potential danger:

- If the convention inference is incomplete, some legitimate mechanical J2
  range may remain inaccessible.
- If someone enters manual `-15..190` directly into the Web field, the robot may
  interpret it in the Web/URDF convention and allow unintended physical range.
- Mitigation: first S10 motion uses only small joint-space deltas inside the
  current Web limits. Do not use J2 limit expansion as a prerequisite for first
  motion.

### Decision 3: Coordinate Frame / RViz Orientation

Decision:
Keep Web installation position as `1-水平正装` on both arms. Do not change Web
installation position, URDF base orientation, or ROS driver frames to make RViz
look like the physical hanging posture.

For S10, treat `arm_a/base_link` and `arm_b/base_link` as robot-local controller
frames. The lab/table/world frame is not calibrated yet. Add explicit static
transforms later from a measured `lab_world` frame to each arm base:

- `lab_world -> arm_a/base_link`
- `lab_world -> arm_b/base_link`

Basis:

- Web status and settings both report `1-水平正装`.
- Upstream `pyAgxArm` NERO CAN mode control defines installation position
  `0x01` as `Horizontal upright`, matching the observed Web option.
- Manual section `6.8.4` says installation position affects coordinate
  calibration and spatial calculation.
- Upstream ROS launch does not expose an installation-pose parameter; it exposes
  namespace, end-effector type, and TCP offset. RViz is currently showing the
  URDF/controller-local frame, not a measured lab frame.
- RViz follow has already been accepted once the read-only driver is running.

Benefits:

- Avoids changing a controller-level installation parameter that already matches
  the observed Web state.
- Keeps ROS/RViz model consistency intact.
- Leaves the correct problem in the correct layer: dual-arm coordination needs a
  measured external base-frame calibration, not a cosmetic URDF rotation.

Potential danger:

- Any Cartesian command interpreted as a lab/world command before external base
  calibration may be wrong.
- Dual-arm coordination without measured `lab_world -> base_link` transforms can
  create collision or reachability errors.
- Mitigation: S10 starts with joint-space, very small, single-arm movement only.
  Do not use MoveIt execute, Cartesian point/linear/circular commands, or
  dual-arm coordinated motion until external transforms are measured and
  validated.

## S9.3 Required Action Before S10

Perform one controlled Web configuration write:

1. With both arms disabled and no motion command active, change Arm A load mode
   from `满载` to the empty/no-load option.
2. Change Arm B the same way.
3. Do not change installation position, joint limits, speed, collision level,
   end-effector config, TCP, or zero.
4. Capture after-change screenshots.
5. Rerun ROS read-only snapshot.

If the Web UI labels differ from `空载/半载/满载`, stop and record the available
options before choosing.

## S9.3 Execution Procedure

Scope:

- Only change load mode.
- Do not click `使能`.
- Do not change installation position, joint limits, speed/acceleration,
  collision level, end-effector config, TCP/tool values, or zero-setting.
- Do not publish ROS `/control/*` commands.

Pre-check:

1. Confirm both arms are mechanically stable and workspace remains clear.
2. Confirm Web status has no visible active motion.
3. If ROS is running, it must be read-only:
   `auto_enable:=false control_enabled:=false`.
4. Keep power cutoff reachable.

Web action for Arm A:

1. Connect to Arm A Web UI.
2. Open system settings / load settings.
3. Record available load-mode options if they are not exactly
   `空载`, `半载`, `满载`.
4. Select the empty/no-load option, expected label `空载`.
5. Submit/apply only the load-mode setting.
6. Capture after-change screenshot, suggested path:
   `docs/pics/S9.3/arm_a_load_mode_after.png`.

Web action for Arm B:

1. Connect to Arm B Web UI.
2. Repeat the same load-mode-only change.
3. Capture after-change screenshot, suggested path:
   `docs/pics/S9.3/arm_b_load_mode_after.png`.

ROS revalidation:

With the dual ROS read-only driver running, run:

```bash
NERO_CONTAINER_NAME=nero-humble-s9-loadmode-snapshot \
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Acceptance:

- Both Web screenshots show empty/no-load load mode.
- No other Web configuration changed.
- ROS snapshot contains both Arm A and Arm B data.
- Arm A and Arm B `arm_status.err_status` remain `0`.
- Arm A and Arm B joint angle limit arrays remain all `false`.
- Arm A and Arm B communication status arrays remain all `false`.
- Joint-state feedback remains close to `200 Hz`.

Stop / rollback conditions:

- If the Web UI does not show an obvious empty/no-load option, stop and record
  the available options.
- If submitting the load mode triggers movement, abnormal sound, error status,
  or unexpected Web warning, stop and power down if needed.
- If ROS revalidation shows nonzero `err_status`, any joint limit, or any joint
  communication error, do not proceed to S10.

## S9.3 Troubleshooting Notes

Web request failure while changing load mode:

- If Web configuration submit fails while the arm is in `CAN` control mode,
  switch to `WEB` mode first, but do not click `使能`.
- Before switching mode, stop ROS/CAN drivers so there is only one control source
  active.
- After the Web change, the top `CAN` button may refer to external CAN push. If
  its tooltip says `关闭外网CAN推送`, CAN push is already on; do not repeatedly
  click it during recovery.

ROS revalidation failure `CAN interface can_arm_a is not visible`:

- This is a host SocketCAN visibility/naming problem, not a Web load-mode
  setting by itself.
- First check host interfaces from a real desktop terminal:

```bash
ip -details link show can_arm_a
ip -details link show can_arm_b
bash scripts/find_can_ports.sh
```

- If `can_arm_a`/`can_arm_b` are missing but USB-CAN modules are detected, reactivate
  deterministic names:

```bash
bash scripts/activate_can.sh can_arm_a 1000000 "1-5:1.0"
bash scripts/activate_can.sh can_arm_b 1000000 "1-11:1.0"
```

- Then launch read-only ROS with either one-line command:

```bash
bash scripts/run_humble_container.sh bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

  or line continuation:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

- Do not type the shell continuation prompt character `>` as part of the
  command. A literal `>` redirects output and may create a local file named
  `bash`.

ROS revalidation failure `Failed to get firmware version` on Arm A:

- This means the ROS driver can see `can_arm_a`, but Arm A did not return the
  firmware response within the node timeout.
- Arm B succeeding in the same launch proves the container and ROS workspace are
  not the general failure point.
- Check in order:

```bash
ip -details link show can_arm_a
bash scripts/find_can_ports.sh
timeout 5s candump -tz can_arm_a
```

- If Arm A passive CAN frames are absent, inspect Arm A Web CAN/external CAN
  push state, physical CAN wiring, power, and USB-CAN bus mapping.
- If passive frames exist, run SDK read-only on Arm A:

```bash
python examples/nero_read_state.py --connect --channel can_arm_a --firmware v112 --duration 3
```

- Retry dual ROS only after Arm A SDK read-only can retrieve state or firmware.

Arm A has no passive frames but Arm B is normal:

- This points below ROS and SDK to Arm A CAN communication/push state, physical
  wiring, power, or USB-CAN mapping.
- Because the Web top `can通讯` button toggles CAN communication on/off, a Web
  configuration sequence can leave one arm's external CAN communication off even
  though the other arm remains normal.
- Recovery order:
  1. Refresh/relogin Arm A Web UI.
  2. Check whether the `CAN` top button means enable or disable based on its
     tooltip/current state.
  3. Enable CAN communication only if it is currently off.
  4. Verify with `timeout 5s candump -tz can_arm_a`.
  5. If still no frames, power-cycle or Web-reboot only Arm A after recording
     the current state.
- SDK commands must be run from the host SDK venv:

```bash
source .venv/nero-sdk/bin/activate
python examples/nero_read_state.py --connect --channel can_arm_a --firmware v112 --duration 3
```

Observed recovery:

- Operator report on 2026-06-25: Arm A CAN recovered after unplugging and
  replugging the USB-CAN adapter, then setting/activating the interface again.
- After recovery, the dual ROS read-only launch command can run successfully:

```bash
bash scripts/run_humble_container.sh bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

- Treat USB-CAN replug + deterministic interface activation as the recovery path
  if a mapped interface exists but produces no passive frames after Web mode
  changes.

## S9.3 Result On 2026-06-25

Operator confirmation:

- Both arms' load settings were changed successfully from `满载` to the current
  bare-arm empty/no-load option.
- No after-change load-mode screenshots were found under `docs/pics/` at review
  time; this acceptance is based on operator field confirmation plus ROS
  revalidation.

Recovery note:

- Arm A produced no passive CAN frames after the Web configuration step.
- Reboot alone did not recover it.
- Replugging the Arm A USB-CAN adapter and reactivating the interface recovered
  Arm A CAN communication.

Final ROS revalidation:

- Snapshot path: `docs/s9_ros_snapshots/20260625_054435/`.
- `README.md` reports `Failed capture commands: 0`.
- Topic list includes both Arm A and Arm B feedback topics.
- Arm A and Arm B `joint_states` names are `joint1` through `joint7`.
- Arm A joint-state sample is about `199.9 Hz`.
- Arm B joint-state sample is about `199.7-199.9 Hz`.
- Arm A and Arm B `arm_status.err_status` are both `0`.
- Arm A and Arm B joint angle limit arrays are all `false`.
- Arm A and Arm B joint communication status arrays are all `false`.

S9 result:

- S9 is accepted.
- Do not treat this as permission for Cartesian, MoveIt, or dual-arm coordinated
  motion. S10 must begin with a separate first-motion checklist and very small
  single-arm joint-space movement.
