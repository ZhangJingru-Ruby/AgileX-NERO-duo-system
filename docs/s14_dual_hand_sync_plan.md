# S14 Dual LinkerHand L6 Synchronization Plan

Date: 2026-06-30

## Goal

Start the first dual-hand coordination gates after both hands have passed
independent CAN identity and first-motion checks.

The goal is not high-performance manipulation yet. The first goal is to prove
that one project script can address the left hand on `can1` and the right hand
on `can2`, apply the correct side-specific presets, and preserve zero-fault
health before and after a very small coordinated command.

## Preconditions

- Left hand accepted:
  - `docs/s14_left_hand_index_micro_result_20260630.md`
  - Interface: `can1`
  - Serial: `LHL6-03-253-L-B-1-C`
- Right hand accepted from SDK/software health:
  - `docs/s14_right_hand_index_micro_result_20260630.md`
  - Interface: `can2`
  - Serial: `LHL6-03-240-R-B-1-C`
- Right-hand physical index response must be recorded before any dual-hand
  execute.
- No SDK GUI, demo, gesture loop, or other hand-control process may be running.
- No object is in either hand.
- Bench power and hand CAN cables are stable and easy to cut power from.

## S14.10.0 Control Source Check

Before any dual-hand execute:

```bash
bash scripts/s10_control_source_audit.sh
```

For hand-only bench testing, the important acceptance point is that no unrelated
SDK demo, GUI, or stale motion process is running. The NERO arm CAN interfaces
may remain UP but must not be used for LinkerHand commands.

## S14.10.1 Dual Open-Anchor Dry Run

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --left-can can1 \
  --right-can can2 \
  --mode open-anchor
```

Acceptance:

- `execute=False`.
- Left base pose is `[255, 179, 255, 255, 255, 255]`.
- Right base pose is `[255, 70, 255, 255, 255, 255]`.
- Sequence is `send_both_base_poses_once`.
- No SDK connection or motion command is requested by the dry-run.

## S14.10.2 Dual Open-Anchor Execute

Only after S14.10.1 is reviewed and both hands have normal physical observations:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --execute \
  --left-can can1 \
  --right-can can2 \
  --mode open-anchor
```

Acceptance:

- SDK identifies both hands.
- Pre/post faults are all zero for both hands.
- Temperature/current raw values remain stable.
- Both hands remain open or make only a small open-pose correction.
- No abnormal sound, heat, smell, vibration, or power jump occurs.
- The script reports send time delta for the paired command.

Live result:

- Accepted from SDK/software health on 2026-06-30; see
  `docs/s14_dual_open_anchor_result_20260630.md`.
- Both hands were identified on `can1` and `can2`.
- Pre/post faults were all zero.
- Send time delta was about `0.593 ms`.
- Operator did not observe visible motion, which is expected when both hands are
  already near the open preset.
- Do not jump directly to `fist`; use dual index-micro first for a visible but
  lower-risk synchronized motion check.

## S14.10.3 Dual Index-Micro Dry Run

Only after dual open-anchor execute is accepted:

```bash
.venv/nero-sdk/bin/python scripts/s14_linkerhand_l6_dual_motion_gate.py \
  --left-can can1 \
  --right-can can2 \
  --mode index-micro \
  --joint index \
  --left-delta -10 \
  --right-delta -10 \
  --speed 30
```

Acceptance:

- Left target is `[255, 179, 245, 255, 255, 255]`.
- Right target is `[255, 70, 245, 255, 255, 255]`.
- Sequence is target for both hands, then return both hands to open.

If the operator needs more visible motion for reporting, the first widened
dual-index dry-run may use `--left-delta -20 --right-delta -20`. Do not exceed
this without a separate plan.

## S14.10.4 Dual Index-Micro Execute

Deferred until S14.10.3 dry-run is accepted and the operator confirms both
hands are clear.

Live result:

- Accepted from SDK/software health on 2026-06-30; see
  `docs/s14_dual_index_micro_result_20260630.md`.
- Dry-run and execute used `--left-delta -20 --right-delta -20`.
- Left target was `[255, 179, 235, 255, 255, 255]`.
- Right target was `[255, 70, 235, 255, 255, 255]`.
- Pre/post faults were all zero.
- Temperature/current raw values remained stable.
- Target send delta was about `0.682 ms`; return send delta was about `0.562 ms`.

This closes S14.10 as the first low-risk dual-hand synchronization gate.
Further work moves to S15 dual arm + dual hand coordination planning.

## Boundaries

- This stage does not authorize grasping objects.
- This stage does not authorize full gesture sequences.
- This stage does not authorize moving the NERO arms while hand sync tests run.
- This stage does not yet prove hard real-time synchronization. The script sends
  commands through two Python threads and reports the send time delta as a
  practical first coordination metric.
