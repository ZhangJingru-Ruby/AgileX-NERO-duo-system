# S15 Motion-Block Diagnostics Result

Date: 2026-07-02

## Command

```bash
NERO_CONTAINER_NAME=nero-humble-s15-diagnostics \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/s15_motion_block_diagnostics.sh
```

## Result Summary

The diagnostics showed that the ROS graph is present and healthy:

- Nodes include both arm drivers:
  - `/arm_a/agx_arm_ctrl_single_node`
  - `/arm_b/agx_arm_ctrl_single_node`
- `/arm_a/control/move_j` has one subscriber from
  `/arm_a/agx_arm_ctrl_single_node`.
- `/arm_b/control/move_j` has one subscriber from
  `/arm_b/agx_arm_ctrl_single_node`.
- `/arm_a/feedback/joint_states` and `/arm_b/feedback/joint_states` each have
  one publisher from the corresponding arm driver.
- Feedback subscriptions are currently from `s15_joint_state_visual_anchor`,
  which matches the accepted anchored RViz observation topology.
- Arm A and Arm B status are normal:
  - `ctrl_mode=1`
  - `arm_status=0`
  - `mode_feedback=1`
  - `motion_status=0`
  - `err_status=0`
  - all joint-limit flags false
  - all joint communication flags false

## Interpretation

This excludes a missing ROS command subscriber as the immediate cause of the
previous S15 left execute timeout.

However, this does not yet prove the current driver was launched in active
control mode. The read-only driver also creates `/control/move_j` subscribers,
but it is started with:

```text
auto_enable=false
control_enabled=false
```

The active driver should be started with:

```text
auto_enable=true
control_enabled=true
```

Therefore the next diagnostic must confirm the driver parameters, not only the
topic graph.

## Code Update

`scripts/s15_motion_block_diagnostics.sh` now prints driver parameters for both
arms:

- `can_port`
- `arm_type`
- `auto_enable`
- `control_enabled`
- `speed_percent`
- `enable_timeout`

## Next Gate

Rerun `scripts/s15_motion_block_diagnostics.sh` with the updated script while
the S15 observation terminal is active. Before any execute retry, confirm:

- `/arm_b/control/move_j` has one subscriber;
- `/arm_b/agx_arm_ctrl_single_node` reports `control_enabled=true`;
- `/arm_b/agx_arm_ctrl_single_node` reports `auto_enable=true`;
- Arm B status remains `err_status=0`, no joint-limit flags, and no
  communication flags.
