# S14 Left LinkerHand L6 CAN Bring-Up Plan

Date: 2026-06-30

## Correction From Live Device Evidence

The left hand was initially described as connected through a computer serial
path. The live host evidence corrects that interpretation:

- `ls -l /dev/serial/by-id/` produced no device.
- `ls -l /dev/ttyUSB* /dev/ttyACM*` produced no device.
- `dmesg` showed a PEAK-System PCAN-USB adapter:
  - USB product: `XCAN-USB`;
  - USB ID: `0c72:000c`;
  - driver: `peak_usb`;
  - attached SocketCAN interface: `can1`;
  - USB bus path after the USB-C hub: `1-3.4.4:1.0`.

Therefore the active left-hand bench branch is CAN over SocketCAN, not
RS485/Modbus. The earlier RS485 plan is superseded unless a real `/dev/ttyUSB*`
or `/dev/ttyACM*` serial adapter appears later.

## Current Evidence

- The selected hand is the left LinkerHand L6.
- The hand is disconnected from NERO arm/J6.
- Bench photo:
  `docs/pics/灵巧手连接设备/灵巧手左手上电操控示意图.jpeg`.
- The photo shows about `24.00 V` and `0.122 A` on the WANPTEK supply.
- The host sees the hand debug adapter as SocketCAN `can1`.
- Existing NERO arm CAN names remain `can_arm_a` and `can_arm_b`; do not probe
  those with LinkerHand frames.

## Interface Facts

From `upstream/linkerhand_sdk`:

- LinkerHand L6 native CAN bitrate: `1000000`.
- Left hand CAN ID: `0x28`.
- Right hand CAN ID: `0x27`.
- L6 read request frames use the hand CAN ID and a one-byte command.
- Responses are accepted by the SDK from the hand ID or hand ID plus `8`, so the
  left hand should respond on `0x28` or `0x30`.
- Motion commands use the same frame type with six payload values. First
  bring-up must avoid those payload commands.

Read-only request frame set for the left hand:

| Request | Meaning |
| --- | --- |
| `028#64` | version query |
| `028#C0` | serial query |
| `028#01` | current joint state query |
| `028#33` | motor temperature query |
| `028#35` | motor fault query |
| `028#36` | current query |
| `028#02` | torque/status query |

Do not send six-byte position, speed, or torque payloads before S14.8.

## S14.5C CAN Interface Baseline

Goal: make the hand CAN interface deterministic and avoid collisions with arm
CAN interfaces.

Recommended live checks:

```bash
ip -br link show type can
ethtool -i can1
ip -details link show can1
```

If `can1` is DOWN, activate it:

```bash
sudo ip link set can1 up type can bitrate 1000000
```

Preferred stabilization after first proof:

- Rename the hand interface to a stable project name such as `can_hand_left`.
- Record USB bus-info `1-3.4.4:1.0`.
- Keep the hand CAN interface separate from `can_arm_a` and `can_arm_b`.

Acceptance:

- Hand interface exists and is UP at `1000000`.
- Driver is `peak_usb`.
- No LinkerHand frame is sent on `can_arm_a` or `can_arm_b`.

## S14.6C CAN Read-Only Probe

Goal: prove LinkerHand identity and health without motion.

Run the project read-only probe:

```bash
bash scripts/s14_linkerhand_l6_can_readonly_probe.sh can1 left
```

The script sends only one-byte read requests and captures responses.

Acceptance:

- Responses appear on `0x28` or `0x30`.
- Version or serial response appears.
- Joint state response `0x01` returns six values.
- Temperature response `0x33` returns plausible values.
- Fault response `0x35` returns all zero values.
- Supply current remains stable around idle.

Stop conditions:

- No response after confirming `can1` is UP at `1000000`.
- Any nonzero fault code.
- Current rises unexpectedly, or the hand heats, twitches, or makes abnormal
  noise during read-only queries.

## S14.7C Optional Tactile Read-Only Probe

Only after S14.6C is accepted, query the tactile/matrix frames. This is optional
before first motion and should be kept separate from the identity/health gate.

## S14.8C First Micro Motion

Goal: prove one actuator can track a small command and return.

Safety gate:

- S14.6C accepted.
- No object is in or near the hand.
- Left hand is the only hand on the bench control path.
- Power supply is still `24 V`; current is stable.
- A human is ready to cut power.

Recommended first motion:

1. Read current six-joint state.
2. Set conservative speed and torque with explicit documented values.
3. Move only a clearly visible non-thumb joint, preferably index flexion
   `joint index 2`.
4. Change the raw value by about `10`, then return to the original state.
5. Read state, fault, temperature, and supply current before and after.

Do not use `test_hand.py`, `gestures.py`, `dual_gui.py`, or SDK demo scripts for
the first motion.

## S14.9C Right Hand Reproduction

After the left hand passes:

1. Power down and disconnect the left hand.
2. Connect the right hand with the same bench wiring discipline.
3. Use right hand CAN ID `0x27`.
4. Repeat the CAN interface, read-only, and first micro-motion gates.
