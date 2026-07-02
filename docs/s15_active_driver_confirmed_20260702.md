# S15 Active Driver Confirmation

Date: 2026-07-02

## Command

```bash
NERO_CONTAINER_NAME=nero-humble-s15-diagnostics \
  bash scripts/run_humble_container.sh \
    bash /workspace/nero/scripts/s15_motion_block_diagnostics.sh
```

## Result

The updated diagnostics confirmed the current observation session is using
active arm drivers:

Arm A driver parameters:

- `can_port=can_arm_a`
- `arm_type=nero`
- `auto_enable=True`
- `control_enabled=True`
- `speed_percent=5`
- `enable_timeout=5.0`

Arm B driver parameters:

- `can_port=can_arm_b`
- `arm_type=nero`
- `auto_enable=True`
- `control_enabled=True`
- `speed_percent=5`
- `enable_timeout=5.0`

Arm status for both arms:

- `ctrl_mode=1`
- `arm_status=0`
- `mode_feedback=1`
- `motion_status=0`
- `err_status=0`
- all joint-limit flags false
- all joint communication flags false

## Interpretation

The current ROS session is active and healthy. A missing command subscriber or
read-only driver mode is not the current blocker.

If Web enable was changed between the failed left execute attempt and this
diagnostic, then the likely cause of the earlier no-motion timeout is that the
arm was not enabled at the time of the execute attempt.

If Web enable was not changed, the cause is still unresolved. The next safe
check is a small Arm B ROS command-path probe before retrying the wide S15
sequence.

## Next Gate

Run a small Arm B J1 `+2 deg` command-path probe using the previously accepted
S12 isolation script:

- dry-run first;
- execute only if the dry-run is accepted;
- keep RViz visible;
- verify Arm B moves and returns while Arm A remains passive.

Do not retry the S15 wide left execute until this small command-path probe is
accepted.
