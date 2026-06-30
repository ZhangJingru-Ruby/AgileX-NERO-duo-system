# S14 Hand CAN Inventory Result

Date: 2026-06-30

## Scope

This result records the read-only inventory after both LinkerHand CAN cables
were connected through the USB-C adapter path. The inventory script did not send
CAN frames.

Command:

```bash
bash scripts/s14_hand_can_inventory.sh
```

## Observed Interfaces

| Interface | Role | State | Driver | USB bus-info | Decision |
| --- | --- | --- | --- | --- | --- |
| `can_arm_a` | NERO arm CAN | UP | `gs_usb` | `1-5:1.0` | Do not use for hand |
| `can_arm_b` | NERO arm CAN | UP | `gs_usb` | `1-11:1.0` | Do not use for hand |
| `can1` | hand CAN candidate | UP | `peak_usb` | `1-3.4.4:1.0` | Left hand, already verified by serial |
| `can2` | hand CAN candidate | DOWN | `peak_usb` | `1-3.4.2:1.0` | Right hand candidate |

## Interpretation

- The two NERO arm CAN interfaces remain separated from hand testing.
- `can1` is the accepted left-hand interface because prior SDK health identified
  serial `LHL6-03-253-L-B-1-C` on `can1`.
- `can2` is the right-hand candidate because it is the second PEAK/XCAN-USB hand
  interface and is not an arm CAN interface.
- `can2` must be activated at `1000000` bitrate before right-hand SDK health.

## Next Gate

Activate `can2`:

```bash
sudo ip link set can2 up type can bitrate 1000000
```

Then verify right-hand identity and health:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_health.py \
  --can can2 \
  --side right
```

Expected right-hand serial:

```text
LHL6-03-240-R-B-1-C
```
