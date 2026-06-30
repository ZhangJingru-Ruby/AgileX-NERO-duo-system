# S14 Right LinkerHand L6 SDK Health Result

Date: 2026-06-30

## Scope

This result records the first SDK-backed identity and health gate for the right
LinkerHand L6 on its independent CAN interface.

The right hand was tested through SocketCAN interface `can2`, which had been
identified as the right-hand candidate in
`docs/s14_hand_can_inventory_result_20260630.md`.

## CAN Activation

Command:

```bash
sudo ip link set can2 up type can bitrate 1000000
ip -details link show can2
```

Observed:

- Interface: `can2`
- State: `UP,LOWER_UP`
- CAN state: `ERROR-ACTIVE`
- Bitrate: `1000000`
- Driver family: `pcan_usb` / `peak_usb`

## SDK Health

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_health.py \
  --can can2 \
  --side right
```

Observed:

- SDK version: `3.1.0`
- SDK connection: `interface='socketcan', channel='can2'`
- Hand ID: `0x27`
- Serial: `LHL6-03-240-R-B-1-C`
- Embedded version: `[2, 3, 7]`

Samples:

| Sample | Temperature raw | Fault raw | Current raw |
| --- | --- | --- | --- |
| 1 | `[29, 31, 31, 30, 30, 31]` | `[0, 0, 0, 0, 0, 0]` | `[12, 0, 0, 4, 4, 1]` |
| 2 | `[29, 31, 31, 30, 30, 31]` | `[0, 0, 0, 0, 0, 0]` | `[10, 0, 1, 4, 2, 2]` |
| 3 | `[29, 31, 31, 30, 30, 31]` | `[0, 0, 0, 0, 0, 0]` | `[12, 0, 0, 4, 3, 1]` |

The script printed:

```text
ACCEPTED: SDK identity/health responses are present; faults are zero.
```

## Acceptance

Accepted for right-hand SDK health:

- `can2` is the active right-hand SocketCAN interface.
- The serial matches the expected right-hand serial from the tuned SDK repo.
- Firmware/embedded version is readable.
- All sampled fault values are zero.
- Temperature and current raw values are stable.
- No motion command was sent by the health script.

Next authorized gate is right-hand open-anchor dry-run only:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can2 \
  --side right \
  --mode open-anchor
```
