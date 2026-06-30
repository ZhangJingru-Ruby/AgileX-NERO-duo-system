# S14 Right LinkerHand L6 Reproduction Plan

Date: 2026-06-30

## Goal

Repeat the accepted left-hand independent CAN bench-test process on the right
LinkerHand L6, using the same standalone PEAK/XCAN-USB adapter and the same
project safety wrappers.

This plan does not authorize bimanual or synchronized hand control. Synchronized
control starts only after the right hand passes the same health, open-anchor,
and index-micro gates.

## Preconditions

- Left hand first-motion baseline is accepted:
  `docs/s14_left_hand_index_micro_result_20260630.md`.
- Power supply can be cut immediately.
- The right hand is disconnected from NERO J6 before bench wiring.
- Only one hand is connected to the standalone bench-test CAN/power harness at
  a time.
- Bench wiring follows the same reviewed LinkerHand L6 XT30(2+2) CAN/power
  discipline used for the left hand.
- `can1` remains the standalone PEAK/XCAN-USB interface, not `can_arm_a` or
  `can_arm_b`.
- The hand is empty and clear of tools, cables, and fingers.

Expected right-hand facts from `upstream/linkerhand_sdk`:

- Side: `right`
- CAN ID: `0x27`
- Expected serial: `LHL6-03-240-R-B-1-C`
- SDK open preset: `[255, 70, 255, 255, 255, 255]`
- Index micro target with `delta=-10`: `[255, 70, 245, 255, 255, 255]`

## S14.9R.0 Physical Rewire

1. Turn off the bench 24 V supply.
2. Disconnect the left hand from the bench-test harness.
3. Connect the right hand to the same bench-test harness.
4. Confirm CAN_H/CAN_L and VCC/GND polarity before power.
5. Power on at 24 V and observe idle current.
6. Confirm the hand is mechanically stable and empty.

Acceptance:

- No heat, smell, sound, twitching, or abnormal current after power-on.
- `can1` is still UP at `1000000`.

Check:

```bash
ip -details link show can1
```

## S14.9R.1 SDK Health

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_health.py \
  --can can1 \
  --side right
```

Acceptance:

- SDK connects to `can1`.
- Serial matches right hand, expected `LHL6-03-240-R-B-1-C`.
- Embedded version is readable.
- Fault samples are all zero.
- Temperature and current raw values are stable.
- No physical motion occurs.

## S14.9R.2 Open-Anchor Dry Run

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can1 \
  --side right \
  --mode open-anchor
```

Acceptance:

- `execute=False`.
- `base_pose=[255, 70, 255, 255, 255, 255]`.
- `sequence=send_base_pose_once`.
- No SDK motion command is sent.

## S14.9R.3 Open-Anchor Execute

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can1 \
  --side right \
  --mode open-anchor
```

Acceptance:

- Pre/post fault values are all zero.
- Temperature and current raw values are stable.
- Physical behavior is no motion or only a small open-pose correction.
- No abnormal bench supply behavior.

## S14.9R.4 Index-Micro Dry Run

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --can can1 \
  --side right \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```

Acceptance:

- `execute=False`.
- Base pose is `[255, 70, 255, 255, 255, 255]`.
- Target pose is `[255, 70, 245, 255, 255, 255]`.
- Sequence is target, then return to base.

## S14.9R.5 Index-Micro Execute

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_sdk_motion_gate.py \
  --execute \
  --can can1 \
  --side right \
  --mode index-micro \
  --joint index \
  --delta -10 \
  --speed 30
```

Acceptance:

- The right index finger makes a small expected motion and returns to open.
- Faults remain all zero before and after.
- Temperature/current remain stable.
- Bench supply remains near 24 V without abnormal current jump.

## After Right-Hand Acceptance

The next stage is synchronized control planning:

- Bring both hands to a known open preset independently.
- Decide whether synchronization is sequential dual-command through one CAN bus
  or true dual-adapter simultaneous control.
- Prefer two separate CAN adapters for real synchronization; one adapter can
  only send commands serially on one bus.
- Start with dry-run pose planning for both hands before any synchronized
  execute.
