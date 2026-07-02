# S15 RViz Pose Diagnostics Result

Date: 2026-07-02

## Context

During S15 dual arm + dual hand coordination preparation, the operator reported
that the real arms were hanging vertically, while RViz showed both arms in a
horizontal, arms-forward posture.

This blocks S15 motion execution. The planned S15 sequence contains large J1,
J2, and J3 targets, so the visual chain must be accepted before any execute
gate.

## Evidence From Diagnostics

Command:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-diagnostics \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/s15_rviz_pose_diagnostics.sh
```

Observed:

- `/arm_a/feedback/joint_states` has one publisher and one
  `robot_state_publisher` subscriber.
- `/arm_b/feedback/joint_states` has one publisher and one
  `robot_state_publisher` subscriber.
- Both raw feedback samples contain live, non-zero joint positions.
- Accepted S11 static TF values are active:
  - `lab_world -> arm_a/world`: `0,0,0,0,-1.5707963,0`
  - `lab_world -> arm_b/world`: `0.260,0,0,3.1415926,-1.5707963,0`
- `lab_world -> arm_a/link7` and `lab_world -> arm_b/link7` are live TFs, but
  their translations are approximately horizontal in the lab frame:
  - Arm A link7: `x=-0.713 m`, `z=0.007 m`
  - Arm B link7: `x=0.977 m`, `z=-0.018 m`

## Interpretation

The current failure is not a missing ROS feedback topic, not a missing
`robot_state_publisher` subscription, and not a missing S11 root transform.

RViz is receiving live raw joint feedback and the accepted S11 root TF, but
the raw joint feedback no longer corresponds to the visual joint convention
used when S11 was accepted. The most likely cause is a changed controller/Web
zero-state convention after later setup work, not a launch typo.

Historical reference:

- S11 accepted RViz posture used snapshot
  `docs/s9_ros_snapshots/20260626_055339/`.
- In that reference, the visually accepted hanging posture had Arm A/Arm B J2
  near `90 deg`.
- Later S14/S15 raw snapshots include near-zero J2 values for the hanging or
  near-hanging posture, which produces the horizontal URDF visual posture.

## Decision

Do not change arm control topics or real motion semantics to fix RViz.

Instead, add a reversible S15 RViz-only visual anchor:

- Raw control/state topics stay unchanged:
  - `/arm_a/feedback/joint_states`
  - `/arm_b/feedback/joint_states`
- New visual-only topics are generated:
  - `/arm_a/visual/joint_states`
  - `/arm_b/visual/joint_states`
- RViz can subscribe to those visual topics during S15 observation.

The visual anchor maps the current first live raw joint sample to the S11
accepted visual reference snapshot, then preserves subsequent live joint
deltas. This is an empirical visualization aid, not a calibration source for
planning or control.

In anchored mode, the expected subscription topology changes:

- `s15_joint_state_visual_anchor` subscribes to
  `/arm_a/feedback/joint_states` and `/arm_b/feedback/joint_states`.
- `robot_state_publisher` subscribes to `/arm_a/visual/joint_states` and
  `/arm_b/visual/joint_states`.

## Files Added Or Changed

- `scripts/ros_s15_joint_state_visual_anchor.py`
- `scripts/launch_s11_dual_model_view.sh`
- `scripts/launch_s15_dual_arm_hand_observe.sh`
- `scripts/s15_rviz_pose_diagnostics.sh`

## Use

Default S15 observation now uses the RViz visual anchor:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh
```

For raw-RViz comparison:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe-raw \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh --raw-rviz
```

## Acceptance Before Motion

Before running S15 arm+hand motion:

- RViz must again match the real hanging posture.
- Moving one arm slightly must be reflected in RViz in the correct direction.
- The operator must understand that `/arm_*/visual/joint_states` are for RViz
  only and must not be used for control, MoveIt planning, joint limits, or
  calibration.

S15 motion remains blocked until this visual revalidation passes.
