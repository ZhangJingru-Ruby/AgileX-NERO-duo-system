# S11 Static TF Plan

Status: static TF values accepted by RViz visual validation; final post-TF snapshot pending.

This document records how to publish the measured dual-arm base transforms for
S11. Do not put placeholder values into runtime scripts.

## Frames

| Parent frame | Child frame | Source |
| --- | --- | --- |
| `lab_world` | `arm_a/world` | `docs/s11_measurement_notes.md` |
| `lab_world` | `arm_b/world` | `docs/s11_measurement_notes.md` |

The measured values describe each base pose. For RViz/model validation, publish
the external static transform to each namespaced URDF root frame
`arm_*/world`, because the NERO URDF already contains a fixed
`world -> base_link` joint. Publishing directly to `arm_*/base_link` can create
a duplicate parent once `robot_state_publisher` is running.

## Command Shape

Use the measured values from `docs/s11_measurement_notes.md`.

Arm A:

```bash
ros2 run tf2_ros static_transform_publisher \
  --x <arm_a_x_m> --y <arm_a_y_m> --z <arm_a_z_m> \
  --roll <arm_a_roll> --pitch <arm_a_pitch> --yaw <arm_a_yaw> \
  --frame-id lab_world \
  --child-frame-id arm_a/world
```

Arm B:

```bash
ros2 run tf2_ros static_transform_publisher \
  --x <arm_b_x_m> --y <arm_b_y_m> --z <arm_b_z_m> \
  --roll <arm_b_roll> --pitch <arm_b_pitch> --yaw <arm_b_yaw> \
  --frame-id lab_world \
  --child-frame-id arm_b/world
```

## Validation Procedure

1. Start the dual-arm ROS read-only driver:

   ```bash
   bash scripts/run_humble_container.sh \
     bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
   ```

2. Publish the two static transforms in the ROS environment.

   Preferred wrapper, used to avoid copy/paste line-break errors:

   ```bash
   NERO_CONTAINER_NAME=nero-humble-s11-static-tf \
     bash scripts/run_humble_container.sh \
       bash /workspace/nero/scripts/publish_s11_static_tf_candidate.sh
   ```

3. Verify TF:

   ```bash
   ros2 run tf2_ros tf2_echo lab_world arm_a/world
   ros2 run tf2_ros tf2_echo lab_world arm_b/world
   ros2 run tf2_ros tf2_echo lab_world arm_a/base_link
   ros2 run tf2_ros tf2_echo lab_world arm_b/base_link
   ```

4. Open RViz and verify that the two arms appear in the same relative layout as
   the physical installation.

   Preferred S11 model-view wrapper:

   ```bash
   NERO_CONTAINER_NAME=nero-humble-s11-rviz \
     bash scripts/run_humble_container.sh --allow-xhost \
       bash /workspace/nero/scripts/launch_s11_dual_model_view.sh
   ```

   This starts two `robot_state_publisher` processes, one for `/arm_a` and one
   for `/arm_b`, and opens RViz with fixed frame `lab_world`. It subscribes to
   feedback joint states only and does not publish control commands.

5. Capture the post-TF read-only snapshot:

   ```bash
   NERO_CONTAINER_NAME=nero-humble-s11-snapshot \
     bash scripts/run_humble_container.sh \
       bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
   ```

## Acceptance

- [x] Static TF uses measured values, not placeholders.
- [x] `tf2_echo` returns the static transform values.
- [x] RViz relative layout matches the physical base relationship by operator report.
- [ ] Post-TF read-only snapshot is clean for both arms.
- [x] Transform values are copied back into this document after acceptance.

## Accepted Values

Candidate values for the first RViz validation:

```text
lab_world -> arm_a/world:
  x=0.000, y=0.000, z=0.000, roll=0, pitch=-1.5707963, yaw=0

lab_world -> arm_b/world:
  x=0.260, y=0.000, z=0.000, roll=3.1415926, pitch=-1.5707963, yaw=0
```

Candidate commands:

Preferred:

```bash
NERO_CONTAINER_NAME=nero-humble-s11-static-tf \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/publish_s11_static_tf_candidate.sh
```

Manual commands, if running directly inside a ROS environment:

```bash
ros2 run tf2_ros static_transform_publisher \
  --x 0.000 --y 0.000 --z 0.000 \
  --roll 0 --pitch -1.5707963 --yaw 0 \
  --frame-id lab_world \
  --child-frame-id arm_a/world
```

```bash
ros2 run tf2_ros static_transform_publisher \
  --x 0.260 --y 0.000 --z 0.000 \
  --roll 3.1415926 --pitch -1.5707963 --yaw 0 \
  --frame-id lab_world \
  --child-frame-id arm_b/world
```

The first pure-yaw candidate published successfully but did not match the
physical layout in RViz. The revised candidate uses the operator's Web-frame
axis observation to rotate both arm roots into `lab_world`. If RViz still shows
a clear mismatch, correct these root rotations and record the correction in
`docs/s11_measurement_notes.md`.

Avoid splitting an option from its value or child frame when copy/pasting manual
commands. For example, `--pitch -1.5707963` and
`--child-frame-id arm_b/world` must remain intact; otherwise
`static_transform_publisher` will fail before publishing TF.

Accepted S11 values:

```text
lab_world -> arm_a/world:
  x=0.000, y=0.000, z=0.000, roll=0, pitch=-1.5707963, yaw=0

lab_world -> arm_b/world:
  x=0.260, y=0.000, z=0.000, roll=3.1415926, pitch=-1.5707963, yaw=0
```
