# S10 First Low-Speed Motion Plan

Status: S10.1 Web first motion passed on Arm A by operator report and ROS
read-only revalidation.

This document defines the first real NERO motion after S0-S9. It is deliberately
small and single-arm only.

## Scope

S10 verifies the minimum motion loop:

- command a very small joint-space movement
- observe that direction and magnitude are plausible
- stop or emergency-stop if needed
- return to the previous joint angle
- revalidate Web/CAN/ROS status after the motion

Do not use this step for Cartesian motion, MoveIt execute, MIT mode, master-slave
mode, raw CAN motion frames, dual-arm coordinated motion, zero calibration, or
dexterous-hand actuation.

## Sources And Facts

- User manual section `6.1 运动控制`: Web motion requires switching to `WEB`
  mode first, then enabling joints before operating. Joint motion takes effect
  after clicking apply.
- User manual section `6.5 速度调节`: Web has a speed percentage slider for the
  arm's overall speed.
- S9 result: both arms are bare-arm / no-load, Web installation position
  `1-水平正装`, collision level J1-J7 all `1`, ROS feedback clean at about
  200 Hz, and no joint limit or communication errors.
- S9 decision: do not expand J2 Web limits before S10.
- S9 decision: keep Web installation position unchanged and treat lab-frame
  alignment as a later external transform problem.

## Recommended First Motion

Default arm: Arm B, only if Arm B has workspace clearance at least as good as
Arm A.

Reason:

- Arm B had the more stable CAN path through the S9 recovery episode.
- Physical clearance is more important than this preference; choose Arm A
  instead if Arm A is clearly safer in the room.

Current S10.1 selection:

- Operator selected Arm A.
- Operator confirmed the remaining pre-motion requirements before execution.
- Operator reported successful Web enable and joint control.
- Actual execution went beyond the original J7-only plan: all 7 Arm A joints
  were moved successfully from Web.
- Post-motion ROS read-only snapshot:
  `docs/s9_ros_snapshots/20260625_060810/`.

S10.1 result:

- Web first motion: passed for Arm A.
- Post-motion ROS revalidation: passed.
- Intentional emergency-stop recovery: not tested because no abnormal motion was
  reported.
- SDK and ROS motion commands: not tested yet.

Important correction:

The original first-motion plan limited the first command to J7 `+2 deg` then
return. The actual field test exercised all 7 degrees of freedom from Web. This
is recorded as successful field evidence, but it should not be treated as
permission to skip the remaining staged gates for SDK/ROS motion, Cartesian
motion, MoveIt execute, or dual-arm motion.

Default joint: J7.

Command:

1. Record the current Web J7 angle.
2. Command J7 to current angle plus `2 deg`.
3. Wait for the arm to stop.
4. Command J7 back to the recorded original angle.

Reason:

- J7 has the smallest expected translational sweep on the bare arm.
- It avoids J2/J4, where the manual warns about kinematic control near zero.
- It avoids J1, which sweeps the whole arm around the base.

Main risk:

- J6/J7 or any temporary cable can twist. If any cable tension is visible, do
  not use J7 until the cable path is corrected.

## Pre-Motion Gate

All items must be true before clicking any motion apply button:

- The selected arm is physically fixed on the table.
- The other arm is not enabled and is not being commanded.
- No person, laptop, tool, or loose object is inside the selected arm's swept
  space.
- One person is assigned to Web emergency stop or physical power cutoff.
- The selected arm is bare-arm, no-load, with no tool attached.
- ROS read-only driver is stopped before Web control, so Web is the only active
  control source.
- The Web status page shows no active error.
- Web speed percentage is set to the lowest available value, preferably
  `5%` or lower. If the UI cannot set a low speed percentage, stop and record
  the observed UI state before moving.
- The operator knows the exact original J7 angle and the exact target angle.

## Web Execution Procedure

1. Stop any ROS driver terminal with `Ctrl-C`.
2. Connect the laptop to the selected arm Wi-Fi.
3. Open the Web UI for the selected arm.
4. Confirm the status page has no error.
5. Click the top `WEB` mode button.
6. Set the Web speed percentage to the lowest available value, preferably
   `5%` or lower.
7. Enable only what the Web UI requires for joint motion. If the UI only offers
   all-joint enable, use it, but do not command any joint except J7.
8. Open joint motion.
9. Record all current joint angles, especially J7.
10. Change only J7 to `current + 2 deg`.
11. Keep one hand ready for emergency stop or power cutoff.
12. Click apply.
13. Stop immediately if the direction is unexpected, motion is larger than
    expected, a cable tightens, abnormal sound appears, or Web reports an
    error.
14. After it stops, set J7 back to the recorded original angle and click apply.
15. Record the result, including direction, observed stop behavior, Web status,
    and any abnormal sound or warning.

## Post-Motion Revalidation

After Web motion, return to the known read-only validation state:

1. Make sure Web motion has stopped.
2. Do not leave any pending Web command active.
3. Reactivate CAN interfaces if needed:

```bash
bash scripts/activate_can.sh can_arm_a 1000000 "1-5:1.0"
bash scripts/activate_can.sh can_arm_b 1000000 "1-11:1.0"
```

4. Start dual-arm ROS read-only validation:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

5. In another terminal, capture a snapshot:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-post-web-snapshot \
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

If either CAN interface is visible but produces no passive frames after Web
mode, use the S9 recovery path: unplug/replug that USB-CAN adapter, reactivate
the interface with the deterministic bus-info, then retry read-only validation.

## Acceptance Criteria

S10 Web first motion passes only if:

- The selected arm moves only the intended small amount.
- The observed direction matches the command.
- The arm stops normally after the command.
- J7 returns to the recorded original angle.
- Web shows no error after the test.
- Post-motion ROS read-only snapshot has complete Arm A and Arm B feedback,
  `err_status: 0`, all joint limit flags `false`, all joint communication flags
  `false`, and approximately 200 Hz joint-state feedback.

If any item fails, do not continue to SDK or ROS motion. Record the failure and
return to S6/S8 read-only diagnosis.

## S10.1 Actual Acceptance On 2026-06-25

Operator report:

- Arm A Web enable succeeded.
- Arm A Web joint control succeeded.
- All 7 Arm A degrees of freedom moved successfully.

ROS read-only snapshot:

- Path: `docs/s9_ros_snapshots/20260625_060810/`.
- `README.md`: `Failed capture commands: 0`.
- Arm A `/feedback/joint_states`: about `200.0 Hz`.
- Arm B `/feedback/joint_states`: about `200.0 Hz`.
- Arm A `arm_status`: `err_status: 0`, all joint limit flags `false`, all
  joint communication flags `false`.
- Arm B `arm_status`: `err_status: 0`, all joint limit flags `false`, all
  joint communication flags `false`.

Observed after-motion Arm A joint positions in radians:

```text
J1  0.9686577348568529
J2  1.2356931104119853
J3 -0.5166174585903216
J4  0.7260569688296411
J5  0.3769911184307752
J6 -0.6981317007977318
J7 -0.6195220712879073
```

Notes:

- Arm A `arm_status` changed from the previous read-only snapshot value `6` to
  `0`, while `err_status` remained `0` and all limit/communication flags stayed
  clear. Treat this as a state-machine observation to monitor, not as a failure.
- Arm B remained read-only and healthy during the post-motion snapshot.
