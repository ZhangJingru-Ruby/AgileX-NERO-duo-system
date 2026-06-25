# S10.8 Dual-Arm First-Motion Closure

Status: accepted on 2026-06-25.

S10.8 closes the first low-speed motion phase after both arms passed Web, SDK,
and ROS single-joint motion with post-motion read-only validation.

## Evidence Summary

Arm A:

- S10.1 Web first motion accepted.
- S10.2 SDK J1 `+2 deg` accepted.
- S10.3 ROS `joint1 +2 deg` accepted.
- Post-ROS snapshot: `docs/s9_ros_snapshots/20260625_064243/`.

Arm B:

- S10.5 Web J1 `+2 deg` accepted.
- S10.6 SDK J1 `+2 deg` accepted.
- S10.7 ROS `joint1 +2 deg` accepted.
- Post-ROS snapshot: `docs/s9_ros_snapshots/20260625_074953/`.

Final control-source audit:

- Saved output: `docs/s10_8_control_source_audit_live_20260625_155538.txt`.
- `can_arm_a`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- `can_arm_b`: UP, LOWER_UP, ERROR-ACTIVE, bitrate `1000000`.
- NERO-related Docker containers: none.
- NERO-related host processes: none.

## Acceptance Criteria

- Both arms have passed Web, SDK, and ROS low-speed single-joint motion.
- Post-motion read-only snapshots for both arms are clean.
- No Web, SDK, or ROS motion process remains active.
- CAN interfaces may remain UP for the next phase.
- Broader motion remains blocked until the next phase plan is accepted.

## Result

S10 is complete.

The system is ready to enter S11 dual-arm experiment baseline and coordinate
closure. Do not proceed directly to dual-arm coordination, Cartesian motion,
MoveIt execution, or dexterous-hand actuation without the S11/S12 gates.
