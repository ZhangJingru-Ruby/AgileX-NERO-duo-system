# S14 Right LinkerHand L6 Index-Micro Result

Date: 2026-06-30

## Scope

This result records the first SDK-backed right index micro-motion on SocketCAN
interface `can2`.

This gate specifically follows the right open-anchor observation where thumb,
middle, ring, and pinky moved, but the index did not show visible motion. The
purpose of this gate is to verify the right index joint with a small isolated
raw-value change.

## Dry Run

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can2 \
  --side right \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```

Observed:

- `execute=False`
- `side=right`
- `can=can2`
- `mode=index-micro`
- `preset=open`
- `speed=30`
- `torque=None`
- `base_pose=[255, 70, 255, 255, 255, 255]`
- `target_pose=[255, 70, 245, 255, 255, 255]`
- `sequence=target_pose_then_return_to_base_pose`

Dry-run acceptance: accepted.

## Execute

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can2 \
  --side right \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```

Observed:

- SDK version: `3.1.0`
- SDK connection: `interface='socketcan', channel='can2'`
- Embedded version: `[2, 3, 7]`
- Serial: `LHL6-03-240-R-B-1-C`

Pre-motion health:

- Temperature raw: `[31, 33, 33, 32, 32, 32]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[22, 13, 1, 0, 2, 1]`

Command sequence:

- `setting_speed=[30, 30, 30, 30, 30, 30]`
- `sending_target_pose=[255, 70, 245, 255, 255, 255]`
- `returning_to_base_pose=[255, 70, 255, 255, 255, 255]`

Post-motion health:

- Temperature raw: `[31, 33, 33, 32, 32, 32]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[22, 13, 1, 1, 0, 3]`

The script completed with `S14 SDK motion gate completed.`

## Acceptance

Accepted from SDK/software health:

- The planned target pose changed only the right index raw value by `-10`.
- The script returned the hand to the SDK right-hand `open` preset.
- Faults were zero before and after the motion.
- Temperature remained stable.
- Current raw values stayed low and stable in the SDK samples.
- The wrapper exited cleanly.

Physical observation is still pending:

- Record whether the right index finger visibly moved during the target step.
- Record whether it returned to open.
- Record whether bench supply voltage/current stayed normal and whether there
  was any abnormal sound, heat, smell, vibration, or unexpected motion.

Synchronized control remains blocked until the physical observation confirms
the right index response or a follow-up diagnosis is completed.
