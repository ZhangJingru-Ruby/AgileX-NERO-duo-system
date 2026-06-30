# S14 Right LinkerHand L6 Open-Anchor Result

Date: 2026-06-30

## Scope

This result records the right-hand open-anchor dry-run and execute gates on
SocketCAN interface `can2`.

The right hand had already passed SDK health in
`docs/s14_right_hand_sdk_health_result_20260630.md`.

## Dry Run

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can2 \
  --side right \
  --mode open-anchor
```

Observed:

- `execute=False`
- `side=right`
- `can=can2`
- `mode=open-anchor`
- `preset=open`
- `speed=30`
- `torque=None`
- `base_pose=[255, 70, 255, 255, 255, 255]`
- `sequence=send_base_pose_once`

Dry-run acceptance: accepted.

## Execute

Command:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can2 \
  --side right \
  --mode open-anchor
```

Observed:

- SDK version: `3.1.0`
- SDK connection: `interface='socketcan', channel='can2'`
- Embedded version: `[2, 3, 7]`
- Serial: `LHL6-03-240-R-B-1-C`
- Base/open pose: `[255, 70, 255, 255, 255, 255]`

Pre-motion health:

- Temperature raw: `[30, 31, 32, 31, 31, 31]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[10, 0, 0, 3, 3, 0]`

Command sequence:

- `setting_speed=[30, 30, 30, 30, 30, 30]`
- `sending_pose=[255, 70, 255, 255, 255, 255]`

Post-motion health:

- Temperature raw: `[30, 31, 32, 31, 31, 31]`
- Fault raw: `[0, 0, 0, 0, 0, 0]`
- Current raw: `[25, 15, 1, 2, 2, 7]`

The script completed with `S14 SDK motion gate completed.`

## Physical Observation

Operator observed the right thumb, middle, ring, and pinky moving during the
open-anchor execute. The right index finger did not show visible motion.

This does not prove an index fault by itself because the open-anchor command
targets index raw value `255`; if the index was already near open, it may not
visibly move. However, the observation must be resolved before any synchronized
hand control.

## Acceptance

Accepted from SDK/software health:

- The SDK identified the expected right hand.
- The script sent exactly one right-hand open preset.
- Faults were zero before and after the command.
- Temperature remained stable.
- Current raw values did not show a persistent high-current condition.

Conditionally accepted from physical observation:

- Non-index fingers moved toward the open preset as expected.
- Right index visible motion remains unverified.

Next gate:

- Run right-hand index-micro dry-run only.
- If dry-run is correct, execute a `delta=-10` index micro-motion to determine
  whether the index joint visibly responds and returns to open.
- Do not run synchronized control, full gestures, GUI, or broader right-hand
  motions before the index observation is resolved.
