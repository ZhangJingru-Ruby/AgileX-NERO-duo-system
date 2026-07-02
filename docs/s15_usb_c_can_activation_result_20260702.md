# S15 USB-C CAN Activation Result

Date: 2026-07-02

## Scope

This result closes the activation gate after moving all four CAN adapters onto
the USB-C hub.

## Commands and Observations

Initial audit before reactivation:

- `can_arm_a`: not visible.
- `can_arm_b`: not visible.
- No NERO-related Docker container was running.
- No NERO-related host process was running.

Arm A activation:

```bash
bash scripts/activate_can.sh can_arm_a 1000000 "1-3.4.1:1.0"
```

Observed:

- Vendor activation script found temporary interface `can3`.
- `can3` was reset to bitrate `1000000`.
- `can3` was renamed to `can_arm_a`.
- Final state: `can_arm_a` UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- Driver: `gs_usb`.

Arm B activation:

```bash
bash scripts/activate_can.sh can_arm_b 1000000 "1-3.4.3:1.0"
```

Observed:

- Vendor activation script found temporary interface `can0`.
- `can0` was reset to bitrate `1000000`.
- `can0` was renamed to `can_arm_b`.
- Final state: `can_arm_b` UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- Driver: `gs_usb`.

Four-interface inventory after activation:

| Interface | Role | State | Driver | USB bus-info |
| --- | --- | --- | --- | --- |
| `can1` | Left LinkerHand L6 | UP / ERROR-ACTIVE | `peak_usb` | `1-3.4.4:1.0` |
| `can2` | Right LinkerHand L6 | UP / ERROR-ACTIVE | `peak_usb` | `1-3.4.2:1.0` |
| `can_arm_a` | Arm A official USB-CAN | UP / ERROR-ACTIVE | `gs_usb` | `1-3.4.1:1.0` |
| `can_arm_b` | Arm B official USB-CAN | UP / ERROR-ACTIVE | `gs_usb` | `1-3.4.3:1.0` |

## Acceptance

Accepted for S15 preflight:

- Arm A and Arm B were restored to deterministic SocketCAN names.
- Both arm CAN interfaces are UP and ERROR-ACTIVE at `1000000`.
- Both hand CAN interfaces stayed UP and ERROR-ACTIVE at `1000000`.
- Arm and hand adapters are distinguishable by driver and bus-info.
- No stale NERO control process was seen before activation.

Next gate: start the S15 observation session, verify ROS feedback, and run
dry-runs before any coordinated motion.
