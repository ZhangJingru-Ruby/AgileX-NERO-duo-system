# S15 Arm + Hand Coordination Sequence Plan

Date: 2026-07-02

## Scope

This plan introduces the first project-owned hybrid control sequence:

- NERO arms: ROS2 topics under `/arm_a` and `/arm_b`.
- LinkerHand L6 hands: local LinkerHand SDK through `can1` and `can2`.
- RViz: S11 accepted dual-arm model and `lab_world` static TF.

The sequence is intentionally gated. It defaults to dry-run and only executes
after explicit operator confirmations.

## Side Mapping

The physical installation remains:

| Operator side | Arm | Hand CAN | Hand serial |
| --- | --- | --- | --- |
| Left side | Arm B / `/arm_b` / `can_arm_b` | `can1` | `LHL6-03-253-L-B-1-C` |
| Right side | Arm A / `/arm_a` / `can_arm_a` | `can2` | `LHL6-03-240-R-B-1-C` |

This is why the S15 motion script maps `--side left` to `arm_b/can1`, and
`--side right` to `arm_a/can2`.

## New Scripts

Observation and control-source session:

```bash
scripts/launch_s15_dual_arm_hand_observe.sh [--readonly|--active]
```

This starts:

- either dual-arm ROS read-only drivers or S13 dual-active ROS arm drivers;
- S11 accepted static TF publishers;
- S11 dual model RobotStatePublisher instances;
- RViz with fixed frame `lab_world`.

It does not publish motion commands.

Default mode is `--readonly`. Use read-only mode for RViz validation and all
dry-runs. Stop the read-only session and relaunch with `--active` only before
an execute gate.

## Preflight Ready-Time Rule

Before S15 observation or motion tests:

- confirm `can_arm_a`, `can_arm_b`, `can1`, and `can2` are physically seated;
- after arm power-on or CAN/power reconnect, wait about `20 s` before treating
  `candump` or ROS topic checks as authoritative;
- if an arm interface is UP but `candump` or the ROS driver has no response,
  first reseat the cable and repeat after the ready-time wait.

This rule was added after a loose Arm B cable caused an active-driver startup
failure on 2026-07-02.

## RViz Pose Diagnostic Rule

If RViz shows both arms in the horizontal/URDF-zero posture while the real arms
are hanging, do not execute motion. This means the S11 visual chain is not
accepted for the current session.

Run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-diagnostics \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/s15_rviz_pose_diagnostics.sh
```

Expected evidence in raw RViz mode:

- `/arm_a/feedback/joint_states` and `/arm_b/feedback/joint_states` each have
  a live publisher and a `robot_state_publisher` subscriber.
- One joint-state sample is available from each arm.
- `lab_world -> arm_a/world` and `lab_world -> arm_b/world` match the accepted
  S11 root transforms.
- `lab_world -> arm_a/link7` and `lab_world -> arm_b/link7` reflect the current
  physical posture, not URDF zero pose.

Expected evidence in anchored RViz mode:

- `/arm_a/feedback/joint_states` and `/arm_b/feedback/joint_states` each have
  a live publisher and an `s15_joint_state_visual_anchor` subscriber.
- `/arm_a/visual/joint_states` and `/arm_b/visual/joint_states` each have the
  visual anchor as publisher and `robot_state_publisher` as subscriber.
- One visual joint-state sample is available from each arm.
- `lab_world -> arm_a/world` and `lab_world -> arm_b/world` still match the
  accepted S11 root transforms.
- `lab_world -> arm_a/link7` and `lab_world -> arm_b/link7` visually match the
  current physical posture.

2026-07-02 result:

- The feedback subscribers and S11 root transforms were present.
- The remaining mismatch was the raw joint-state visual convention. Raw
  `link7` TFs were live but horizontal in `lab_world`.
- S15 observation now defaults to the RViz-only visual anchor:
  `/arm_a/visual/joint_states` and `/arm_b/visual/joint_states`.
- The visual anchor uses the S11 accepted snapshot
  `docs/evidence/ros_snapshots/20260626_055339/` as a reference and preserves live
  joint deltas after startup.
- Visual anchor topics must not be used for control, planning, limits, or
  calibration.
- The operator subsequently confirmed that robot positions in anchored RViz are
  correct and visual following is correct. S15 RViz visual revalidation is
  accepted for the current session.

Coordinated sequence:

```bash
scripts/ros_s15_arm_hand_sequence.py
```

The sequence is:

1. Read both arm joint states and arm status.
2. Validate target joint limits and a conservative singularity guard.
3. Segment J1/J2/J3 motion into waypoints of at most `10 deg` by default.
4. Move selected arm or both arms to the target posture.
5. Send hand open.
6. Send hand close pose, using a blend from open to SDK fist.
7. Return hand to open.
8. Return active arms to their original joint positions.

## Target Requested by Operator

Default S15 target:

| Joint | Target mode | Value |
| --- | --- | --- |
| J1 / `joint1` | absolute | `30 deg` |
| J2 / `joint2` | absolute | `90 deg` |
| J3 / `joint3` | absolute | `30 deg` |

The script also supports `--target-mode delta`, but the first S15 tests should
use absolute mode. This avoids accidentally applying a `+90 deg` J2 delta from
an already raised posture.

## Safety Gates

The script refuses execution unless:

- `--execute` is explicitly supplied;
- `--confirm-clearance` is supplied;
- `--confirm-rviz-visible` is supplied;
- any planned joint change above `30 deg` is explicitly accepted with
  `--allow-wide-motion`;
- full or near-full fist is explicitly accepted with `--allow-full-fist`;
- arm feedback and arm status are available;
- arm `err_status` is zero;
- joint-limit and joint-communication flags are not active;
- hand faults are zero before and after hand motion.

The singularity guard is conservative and heuristic, not a full Jacobian
singularity detector. It blocks extreme J2/J3 configurations and near-straight
folded postures before command publication.

## Execution Order

Terminal 1, observation session for dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh --readonly
```

Terminal 2, left side dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-left-dryrun \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_arm_hand_sequence.py \
      --side left
```

2026-07-02 first retry note:

- The first left-side dry-run attempt failed before any command publication
  because the script used `self.publishers`, which conflicts with a read-only
  `rclpy.node.Node` attribute.
- The member was renamed to `self._move_publishers`; retry the same dry-run
  command.

2026-07-02 accepted dry-run:

- `--side left` maps to Arm B + left hand `can1`.
- The dry-run completed with `execute=False`.
- Planned target for Arm B:
  `[30.0, 90.0, 30.0, -1.078, -91.627, 0.259, -3.635] deg`.
- `waypoint_count=9`.
- `max_planned_joint_delta_deg=89.868`.
- Hand close pose is full fist: `[67, 151, 0, 0, 0, 0]`.
- Execute requires `--allow-wide-motion`, `--allow-full-fist`,
  `--confirm-clearance`, and `--confirm-rviz-visible` after physical clearance
  review.

Terminal 2, left side execute only after dry-run acceptance:

Stop the read-only observation session, then restart Terminal 1 in active mode:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh --active
```

Then execute:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-left-execute \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_arm_hand_sequence.py \
      --side left \
      --execute \
      --allow-wide-motion \
      --allow-full-fist \
      --confirm-clearance \
      --confirm-rviz-visible
```

Then repeat for `--side right`. Only after left and right single-side tests are
accepted should `--side both` be dry-run and executed.

2026-07-02 first execute result:

- Left-side execute published waypoint `1/9`.
- Arm B feedback did not change from the starting values before timeout.
- No hand command was sent.
- The script called A/B emergency stop after the timeout.
- Do not retry execute immediately. Restart S15 active observation and run
  `scripts/s15_motion_block_diagnostics.sh` first.
- The script now checks active-arm `/control/move_j` subscription counts before
  future execute attempts.
- Follow-up diagnostics showed `/arm_b/control/move_j` has a subscriber and arm
  status is normal. This still does not prove active mode because read-only
  drivers also create command subscribers. Confirm `control_enabled=true` and
  `auto_enable=true` from driver parameters before retrying execute.
- Updated diagnostics confirmed both drivers are active:
  `auto_enable=True`, `control_enabled=True`, and `speed_percent=5`.
  If Web enable changed after the failed execute attempt, the earlier no-motion
  event is likely explained by the arm not being enabled at execute time. If Web
  enable did not change, run a small Arm B J1 `+2 deg` command-path probe before
  retrying the wide S15 sequence.
- The small Arm B J1 `+2 deg` command-path probe passed by operator report.
  The next gate is retrying S15 left-side execute with active observation
  running, RViz visible, and physical clearance rechecked.
- A later operator report said the commanded motion did not match the intended
  human-like elbow-curl/fist gesture because the assumed joint-number mapping
  was wrong. Do not continue using the absolute `joint1=30`, `joint2=90`,
  `joint3=30` target as the gesture definition. Use
  `scripts/ros_s15_return_to_initial.py` to return to the accepted initial
  posture, then run the joint-mapping probes in
  `docs/phases/s15_return_to_initial_and_elbow_curl_design.md`.
- The operator then confirmed the initialization path succeeded and found by
  Web control that left-side Arm B `J1 -10 deg` plus `J4 +10 deg` better
  matches the demo intent. The next executable gate is
  `scripts/ros_s15_elbow_curl_demo.py`: first `J1 -2 deg`, `J4 +2 deg` with
  `--skip-hand`, then the formal `J1 -10 deg`, `J4 +10 deg` hand
  open/close/open demo after acceptance.
- The left-side and right-side smoother elbow-curl/fist demos were accepted.
  The script now supports `--side both` with per-side deltas. For the first
  dual-arm gate, use left Arm B semantic `J1 -10 deg`, right Arm A semantic
  `J1 -20 deg`, and `J4 +15 deg` on both sides. Because `J1` defaults to the
  `lab_world X` semantic frame, dry-run should show raw Arm B `joint1=-10 deg`
  and raw Arm A `joint1=+20 deg`.

Dual-arm dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-both-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side both \
      --left-j1-delta-deg -10 \
      --right-j1-delta-deg -20 \
      --left-j4-delta-deg 15 \
      --right-j4-delta-deg 15 \
      --arm-profile single-target \
      --hand-timing during-curl \
      --hand-start-delay 0.4 \
      --hand-dwell 0.8 \
      --hand-close-fraction 0.5 \
      --hold-seconds 0.5
```

Dual-arm execute after dry-run acceptance:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-both-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side both \
      --left-j1-delta-deg -10 \
      --right-j1-delta-deg -20 \
      --left-j4-delta-deg 15 \
      --right-j4-delta-deg 15 \
      --arm-profile single-target \
      --hand-timing during-curl \
      --hand-start-delay 0.4 \
      --hand-dwell 0.8 \
      --hand-close-fraction 0.5 \
      --hold-seconds 0.5 \
      --allow-wide-motion \
      --execute \
      --confirm-clearance \
      --confirm-rviz-visible
```

2026-07-02 dual-arm result:

- The dual-arm/dual-hand coordinated elbow-curl/fist gate ran through by
  operator report.
- The remaining correction is return-to-initial semantics: the return script
  now defaults to `--pose zero`, commanding both arms to
  `joint1..joint7 = 0 deg` while opening both hands.
- The older S15 field park remains available only through explicit
  `--pose s15-park`.

## Acceptance Criteria

For each side and for the final `both` test:

- RViz is open and follows the moving arm or arms.
- The script prints the expected side mapping.
- The target motion profile matches the accepted dry-run. For the smoother
  elbow-curl demo this is `--arm-profile single-target`, not the older
  segmented inspection profile.
- No non-commanded arm moves beyond tolerance.
- The passive arm remains within tolerance during single-side tests.
- Hand open/close/open commands complete with zero pre/post faults.
- Both active arms return to their original joint positions.
- Operator visually confirms the physical motion matches the dry-run plan.

Failure of any gate blocks the next test.
