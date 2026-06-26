# S11 Static TF Plan

Status: candidate values prepared; awaiting ROS/RViz validation.

This document records how to publish the measured dual-arm base transforms for
S11. Do not put placeholder values into runtime scripts.

## Frames

| Parent frame | Child frame | Source |
| --- | --- | --- |
| `lab_world` | `arm_a/base_link` | `docs/s11_measurement_notes.md` |
| `lab_world` | `arm_b/base_link` | `docs/s11_measurement_notes.md` |

## Command Shape

Use the measured values from `docs/s11_measurement_notes.md`.

Arm A:

```bash
ros2 run tf2_ros static_transform_publisher \
  --x <arm_a_x_m> --y <arm_a_y_m> --z <arm_a_z_m> \
  --roll <arm_a_roll> --pitch <arm_a_pitch> --yaw <arm_a_yaw> \
  --frame-id lab_world \
  --child-frame-id arm_a/base_link
```

Arm B:

```bash
ros2 run tf2_ros static_transform_publisher \
  --x <arm_b_x_m> --y <arm_b_y_m> --z <arm_b_z_m> \
  --roll <arm_b_roll> --pitch <arm_b_pitch> --yaw <arm_b_yaw> \
  --frame-id lab_world \
  --child-frame-id arm_b/base_link
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
   ros2 run tf2_ros tf2_echo lab_world arm_a/base_link
   ros2 run tf2_ros tf2_echo lab_world arm_b/base_link
   ```

4. Open RViz and verify that the two arms appear in the same relative layout as
   the physical installation.

5. Capture the post-TF read-only snapshot:

   ```bash
   NERO_CONTAINER_NAME=nero-humble-s11-snapshot \
     bash scripts/run_humble_container.sh \
       bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
   ```

## Acceptance

- [ ] Static TF uses measured values, not placeholders.
- [ ] `tf2_echo` returns both transforms.
- [ ] RViz relative layout matches the physical base relationship.
- [ ] Post-TF read-only snapshot is clean for both arms.
- [ ] Transform values are copied back into this document after acceptance.

## Accepted Values

Candidate values for the first RViz validation:

```text
lab_world -> arm_a/base_link:
  x=0.000, y=0.000, z=0.000, roll=0, pitch=0, yaw=0

lab_world -> arm_b/base_link:
  x=0.260, y=0.000, z=0.000, roll=0, pitch=0, yaw=3.1415926
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
  --roll 0 --pitch 0 --yaw 0 \
  --frame-id lab_world \
  --child-frame-id arm_a/base_link
```

```bash
ros2 run tf2_ros static_transform_publisher \
  --x 0.260 --y 0.000 --z 0.000 \
  --roll 0 --pitch 0 --yaw 3.1415926 \
  --frame-id lab_world \
  --child-frame-id arm_b/base_link
```

The Arm B yaw is a candidate inferred from the operator's Web-frame observation.
If RViz shows the two arms with a 180 deg error or another clear mismatch,
correct this value and record the correction in `docs/s11_measurement_notes.md`.

Avoid splitting an option from its value or child frame when copy/pasting manual
commands. For example, `--yaw 3.1415926` and
`--child-frame-id arm_b/base_link` must remain intact; otherwise
`static_transform_publisher` will fail before publishing TF.

Accepted values, to be filled only after RViz validation:

```text
lab_world -> arm_a/base_link: TBD
lab_world -> arm_b/base_link: TBD
```
