# S15 Left-Side Dry-Run Result

Date: 2026-07-02

## Command

```bash
NERO_CONTAINER_NAME=nero-humble-s15-left-dryrun \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_arm_hand_sequence.py \
      --side left
```

## Result

The command completed as a dry-run:

- `execute=False`
- side mapping: `left -> arm_b/can1`
- active arm: `arm_b`
- passive arm: `arm_a`
- requested target: `joint1=30 deg`, `joint2=90 deg`, `joint3=30 deg`
- waypoint count: `9`
- max planned joint delta: `89.868 deg`
- wide motion required: `true`

Current raw arm states from the script:

- Arm A: `[2.651, -0.774, -95.039, -6.746, 92.126, -2.173, 9.687] deg`
- Arm B: `[0.824, 0.132, 101.705, -1.078, -91.627, 0.259, -3.635] deg`

Arm B target:

- summary: `joint1=30 deg`, `joint2=90 deg`, `joint3=30 deg`
- full target:
  `[30.0, 90.0, 30.0, -1.078, -91.627, 0.259, -3.635] deg`

Hand plan:

- open pose: `[255, 179, 255, 255, 255, 255]`
- close pose: `[67, 151, 0, 0, 0, 0]`
- close fraction: `1.00`

Arm status:

- Arm A: `ctrl_mode=1`, `arm_status=6`, `mode_feedback=1`,
  `motion_status=1`, `err_status=0`
- Arm B: `ctrl_mode=1`, `arm_status=6`, `mode_feedback=1`,
  `motion_status=1`, `err_status=0`

## Assessment

The software dry-run gate passed: mapping, feedback, status, target generation,
segmentation, and dry-run behavior are all as expected.

This is a wide-motion plan, not a micro-motion plan. The largest planned joint
change is about `89.9 deg`, driven mainly by Arm B J2 and J3. Execution requires
explicit `--allow-wide-motion`.

The hand command is a full close/fist plan. Execution requires explicit
`--allow-full-fist` and physical confirmation that the fingers, palm, cable
routing, and nearby workspace are clear.

## Next Gate

Before execute:

- Keep RViz anchored observation running and visible.
- Confirm Arm B sweep volume is clear for the 9-segment J1/J2/J3 path.
- Confirm left-hand finger closing volume is clear and no object/contact is
  present unless intentionally planned.
- Confirm J6/J7 cable routing has enough slack and will not be stressed by the
  planned posture.

If all are confirmed, the next command is left-side execute with explicit
wide-motion and full-fist confirmations. Otherwise, rerun dry-run with a reduced
hand close fraction or smaller arm target.
