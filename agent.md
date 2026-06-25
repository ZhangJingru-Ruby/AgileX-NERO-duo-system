# NERO Agent Operating Rules

Last updated: 2026-06-25

This file defines how any agent, operator, or collaborator should continue the
NERO arm deployment work in this repository.

## Core Principle

Be faithful to documents, facts, and observed results.

Do not invent missing hardware facts, software versions, wiring details, launch
arguments, firmware behavior, or safety status. If something is unknown, write it
as unknown and define how it will be verified.

## Source Of Truth Order

Use sources in this order:

1. Local project documents and assets:
   - `docs/机器人部署与调试行动路线.md`
   - `docs/current_bringup_status.md`
   - `docs/bringup_checklist.md`
   - `docs/setup_framework.md`
   - `docs/s2_hybrid_host_container_plan.md`
   - `docs/s9_configuration_review.md`
   - `docs/s11_dual_arm_experiment_baseline.md`
   - `docs/nero 用户手册.md`
   - `docs/机械臂通信协议V1.2.1.xlsx`
   - `docs/pics/`
   - `config/nero.env`
2. Direct observations from this machine:
   - terminal output
   - installed package versions
   - ROS topic output
   - CAN captures
   - Web UI screenshots or user-provided observations
3. Official upstream project sources:
   - `agx_arm_ros`
   - `pyAgxArm`
   - `piper_ros`
   - official AgileX documentation or repositories
4. User-provided现场事实, with date and context recorded.

If two sources conflict, stop and document the conflict before acting. Prefer
the local manual/protocol for hardware facts, and prefer live machine output for
current environment state.

## Upstream Repository Roles

Do not treat the three cloned GitHub repositories as interchangeable. Their
roles are different:

| Repository | Local evidence path | Role | How to use later |
| --- | --- | --- | --- |
| `agilexrobotics/agx_arm_ros` | `upstream/agx_arm_ros` | Main ROS integration and control workspace. It is the current ROS2 path for NERO. | Use for S2B ROS host setup, S3 ROS2 model display, S8 ROS read-only feedback, and later MoveIt/application integration after safety gates. Clone branch `ros2` with submodules in the real ROS workspace. |
| `agilexrobotics/pyAgxArm` | `upstream/pyAgxArm` | Python SDK and hardware access layer over CAN. It is usable without ROS and is also used by the ROS driver. | Use for S2A SDK/CAN-only preparation and S7 read-only status checks. Firmware selector must be chosen from observed robot firmware. Do not use SDK motion APIs before the motion gates. |
| `agilexrobotics/piper_ros` | `upstream/piper_ros` | Reference source for the user-provided NERO URDF path on branch `humble_beta1`. It is a model/description reference, not the current NERO control route. | Use to cross-check NERO model files, meshes, joint naming, and historical URDF differences. Do not make it the default ROS control workspace unless a separate validation plan is written. |

The `agx_arm_ros` submodule `agx_arm_urdf` is the model set used by the current
ROS2 driver. Prefer it for the runtime ROS2 workspace unless a documented model
comparison shows a reason to use the older `piper_ros` description package.

The `upstream/` directory is an evidence cache in this project. Runtime builds
should happen in the selected deployment workspace, normally `~/agx_arm_ws`, on
the selected ROS2 host.

## Phase Discipline

Follow the route in `docs/机器人部署与调试行动路线.md`.

Do not skip phase gates. A later phase may be prepared offline, but it must not
be marked complete until its acceptance criteria are satisfied.

Current phase state is tracked in `docs/current_bringup_status.md`.

## Mandatory Work Cycle

For every deployment step, use this cycle:

1. Read the current status and relevant phase section.
2. State the intended action and why it belongs to the current phase.
3. Execute the smallest useful step.
4. Verify the result with a command, file check, screenshot, CAN capture, ROS
   output, or explicit user现场确认.
5. Record the step in `docs/deployment_log.md`.
6. Update `docs/current_bringup_status.md` if phase status, assumptions,
   blockers, or confirmed configuration changed.
7. Update and correct `docs/机器人部署与调试行动路线.md` after the step:
   - add newly learned facts
   - correct wrong assumptions
   - refine acceptance criteria
   - add safety notes or blockers
   - keep phase ordering consistent
8. Update `config/nero.env`, scripts, or checklists if a deployment choice became
   durable.

The route document must remain a living plan, not a stale plan.

## Documentation Requirements

Every step record must preserve:

- date and phase
- goal
- action taken
- commands or tools used
- key output or observed result
- deployment choice made
- files changed
- verification result
- blockers or residual risk
- next step

Use this minimum format in `docs/deployment_log.md`:

```markdown
## YYYY-MM-DD - Sx.y Short Title

Phase: Sx phase name
Goal:
Action:
Commands / evidence:
Result:
Deployment choices:
Files changed:
Verification:
Route updates:
Open risks:
Next:
```

Do not paste huge logs unless needed. Summarize key lines and point to saved log
files when appropriate.

## Safety Rules

The default state is no motion.

Before any real robot motion:

- S0-S9 must be completed or explicitly scoped for the motion being attempted.
- The base must be physically fixed.
- Only one control source may be active.
- The power cutoff / emergency stop path must be assigned to a person.
- The arm workspace must be clear.
- Feedback must be sane through Web/CAN/SDK/ROS as required by the current phase.

High-risk actions require an explicit route entry and operator confirmation:

- first real robot motion in a new control path
- zero calibration
- firmware upgrade
- MIT control
- master-slave mode
- collision-level changes
- joint limit or max-speed changes
- raw CAN motion commands
- dexterous hand installation and first actuation

## Current Project Defaults

These are the current deployment assumptions. Update them only when verified.

| Item | Current value |
| --- | --- |
| Current end effector | Bare arm |
| Planned end effector | Dexterous hand, later |
| Physical arm count | `2`, independent power |
| Arm A | Web verified; hotspot `agx-7ax-armA`; CAN `can_arm_a`; namespace `arm_a`; USB bus `1-5:1.0` |
| Arm B | Web verified; hotspot `agx-7ax-armB`; CAN `can_arm_b`; namespace `arm_b`; USB bus `1-11:1.0` |
| Initial ROS `effector_type` | `none` |
| Installation pose | Table upright |
| Power supply | Factory adapter |
| CAN ports | `can_arm_a`, `can_arm_b` |
| CAN bitrate | `1000000` |
| Initial TCP offset | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| Deployment mode | Ubuntu 20.04 host SDK/CAN-only + Docker ROS2 Humble |
| Current live state | S10 complete: Arm A and Arm B both passed Web/SDK/ROS low-speed single-joint motion and final control-source closure |
| Observed Web model | `7ax`, interpreted as one NERO 7-axis arm/controller per physical arm |
| Observed Web footer version | `v1.121`; current SDK firmware selector is `v112` |
| Current next phase | S11 dual-arm experiment baseline and coordinate closure |

Current Web evidence shows one set of joint tabs, `关节1` through `关节7`.
Treat this as normal for one NERO 7-axis arm/controller. The physical setup has
two arms, so each arm is treated as a separate controller/IP/CAN device with its
own ROS namespace.

Dual-arm safety rule: unique Wi-Fi names and independent CAN paths are verified.
Do not place both arms on the same CAN bus unless a separate bus-design review is
completed. For ROS read-only launches, explicitly use `auto_enable:=false` and
`control_enabled:=false`, because the upstream single-arm launch defaults both
to `true`.

S10.1 Web first motion passed on Arm A by operator report. Actual Web scope was
all 7 Arm A degrees of freedom, which exceeded the original J7-only plan but
was followed by a clean ROS read-only snapshot. Do not use this to skip staged
gates: SDK/ROS/raw-CAN motion, Cartesian motion, MoveIt execute, and dual-arm
motion still require separate procedures and confirmation.

S10.2 prepared path: use `examples/nero_sdk_single_joint_step.py` with SDK
dry-run first, then optional `--execute` only after operator confirmation. J7
dry-run passed, but the execution candidate was revised to J1 for visual
observability. J1 `+1 deg` dry-run also passed, and the operator confirmed the
J1 swept area is clear. S10.2 SDK motion passed on Arm A: J1 `+2 deg` then
return, actual speed `10%`, final status NORMAL/reached target. Post-SDK ROS
read-only snapshot `docs/s9_ros_snapshots/20260625_062910/` passed.

S10.3 ROS `joint1 +2 deg` execution completed on Arm A and returned within
script tolerance; operator visually confirmed motion and return. Post-motion
dual-arm read-only snapshot `docs/s9_ros_snapshots/20260625_064243/` passed, so
S10.3 is accepted. Next preferred phase is S10.4 stop/recovery and
control-source closure. Do not run Cartesian, MoveIt, MIT/JS, raw CAN,
dexterous hand, or dual-arm coordinated motion yet.

S10.4 prepared path: use `docs/s10_4_stop_recovery_closure.md` and
`scripts/s10_control_source_audit.sh` to confirm no Arm A ROS control driver,
SDK motion script, or Web motion command remains active before repeating the
minimal first-motion ladder on Arm B. This closure is intentionally no-motion:
intentional emergency-stop and power-cut recovery tests remain deferred.
The script passed local syntax checking. A Codex-session run saw no NERO-related
host process but could not see `can_arm_a` or `can_arm_b`; the live
desktop-terminal audit then passed on 2026-06-25 and is saved at
`docs/s10_4_control_source_audit_live_20260625_150438.txt`. S10.4 is accepted
with handoff state `handoff_to_arm_b`.

S10.5 Arm B status: accepted. Pre-motion audit
`docs/s10_5_control_source_audit_live_20260625_152039.txt` is clean,
post-Web/read-only snapshot `docs/s9_ros_snapshots/20260625_072129/` is clean,
and the operator confirmed Arm B Web motion was normal.

S10.6 Arm B status: accepted. SDK dry-run used `can_arm_b`, firmware `v112`,
J1 `+2 deg`, speed `5%`, and target differed only in J1. Operator confirmed SDK
real motion was observed successfully and execution was smooth. Post-SDK
snapshot `docs/s9_ros_snapshots/20260625_074048/` is clean. Full SDK execute
terminal output was not pasted, so exact `after_step_deg` and `after_return_deg`
values are not recorded.

S10.7 prepared path: use `docs/s10_7_arm_b_ros_motion_plan.md`. Stop the
dual-arm read-only driver, start only the Arm B ROS control driver with
`namespace:=arm_b`, `can_port:=can_arm_b`, `auto_enable:=true`,
`control_enabled:=true`, `speed_percent:=5`, then run the `/arm_b` dry-run
before any ROS execute.

S10.7 Arm B status: accepted. ROS execute moved Arm B `joint1` from about
`32.798 deg` to `34.553 deg`, returned to about `33.026 deg` within script
tolerance, and final status was `ctrl_mode=1`, `arm_status=0`,
`mode_feedback=1`, `motion_status=0`. Post-ROS snapshot
`docs/s9_ros_snapshots/20260625_074953/` is clean; sampled Arm B J1 is about
`32.797 deg`, consistent with settled return. Next step is S10.8 closure:
stop/account for Arm B ROS control and audit active control sources before any
broader motion phase.

S10.8 status: accepted. Final control-source audit
`docs/s10_8_control_source_audit_live_20260625_155538.txt` shows A/B CAN
UP/ERROR-ACTIVE at 1 Mbps, no NERO Docker containers, and no NERO host
processes. S10 is complete. Next phase is S11 dual-arm experiment baseline:
define `lab_world`, measure both base transforms, establish static TF, and
create logging/rosbag rules before any coordinated dual-arm motion.

S11 prepared path: use `docs/s11_dual_arm_experiment_baseline.md`. S11 is a
coordinate, TF, TCP, and logging baseline phase, not a motion-expansion phase.
Keep `effector_type:=none` and TCP offset zero until an end effector is
installed and measured. End-effector installation is now S14, not S11.

## Raw CAN Policy

Raw CAN is not the default control path. Use raw CAN first for observation and
diagnostics.

Before sending any raw CAN command:

- write the frame ID, length, byte meaning, unit, and expected response
- confirm the arm mode
- confirm emergency stop behavior
- watch `0x2A1` and the relevant feedback IDs
- record the command and result in `docs/deployment_log.md`

Never send undocumented `cansend` commands during bring-up.

## Tooling And File Hygiene

- Prefer read-only checks first.
- Keep changes scoped to the current phase.
- Do not delete or rewrite source documents.
- Do not modify generated CAD/model assets unless explicitly required.
- Do not treat `docs/bringup_checklist.md` as a permanent log. It is a reusable
  checklist; durable evidence belongs in `docs/deployment_log.md` and
  `docs/current_bringup_status.md`.
- If a script or command changes deployment behavior, document the reason and
  update the route.

## Completion Rule

A phase is complete only when:

- its acceptance criteria are met
- evidence is recorded
- the current status file is updated
- the action route has been corrected with what was learned
- the next phase entry is clear
