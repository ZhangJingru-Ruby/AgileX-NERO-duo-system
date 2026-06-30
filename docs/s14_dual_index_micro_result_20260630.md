# S14 Dual LinkerHand L6 Index-Micro Result

Date: 2026-06-30

## Scope

This result records the first visible dual-hand synchronized micro-motion on
the independent LinkerHand CAN interfaces:

- Left hand: `can1`, serial `LHL6-03-253-L-B-1-C`
- Right hand: `can2`, serial `LHL6-03-240-R-B-1-C`

The tested motion changed only the index raw value on both hands by `-20`, then
returned both hands to the SDK `open` preset.

## Dry Run

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --left-can can1 \
  --right-can can2 \
  --mode index-micro \
  --joint index \
  --left-delta -20 \
  --right-delta -20 \
  --speed 30
```

Observed:

- `execute=False`
- `left_can=can1`
- `right_can=can2`
- `mode=index-micro`
- `preset=open`
- `speed=30`
- `torque=None`
- Left base pose: `[255, 179, 255, 255, 255, 255]`
- Right base pose: `[255, 70, 255, 255, 255, 255]`
- Left target pose: `[255, 179, 235, 255, 255, 255]`
- Right target pose: `[255, 70, 235, 255, 255, 255]`
- Sequence: send both targets, then return both to base.

Dry-run acceptance: accepted.

## Execute

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --execute \
  --left-can can1 \
  --right-can can2 \
  --mode index-micro \
  --joint index \
  --left-delta -20 \
  --right-delta -20 \
  --speed 30
```

Observed:

- Left SDK connection: `interface='socketcan', channel='can1'`
- Left embedded version: `[2, 3, 7]`
- Left serial: `LHL6-03-253-L-B-1-C`
- Right SDK connection: `interface='socketcan', channel='can2'`
- Right embedded version: `[2, 3, 7]`
- Right serial: `LHL6-03-240-R-B-1-C`

Pre-motion health:

- Left temperature raw: `[34, 36, 36, 36, 36, 36]`
- Left fault raw: `[0, 0, 0, 0, 0, 0]`
- Left current raw: `[21, 3, 2, 3, 4, 2]`
- Right temperature raw: `[33, 35, 35, 34, 35, 35]`
- Right fault raw: `[0, 0, 0, 0, 0, 0]`
- Right current raw: `[22, 11, 2, 0, 2, 1]`

Command sequence:

- `setting_left_speed=[30, 30, 30, 30, 30, 30]`
- `setting_right_speed=[30, 30, 30, 30, 30, 30]`
- `sending_left_target_pose=[255, 179, 235, 255, 255, 255]`
- `sending_right_target_pose=[255, 70, 235, 255, 255, 255]`
- `target_send_time_delta_ms=0.682`
- `returning_left_to_base_pose=[255, 179, 255, 255, 255, 255]`
- `returning_right_to_base_pose=[255, 70, 255, 255, 255, 255]`
- `return_send_time_delta_ms=0.562`

Post-motion health:

- Left temperature raw: `[34, 36, 36, 36, 36, 36]`
- Left fault raw: `[0, 0, 0, 0, 0, 0]`
- Left current raw: `[18, 0, 2, 2, 3, 5]`
- Right temperature raw: `[33, 36, 35, 34, 35, 35]`
- Right fault raw: `[0, 0, 0, 0, 0, 0]`
- Right current raw: `[18, 15, 1, 0, 4, 2]`

The script completed with `S14 dual-hand SDK motion gate completed.`

## Acceptance

Accepted from SDK/software health:

- Both hands were identified on their expected CAN interfaces.
- The planned command changed only both index raw values by `-20`.
- Both hands returned to their side-specific SDK `open` presets.
- Pre/post fault values were all zero for both hands.
- Temperature and current raw values remained stable.
- Paired target send time delta was about `0.682 ms`.
- Paired return send time delta was about `0.562 ms`.

This closes the first dual-hand low-risk synchronization gate. It does not
authorize full-hand gestures, grasping, or arm motion.
