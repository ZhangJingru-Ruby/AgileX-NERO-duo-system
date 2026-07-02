# NERO Dual-Arm Dual-Hand Delivery Workspace

This repository packages the deployment, bring-up, validation evidence, and operating workflow for a NERO dual 7-DOF arm system with two LinkerHand L6 dexterous hands.

As of 2026-07-02, S0-S14 are complete, and the S15 dual-arm dual-hand elbow-curl/fist demo has run through by operator report. The next gate is zero-return revalidation using the default `zero` pose, then S15 delivery closure. This is still a bring-up/demo workflow, not a contact grasping, handoff, or close-proximity manipulation primitive.

Chinese entry: [README.md](README.md)  
Full workflow: [PLAN.md](PLAN.md) / [PLAN_EN.md](PLAN_EN.md)

## Required Entry Points

- [Agent Operating Rules](agent.md): Required facts, logging rules, and safety discipline for future collaborators.
- [Current Bring-Up Status](docs/status/current_bringup_status.md): Current configuration, phase state, accepted results, and next step.
- [Deployment Log](docs/status/deployment_log.md): Actual commands, evidence, decisions, risks, and next actions.
- [Bring-Up Checklist](docs/status/bringup_checklist.md): Field checklist for revalidation.
- [Setup Framework](docs/status/setup_framework.md): Engineering layers, hardware facts, and defaults.
- [Deployment Route](docs/phases/机器人部署与调试行动路线.md): Historical phase route and detailed notes.
- [S15 Coordination Plan](docs/phases/s15_dual_arm_hand_coordination_plan.md): Current hybrid control architecture and S15 gates.
- [S15 Sequence Plan](docs/phases/s15_arm_hand_coordination_sequence_plan.md): Observe, dry-run, active, and execute order.
- [S15 Return/Elbow-Curl Design](docs/phases/s15_return_to_initial_and_elbow_curl_design.md): Return target, gesture definition, and side mapping.

## Repository Layout

```text
.
├── config/                 # Stable environment variables and device mapping
├── docker/                 # ROS2 Humble container
├── examples/               # SDK-only examples
├── rviz/                   # RViz configuration
├── scripts/                # Accepted operation scripts, paths kept stable
├── docs/
│   ├── status/             # Current status, logs, checklist, framework
│   ├── phases/             # S2-S15 plans, designs, procedures
│   ├── results/            # Accepted results, audits, diagnostics
│   ├── evidence/           # Image evidence and ROS snapshot entry
│   ├── assets/             # Manuals, protocol sheets, CAD/STEP/STL
│   └── upstream/           # Upstream analysis and reviews
└── upstream/               # Ignored local upstream source cache
```

ROS read-only snapshots are archived under `docs/evidence/ros_snapshots`. This directory contains the historical S9/S10-S14 snapshot set, and new snapshots also write to the same evidence path.

## Fixed Control Architecture

| Device | Interface | Control path |
| --- | --- | --- |
| Arm A / right side | `can_arm_a`, USB `1-3.4.1:1.0`, ROS `/arm_a` | ROS2 `agx_arm_ros` |
| Arm B / left side | `can_arm_b`, USB `1-3.4.3:1.0`, ROS `/arm_b` | ROS2 `agx_arm_ros` |
| Left hand | `can1`, USB `1-3.4.4:1.0` | LinkerHand SDK wrapper |
| Right hand | `can2`, USB `1-3.4.2:1.0` | LinkerHand SDK wrapper |

Do not run arm SDK motion while the ROS arm driver is active. Do not run LinkerHand GUI/demo/gesture scripts while the project hand wrappers are active.

## Quick Commands

```bash
source config/nero.env
bash scripts/check_environment.sh
bash scripts/s10_control_source_audit.sh
```

Start S15 read-only observation and RViz:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh --readonly
```

S15 zero-return dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-init \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_return_to_initial.py
```

S15 zero-return execute:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-init \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_return_to_initial.py \
      --execute \
      --allow-wide-motion \
      --confirm-clearance \
      --confirm-rviz-visible
```

S15 dual-arm dual-hand elbow-curl/fist dry-run:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side both \
      --left-j1-delta-deg -10 \
      --right-j1-delta-deg -20 \
      --left-j4-delta-deg 15 \
      --right-j4-delta-deg 15 \
      --arm-profile single-target \
      --hand-timing during-curl \
      --hand-close-fraction 0.5
```

Before execution, stop the readonly observe session and restart the observe/driver session with `--active`.

## Hard Safety Boundaries

- Default state is no motion; every real motion must pass dry-run first.
- External supply must not exceed 25V and must provide at least 10A. The end XT30 2+2 interface is 24V, 2A MAX.
- Any new control path, larger motion, contact task, MoveIt execute, Cartesian motion, raw CAN motion, MIT control, zero calibration, firmware upgrade, or collision-level change requires a separate plan and gate.
- The S15 RViz visual anchor is for observation only. It must not be used for control, planning, limits, calibration, or semantic acceptance.
- After USB/CAN or arm power reconnect, wait about 20 seconds before judging `candump` or ROS topic health.
- If RViz does not match the physical posture, run `scripts/s15_rviz_pose_diagnostics.sh` before any motion.

## Git Package Boundary

Commit project-owned scripts, configuration, documents, evidence, images, and CAD assets. The following are intentionally excluded:

- `upstream/`: reproducible upstream source cache.
- `.venv/`: local SDK virtual environment.
- `build/`, `install/`, `log/`: ROS/colcon build outputs.
- `.agents/`, `.codex/`, `__pycache__/`: local runtime caches.
- `docs/vendor/`: large vendor packages and extracted trees; keep the review documents instead.

## Recreating Upstream Evidence

```bash
mkdir -p upstream

git clone https://github.com/agilexrobotics/agx_arm_ros.git upstream/agx_arm_ros
git -C upstream/agx_arm_ros checkout c73d33f2ab377447261423f1b881bd89c6663627

git clone https://github.com/agilexrobotics/pyAgxArm.git upstream/pyAgxArm
git -C upstream/pyAgxArm checkout a226840db0c3d5c5dc7f3ec78d6cef1a6800f9e6

git clone https://github.com/agilexrobotics/piper_ros.git upstream/piper_ros
git -C upstream/piper_ros checkout 2dc30fca68cbf4e04d1d0bc15c123d026380ece7
```

LinkerHand SDK is user-provided or requires private repository access:

```bash
git clone https://github.com/LV-Robotics-Lab/linkerhand_sdk upstream/linkerhand_sdk
```
