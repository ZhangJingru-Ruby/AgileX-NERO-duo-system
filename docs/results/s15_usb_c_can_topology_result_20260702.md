# S15 USB-C Hub CAN Topology Result

Date: 2026-07-02

## Scope

This result records the operator-requested move of the NERO arm USB-CAN adapters
onto the same USB-C hub already used by the two LinkerHand CAN adapters.

This is a topology discovery result only. At the time of this record, the arm
interfaces were discovered as temporary kernel names and were still DOWN. The
accepted deterministic names remain `can_arm_a` and `can_arm_b`, and must be
recreated with `scripts/activate_can.sh` before ROS or SDK arm checks.

## Observed Interfaces

Initial host view after moving the arm adapters:

```text
can1             UP             <NOARP,UP,LOWER_UP,ECHO>
can2             UP             <NOARP,UP,LOWER_UP,ECHO>
can3             DOWN           <NOARP,ECHO>
can0             DOWN           <NOARP,ECHO>
```

USB bus-info inventory with all four adapters present:

| Temporary interface | USB bus-info | Device role | Status |
| --- | --- | --- | --- |
| `can1` | `1-3.4.4:1.0` | Left LinkerHand L6 | Previously accepted |
| `can2` | `1-3.4.2:1.0` | Right LinkerHand L6 | Previously accepted |
| `can3` | `1-3.4.1:1.0` | Arm A official USB-CAN | Newly identified |
| `can0` | `1-3.4.3:1.0` | Arm B official USB-CAN | Newly identified |

Operator unplug/replug checks confirmed:

- Arm A appears as temporary `can3` at USB bus-info `1-3.4.1:1.0`.
- Arm B appears as temporary `can0` at USB bus-info `1-3.4.3:1.0`.
- Left hand remains `can1` at USB bus-info `1-3.4.4:1.0`.
- Right hand remains `can2` at USB bus-info `1-3.4.2:1.0`.

## Updated Deterministic Mapping

| Device | Deterministic interface | USB bus-info |
| --- | --- | --- |
| Arm A | `can_arm_a` | `1-3.4.1:1.0` |
| Arm B | `can_arm_b` | `1-3.4.3:1.0` |
| Left hand | `can1` | `1-3.4.4:1.0` |
| Right hand | `can2` | `1-3.4.2:1.0` |

Historical arm bus-info values before the USB-C hub move were:

- Arm A: `1-5:1.0`
- Arm B: `1-11:1.0`

Those historical values must not be used after this topology change unless the
adapters are physically moved back to the original host USB ports.

## Required Re-activation

Run after confirming no ROS, SDK, Web, GUI, or demo process is commanding the
robot:

```bash
bash scripts/s10_control_source_audit.sh

bash scripts/activate_can.sh can_arm_a 1000000 "1-3.4.1:1.0"
bash scripts/activate_can.sh can_arm_b 1000000 "1-3.4.3:1.0"

ip -details link show can_arm_a
ip -details link show can_arm_b
bash scripts/s14_hand_can_inventory.sh
```

## Acceptance Criteria

The USB-C topology is accepted only after all of the following are true:

- `can_arm_a` exists and is UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- `can_arm_b` exists and is UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- `can1` remains the left-hand SDK interface.
- `can2` remains the right-hand SDK interface.
- Arm adapters report the expected official USB-CAN driver.
- Hand adapters report `peak_usb`.
- No unexpected ROS, SDK, Web, GUI, or demo control process is running.
- Dual-arm ROS read-only starts with `/arm_a` and `/arm_b` feedback at the
  expected rate.
- Hand SDK health still reports the expected serial numbers and all-zero faults.

Until these checks pass, S15 arm+hand coordination remains blocked.
