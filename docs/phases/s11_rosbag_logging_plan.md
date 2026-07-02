# S11 ROS Bag And Experiment Logging Plan

Status: logging rules accepted for S11; first rosbag motion run deferred to S12.

S11 defines the directory and topic rules that later S12/S13 motion tests must
use. The goal is that a failed manipulation experiment can be traced back to
commands, feedback, robot state, TF, and git commit.

## Run Directory

Recommended pattern:

```text
docs/experiment_runs/YYYYMMDD_HHMMSS_<phase>_<short_label>/
```

Example for the first S11 TF validation:

```text
docs/experiment_runs/20260625_HHMMSS_s11_static_tf_validation/
```

Each run directory should contain:

```text
README.md
snapshot/
rosbag/
web/
notes.md
```

## Run README Fields

Each `README.md` should record:

- Date/time.
- Operator.
- Git commit.
- Phase and short label.
- Safety state.
- Commands run.
- ROS topics recorded.
- Snapshot path.
- Web screenshot path if relevant.
- Result.
- Deviations or anomalies.

## Minimum ROS Topics

Record these topics for later motion tests unless the run is explicitly
read-only and the reason is documented:

```text
/arm_a/feedback/joint_states
/arm_a/feedback/tcp_pose
/arm_a/feedback/arm_status
/arm_b/feedback/joint_states
/arm_b/feedback/tcp_pose
/arm_b/feedback/arm_status
/tf
/tf_static
```

## rosbag Command Shape

Use from inside the Humble ROS environment after the relevant nodes are running:

```bash
ros2 bag record \
  -o docs/experiment_runs/<run_id>/rosbag/s11_static_tf_validation \
  /arm_a/feedback/joint_states \
  /arm_a/feedback/tcp_pose \
  /arm_a/feedback/arm_status \
  /arm_b/feedback/joint_states \
  /arm_b/feedback/tcp_pose \
  /arm_b/feedback/arm_status \
  /tf \
  /tf_static
```

If the output path is inside the container, mount or copy it back into this
repository before acceptance.

## Acceptance

- [x] Directory pattern is defined.
- [x] Run README fields are defined.
- [x] Minimum ROS topics are defined for later motion tests.
- [x] S11 read-only snapshot is saved:
  `docs/evidence/ros_snapshots/20260626_055339/`.
- [ ] First full experiment run directory with rosbag is deferred to S12, where
  motion/control-isolation tests require it.
