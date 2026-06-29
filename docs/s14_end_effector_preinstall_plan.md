# S14 End-Effector Installation Plan

Status: mechanical installation reported; no-motion verification pending.

S14 starts after S13 closed the bare-arm low-risk dual-arm primitive. Installing
the dexterous hands changes mass, TCP, cable routing, collision envelope, and
model/driver parameters. Do not reuse S13 bare-arm assumptions without
revalidation.

## Current Field State

Reported on 2026-06-29:

- Both dexterous hands are mechanically installed.
- Selected hand mapping:
  - Arm A: right dexterous hand.
  - Arm B: left dexterous hand.
- Cable routing constrains wrist motion, especially around J6 and J7.
- Operator reports the cable does not interfere when bends stay below about
  `70 deg`; larger wrist bends may pull or over-bend the cable.

The `70 deg` limit is a cable-bend observation, not a verified joint-angle
limit. Treat it as a field safety constraint until measured against actual
joint poses.

## Documented Installation Facts

From the NERO user manual and local images:

- Dexterous hand installation uses the flange path.
- The hand cable outlet should align with the flange notch center.
- The hand is fixed to the flange with four `M3x6` screws.
- The accessory power/communication cable connects to the J6 end connector.
- The end connector reference is `docs/pics/2.1.2末端连接电器说明.png`.
- The hand size and flange references are:
  - `docs/pics/4 灵巧手示意图.png`.
  - `docs/pics/5 灵巧手法兰安装示意图.png`.

From upstream ROS/SDK code:

- ROS launch supports `effector_type:=revo2`.
- NERO model variants include left/right Revo2 hand xacro files.
- The control package exposes `/feedback/hand_status`, `/control/hand`, and
  `/control/hand_position_time`.
- The SDK exposes Revo2 status and position/speed/current/time control APIs.

These capabilities are evidence that the software path exists. They do not
authorize motion before S14 gates are accepted.

## Immediate Gates

### S14.0 Mechanical And Cable Review

Accept only if:

- Left/right hand mapping is physically confirmed: Arm A right hand, Arm B left
  hand.
- All flange screws are present and tightened after orientation check.
- Cable exits are aligned with flange notches.
- Cable slack is checked across the current parked posture.
- J6/J7 cable risk is documented with photos or operator notes.
- No commanded wrist motion exceeds the cable-safe envelope.

Temporary cable rule:

- Do not command J6/J7 large wrist motions in S14.0/S14.1.
- Do not exceed the observed about `70 deg` cable-bend envelope.
- Prefer no wrist motion until a visual cable-clearance test plan is written.

### S14.1 No-Motion Read-Only Verification

Goal:
Confirm the arm controllers remain healthy after hand installation before any
finger or wrist motion.

Accept only if:

- Only one ROS feedback publisher exists per arm feedback topic.
- A/B arm status has `err_status: 0`.
- A/B joint-limit and joint-communication flags are all `false`.
- No dexterous-hand control topic is published by the test.
- No Web dexterous-hand action is used.

### S14.2 Model And Parameter Decision

Decide before hand motion:

- Whether Web end-effector type is changed, and to what exact value.
- Whether ROS drivers use `effector_type:=revo2`.
- Which `revo2_type` is used for RViz/model per arm:
  - Arm A: `right`.
  - Arm B: `left`.
- Load mode and TCP offset after hand installation.
- Whether hand status is checked through ROS or SDK first.

### S14.3 Hand Read-Only

Goal:
Read hand status without finger motion.

Accept only if:

- Revo2/hand status topic or SDK status is present for the selected arm.
- Hand left/right flag matches the physical mapping where available.
- No motor blocked/over-current/over-temperature/error state is reported.
- Feedback frequency is stable enough to trust before motion.

### S14.4 First Finger Motion

Deferred. Requires a separate dry-run/safety gate. First finger motion should be
single arm, single finger or small grouped position change, low speed/current,
with no object in the hand.

## Stop Conditions

Stop immediately if:

- Cable starts to pull, twist sharply, or rub across J6/J7.
- The installed hand does not match the expected left/right side.
- A screw or flange component shifts under hand weight.
- Web, ROS, or SDK reports non-zero error status.
- Hand feedback is missing but control commands would be sent.
- Any finger moves without an explicit S14 motion gate.
