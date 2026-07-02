# S15 Left Dry-Run Script Bugfix

Date: 2026-07-02

## Context

The first S15 left-side dry-run was attempted with:

```bash
NERO_CONTAINER_NAME=nero-humble-s15-left-dryrun \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_arm_hand_sequence.py \
      --side left
```

The script exited before reading feedback or publishing any command.

## Error

```text
AttributeError: can't set attribute 'publishers'
```

The failure occurred during `S15ArmHandNode` initialization.

## Cause

`rclpy.node.Node` already exposes a read-only `publishers` attribute. The S15
script attempted to assign `self.publishers = {}`, causing the initialization
failure.

## Fix

Renamed internal members:

- `self.publishers` -> `self._move_publishers`
- `self.estop_clients` -> `self._estop_clients`

## Safety Assessment

No arm or hand command was sent. The failure happened before ROS publishers were
used and before any LinkerHand SDK connection or motion sequence.

## Verification

Local static checks passed:

```bash
python3 -m py_compile scripts/ros_s15_arm_hand_sequence.py
git diff --check
```

## Next Gate

Retry the same S15 left-side dry-run command. It remains a dry-run because
`--execute` is not supplied.
