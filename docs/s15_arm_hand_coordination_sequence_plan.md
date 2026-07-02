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
