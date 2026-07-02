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
  `docs/s9_ros_snapshots/20260626_055339/` as a reference and preserves live
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

## Acceptance Criteria

For each side and for the final `both` test:

- RViz is open and follows the moving arm or arms.
- The script prints the expected side mapping.
- The target posture is segmented, not sent as one large jump.
- No non-commanded arm moves beyond tolerance.
- The passive arm remains within tolerance during single-side tests.
- Hand open/close/open commands complete with zero pre/post faults.
- Both active arms return to their original joint positions.
- Operator visually confirms the physical motion matches the dry-run plan.

Failure of any gate blocks the next test.
