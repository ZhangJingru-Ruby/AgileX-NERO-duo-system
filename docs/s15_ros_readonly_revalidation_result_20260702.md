# S15 ROS Read-Only Revalidation Result

Date: 2026-07-02

## Scope

This result records the recovery and read-only revalidation after the first S15
observation attempt failed on Arm B.

## Failure Symptom

The first active observation attempt started RViz and Arm A successfully, but
Arm B failed during active driver startup:

- `Timeout waiting for arm to enable after 5.0 seconds`
- `Failed to auto-enable the arm`
- `Failed to get firmware version`

The failure was not caused by RViz or static TF. It was isolated to the Arm B
CAN request/response path during active driver startup.

## Root Cause Found On Site

Operator diagnosis:

- The Arm B cable was loose.
- After power-on or reconnect, the arm should be given about `20 s` before
  running `timeout ... candump` or ROS validation.

Important operational lesson:

- A SocketCAN interface can be UP and ERROR-ACTIVE while the physical robot-side
  cable is loose or the arm controller is not ready yet.
- `timeout 5s candump -tz can_arm_a` or `timeout 5s candump -tz can_arm_b`
  returning no frames immediately after power-on is not by itself enough to
  prove wrong USB mapping.
- First check cable seating and wait about `20 s` after power-on/reconnect, then
  test again.

## Read-Only ROS Revalidation

After correcting the loose cable and allowing the arm to become ready, ROS topic
discovery succeeded:

```text
/arm_a/feedback/joint_states
/arm_a/feedback/arm_status
/arm_a/feedback/tcp_pose
/arm_b/feedback/joint_states
/arm_b/feedback/arm_status
/arm_b/feedback/tcp_pose
```

Joint-state feedback rates:

| Arm | Topic | Observed rate |
| --- | --- | --- |
| Arm A | `/arm_a/feedback/joint_states` | about `199.8 Hz` |
| Arm B | `/arm_b/feedback/joint_states` | about `199.8 Hz` |

The trailing message:

```text
failed to initialize wait set: the given context is not valid...
```

appeared after the `timeout 5s ros2 topic hz ...` command terminated. This is
treated as ROS shutdown noise from `timeout`, not as a feedback failure, because
the measured rates were already stable at about `200 Hz`.

## Acceptance

Accepted for S15 read-only preflight:

- Arm A and Arm B ROS feedback topics are visible.
- Arm A and Arm B joint-state feedback are both about `200 Hz`.
- The USB-C hub CAN mapping remains valid after the cable correction.
- The failed active attempt is reclassified as a physical cable/ready-time issue,
  not a confirmed A/B bus-info mapping error.

Next gate: run the S15 observation script in `--readonly` mode, then run the
left-side dry-run before any active motion.
