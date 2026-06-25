# S10.7 Arm B ROS Single-Joint Motion Plan

Status: accepted. ROS execution passed and post-motion read-only snapshot is
clean.

S10.5 Arm B Web motion and S10.6 Arm B SDK motion have passed. S10.7 tests the
ROS control layer on Arm B, matching the Arm A S10.3 path.

## Scope

Only one Arm B ROS `move_j` step is allowed:

- Control source: ROS only.
- Arm: Arm B.
- CAN interface: `can_arm_b`.
- ROS namespace: `/arm_b`.
- Joint: `joint1`.
- Command: read `/arm_b/feedback/joint_states`, publish `/arm_b/control/move_j`
  with `joint1 +2 deg`, then return to the original joint angle.
- Driver speed: `5%`.

Do not use `/control/move_p`, `/control/move_l`, `/control/move_c`,
`/control/move_js`, `/control/move_mit`, MoveIt execute, raw CAN, Cartesian
motion, dual-arm coordinated motion, master-slave mode, zero calibration,
firmware update, or dexterous-hand commands.

## Pre-Motion Gate

All items must be true before `--execute`:

- S10.6 post-SDK snapshot is accepted.
- Arm B J1 swept area remains clear.
- Arm A remains uncommanded.
- No Web or SDK command is active.
- The dual-arm read-only driver is stopped before starting the Arm B ROS
  control driver.
- The ROS driver is launched only for Arm B control, not dual-arm control.
- One person is assigned to Web emergency stop or physical power cutoff.

## Terminal 1: Start Arm B ROS Control Driver

Stop any existing read-only driver first. Then:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-arm-b \
bash scripts/run_humble_container.sh \
  ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
    namespace:=arm_b \
    can_port:=can_arm_b \
    arm_type:=nero \
    effector_type:=none \
    auto_enable:=true \
    control_enabled:=true \
    speed_percent:=5 \
    tcp_offset:='[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]'
```

Wait until the log shows feedback is ready and the arm is enabled. If enable
fails or firmware cannot be read, stop and return to S8/S10.6 diagnosis.

## Terminal 2: Dry Run

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-tool \
bash scripts/run_humble_container.sh \
  python3 /workspace/nero/scripts/ros_single_joint_step.py \
    --namespace arm_b \
    --joint joint1 \
    --delta-deg 2
```

Expected:

- Current 7 joint angles are printed.
- Target 7 joint angles are printed.
- Target differs from current only in `joint1` by `+2 deg`.
- `pre_status` is printed.
- No motion occurs.

Actual dry-run result on 2026-06-25:

- Namespace: `arm_b`.
- Feedback topic: `/arm_b/feedback/joint_states`.
- Command topic: `/arm_b/control/move_j`.
- Current degrees:
  `[32.798, 80.098, -17.204, 20.797, -70.9, 21.403, 9.198]`.
- Target degrees:
  `[34.798, 80.098, -17.204, 20.797, -70.9, 21.403, 9.198]`.
- Target differs from current only in `joint1` by `+2 deg`.
- `pre_status`: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`.
- No motion occurred.
- Dry-run is accepted.

## Terminal 2: Execute

Only after the dry-run target is correct:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-tool \
bash scripts/run_humble_container.sh \
  python3 /workspace/nero/scripts/ros_single_joint_step.py \
    --execute \
    --namespace arm_b \
    --joint joint1 \
    --delta-deg 2
```

Expected:

- Arm B `joint1` moves by about `+2 deg`.
- Arm B `joint1` returns to the original angle within script tolerance.
- Script prints `S10.3 ROS single-joint step completed.`
- Final status has no error flags.

Actual execution result on 2026-06-25:

- Namespace: `arm_b`.
- Feedback topic: `/arm_b/feedback/joint_states`.
- Command topic: `/arm_b/control/move_j`.
- Current degrees:
  `[32.798, 80.098, -17.204, 20.798000000000002, -70.9, 21.402, 9.198]`.
- Target degrees:
  `[34.798, 80.098, -17.204, 20.798000000000002, -70.9, 21.402, 9.198]`.
- `pre_status`: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`.
- `after_step_deg`:
  `[34.553, 80.09700000000001, -17.209, 20.791, -70.9, 21.402, 9.198]`.
- `after_return_deg`:
  `[33.026, 80.096, -17.207, 20.797, -70.9, 21.402, 9.198]`.
- `final_status`: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`.
- Script printed `S10.3 ROS single-joint step completed.`

## Post-Execute Snapshot

After execution, stop the Arm B ROS control driver, start dual-arm read-only
validation, and capture a new snapshot:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

```bash
NERO_CONTAINER_NAME=nero-humble-s10b-ros-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Actual post-execute snapshot on 2026-06-25:

- Path: `docs/s9_ros_snapshots/20260625_074953/`.
- Failed capture commands: `0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback topics.
- Arm A joint-state feedback: about `200 Hz`.
- Arm B joint-state feedback: about `200 Hz`.
- Arm A `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B sampled joint positions in radians:
  `[0.5724156347765803, 1.3979563709698983, -0.30026644451310447,
  0.3629935778297807, -1.2374733462490195, 0.37351791321930644,
  0.1604830247208786]`.
- Arm B sampled J1 is about `32.797 deg`, consistent with return to the
  original angle after settling.

Acceptance:

- S10.7 ROS execution is accepted.
- Arm B has now passed Web, SDK, and ROS low-speed single-joint motion with
  post-motion read-only validation.
