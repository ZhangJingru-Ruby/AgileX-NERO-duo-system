# S14 Left LinkerHand L6 Open-Anchor Dry Run Result

Date: 2026-06-30

## Scope

This result records the dry-run gate before the first SDK-backed open-anchor
command on the bench-connected left LinkerHand L6.

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can1 \
  --side left \
  --mode open-anchor
```

## Observed Output

- `execute=False`
- `side=left`
- `can=can1`
- `mode=open-anchor`
- `preset=open`
- `speed=30`
- `torque=None`
- `base_pose=[255, 179, 255, 255, 255, 255]`
- `sequence=send_base_pose_once`
- Script ended at the dry-run gate and printed:
  `Dry run only. Add --execute after the S14 safety gate is confirmed.`

## Acceptance

Accepted for dry-run:

- The command resolved the intended left-hand SDK open preset.
- No SDK connection, CAN motion command, or hand movement was requested by this
  dry-run.
- The next authorized gate is only the explicit open-anchor execute command.

Next command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can1 \
  --side left \
  --mode open-anchor
```

This next gate sends one SDK `finger_move()` command with the `open` preset. It
does not authorize full gestures, grasping, GUI, demo scripts, contact, or
closed-hand motion.
