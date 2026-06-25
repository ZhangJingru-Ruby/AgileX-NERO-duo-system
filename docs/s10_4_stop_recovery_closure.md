# S10.4 Stop / Recovery / Control-Source Closure

Status: accepted for no-motion control-source closure on 2026-06-25.

S10.1 Web motion, S10.2 SDK motion, and S10.3 ROS motion have passed on Arm A.
S10.4 closes the Arm A control path before repeating the same ladder on Arm B.

## Scope

This is a no-motion closure step.

- Stop or account for every active control source.
- Leave the system in a known read-only or stopped state.
- Preserve the last accepted evidence.
- Record the handoff state before Arm B motion.

S10.4 does not intentionally trigger emergency stop, power cut, Cartesian motion,
MoveIt execution, MIT/JS control, raw CAN motion, dual-arm coordination, or
dexterous-hand actuation.

## Recommended Handoff State

Use `handoff_to_arm_b` before Arm B first-motion replication:

- Arm A and Arm B remain powered and stable.
- No Web motion command is active.
- No SDK motion script is running.
- No ROS motion/control script is running.
- CAN interfaces may remain UP.
- A dual-arm read-only driver may run only for monitoring. Stop it before Arm B
  Web/SDK/ROS motion so the next step again has one deliberate control source.

## Procedure

1. Stop any Arm A ROS control driver left from S10.3 with `Ctrl-C`.
2. Confirm the ROS control driver exits cleanly.
3. If a dual-arm read-only driver is still running and monitoring is complete,
   stop it with `Ctrl-C`. If it remains running, label it explicitly as
   read-only monitoring.
4. Run:

   ```bash
   bash scripts/s10_control_source_audit.sh
   ```

5. Confirm the audit shows no Arm A ROS control container, no SDK motion script,
   and no Web command in progress.
6. Keep the last accepted snapshot as evidence:
   `docs/s9_ros_snapshots/20260625_064243/`.
7. Record the next state as one of:
   `handoff_to_arm_b`, `monitor_readonly`, or `shutdown`.

Optional final read-only snapshot, only if the dual-arm read-only driver state
needs fresh evidence:

```bash
NERO_CONTAINER_NAME=nero-humble-s10-closure-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

## Acceptance Criteria

- Arm A ROS control driver is stopped.
- No SDK or ROS motion script is running.
- Web has no active motion command.
- The next handoff state is recorded.
- The latest accepted snapshot path is recorded.
- The operator can state which control source, if any, is active.

## Codex-Session Check On 2026-06-25

The audit script passed `bash -n` and was run once from the Codex session. That
session reported:

- `can_arm_a`: not visible
- `can_arm_b`: not visible
- Docker status: unavailable without interactive sudo
- NERO-related host processes: none

Because the CAN interfaces were not visible in this session, this result does
not replace the required live desktop-terminal audit before Arm B motion.

Saved output: `docs/s10_4_control_source_audit_codex_20260625_150052.txt`.

## Live Desktop-Terminal Audit On 2026-06-25

Saved output: `docs/s10_4_control_source_audit_live_20260625_150438.txt`.

Result:

- `can_arm_a`: visible, UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- `can_arm_b`: visible, UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- NERO-related Docker containers: none.
- NERO-related host processes: none.

Acceptance:

- S10.4 no-motion control-source closure is accepted.
- Recommended handoff state is `handoff_to_arm_b`.
- Before Arm B Web/SDK/ROS motion, keep the rule that only one deliberate
  control source is active.

## Deferred Tests

- Intentional emergency-stop recovery.
- Power-cut recovery.
- Arm B parity motion.
- Dual-arm coordinated motion.
- Cartesian and MoveIt execution.
- Dexterous-hand installation and actuation.
