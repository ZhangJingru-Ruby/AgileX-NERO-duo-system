# S10.6 Arm B SDK Single-Joint Motion Plan

Status: accepted. SDK execution passed by operator observation and post-motion
read-only snapshot.

S10.5 Arm B Web first motion passed by operator confirmation and read-only
snapshot validation. S10.6 tests direct SDK control on Arm B, matching the
Arm A S10.2 path.

## Scope

Only one Arm B SDK joint-space step is allowed:

- Control source: SDK only.
- Arm: Arm B.
- CAN interface: `can_arm_b`.
- Joint: J1.
- Command: read current joints, command J1 to current angle plus `2 deg`, then
  return J1 to the original angle.
- Speed: `5%`.

Do not keep a ROS driver running during SDK execution. Do not use Web motion,
ROS `/control/*`, raw CAN, Cartesian motion, MoveIt execute, MIT/JS mode,
master-slave mode, dual-arm coordinated motion, zero calibration, firmware
update, or dexterous-hand commands during S10.6.

## Pre-Execute Gate

Before `--execute`, all items must be true:

- S10.5 Web motion is accepted.
- Arm B J1 swept area is clear.
- Arm A remains uncommanded.
- Web has no active motion command.
- Dual-arm ROS read-only driver is stopped.
- No ROS control driver is running.
- `can_arm_b` is UP, ERROR-ACTIVE, and bitrate `1000000`.
- One person is assigned to Web emergency stop or physical power cutoff.

## Dry-Run Command

```bash
.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
  --channel can_arm_b \
  --firmware v112 \
  --joint 1 \
  --delta-deg 2 \
  --speed-percent 5
```

Actual dry-run result on 2026-06-25:

- Firmware read succeeded: `{'software_version': '1.121'}`.
- Current Arm B joint angles in degrees:
  `[32.799, 80.10000000000001, -17.199, 20.799, -70.9, 21.398,
  9.200000000000001]`.
- Target Arm B joint angles in degrees:
  `[34.799, 80.10000000000001, -17.199, 20.799, -70.9, 21.398,
  9.200000000000001]`.
- Target differs from current only in J1 by `+2 deg`.
- `pre_status`: `ctrl_mode=CAN_CTRL(0x1)`, `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- No motion occurred.

Dry-run is accepted.

## Read-Only Evidence After Dry-Run

Snapshot: `docs/evidence/ros_snapshots/20260625_072742/`.

- Failed capture commands: `0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback topics.
- Arm A joint-state feedback: about `200 Hz`.
- Arm B joint-state feedback: about `200 Hz`.
- Arm A `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.

## Execute Command

Only after stopping the read-only driver:

```bash
.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
  --execute \
  --channel can_arm_b \
  --firmware v112 \
  --joint 1 \
  --delta-deg 2 \
  --speed-percent 5
```

Expected:

- J1 moves from about `32.799 deg` to about `34.799 deg`.
- J1 returns to about `32.799 deg`.
- Script prints `S10.2 SDK single-joint step completed.`
- Final status has no error flags.

Actual execution result on 2026-06-25:

- Operator report: real motion was observed successfully and execution was
  smooth.
- Full SDK execute terminal output was not pasted into the chat log, so exact
  `after_step_deg` and `after_return_deg` values are not recorded here.

## Post-Execute Snapshot

After execution, start dual-arm read-only validation and capture a new snapshot:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

```bash
NERO_CONTAINER_NAME=nero-humble-s10b-sdk-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Actual post-execute snapshot on 2026-06-25:

- Path: `docs/evidence/ros_snapshots/20260625_074048/`.
- Failed capture commands: `0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback topics.
- Arm A joint-state feedback: about `200 Hz`.
- Arm B joint-state feedback: about `200 Hz`.
- Arm A `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B sampled joint positions in radians:
  `[0.57246799465414, 1.3979563709698983, -0.30017917805050476,
  0.36302848441482055, -1.2374035330789397, 0.37355281980434635,
  0.16053538459843844]`.

Acceptance:

- S10.6 SDK execution is accepted.
- S10.7 Arm B ROS motion may start after stopping the read-only driver.
