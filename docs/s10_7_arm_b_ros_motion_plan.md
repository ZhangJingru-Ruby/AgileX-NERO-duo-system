# S10.7 Arm B ROS Single-Joint Motion Plan

Status: prepared, not executed.

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

S10.7 passes only if ROS execution succeeds and the post-execute snapshot is
clean for both arms.
