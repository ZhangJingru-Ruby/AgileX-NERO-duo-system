# S12 Control Isolation And Logging Plan

Status: accepted / closed on 2026-06-26.

S12 verifies that the two NERO arms can be controlled independently without
cross-control. This is still not dual-arm coordination: only one arm receives a
motion command at a time, while the other arm is monitored read-only.

## Acceptance View

An evaluator should be able to answer:

- Which arm was commanded?
- Which CAN interface and ROS namespace accepted the command?
- Did the other arm remain still within tolerance?
- Are command, feedback, status, snapshot, and git evidence tied together?
- If the test fails, can we tell whether the issue is namespace, CAN mapping,
  control gate, script logic, or physical robot behavior?

## Motion Choice

The operator requested a visible J1 motion toward `lab_world -Y`, with a
nominal amplitude of `30 deg`, and reported that the surrounding area is clear.

Accepted S12 first-test target:

| Test | Target arm | Commanded joint | Delta | Intended world motion |
| --- | --- | --- | --- | --- |
| S12.1 | Arm A | `joint1` | `+30 deg` | approximately toward `lab_world -Y` |
| S12.2 | Arm B | `joint1` | `-30 deg` | approximately toward `lab_world -Y` |

Basis:

- URDF: `joint1` axis is local `Z`.
- Accepted S11 TF maps Arm A local `Z` approximately to `lab_world -X`.
- Accepted S11 TF maps Arm B local `Z` approximately to `lab_world +X`.
- With the current hanging posture, positive J1 on Arm A and negative J1 on
  Arm B are the predicted signs for the same visible `-Y` sweep direction.

This is an inferred sign convention, not a substitute for observation. If the
first dry-run or small sign check indicates the sweep direction is wrong, stop
and correct the sign before using the `30 deg` acceptance move.

## Safety Gate

Before any `--execute`:

- S11 is accepted and the base layout has not moved.
- Workspace and the full J1 swept area are clear.
- Cable slack is checked for a `30 deg` J1 sweep and return.
- One operator is assigned to Web emergency stop or physical power cutoff.
- No Web/SDK/manual motion command is active.
- No S11 RViz/static-TF or old ROS control terminal is accidentally running,
  unless it is intentionally part of the monitoring setup.
- Both CAN interfaces are UP and mapped as:
  - Arm A: `can_arm_a`
  - Arm B: `can_arm_b`
- Use `speed_percent=5` for the first S12 tests. Do not exceed `10` without a
  separate route update.

## Driver Topology

Use one active control driver and one passive read-only driver:

- Active target arm:
  - `auto_enable:=true`
  - `control_enabled:=true`
- Passive monitored arm:
  - `auto_enable:=false`
  - `control_enabled:=false`

Use the wrapper:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-arm-a \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/launch_s12_isolation_pair.sh arm_a
```

For Arm B:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-arm-b \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/launch_s12_isolation_pair.sh arm_b
```

The wrapper does not publish motion commands.

## S12.1 Arm A Procedure

Terminal 0, audit before starting:

```bash
bash scripts/s10_control_source_audit.sh
```

Terminal 1, start Arm A active / Arm B passive:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-arm-a \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/launch_s12_isolation_pair.sh arm_a
```

Terminal 2, dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --target arm_a \
      --joint joint1 \
      --delta-deg 30
```

Expected dry-run:

- Target is `/arm_a/control/move_j`.
- Only Arm A `joint1` changes in the target vector.
- Arm B current joint vector is printed for passive monitoring.
- No motion occurs.

Execute only after the dry-run target and direction are accepted:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --execute \
      --target arm_a \
      --joint joint1 \
      --delta-deg 30
```

Actual execution result on 2026-06-26:

- Operator reported the observed Arm A motion matched the expected direction.
- Arm B did not visibly move.
- Arm A target: `joint1 1.109 deg -> 31.109 deg`.
- Arm A after step: `joint1 30.490 deg`, target error about `0.619 deg`.
- Arm A after return: `joint1 1.704 deg`, return error about `0.595 deg`.
- Passive Arm B maximum deviation: `0.005 deg`.
- Final A/B `err_status: 0`.
- Post-motion read-only snapshot:
  `docs/evidence/ros_snapshots/20260626_080809/`.
- Snapshot result: `Failed capture commands: 0`, A/B joint-state feedback
  about `200 Hz`, A/B `err_status: 0`, all joint-limit flags `false`, and all
  joint-communication flags `false`.
- S12.1 Arm A is accepted.

## S12.2 Arm B Procedure

Stop the Arm A active driver terminal first. Then audit if anything looks
unclear.

Terminal 1, start Arm B active / Arm A passive:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-arm-b \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/launch_s12_isolation_pair.sh arm_b
```

Terminal 2, dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --target arm_b \
      --joint joint1 \
      --delta-deg -30
```

Actual dry-run result on 2026-06-26:

- Target arm: Arm B.
- Passive arm: Arm A.
- `execute=False`, so no motion command was published.
- Arm B target: `joint1 -1.988 deg -> -31.988 deg`.
- Arm A passive current joint vector was printed for monitoring.
- Target status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=1`, `err_status=0`.
- Passive status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`, `err_status=0`.
- S12.2 Arm B dry-run was accepted; the later execution and post-motion
  snapshot also passed.

Actual execution result on 2026-06-26:

- Operator reported the observed Arm B motion matched expectation.
- Arm A did not visibly move.
- Arm B target: `joint1 -1.988 deg -> -31.988 deg`.
- Arm B after step: `joint1 -31.398 deg`, target error about `0.590 deg`.
- Arm B after return: `joint1 -2.583 deg`, return error about `0.595 deg`.
- Passive Arm A maximum deviation: `0.008 deg`.
- Final A/B `err_status: 0`.
- Post-motion read-only snapshot:
  `docs/evidence/ros_snapshots/20260626_083210/`.
- Snapshot result: `Failed capture commands: 0`, A/B joint-state feedback
  about `200 Hz`, A/B `err_status: 0`, all joint-limit flags `false`, and all
  joint-communication flags `false`.
- S12.2 Arm B is accepted.

Execute only after the dry-run target and direction are accepted:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s12_isolation_step.py \
      --execute \
      --target arm_b \
      --joint joint1 \
      --delta-deg -30
```

## Optional Sign Gate

If the operator is not fully confident that the predicted sign moves toward
`lab_world -Y`, run the same procedure with `5 deg` first:

- Arm A sign check: `--delta-deg 5`
- Arm B sign check: `--delta-deg -5`

If the direction is wrong, stop and reverse the sign before any `30 deg` move.

## Snapshot And Evidence

After each executed test, stop the S12 driver pair and capture a read-only
snapshot:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

In another terminal:

```bash
NERO_CONTAINER_NAME=nero-humble-s12-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Save the terminal output from the S12 tool. It should include:

- `target_current_deg`
- `target_goal_deg`
- `passive_current_deg`
- `after_step_target_deg`
- `after_step_passive_deg`
- `after_return_target_deg`
- `after_return_passive_deg`
- `max_passive_dev_total_deg`
- final target/passive arm statuses

## Acceptance Criteria

S12.1 or S12.2 passes only if:

- Target arm reaches the commanded J1 target within `0.7 deg`.
- Target arm returns to the original J1 angle within `0.7 deg`.
- Passive arm maximum joint deviation remains within `1.0 deg` during move and
  return.
- No non-target control command is published.
- A/B `err_status: 0`.
- All A/B joint-limit flags are `false`.
- All A/B joint-communication flags are `false`.
- Post-test read-only snapshot has `Failed capture commands: 0`.
- Operator reports no abnormal sound, cable tension, Web warning, or physical
  interference.

## Accepted Evidence

- Arm A dry-run commit: `c6a92eb`.
- Arm A execution commit: `3e4e2a0`.
- Arm A post-motion snapshot:
  `docs/evidence/ros_snapshots/20260626_080809/`.
- Arm B dry-run commit: `19e007e`.
- Arm B execution commit: `64fe5a4`.
- Arm B post-motion snapshot:
  `docs/evidence/ros_snapshots/20260626_083210/`.
- S12 did not record rosbag files. The accepted evidence set is terminal output
  captured in `docs/status/deployment_log.md`, read-only snapshots, configuration
  records, and git commits.
- Intentional emergency-stop testing was not performed in S12; stop-condition
  and recovery-record formats are documented here for future tests.

## Stop Conditions

Stop immediately if:

- Dry-run target changes any joint other than the selected `joint1`.
- The observed direction is not the intended direction.
- The passive arm visibly moves.
- `ros_s12_isolation_step.py` reports passive movement above tolerance.
- Any cable becomes taut.
- Any object or person enters the swept area.
- ROS driver logs firmware/readiness/control-gate errors.
- Web or ROS status shows a non-zero error flag.
