# S13 Low-Risk Dual-Arm Primitives Plan

Status: corrected direction-sign dry-run accepted; corrected execution pending.

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
S12. The first S13 command intentionally tested the local joint-space signs from
S12 under simultaneous control:

| Arm | Joint | Delta | Rationale |
| --- | --- | --- | --- |
| Arm A | `joint1` | `+30 deg` | Accepted in S12; visible direction matched expectation |
| Arm B | `joint1` | `-30 deg` | Accepted in S12; visible direction matched expectation |

The intended first primitive is a low-risk, non-contact sweep with an
operator-visible world-frame direction criterion. The two arms are not
commanded to approach each other. Local joint signs do not by themselves prove
the visible world-frame direction; the direction must be accepted by operator
observation.

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

Actual dry-run and hold result on 2026-06-26:

- `execute=False`, so no motion command was published.
- Arm A current: `joint1=1.111 deg`.
- Arm A target: `joint1=31.111 deg`; only `joint1` changes by `+30 deg`.
- Arm B current: `joint1=-1.988 deg`.
- Arm B target: `joint1=-31.988 deg`; only `joint1` changes by `-30 deg`.
- Arm A status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`, `err_status=0`.
- Arm B status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`, `err_status=0`.
- `hold_max_dev_deg={'arm_a': 0.0, 'arm_b': 0.0}`.
- S13 dry-run and hold gate is accepted; execution is pending.

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

Actual execution result on 2026-06-26:

- Command: Arm A `joint1 +30 deg`, Arm B `joint1 -30 deg`.
- Hold before motion remained stable:
  `hold_max_dev_deg={'arm_a': 0.0, 'arm_b': 0.006000000000000263}`.
- Arm A after step: `joint1=30.513 deg`; after return:
  `joint1=1.753 deg`.
- Arm B after step: `joint1=-31.441 deg`; after return:
  `joint1=-2.660 deg`.
- Non-target deviations remained inside tolerance:
  `max_non_target_dev_total_deg={'arm_a': 0.01299999999999951, 'arm_b': 0.00800000000000141}`.
- Final status was healthy on both arms: A/B `ctrl_mode=1`,
  `arm_status=0`, `mode_feedback=1`, `motion_status=0`, `err_status=0`.
- Operator observation: Arm B did not move in the expected opposite visible
  direction; both arms appeared to rotate in the same visible direction.

Result:

- Numeric ROS/CAN joint-space execution passed.
- The intended world-direction semantics did not pass.
- Do not close S13 on this run.
- Do not repeat this exact sign pair as an "opposite direction" primitive.
- Next gate is post-motion read-only snapshot, then a corrected direction-sign
  dry-run before any further simultaneous motion.

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

Actual post-motion snapshot result on 2026-06-26:

- Snapshot: `docs/s9_ros_snapshots/20260626_090214/`.
- `Failed capture commands: 0`.
- Arm A joint-state feedback: about `200 Hz`.
- Arm B joint-state feedback: about `200 Hz`.
- A/B status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`, `err_status=0`.
- A/B joint-limit flags: all `false`.
- A/B joint-communication flags: all `false`.

This snapshot accepts the hardware/ROS health after the failed direction
semantics run. It does not accept the original sign pair as the intended S13
primitive.

## Corrected Direction-Sign Gate

Next dry-run hypothesis:

```bash
NERO_CONTAINER_NAME=nero-humble-s13-tool \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s13_dual_joint_step.py \
      --joint joint1 \
      --arm-a-delta-deg 30 \
      --arm-b-delta-deg 30
```

Expected dry-run:

- No motion command is published.
- Only Arm A `joint1` target changes by `+30 deg`.
- Only Arm B `joint1` target changes by `+30 deg`.
- Hold check remains within tolerance.
- Execute only after the operator accepts this corrected target and reconfirms
  swept areas, cable slack, and emergency stop.

Actual corrected dry-run result on 2026-06-26:

- `execute=False`, so no motion command was published.
- Command hypothesis: Arm A `joint1 +30 deg`, Arm B `joint1 +30 deg`.
- Arm A current: `joint1=1.110 deg`.
- Arm A target: `joint1=31.110 deg`; only `joint1` changes by `+30 deg`.
- Arm B current: `joint1=-1.988 deg`.
- Arm B target: `joint1=28.012 deg`; only `joint1` changes by `+30 deg`.
- Arm A status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`, `err_status=0`.
- Arm B status: `ctrl_mode=1`, `arm_status=0`, `mode_feedback=1`,
  `motion_status=0`, `err_status=0`.
- `hold_max_dev_deg={'arm_a': 0.00799999999999823, 'arm_b': 0.005999999999997082}`.

Result:

- Corrected direction-sign dry-run is accepted.
- The next gate is corrected execution with the same signs, only after the
  operator reconfirms simultaneous swept areas, cable slack, and emergency stop.

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
