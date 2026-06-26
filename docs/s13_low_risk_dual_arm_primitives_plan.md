# S13 Low-Risk Dual-Arm Primitives Plan

Status: prepared for field execution.

S13 starts the minimum dual-arm primitive layer after S12 proved control
isolation. This phase still does not authorize Cartesian motion, MoveIt
execution, manipulation, contact, handoff, dexterous-hand actuation, or
close-proximity bimanual tasks.

## Acceptance View

An evaluator should be able to answer:

- Can both ROS control drivers be active at the same time without immediate
  drift or errors?
- Can both arms receive a bounded joint-space command in one test and return?
- Did only the commanded joint move materially on each arm?
- Did A/B status remain healthy through the test?
- Is the evidence tied to commands, feedback, snapshots, and git commits?

## First Primitive

Use the same visible J1 magnitude requested by the operator and accepted in
S12:

| Arm | Joint | Delta | Rationale |
| --- | --- | --- | --- |
| Arm A | `joint1` | `+30 deg` | Accepted in S12; visible direction matched expectation |
| Arm B | `joint1` | `-30 deg` | Accepted in S12; visible direction matched expectation |

The intended first primitive is a low-risk, non-contact, same-direction
world-frame sweep. The two arms are not commanded to approach each other.

## Safety Gate

Before any `--execute`:

- S12 is accepted and closed.
- Both bases and the S11 `lab_world` baseline are unchanged.
- The full swept area for both J1 motions is clear at the same time.
- Cable slack is checked for both arms during simultaneous motion and return.
- One operator is assigned to Web emergency stop or physical power cutoff.
- No Web/SDK/manual motion command is active.
- Stop old S12/S11 driver or RViz terminals unless they are intentionally part
  of monitoring.
- Use `speed_percent=5` for the first S13 test. Do not exceed `10` without a
  separate route update.

## Driver Topology

S13 uses two active control drivers:

- Arm A: `auto_enable:=true`, `control_enabled:=true`.
- Arm B: `auto_enable:=true`, `control_enabled:=true`.

Start them with:

```bash
NERO_CONTAINER_NAME=nero-humble-s13-dual-active \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/launch_s13_dual_active_pair.sh
```

The wrapper does not publish motion commands.

## Dry-Run And Hold Check

Dry-run also monitors a short hold period with both drivers active:

```bash
NERO_CONTAINER_NAME=nero-humble-s13-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s13_dual_joint_step.py \
      --joint joint1 \
      --arm-a-delta-deg 30 \
      --arm-b-delta-deg -30
```

Expected dry-run:

- Both current joint vectors are printed.
- Both target vectors are printed.
- Only Arm A `joint1` changes by `+30 deg`.
- Only Arm B `joint1` changes by `-30 deg`.
- `hold_max_dev_deg` stays within `1.0 deg` for both arms.
- No motion command is published.

## Execution

Execute only after dry-run and hold check are accepted:

```bash
NERO_CONTAINER_NAME=nero-humble-s13-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s13_dual_joint_step.py \
      --execute \
      --joint joint1 \
      --arm-a-delta-deg 30 \
      --arm-b-delta-deg -30
```

Expected execution:

- Both arms move in joint-space and return to their original joint angles.
- Target joint errors are within `0.7 deg`.
- Non-target joint deviations stay within `1.0 deg`.
- A/B final `err_status: 0`.
- Operator reports no cable tension, abnormal sound, Web warning, or physical
  interference.

## Post-Motion Snapshot

After execution, stop the S13 driver pair and capture the dual-arm read-only
snapshot:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

In another terminal:

```bash
NERO_CONTAINER_NAME=nero-humble-s13-post-snapshot \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/snapshot_ros_readonly_state.sh
```

Acceptance:

- Snapshot has `Failed capture commands: 0`.
- A/B joint-state feedback is about `200 Hz`.
- A/B `err_status: 0`.
- A/B joint-limit flags are all `false`.
- A/B joint-communication flags are all `false`.

## Stop Conditions

Stop immediately if:

- Dry-run target changes any joint other than `joint1`.
- Either arm moves during dry-run or hold check.
- Observed simultaneous motion is not the intended low-risk sweep.
- Non-target joints exceed tolerance.
- Any cable becomes taut.
- Any object or person enters either swept area.
- ROS driver logs firmware/readiness/control-gate errors.
- Web or ROS status shows a non-zero error flag.
