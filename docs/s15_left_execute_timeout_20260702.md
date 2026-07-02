# S15 Left Execute Timeout

Date: 2026-07-02

## Command

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

## Observed Result

The script planned the same left-side sequence as the accepted dry-run, then
published waypoint `1/9`.

It timed out waiting for Arm B to reach the first waypoint:

```text
joint1 last=0.82 target=4.07
joint2 last=0.13 target=10.12
joint3 last=101.70 target=93.74
```

The `last` values were still the starting values, so no measurable Arm B motion
occurred after the command publication.

The script then called:

- `arm_a emergency_stop`
- `arm_b emergency_stop`

## Interpretation

This was not a mid-trajectory tracking error. The first command did not produce
observable motion at all.

Most likely causes to inspect:

- S15 observation terminal was not actually in `--active` mode, or a stale
  read-only/control process was still present.
- `/arm_b/control/move_j` had no active driver subscriber at the moment the
  command was published.
- The active-driver terminal logged a command rejection or post-estop state.

The S15 script uses the same `sensor_msgs/JointState` command style as the
previous accepted S12/S13 ROS motion scripts, so the command message format is
not the first suspected cause.

## Safety Assessment

No hand command was sent. The timeout happened before the hand open/close/open
stage.

The script called emergency stop after the timeout. Before retrying any execute,
stop and restart the S15 active observation session so the arms are explicitly
re-enabled and the active-driver logs are visible.

## Code Update

The S15 script now checks active-arm `/control/move_j` subscription counts before
execute. If the command topic has no subscriber, it will fail before publishing a
motion command.

Added diagnostic helper:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-diagnostics \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/s15_motion_block_diagnostics.sh
```

## Next Gate

Do not retry execute immediately.

1. Stop the current S15 active observation terminal.
2. Restart S15 active observation.
3. Run `scripts/s15_motion_block_diagnostics.sh`.
4. Confirm `/arm_b/control/move_j` has a subscriber and Arm B status is normal.
5. Only then decide whether to retry execute or switch to a smaller Arm B
   motion target.
