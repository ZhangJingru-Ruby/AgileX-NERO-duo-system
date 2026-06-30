# S14 Left LinkerHand L6 Open-Anchor Execute Result

Date: 2026-06-30

## Scope

This result records the first SDK-backed motion gate for the bench-connected
left LinkerHand L6. The command sent one SDK `open` preset to the left hand on
SocketCAN `can1`.

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can1 \
  --side left \
  --mode open-anchor
```

## Observed Output

- `execute=True`
- `side=left`
- `can=can1`
- `mode=open-anchor`
- `preset=open`
- `speed=30`
- `torque=None`
- `base_pose=[255, 179, 255, 255, 255, 255]`
- `sequence=send_base_pose_once`
- SDK version: `3.1.0`
- SDK connection: `interface='socketcan', channel='can1'`
- Embedded version: `[2, 3, 7]`
- Serial: `LHL6-03-253-L-B-1-C`

Pre-motion health:

- Temperature raw: `[36, 37, 36, 37, 37, 36]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[37, 15, 0, 5, 3, 6]`

Command:

- Speed command: `[30, 30, 30, 30, 30, 30]`
- Pose command: `[255, 179, 255, 255, 255, 255]`

Post-motion health:

- Temperature raw: `[36, 37, 36, 37, 37, 36]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[22, 3, 0, 6, 2, 6]`

The script printed `S14 SDK motion gate completed.` Afterwards, one SDK receive
thread shutdown message appeared:

```text
Error receiving CAN message: Error receiving: Bad file descriptor [Error Code 9]
```

This message occurred after the motion gate had completed and after post-motion
zero-fault health was reported. It is treated as a software shutdown artifact,
not as a hand fault. The project wrapper was updated to join the SDK receive
thread before shutting down the CAN bus to reduce this exit noise.

## Acceptance

Accepted from the SDK/software health perspective:

- The SDK identified the expected left L6 hand.
- The script sent exactly one open-anchor preset command.
- Faults were zero before and after the command.
- Temperatures were stable before and after the command.
- Current raw values did not show a persistent high-current condition in the
  SDK samples.

Before any executed index micro-motion, the operator should still confirm the
physical observation and bench supply reading for this open-anchor command:

- no unexpected finger motion;
- no abnormal sound, heat, smell, or vibration;
- bench supply remained near `24 V` without an abnormal current jump.

Next authorized software gate is the index micro-motion dry-run only:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can1 \
  --side left \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```
