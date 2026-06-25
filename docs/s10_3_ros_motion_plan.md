# S10.3 ROS Single-Joint Motion Plan

Status: accepted. ROS `joint1 +2 deg` execution passed, and post-motion
dual-arm ROS read-only snapshot passed.

S10.1 Web motion and S10.2 SDK motion passed. S10.3 tests the ROS control layer
that wraps the SDK driver.

## Scope

Only one ROS `move_j` step is allowed in this procedure:

- Control source: ROS only.
- Arm: Arm A.
- CAN interface: `can_arm_a`.
- ROS namespace: `/arm_a`.
- Joint: `joint1`.
- Command: read `/arm_a/feedback/joint_states`, publish `/arm_a/control/move_j`
  with `joint1 + 2 deg`, then return to the original joint angle.
- Driver speed: `5%` preferred; `10%` maximum for this first ROS test.

Do not use `/control/move_p`, `/control/move_l`, `/control/move_c`,
`/control/move_js`, `/control/move_mit`, MoveIt execute, raw CAN, Cartesian
motion, dual-arm motion, master-slave mode, or dexterous-hand commands.

## Evidence For ROS Interface

Local ROS driver evidence:

- `agx_arm_ctrl_single_node.py` subscribes to `control/move_j` as
  `sensor_msgs/msg/JointState`.
- The callback constructs a 7-joint array and calls SDK `move_j()`.
- Control is accepted only if feedback is ready, the arm is enabled, and
  `control_enabled` is true.
- `start_single_agx_arm.launch.py` exposes `auto_enable`, `control_enabled`,
  `speed_percent`, `can_port`, `namespace`, `arm_type`, and `effector_type`.

## Script

Use:

```bash
scripts/ros_single_joint_step.py
```

The script defaults to dry-run. It subscribes to current joint feedback and
prints the target without publishing unless `--execute` is provided.

Safety behavior:

- Refuses delta above `2 deg` by default.
- Reads the live 7-joint feedback vector and modifies only one joint.
- Publishes to `/arm_a/control/move_j` only with `--execute`.
- Publishes a return command to the original joint angle by default.
- On Ctrl-C during execution, calls the ROS `emergency_stop` service unless
  `--no-estop-on-ctrl-c` is given.

## Pre-Motion Gate

All items must be true before `--execute`:

- S10.2 post-SDK ROS read-only snapshot is accepted.
- Arm A workspace and J1 swept area remain clear.
- Arm A base is fixed.
- Arm B remains uncommanded.
- No Web or SDK command is active.
- The ROS driver is launched only for Arm A control, not dual-arm control.
- One person is assigned to Web emergency stop or physical power cutoff.

## Terminal 1: Start Arm A ROS Control Driver

Stop any existing read-only driver first. Then:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-arm-a \
bash scripts/run_humble_container.sh \
  ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
    namespace:=arm_a \
    can_port:=can_arm_a \
    arm_type:=nero \
    effector_type:=none \
    auto_enable:=true \
    control_enabled:=true \
    speed_percent:=5 \
    tcp_offset:='[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]'
```

Wait until the log shows feedback is ready and the arm is enabled. If enable
fails or firmware cannot be read, stop and return to S8/S10.2 diagnosis.

## Terminal 2: Dry Run

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-tool \
bash scripts/run_humble_container.sh \
  python3 /workspace/nero/scripts/ros_single_joint_step.py \
    --namespace arm_a \
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

- Namespace: `arm_a`.
- Feedback topic: `/arm_a/feedback/joint_states`.
- Command topic: `/arm_a/control/move_j`.
- Current degrees:
  `[55.498000000000005, 70.797, -29.62, 41.599000000000004, 21.6, -39.998, -35.505]`.
- Target degrees:
  `[57.498000000000005, 70.797, -29.62, 41.599000000000004, 21.6, -39.998, -35.505]`.
- `pre_status`: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`.
- No motion occurred.
- Dry-run accepted: target differs only in `joint1` by `+2 deg`.

## Terminal 2: Execute

Only after the dry-run target is correct:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-tool \
bash scripts/run_humble_container.sh \
  python3 /workspace/nero/scripts/ros_single_joint_step.py \
    --execute \
    --namespace arm_a \
    --joint joint1 \
    --delta-deg 2
```

Expected:

- `joint1` moves about `+2 deg`.
- `joint1` returns to the original angle.
- Script prints `S10.3 ROS single-joint step completed.`
- No Web, ROS, or CAN errors appear.

Actual execution result on 2026-06-25:

- Operator reported the J1 angle change was visually observable and returned to
  the original position.
- Command:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-tool \
bash scripts/run_humble_container.sh \
  python3 /workspace/nero/scripts/ros_single_joint_step.py \
    --execute \
    --namespace arm_a \
    --joint joint1 \
    --delta-deg 2
```

- Current degrees:
  `[55.498000000000005, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.505]`.
- Target degrees:
  `[57.498000000000005, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.505]`.
- After step:
  `[57.294000000000004, 70.801, -29.615000000000002, 41.595, 21.6, -39.999, -35.505]`.
- After return:
  `[55.743, 70.798, -29.613999999999997, 41.598, 21.6, -39.999, -35.505]`.
- Return error on `joint1`: about `0.245 deg`, within the script tolerance
  `0.3 deg`.
- Final status:
  `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`, `motion_status=1`.
- Script completed with `S10.3 ROS single-joint step completed.`

Acceptance status:

- ROS motion command and return are accepted by operator observation and script
  target tolerance.
- `motion_status=1` in the final printed status was an observation item. The
  post-motion dual-arm ROS read-only snapshot showed Arm A `motion_status=0`,
  resolving the observation.

## Post-Motion Validation

Stop the S10.3 control driver, then return to dual-arm read-only validation:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

In another terminal:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-ros-post-snapshot \
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Acceptance:

- Snapshot has failed capture commands `0`.
- A/B feedback topics are complete.
- A/B `err_status: 0`.
- A/B joint limit flags are all `false`.
- A/B joint communication flags are all `false`.
- A/B joint-state feedback is about `200 Hz`.

Actual post-ROS validation on 2026-06-25:

- Snapshot: `docs/s9_ros_snapshots/20260625_064243/`.
- `README.md`: `Failed capture commands: 0`.
- Arm A joint-state frequency: about `200.0 Hz`.
- Arm B joint-state frequency: about `200.0 Hz`.
- Arm A `arm_status`: `ctrl_mode=1`, `arm_status=0`,
  `mode_feedback=1`, `motion_status=0`, `err_status=0`, all joint limit flags
  `false`, all joint communication flags `false`.
- Arm B `arm_status`: `ctrl_mode=1`, `arm_status=6`,
  `mode_feedback=1`, `motion_status=1`, `err_status=0`, all joint limit flags
  `false`, all joint communication flags `false`.
- Arm A post-ROS joint positions in radians:
  `[0.9686228282718131, 1.2356756571194656, -0.5170188843182802,
  0.7260569688296411, 0.3769911184307752, -0.6981142475052119,
  -0.6197140575056266]`.

## Stop Conditions

Stop S10.3 immediately if:

- Dry-run target is not a `joint1`-only `+2 deg` change.
- ROS driver logs failed firmware read, failed enable, or control gate errors.
- Motion direction is unexpected.
- Any cable tightens or workspace object enters the J1 swept area.
- Any abnormal sound, vibration, Web warning, ROS error, or non-zero error flag
  appears.
