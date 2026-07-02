# S15 Arm B Command-Path Probe Result

Date: 2026-07-02

## Goal

Verify that the current active ROS command path can move Arm B before retrying
the wide S15 left-side coordinated sequence.

## Procedure

Recommended commands:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-b-probe \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --target arm_b \
      --joint joint1 \
      --delta-deg 2
```

```bash
NERO_CONTAINER_NAME=nero-humble-s15-b-probe \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --execute \
      --target arm_b \
      --joint joint1 \
      --delta-deg 2
```

## Operator Result

The operator reported that the probe passed.

Detailed terminal output was not provided in this turn. The accepted result is
therefore recorded from operator observation and should be supplemented later if
the exact numeric output is needed.

## Acceptance

S15 Arm B small ROS command-path probe is accepted by operator report.

This confirms that, in the current session, the active ROS driver can execute a
small Arm B command. It reduces the likelihood that the S15 left execute timeout
was caused by message format or a broken `/arm_b/control/move_j` path.

## Interpretation

The earlier S15 left execute no-motion timeout was likely caused by the arm not
being fully enabled at the time of the wide sequence attempt, especially if Web
enable was changed between that attempt and the later diagnostics.

## Next Gate

Retry S15 left-side execute only if:

- active observation is running;
- RViz is visible and following correctly;
- Arm B sweep volume remains clear;
- left-hand closing volume is clear;
- J6/J7 cable slack is still acceptable;
- operator can stop the robot immediately if unexpected motion occurs.
