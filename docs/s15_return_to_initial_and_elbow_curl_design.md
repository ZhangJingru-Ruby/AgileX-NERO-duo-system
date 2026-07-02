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

## Operator-Observed Joint Mapping

After returning to the initial S15 park posture, the operator used Web control
to check the visible gesture mapping directly.

Accepted current candidate for the left-side demo:

```text
left side = Arm B + left hand can1
Arm B J1: -10 deg
Arm B J4: +10 deg
```

Observed effect:

- This combination is closer to the intended human-like elbow-curl/fist demo
  than the previous absolute `joint1=30`, `joint2=90`, `joint3=30` target.
- Because this result is based on field observation, the next command gate is a
  small `2 deg` probe using the same J1/J4 signs, not a new wide J2/J3 search.

Use this slow dry-run first:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-elbow-probe \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side left \
      --j1-delta-deg -2 \
      --j4-delta-deg 2 \
      --skip-hand
```

Then execute the same `2 deg` arm-only probe only if RViz, clearance, and Web or
driver enable state are all confirmed:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-elbow-probe \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side left \
      --j1-delta-deg -2 \
      --j4-delta-deg 2 \
      --skip-hand \
      --execute \
      --confirm-clearance \
      --confirm-rviz-visible
```

The formal first demo is:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side left \
      --j1-delta-deg -10 \
      --j4-delta-deg 10 \
      --hand-close-fraction 0.5 \
      --allow-wide-motion \
      --execute \
      --confirm-clearance \
      --confirm-rviz-visible
```

The first formal demo above intentionally uses the safe segmented profile. If
the motion is semantically correct but visually stop-start, that is expected:
the script sends one `move_j` waypoint at a time, waits for that waypoint to be
reached, and then applies `waypoint_dwell`.

For a smoother demo after the segmented version is accepted, use the single
target arm profile and run the hand during the curl:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side left \
      --j1-delta-deg -10 \
      --j4-delta-deg 15 \
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

This is still not a hard real-time synchronization primitive. It is a smoother
demo mode: arm target is sent once, while hand commands are sent from the
LinkerHand SDK after a small delay.

## Right-Side / Arm A Reproduction

Right side maps to Arm A and right hand:

```text
right side = Arm A + right hand can2
```

The first Arm A reproduction exposed a coordinate-sign problem:

- Arm B raw `J1 -10 deg` moved in the intended `lab_world -X` direction.
- Arm A raw `J1 -20 deg` moved toward `lab_world +X`, not `lab_world -X`.

Root cause:

- Arm A and Arm B face each other.
- J1 raw joint signs are local to each arm.
- A raw J1 sign is not a shared world-frame direction.

Decision:

- `ros_s15_elbow_curl_demo.py` now interprets `--j1-delta-deg` in the
  `lab_world X` semantic frame by default.
- `--j1-delta-deg -20` means "move J1 toward `lab_world -X` by 20 deg".
- Conversion:
  - Arm B command raw J1 delta = requested J1 delta.
  - Arm A command raw J1 delta = negative requested J1 delta.
- Use `--j1-delta-frame raw-joint` only for low-level sign debugging.

For the first Arm A reproduction, the operator requested semantic
`J1 -20 deg` so Arm A stays away from the support column between the two arms.
The script will command Arm A raw J1 `+20 deg` to achieve that semantic
direction. Keep J6/J7 unchanged because the hand cable still limits large wrist
bends.

Dry-run first:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-right-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side right \
      --j1-delta-deg -20 \
      --j1-delta-frame lab-world-x \
      --j4-delta-deg 15 \
      --arm-profile single-target \
      --hand-timing during-curl \
      --hand-start-delay 0.4 \
      --hand-dwell 0.8 \
      --hand-close-fraction 0.5 \
      --hold-seconds 0.5
```

Execute only after the dry-run target summary and physical clearance are
accepted:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-right-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side right \
      --j1-delta-deg -20 \
      --j1-delta-frame lab-world-x \
      --j4-delta-deg 15 \
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

Full fist remains a separate confirmation:

```bash
--hand-close-fraction 1.0 --allow-full-fist
```

Do not probe J6/J7 for this gesture until the cable clearance plan is improved.

## Likely Gesture Construction

Build the action in this order:

1. Return to S15 park.
2. Run the `J1 -2 deg`, `J4 +2 deg` arm-only probe.
3. If accepted, run the `J1 -10 deg`, `J4 +10 deg` arm motion with hand
   open/close/open.
4. Close the hand with `hand_close_fraction=0.5` first.
5. Only after the half close is accepted, try `hand_close_fraction=1.0`.

Recommended first gesture should be delta-based, not absolute:

```text
arm_delta:
  joint1: -10 deg
  joint4: +10 deg
hand:
  close_fraction: 0.5 first, then 1.0 after acceptance
```

Do not reattempt the wide absolute `joint2=90, joint3=30` sequence as the
gesture definition. It is a valid numerical target but not an accepted semantic
gesture.
