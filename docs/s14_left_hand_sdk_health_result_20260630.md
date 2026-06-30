# S14 Left LinkerHand L6 SDK Health Result

Date: 2026-06-30

## Scope

This result records the first SDK-backed identity and health gate for the
bench-connected left LinkerHand L6. The hand was disconnected from NERO J6 and
connected through the standalone PEAK/XCAN-USB SocketCAN interface `can1`.

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_health.py \
  --can can1 \
  --side left
```

The script intentionally did not call SDK `get_state()`, `get_torque()`,
`finger_move()`, GUI tools, or motion demos.

## Observed Output

- CAN interface: `can1`
- Driver family: `pcan_usb` / `peak_usb`
- CAN state: `ERROR-ACTIVE`
- Bitrate: `1000000`
- SDK version: `3.1.0`
- SDK connection: `interface='socketcan', channel='can1'`
- Embedded version: `[2, 3, 7]`
- Hand ID: `0x28`
- Serial: `LHL6-03-253-L-B-1-C`

Samples:

| Sample | Temperature raw | Fault raw | Current raw |
| --- | --- | --- | --- |
| 1 | `[36, 37, 36, 36, 36, 36]` | `[0, 0, 0, 0, 0, 0]` | `[37, 11, 1, 3, 4, 4]` |
| 2 | `[36, 37, 36, 36, 36, 36]` | `[0, 0, 0, 0, 0, 0]` | `[37, 12, 0, 5, 5, 6]` |
| 3 | `[36, 37, 36, 36, 36, 36]` | `[0, 0, 0, 0, 0, 0]` | `[37, 11, 1, 4, 5, 4]` |

Bench supply reported by the operator before this gate remained stable at about
`24 V` and `0.135 A`.

## Acceptance

Accepted for S14 SDK health:

- The SDK can identify the left L6 hand on `can1`.
- The serial matches the expected left-hand serial from the tuned
  `upstream/linkerhand_sdk` repository.
- Firmware/embedded version is readable.
- All sampled fault values are zero.
- Temperature values are stable and plausible for a powered bench device.
- Current raw values are stable and low.

This result authorizes only the next dry-run gate:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can1 \
  --side left \
  --mode open-anchor
```

It does not authorize full SDK demos, GUI, gesture loops, grasping, or
closed-hand/contact tests.
