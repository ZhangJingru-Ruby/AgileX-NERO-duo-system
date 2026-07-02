# S6 Dual-Arm CAN And ROS Read-Only Plan

Date: 2026-06-25

## Current Facts

- The site has two NERO arms.
- Both arms passed S5 Web read-only checks.
- Arm A Wi-Fi hotspot: `agx-7ax-armA`.
- Arm B Wi-Fi hotspot: `agx-7ax-armB`.
- Both arms are currently bare-arm configurations.
- Dexterous hands are planned later and are not part of the S6/S8 baseline.
- The operator confirmed two official USB-CAN modules are available, one per
  arm.

## Decision

The system will be prepared for simultaneous dual-arm control, but the next
phase remains read-only.

Do not put both arms on one CAN bus. Use two independent official USB-CAN
modules:

| Arm | ROS namespace | CAN interface | Wi-Fi hotspot |
| --- | --- | --- | --- |
| Arm A | `arm_a` | `can_arm_a` | `agx-7ax-armA` |
| Arm B | `arm_b` | `can_arm_b` | `agx-7ax-armB` |

USB bus-info mapping observed on 2026-06-25:

| Arm | USB-CAN bus-info |
| --- | --- |
| Arm A | `1-5:1.0` |
| Arm B | `1-11:1.0` |

Physical host USB port orientation:

| Arm | Physical USB port note |
| --- | --- |
| Arm A | Vertical USB port |
| Arm B | Horizontal USB port |

This mapping depends on the physical USB ports. If modules are moved to other
USB ports, run `bash scripts/find_can_ports.sh` again and update this table.

## Wi-Fi Role

The host's built-in Wi-Fi can connect to only one arm hotspot at a time. This is
acceptable for dual-arm control because the planned real-time control path is
USB-CAN, not Wi-Fi.

Use Wi-Fi for Web configuration, checks, and screenshots. Use `can_arm_a` and
`can_arm_b` for simultaneous control and feedback. If simultaneous Web access to
both controllers is needed later, use wired Ethernet with unique static IPs or a
second Wi-Fi adapter, and document that network plan before changing IPs.

## Why Two CAN Interfaces

The NERO CAN protocol uses fixed feedback and control frame IDs such as `0x2A1`,
`0x2A5-0x2A7`, and `0x2A9`. The local manual also warns not to enable CAN push
on two connected arms simultaneously. Therefore the safe default is one CAN bus
per physical arm.

## S6 Acceptance Criteria

For each arm independently:

- The USB-CAN module bus-info is recorded.
- The interface is renamed deterministically to `can_arm_a` or `can_arm_b`.
- The interface is UP with bitrate `1000000`.
- `candump` receives continuous feedback frames.
- `0x2A1`, `0x2A5-0x2A7`, and `0x2A9` are observed.
- No control frame is sent.

For dual-arm readiness:

- Both interfaces can be UP at the same time.
- `candump can_arm_a` and `candump can_arm_b` each receive only that arm's
  feedback.
- Unplugging Arm A's CAN stops only `can_arm_a` feedback.
- Unplugging Arm B's CAN stops only `can_arm_b` feedback.

If Web CAN communication must be toggled to receive feedback, first toggle and
capture one arm at a time. Only test simultaneous feedback after the CAN buses
are proven independent. If feedback becomes abnormal, stop capture, turn off CAN
communication from Web if reachable, and power-cycle the affected controller if
needed.

## S8 ROS Read-Only Direction

After S6 and S7 pass, launch two ROS driver instances with distinct namespaces
and CAN interfaces. For read-only tests, explicitly disable auto-enable and the
external control gate:

Preferred project wrapper, run from the host:

```bash
bash scripts/run_humble_container.sh \
  bash /workspace/nero/scripts/launch_dual_ros_readonly.sh
```

```bash
ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
  namespace:=arm_a \
  can_port:=can_arm_a \
  arm_type:=nero \
  effector_type:=none \
  auto_enable:=false \
  control_enabled:=false
```

```bash
ros2 launch agx_arm_ctrl start_single_agx_arm.launch.py \
  namespace:=arm_b \
  can_port:=can_arm_b \
  arm_type:=nero \
  effector_type:=none \
  auto_enable:=false \
  control_enabled:=false
```

Expected read-only ROS topics:

- `/arm_a/feedback/joint_states`
- `/arm_a/feedback/tcp_pose`
- `/arm_a/feedback/arm_status`
- `/arm_b/feedback/joint_states`
- `/arm_b/feedback/tcp_pose`
- `/arm_b/feedback/arm_status`

Do not use MoveIt execute, `/control/*`, `enable_agx_arm`, or `move_home` during
S8 read-only validation.
