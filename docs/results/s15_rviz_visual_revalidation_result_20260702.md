# S15 RViz Visual Revalidation Result

Date: 2026-07-02

## Goal

Revalidate the S15 RViz observation chain after the raw joint-state visual
convention mismatch was diagnosed.

## Method

The operator relaunched S15 observation with the default anchored RViz path:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh
```

The default S15 path publishes RViz-only visual joint states:

- `/arm_a/visual/joint_states`
- `/arm_b/visual/joint_states`

These are generated from live raw feedback plus the S11 accepted visual
reference snapshot. They are for RViz observation only.

## Operator Result

The operator reported:

- the robot positions in RViz are correct;
- visual following is correct when the real robot moves.

## Acceptance

S15 RViz visual revalidation is accepted for the current session.

This acceptance only applies to visual observation. It does not change the
control source, joint limits, planning semantics, or calibration state.

## Next Gate

Proceed to S15 left-side dry-run only:

- selected side: `left`;
- physical mapping: Arm B + left LinkerHand L6 on `can1`;
- no `--execute`;
- observation session remains read-only.

Do not execute motion until the dry-run output is reviewed and accepted.
