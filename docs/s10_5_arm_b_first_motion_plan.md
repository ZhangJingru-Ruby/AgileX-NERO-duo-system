# S10.5 Arm B First-Motion Replication Plan

Status: accepted. Arm B Web J1 motion was confirmed normal by the operator, and
the read-only snapshot passed.

Arm A has passed Web, SDK, and ROS low-speed first motion. S10.4 no-motion
control-source closure is accepted. S10.5 starts the same ladder on Arm B, but
keeps the first Arm B step narrower than the Arm A Web result.

## Scope

Only Arm B is allowed to move in this procedure.

- Arm: Arm B.
- Web identity: `agx-7ax-armB`.
- CAN interface: `can_arm_b`.
- ROS namespace for later steps: `/arm_b`.
- First Web joint: J1.
- First Web target: current J1 angle plus `2 deg`, then return to the original
  angle.
- Preferred speed: lowest available Web speed, preferably `5%` or lower.

Do not use SDK, ROS `/control/*`, raw CAN, Cartesian motion, MoveIt execute,
MIT/JS mode, master-slave mode, dual-arm coordinated motion, zero calibration,
firmware update, or dexterous-hand commands during S10.5 Web motion.

## Why J1 Again

Arm A showed that J7 is difficult to observe visually and J1 `+2 deg` is easy
to verify. Reusing J1 keeps the comparison between Arm A and Arm B simple.
The tradeoff is that J1 sweeps the whole arm around the base, so the full J1
swept area must be clear.

At the manual working radius of about `580 mm`, `2 deg` corresponds to about
`20 mm` of outer-radius arc displacement.

## Pre-Motion Gate

All items must be true before touching Web motion controls:

- S10.4 live audit is accepted.
- Arm B base is fixed.
- Arm B J1 swept area is clear.
- Arm A is not being commanded.
- No ROS driver is running.
- No SDK motion script is running.
- No Web motion command is active on Arm A.
- `can_arm_b` is UP, ERROR-ACTIVE, and bitrate `1000000`.
- The operator is connected to Arm B Web UI, not Arm A.
- One person is assigned to Web emergency stop or physical power cutoff.
- The selected Web speed is the lowest available value, preferably `5%` or
  lower.

Confirm current control-source state from the real desktop terminal:

```bash
bash scripts/s10_control_source_audit.sh
```

Expected before S10.5:

- `can_arm_a` and `can_arm_b` visible.
- Both CAN interfaces ERROR-ACTIVE at `1000000`.
- NERO-related Docker containers: none, unless explicitly read-only.
- NERO-related host processes: none.

## S10.5 Web Procedure

1. Connect the laptop Wi-Fi to `agx-7ax-armB`.
2. Open `http://192.168.31.1/`.
3. Login with the documented Web credentials.
4. Confirm the physical arm is Arm B.
5. Confirm the Web page shows the expected NERO 7-axis controller.
6. Confirm load, installation pose, and collision settings remain as recorded.
7. Switch to Web/manual control mode if required by the UI.
8. Set speed to the lowest available value.
9. Enable Arm B in Web.
10. Record the current J1 angle.
11. Command J1 to current J1 plus `2 deg`.
12. Confirm the direction, amount, sound, and cable behavior are normal.
13. Command J1 back to the original angle.
14. Stop Web motion and leave no active command.

Abort immediately if direction is unexpected, motion is larger than intended,
cables pull, sound is abnormal, Web reports an error, or the operator loses
confidence in the current state.

## Post-Web Read-Only Validation

After Web motion succeeds, return to dual-arm ROS read-only validation.

Terminal 1:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

Terminal 2:

```bash
NERO_CONTAINER_NAME=nero-humble-s10b-web-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Accept S10.5 only if the snapshot shows:

- Arm A and Arm B feedback topics are present.
- Arm A and Arm B joint states publish at about `200 Hz`.
- Arm B `err_status: 0`.
- Arm B joint angle limits are all `false`.
- Arm B joint communication statuses are all `false`.
- Arm A remains healthy.

Stop the dual read-only driver after the snapshot unless it is intentionally
kept for monitoring. It must not remain active before SDK or ROS motion unless
we explicitly label it read-only and account for it.

## Next Steps After S10.5

If S10.5 passes:

1. S10.6 SDK dry-run on Arm B:

   ```bash
   .venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
     --channel can_arm_b \
     --firmware v112 \
     --joint 1 \
     --delta-deg 2 \
     --speed-percent 5
   ```

2. S10.6 SDK execute only after dry-run acceptance:

   ```bash
   .venv/nero-sdk/bin/python examples/nero_sdk_single_joint_step.py \
     --execute \
     --channel can_arm_b \
     --firmware v112 \
     --joint 1 \
     --delta-deg 2 \
     --speed-percent 5
   ```

3. S10.7 ROS control on Arm B, using namespace `arm_b`, CAN `can_arm_b`, and
   `joint1 +2 deg`, then return.

Do not start S10.6 until S10.5 has a clean post-Web snapshot.

## S10.5 Live Evidence On 2026-06-25

Pre-motion audit:

- Saved output: `docs/s10_5_control_source_audit_live_20260625_152039.txt`.
- `can_arm_a`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- `can_arm_b`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- NERO-related Docker containers: none.
- NERO-related host processes: none.

Read-only snapshot:

- Path: `docs/s9_ros_snapshots/20260625_072129/`.
- Failed capture commands: `0`.
- Topic list includes complete `/arm_a/...` and `/arm_b/...` feedback topics.
- Arm A joint-state feedback: about `200 Hz`.
- Arm B joint-state feedback: about `200 Hz`.
- Arm A `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B `err_status: 0`, all joint limits `false`, all joint communication
  statuses `false`.
- Arm B sampled joint positions in radians:
  `[0.5724505413616201, 1.3979912775549381, -0.3002140846355446,
  0.3630110311223006, -1.2374035330789397, 0.37346555334174664,
  0.16057029118347835]`.

Acceptance:

- The audit and snapshot are accepted.
- Operator confirmed Arm B Web operation was normal.
- S10.5 is accepted.
- S10.6 SDK dry-run may start.
