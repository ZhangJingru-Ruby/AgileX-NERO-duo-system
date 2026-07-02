# S15 Return-To-Initial And Elbow-Curl Design

Date: 2026-07-02

## Why The Previous Motion Did Not Match The Intended Gesture

The previous S15 target was defined as absolute joint values:

```text
joint1 = 30 deg
joint2 = 90 deg
joint3 = 30 deg
hand = full fist
```

This was numerically valid, but it did not encode the intended human-like
gesture. NERO is a 7-DOF robot arm, not a human arm skeleton with directly named
shoulder/elbow/wrist joints. In the current field setup, raw joint values also
have a visual-convention mismatch against URDF zero, which is why RViz uses the
S15 visual-anchor path.

Therefore the correct workflow is:

1. Return to a known field `park` posture.
2. Probe each candidate joint with small deltas.
3. Record the observed semantic effect.
4. Build the gesture from those observed effects, preferably in delta mode.

## Return-To-Initial Script

Script:

```bash
scripts/ros_s15_return_to_initial.py
```

Default target:

- Arm A S15 park:
  `[2.651, -0.774, -95.039, -6.746, 92.13, -2.174, 9.687] deg`
- Arm B S15 park:
  `[0.824, 0.132, 101.705, -1.078, -91.63, 0.259, -3.628] deg`
- Left hand open:
  `[255, 179, 255, 255, 255, 255]`
- Right hand open:
  `[255, 70, 255, 255, 255, 255]`

Important:

- This is not factory zero.
- This is not Web zero calibration.
- This is the S15 field park posture recorded from the accepted S15
  anchored-RViz/current-state checks.

Dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-init \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_return_to_initial.py
```

Execute:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-init \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_return_to_initial.py \
      --execute \
      --allow-wide-motion \
      --confirm-clearance \
      --confirm-rviz-visible
```

The script opens both hands first, then moves selected arms back to S15 park in
segmented waypoints.

## Human-Like Elbow-Curl Gesture Definition

Desired visible action:

1. Start from S15 park.
2. Keep the upper arm/shoulder posture visually stable.
3. Flex the forearm toward the body, like bending an elbow.
4. Close the hand into a fist.
5. Optionally return hand open and arm park.

The first mistake to avoid is using absolute `joint2=90, joint3=30` as the
gesture definition. Those are just raw joint values; they do not guarantee the
visual semantic "bend elbow".

## Candidate Joint Semantics

The following table is a working hypothesis. It must be filled by physical
observation in the current setup.

| Joint | Likely role | Why it matters |
| --- | --- | --- |
| J1 / `joint1` | base/shoulder yaw | Positions the arm left/right around the base; useful for presentation but not elbow flex. |
| J2 / `joint2` | shoulder lift/pitch candidate | Large J2 changes strongly alter the whole arm posture; use cautiously. |
| J3 / `joint3` | elbow/forearm flex candidate | Most likely to create visible forearm folding in the current left-arm park posture, but sign must be verified. |
| J4 / `joint4` | forearm roll or secondary bend candidate | May help make the curl look human-like after J3 sign is known. |
| J5 / `joint5` | wrist/palm orientation candidate | Useful to keep the palm/fist facing the desired direction. |
| J6/J7 | wrist joints | Keep small because current hand cable routing limits large wrist bends. |

## Required Joint-Mapping Probes

Use Arm B first because the left-side S15 sequence uses Arm B + left hand.

Dry-run and then execute one probe at a time:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-map \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --target arm_b \
      --joint joint2 \
      --delta-deg 10
```

```bash
NERO_CONTAINER_NAME=nero-humble-s15-map \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --execute \
      --target arm_b \
      --joint joint2 \
      --delta-deg 10
```

Repeat for:

- `joint2 +10 deg`
- `joint2 -10 deg`
- `joint3 +10 deg`
- `joint3 -10 deg`
- `joint4 +10 deg`
- `joint4 -10 deg`

Record for each probe:

| Probe | Observed motion | Useful for elbow curl? | Safe sign |
| --- | --- | --- | --- |
| Arm B J2 +10 | TBD | TBD | TBD |
| Arm B J2 -10 | TBD | TBD | TBD |
| Arm B J3 +10 | TBD | TBD | TBD |
| Arm B J3 -10 | TBD | TBD | TBD |
| Arm B J4 +10 | TBD | TBD | TBD |
| Arm B J4 -10 | TBD | TBD | TBD |

Do not probe J6/J7 for this gesture until the cable clearance plan is improved.

## Likely Gesture Construction

After mapping probes, build the action in this order:

1. Return to S15 park.
2. Move the selected elbow-flex candidate joint by `10-20 deg`.
3. Add a small wrist/palm compensation only if needed.
4. Close the hand with `hand_close_fraction=0.5` first.
5. Only after the half close is accepted, try `hand_close_fraction=1.0`.

Recommended first gesture should be delta-based, not absolute:

```text
arm_delta:
  joint3: sign_from_probe * 15..25 deg
hand:
  close_fraction: 0.5 first, then 1.0 after acceptance
```

Do not reattempt the wide absolute `joint2=90, joint3=30` sequence as the
gesture definition. It is a valid numerical target but not an accepted semantic
gesture.
