# S14 Left LinkerHand L6 Index-Micro Result

Date: 2026-06-30

## Scope

This result records the first SDK-backed small finger motion on the
bench-connected left LinkerHand L6. The hand was controlled through the
standalone SocketCAN interface `can1`.

The tested motion was an index raw-value micro step from the SDK `open` preset:

- Base pose: `[255, 179, 255, 255, 255, 255]`
- Target pose: `[255, 179, 245, 255, 255, 255]`
- Changed joint: `index`
- Delta: `-10`
- Speed: `[30, 30, 30, 30, 30, 30]`
- Sequence: target pose, then return to base pose

## Dry Run

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can1 \
  --side left \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```

Observed output:

- `execute=False`
- `base_pose=[255, 179, 255, 255, 255, 255]`
- `target_pose=[255, 179, 245, 255, 255, 255]`
- `sequence=target_pose_then_return_to_base_pose`
- The script stopped at the dry-run gate.

Dry-run acceptance: accepted.

## Execute

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can1 \
  --side left \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```

Observed output:

- SDK version: `3.1.0`
- SDK connection: `interface='socketcan', channel='can1'`
- Embedded version: `[2, 3, 7]`
- Serial: `LHL6-03-253-L-B-1-C`

Pre-motion health:

- Temperature raw: `[35, 37, 36, 37, 37, 36]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[20, 2, 0, 5, 3, 5]`

Command sequence:

- `setting_speed=[30, 30, 30, 30, 30, 30]`
- `sending_target_pose=[255, 179, 245, 255, 255, 255]`
- `returning_to_base_pose=[255, 179, 255, 255, 255, 255]`

Post-motion health:

- Temperature raw: `[35, 37, 36, 37, 36, 36]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[18, 2, 0, 4, 2, 6]`

The script completed with `S14 SDK motion gate completed.` No SDK receive-thread
shutdown error appeared in this run.

## Acceptance

Accepted from SDK/software health:

- The planned target pose changed only the index raw value by `-10`.
- The script returned the hand to the SDK `open` preset.
- Faults were zero before and after the motion.
- Temperature remained stable.
- Current raw values remained low and stable in the SDK samples.
- The wrapper exited cleanly.

Operator physical observation and bench power behavior should still be recorded
before widening the motion envelope, running multi-finger gestures, or moving to
the right hand.

Next recommended gate:

- Confirm physical observation and bench supply behavior for this index-micro
  execution.
- If accepted, repeat the same SDK health/dry-run/execute discipline on the
  right hand after moving the bench wiring to the right hand, or plan a
  slightly larger left-hand single-finger motion with explicit dry-run first.
