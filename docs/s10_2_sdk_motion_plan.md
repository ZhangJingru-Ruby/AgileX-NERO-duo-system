# S10.2 SDK Single-Joint Motion Plan

Status: accepted. SDK J1 `+2 deg` motion passed on Arm A, and post-motion ROS
read-only snapshot passed.

S10.1 Web first motion passed on Arm A. S10.2 tests the next control path:
direct `pyAgxArm` SDK control over SocketCAN.

## Scope

Only one Arm A SDK joint-space step is allowed in this procedure:

- Control source: SDK only.
- Arm: Arm A.
- CAN interface: `can_arm_a`.
- Joint: J1 for execution, after a new J1 `+2 deg` dry-run.
- Command: read current joints, command J1 to current angle plus `2 deg`, then
  return J1 to the original angle.
- Speed: `5%`.

Actual S10.2 execution used speed `10%`. This is higher than the planned `5%`
but still inside the script's S10.2 hard limit of `0..10%`.

Do not use ROS `/control/*`, raw `cansend`, Cartesian motion, MoveIt execute,
MIT/JS mode, master-slave mode, dual-arm motion, zero calibration, or dexterous
hand commands during S10.2.

## Evidence For Interface Choice

Local SDK evidence:

- `pyAgxArm/docs/nero/nero_api.md` defines NERO joint angles as 7-element lists
  in radians.
- `move_j(joints)` commands joint-space targets.
- `set_speed_percent(percent)` accepts `0..100`; S10.2 restricts this to
  `0..10`.
- NERO firmware `v112` is the current selector for observed software version
  `1.121`.
- The v112 driver can enable all joints and uses CAN control mode.

Reason to test SDK before ROS:

- SDK is the direct layer used by the ROS driver.
- It avoids ROS `auto_enable`, `control_enabled`, and topic remapping variables
  while proving that programmatic CAN control is safe at the SDK layer.

## Script

Use:

```bash
examples/nero_sdk_single_joint_step.py
```

The script defaults to dry-run. It connects, reads current joint feedback,
prints current and target angles, and exits without motion unless `--execute`
is provided.

Safety behavior:

- Refuses absolute deltas above `2 deg` by default.
- Refuses speed percent above `10`.
- Reads the current 7-joint vector and modifies only one element.
- Checks configured SDK joint limits before motion.
- Enables all joints only after `--execute`.
- Sends `move_j()` once for the step and once for return.
- Does not disable the arm at the end, because disabling can allow gravity
  motion depending on posture and brake state.
- On Ctrl-C during execution, sends SDK `electronic_emergency_stop()` unless
  `--no-estop-on-ctrl-c` is given.

## Pre-Motion Gate

All items must be true before running the `--execute` command:

- S10.1 Web motion result is accepted.
- Arm A workspace is clear.
- Arm A base is fixed.
- Arm B remains uncommanded.
- ROS driver is stopped.
- Web page is not sending a motion command.
- `can_arm_a` is active and mapped to USB bus `1-5:1.0`.
- One person is assigned to Web emergency stop or physical power cutoff.
- Operator accepts that SDK will enable all joints and command J1 by `2 deg`.

## Dry Run

J7 dry-run result on 2026-06-25:

- Firmware read succeeded: `{'software_version': '1.121'}`.
- Current Arm A joint angles in degrees:
  `[55.5, 70.798, -29.599, 41.602000000000004, 21.6, -39.999, -35.5]`.
- J7 dry-run target in degrees:
  `[55.5, 70.798, -29.599, 41.602000000000004, 21.6, -39.999, -34.5]`.
- `pre_status`: `ctrl_mode=CAN_CTRL(0x1)`, `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- No motion occurred.

Operator proposed changing execution from J7 to J1 because J7 rotation is hard
to observe visually. J1 `+1 deg` dry-run then passed, but the operator judged
`1 deg` may still be too small for easy observation and confirmed the J1 swept
area is clear. S10.2 execution delta is therefore revised to J1 `+2 deg`, which
remains within the script's default `--max-delta-deg 2` safety limit. At the
manual working radius of about `580 mm`, `2 deg` corresponds to about `20 mm`
of arc displacement at the outer radius. The tradeoff is that J1 moves the
whole arm around the base, so the entire J1 swept area must remain clear.

J1 `+1 deg` dry-run result on 2026-06-25:

- Firmware read succeeded: `{'software_version': '1.121'}`.
- Current Arm A joint angles in degrees:
  `[55.498000000000005, 70.796, -29.599, 41.599000000000004, 21.599, -40.0, -35.499]`.
- J1 `+1 deg` dry-run target in degrees:
  `[56.49800000000001, 70.796, -29.599, 41.599000000000004, 21.599, -40.0, -35.499]`.
- `pre_status`: `ctrl_mode=CAN_CTRL(0x1)`, `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- No motion occurred.

Run first:

```bash
.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
  --channel can_arm_a \
  --firmware v112 \
  --joint 1 \
  --delta-deg 2 \
  --speed-percent 5
```

Expected dry-run result:

- SDK imports successfully.
- Firmware is readable.
- Current 7 joint angles are printed in degrees.
- Target 7 joint angles are printed in degrees.
- The target differs from current only in J1 by `+2 deg`.
- `pre_status` is printed.
- Final line says dry run only.
- No motion occurs.

If dry-run fails, do not run `--execute`.

## Execute

Only after the dry-run output looks correct:

```bash
.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
  --execute \
  --channel can_arm_a \
  --firmware v112 \
  --joint 1 \
  --delta-deg 2 \
  --speed-percent 5
```

Expected execution:

- Arm A enables if not already enabled.
- J1 moves about `+2 deg`.
- J1 returns to its original angle.
- Script prints `S10.2 SDK single-joint step completed.`
- No joint limit or communication errors appear.

## S10.2 Actual Acceptance On 2026-06-25

Operator report:

- J1 visibly moved a small amount and then returned to the original position.
- No interference was observed.

Execution command:

```bash
.venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
  --execute \
  --channel can_arm_a \
  --firmware v112 \
  --joint 1 \
  --delta-deg 2 \
  --speed-percent 10
```

Script output summary:

- Firmware: `{'software_version': '1.121'}`.
- Current degrees:
  `[55.499, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.502]`.
- Target degrees:
  `[57.499, 70.799, -29.62, 41.599000000000004, 21.6, -39.999, -35.502]`.
- After step:
  `[57.503, 70.8, -29.625000000000004, 41.598, 21.6, -39.999, -35.502]`.
- After return:
  `[55.49500000000001, 70.8, -29.619, 41.597, 21.6, -40.005, -35.502]`.
- Final status:
  `ctrl_mode=CAN_CTRL(0x1)`, `arm_status=NORMAL(0x0)`,
  `mode_feedback=MOVE_J(0x1)`,
  `motion_status=REACH_TARGET_POS_SUCCESSFULLY(0x0)`.
- Script completed with `S10.2 SDK single-joint step completed.`

Acceptance:

- SDK J1 `+2 deg` step passed.
- SDK return-to-original command passed within normal feedback tolerance.
- Actual speed was `10%`; this deviated from planned `5%` but remained within
  the script's safety cap.
- Post-motion ROS read-only snapshot passed, so S10.3 ROS motion can be
  prepared.

## Post-Motion Validation

After execution, return to read-only ROS validation:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

In another terminal:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-sdk-post-snapshot \
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

Actual post-SDK ROS read-only validation:

- Snapshot: `docs/s9_ros_snapshots/20260625_062910/`.
- `README.md`: `Failed capture commands: 0`.
- Arm A `/feedback/joint_states`: about `200.0 Hz`.
- Arm B `/feedback/joint_states`: about `200.0 Hz`.
- Arm A `arm_status`: `ctrl_mode=1`, `arm_status=0`,
  `mode_feedback=1`, `motion_status=0`, `err_status=0`, all joint limit flags
  `false`, all joint communication flags `false`.
- Arm B `arm_status`: `ctrl_mode=1`, `arm_status=6`,
  `mode_feedback=1`, `motion_status=1`, `err_status=0`, all joint limit flags
  `false`, all joint communication flags `false`.
- Arm A post-SDK joint positions in radians:
  `[0.968640281564333, 1.2356582038269455, -0.5169490711482004,
  0.7260220622446012, 0.37697366513825525, -0.6980967942126919,
  -0.619591884457987]`.

## Stop Conditions

Stop S10.2 immediately if any of these happens:

- Dry-run target angle is not the expected J1-only `+2 deg` change.
- SDK cannot read firmware or current joint angles.
- `can_arm_a` has no passive frames.
- Enable fails.
- Motion direction is unexpected.
- Any cable tightens.
- Anything is inside the small J1 swept area.
- Any abnormal sound, vibration, Web warning, SDK error, ROS error, or non-zero
  error flag appears.
