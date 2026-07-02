# S11 Dual-Arm Experiment Baseline

Status: accepted / closed on 2026-06-26.

S10 proved that Arm A and Arm B can each be controlled safely through Web, SDK,
and ROS. S11 turns the machine into a measurable dual-arm experiment platform
before any coordinated manipulation algorithm is tested.

## Acceptance View

An evaluator should be able to answer these questions from the S11 evidence:

- Where is each arm base in a shared lab/world frame?
- Are the ROS TF frames consistent with the physical machine?
- What TCP is being used right now, and what must be redone after installing
  the dexterous hand?
- Can a later experiment be replayed from logs and tied to a git commit?
- If an algorithm fails, can we separate algorithm, calibration, control, and
  hardware-state issues?

S11 is not a motion-expansion phase. Do not run dual-arm coordinated motion,
Cartesian motion, MoveIt execution, raw CAN motion, or dexterous-hand actuation
in S11.

## Current Assumptions

- Both arms are bare arms.
- Current ROS `effector_type` is `none`.
- Current TCP offset is `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`.
- Arm A ROS namespace is `/arm_a`.
- Arm B ROS namespace is `/arm_b`.
- Arm A CAN is `can_arm_a`.
- Arm B CAN is `can_arm_b`.
- Arm A USB bus is `1-5:1.0`.
- Arm B USB bus is `1-11:1.0`.

## Required Artifacts

Create or update these artifacts during S11:

- `docs/phases/s11_dual_arm_experiment_baseline.md`
- `docs/phases/s11_measurement_notes.md`
- `docs/phases/s11_static_tf_plan.md`
- `docs/phases/s11_rosbag_logging_plan.md`
- `docs/phases/s11_operator_guide.md`
- A photo set showing the physical base relationship and measurement reference.
- A read-only ROS snapshot after static TF is published.
- A git commit after S11 acceptance.

The S11 execution templates, operator guide, measurement notes, static TF plan,
accepted RViz screenshot, and post-TF ROS snapshot now exist. The current
baseline is a first engineering baseline accepted by RViz visual validation and
ROS read-only feedback, not a high-precision external calibration.

## Coordinate Convention

Define a shared frame named `lab_world`.

Accepted convention:

- `lab_world` origin: Arm A base center projected onto the tabletop.
- `lab_world +X`: from Arm A base center toward Arm B base center.
- `lab_world +Y`: left direction when facing +X.
- `lab_world +Z`: up, opposite gravity.
- `arm_a/base_link` and `arm_b/base_link`: keep the robot-local frames from the
  ROS model. Runtime S11 static TF is published to `arm_a/world` and
  `arm_b/world`, because the URDF already contains a fixed `world -> base_link`
  joint.

## Measurement Requirements

For each arm, record:

- Translation from `lab_world` to `base_link`: `x`, `y`, `z` in meters.
- Rotation from `lab_world` to `base_link`: roll, pitch, yaw in radians or
  degrees, with units stated.
- Measurement method: tape measure, caliper, fixture CAD, camera calibration,
  or another method.
- Estimated uncertainty.
- Photos showing the measurement references.
- Date, operator, and git commit.

Minimum target for a refined baseline:

- Translation measured to within about `5 mm`.
- Yaw measured to within about `1 deg`.
- Roll/pitch recorded as `0` only if the table mounting is physically level
  enough for the current experiments and the assumption is stated.

S11 accepted the first engineering baseline with operator-provided `260 mm`
Arm A-to-Arm B spacing and visual RViz validation. The exact measurement tool
and uncertainty were not quantified; this limitation is documented and must be
revisited before high-precision bimanual manipulation.

## Static TF Plan

After measurement, publish the external transform to each namespaced URDF root:

- `lab_world -> arm_a/world`
- `lab_world -> arm_b/world`

Use static transforms only after values are measured and reviewed.

Accepted S11 values:

```text
lab_world -> arm_a/world:
  x=0.000, y=0.000, z=0.000, roll=0, pitch=-1.5707963, yaw=0

lab_world -> arm_b/world:
  x=0.260, y=0.000, z=0.000, roll=3.1415926, pitch=-1.5707963, yaw=0
```

Example command shape:

```bash
ros2 run tf2_ros static_transform_publisher \
  --x <x_a> --y <y_a> --z <z_a> \
  --roll <roll_a> --pitch <pitch_a> --yaw <yaw_a> \
  --frame-id lab_world \
  --child-frame-id arm_a/world
```

Repeat for Arm B. Do not copy placeholder values into runtime scripts.

## ROS Read-Only Validation

Before publishing static TF:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

After static TF is published:

```bash
NERO_CONTAINER_NAME=nero-humble-s11-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Additional checks:

- `ros2 topic list` includes both `/arm_a/...` and `/arm_b/...` feedback topics.
- `/arm_a/feedback/joint_states` and `/arm_b/feedback/joint_states` are about
  `200 Hz`.
- A/B `err_status: 0`.
- All joint angle limits are `false`.
- All joint communication statuses are `false`.
- RViz shows the two arms in the measured relative layout.

## Logging Baseline

S11 must define the logging format before S12/S13 motion tests.

Recommended directory pattern:

```text
docs/experiment_runs/YYYYMMDD_HHMMSS_<phase>_<short_label>/
```

Each run directory should contain:

- `README.md`: purpose, operator, git commit, command list, result.
- `snapshot/`: ROS read-only snapshot or links to snapshot paths.
- `rosbag/`: bag files when used.
- `web/`: Web screenshots when configuration matters.
- `notes.md`: observations, deviations, and safety notes.

Minimum rosbag topics for later motion tests:

- `/arm_a/feedback/joint_states`
- `/arm_a/feedback/tcp_pose`
- `/arm_a/feedback/arm_status`
- `/arm_b/feedback/joint_states`
- `/arm_b/feedback/tcp_pose`
- `/arm_b/feedback/arm_status`
- `/tf`
- `/tf_static`

## S11 Acceptance Criteria

S11 passes only if:

- `lab_world` convention is documented.
- `lab_world -> arm_a/world` is measured/derived from the base convention,
  recorded, and accepted for RViz/model validation.
- `lab_world -> arm_b/world` is measured/derived from the base convention,
  recorded, and accepted for RViz/model validation.
- Static TF plan is documented and values are not placeholders.
- RViz visual layout matches the physical base relationship.
- A read-only snapshot after TF publication is clean for both arms.
- Logging and rosbag conventions are documented.
- Next phase S12 control-isolation tests can be run without inventing file
  paths, naming rules, or coordinate assumptions.

## Accepted Evidence

- Measurement notes: `docs/phases/s11_measurement_notes.md`.
- Static TF plan: `docs/phases/s11_static_tf_plan.md`.
- RViz accepted screenshot:
  `docs/evidence/pics/S11_RViz_accepted_dual_arm_layout.png`.
- Post-TF read-only snapshot:
  `docs/evidence/ros_snapshots/20260626_055339/`.
- Snapshot result: `Failed capture commands: 0`; A/B joint-state feedback about
  `200 Hz`; A/B `err_status: 0`; all joint-limit and joint-communication flags
  `false`.
- X11 cleanup: `xhost` reported access control enabled and only
  `SI:localuser:lv-robotics`.

## Deferred Until Later

- Dual-arm coordinated motion.
- Cartesian motion.
- MoveIt execution.
- Dexterous-hand installation and actuation.
- Manipulation algorithms.
- Intentional emergency-stop recovery.
