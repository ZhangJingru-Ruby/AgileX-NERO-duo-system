# S14 Dual LinkerHand L6 Open-Anchor Result

Date: 2026-06-30

## Scope

This result records the first dual-hand SDK gate using both independent
LinkerHand CAN interfaces:

- Left hand: `can1`, serial `LHL6-03-253-L-B-1-C`
- Right hand: `can2`, serial `LHL6-03-240-R-B-1-C`

The tested command was the side-specific SDK `open` preset on both hands.

## Dry Run

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --left-can can1 \
  --right-can can2 \
  --mode open-anchor
```

Observed:

- `execute=False`
- `left_can=can1`
- `right_can=can2`
- `mode=open-anchor`
- `preset=open`
- `speed=30`
- `torque=None`
- `left_base_pose=[255, 179, 255, 255, 255, 255]`
- `right_base_pose=[255, 70, 255, 255, 255, 255]`
- `sequence=send_both_base_poses_once`

Dry-run acceptance: accepted.

## Execute

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --execute \
  --left-can can1 \
  --right-can can2 \
  --mode open-anchor
```

Observed:

- Left SDK connection: `interface='socketcan', channel='can1'`
- Left embedded version: `[2, 3, 7]`
- Left serial: `LHL6-03-253-L-B-1-C`
- Right SDK connection: `interface='socketcan', channel='can2'`
- Right embedded version: `[2, 3, 7]`
- Right serial: `LHL6-03-240-R-B-1-C`

Pre-motion health:

- Left temperature raw: `[34, 37, 36, 36, 36, 36]`
- Left fault raw: `[0, 0, 0, 0, 0, 0]`
- Left current raw: `[18, 2, 0, 4, 3, 6]`
- Right temperature raw: `[32, 35, 34, 34, 34, 34]`
- Right fault raw: `[0, 0, 0, 0, 0, 0]`
- Right current raw: `[22, 12, 0, 0, 3, 3]`

Command sequence:

- `setting_left_speed=[30, 30, 30, 30, 30, 30]`
- `setting_right_speed=[30, 30, 30, 30, 30, 30]`
- `sending_left_pose=[255, 179, 255, 255, 255, 255]`
- `sending_right_pose=[255, 70, 255, 255, 255, 255]`
- `send_time_delta_ms=0.593`

Post-motion health:

- Left temperature raw: `[34, 37, 36, 36, 36, 36]`
- Left fault raw: `[0, 0, 0, 0, 0, 0]`
- Left current raw: `[19, 1, 0, 3, 2, 5]`
- Right temperature raw: `[32, 35, 34, 34, 34, 34]`
- Right fault raw: `[0, 0, 0, 0, 0, 0]`
- Right current raw: `[22, 12, 1, 1, 3, 4]`

The script completed with `S14 dual-hand SDK motion gate completed.`

## Physical Observation

Operator reported that no visible response was observed.

Interpretation:

- This is not treated as a failure. Both hands were already near the SDK open
  preset, so sending open-anchor can produce no visible motion.
- The SDK/software health evidence is accepted.
- A full fist command is not recommended as the immediate next step because it
  is a large multi-finger motion.

## Acceptance

Accepted from SDK/software health:

- Both hands were identified on their expected CAN interfaces.
- Pre/post fault values were all zero.
- Temperature and current raw values remained stable.
- The paired command send time delta was about `0.593 ms`.

Next recommended gate:

- Use dual index-micro dry-run for visible but still low-risk synchronized
  motion.
- If more visible motion is needed, prefer `left_delta=-20` and
  `right_delta=-20` on index only before considering full-hand presets.
- Do not run fist/full gesture execute before a separate dry-run and acceptance.
