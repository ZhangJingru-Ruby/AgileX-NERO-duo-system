# S14 End-Effector Installation Plan

Status: S14.3L LinkerHand L6 read-only identification pending; AgileX Revo2 path is no longer the preferred hand path.

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

Actual S14.0 result on 2026-06-29:

- Operator archived cable photos:
  - `docs/pics/S14自然状态线束.jpeg`.
  - `docs/pics/S14手腕弯折状态线束.jpeg`.
- Left/right hand mapping is confirmed:
  - Arm A: right dexterous hand.
  - Arm B: left dexterous hand.
- Both hands are mechanically stable after installation.
- Cable routing still constrains J6/J7, but the operator reports no interference
  as long as wrist/cable bending does not exceed about `70 deg`.

S14.0 is accepted within this temporary cable boundary. It does not authorize
finger actuation, Web hand controls, or large J6/J7 wrist motion.

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

Actual S14.1 result on 2026-06-29:

- Operator confirmed ROS publisher count:
  - `/arm_a/feedback/joint_states`: `Publisher count: 1`.
  - `/arm_b/feedback/joint_states`: `Publisher count: 1`.
- Snapshot: `docs/s9_ros_snapshots/20260629_074337/`.
- `Failed capture commands: 0`.
- Arm A joint-state feedback: about `200 Hz`.
- Arm B joint-state feedback: about `200 Hz`.
- A/B `err_status: 0`.
- A/B joint-limit flags: all `false`.
- A/B joint-communication flags: all `false`.
- A/B `arm_status=3`; upstream documentation maps this value to `奇异点`
  / `SINGULARITY_POINT`.
- A/B `motion_status=1`; upstream documentation maps this value to not reached
  target.
- The topic list still only contains arm feedback/control topics because this
  snapshot used the normal read-only launch with `effector_type:=none`.

Result:

- S14.1 is accepted as arm-controller read-only communication evidence after
  mechanical hand installation.
- It is not accepted as a motion-ready posture. Before any wrist, Cartesian, or
  finger motion, S14 must either move to or explicitly accept a non-problematic
  posture under a separate gate.

### S14.2 Model And Parameter Decision

Decide before hand motion:

- Whether Web end-effector type is changed, and to what exact value.
- Whether ROS drivers use `effector_type:=revo2`.
- Which `revo2_type` is used for RViz/model per arm:
  - Arm A: `right`.
  - Arm B: `left`.
- Load mode and TCP offset after hand installation.
- Whether hand status is checked through ROS or SDK first.

Actual S14.2 decision on 2026-06-29:

- Keep the global/default arm-only ROS configuration as `effector_type:=none`.
  This preserves the already accepted S9-S13 arm-only regression path.
- For S14 hand read-only only, use a dedicated launch path with
  `effector_type:=revo2`.
- Use the current physical/model mapping:
  - Arm A: right Revo2 hand, model `revo2_type:=right` where a model launch
    needs that argument.
  - Arm B: left Revo2 hand, model `revo2_type:=left` where a model launch needs
    that argument.
- Do not use Web dexterous-hand controls yet.
- Do not publish ROS `/control/hand` or `/control/hand_position_time` yet.
- Keep TCP offset at zero for read-only checks. This is not a final manipulation
  TCP calibration.
- Keep the current load/TCP state out of motion acceptance until the hand mass,
  center of gravity, and TCP are measured or explicitly accepted.
- Because S14.1 observed A/B `arm_status=3` / singularity, do not start wrist,
  Cartesian, or finger motion from the current posture without a separate
  posture/safety gate.

### S14.3 Hand Read-Only

Goal:
Read hand status without finger motion.

Accept only if:

- Revo2/hand status topic or SDK status is present for the selected arm.
- Hand left/right flag matches the physical mapping where available.
- No motor blocked/over-current/over-temperature/error state is reported.
- Feedback frequency is stable enough to trust before motion.

First S14.3 attempt on 2026-06-29:

- Operator started the usual dual-arm read-only script with a host-side
  `NERO_EFFECTOR_TYPE=revo2` assignment.
- The ROS driver logs still printed `effector_type: none` for both arms.
- `ros2 topic list` contained no `hand` topics.
- Interpretation: this is not evidence of Revo2 hardware feedback failure. The
  host-side environment override was not passed into the Docker container, and
  the container-side script sourced `config/nero.env`, whose global default is
  still `NERO_EFFECTOR_TYPE="none"`.

Corrected S14.3 retry path:

- Use `scripts/launch_s14_dual_revo2_readonly.sh`.
- The corrected driver terminal must print `effector_type=revo2` in the script
  banner and `effector_type: revo2` in both driver logs.
- Expected topic evidence after startup:
  - `/arm_a/feedback/hand_status`
  - `/arm_b/feedback/hand_status`
  - `/arm_a/control/hand` and/or `/arm_a/control/hand_position_time` may appear
    as advertised control endpoints, but they must not be published to in
    S14.3.
  - `/arm_b/control/hand` and/or `/arm_b/control/hand_position_time` may appear
    as advertised control endpoints, but they must not be published to in
    S14.3.

Corrected S14.3 observation on 2026-06-29:

- The corrected Revo2 launch exposed the expected ROS endpoints:
  - `/arm_a/feedback/hand_status`
  - `/arm_b/feedback/hand_status`
  - `/arm_a/control/hand`
  - `/arm_a/control/hand_position_time`
  - `/arm_b/control/hand`
  - `/arm_b/control/hand_position_time`
- `ros2 topic echo --once /arm_a/feedback/hand_status` waited without output.

Interpretation:

- The ROS graph has switched into the Revo2 software path.
- A visible `hand_status` topic is not yet proof of physical hand feedback.
- Upstream code publishes `feedback/hand_status` only after the SDK has a
  non-empty `get_hand_status()` result.
- The upstream pyAgxArm Revo2 virtual CAN test models Revo2 feedback as a reply
  after host `0x1Bx` command frames, not as a proven periodic no-command
  stream. Therefore, no output from a strict no-command `echo --once` may mean
  either no passive feedback is expected, or that the physical hand feedback
  path is not yet active.

Next read-only probe:

- Use `scripts/s14_revo2_hand_status_probe.sh` instead of raw
  `ros2 topic echo --once` so the check has a bounded timeout and explicit
  result.
- Do not publish `/control/hand` or `/control/hand_position_time` until a
  separate S14.4 motion/safety gate is written and accepted.

### S14.3b LinkerHand SDK Source Review

New field information on 2026-06-29:

- The two installed hands were previously debugged with
  `https://github.com/LV-Robotics-Lab/linkerhand_sdk`.
- This SDK should be treated as the preferred hand-side software reference once
  its source is available locally and reviewed.

Current access status:

- Initial direct clone was blocked because GitHub requested credentials.
- The operator downloaded the source tree manually.
- The local source is now stored at `upstream/linkerhand_sdk/`.
- The local copy is a downloaded tree, not a git clone, so no commit hash is
  available locally.

Decision:

- Pause any attempt to solve the hand through AgileX `effector_type:=revo2`
  control commands.
- Do not publish to AgileX ROS `/control/hand` or
  `/control/hand_position_time` while LinkerHand source review is pending.
- Review result is recorded in `docs/s14_linkerhand_sdk_review.md`.

Key review findings:

- The installed hands should be treated as LinkerHand `L6` unless later evidence
  proves otherwise.
- The SDK expects direct CAN communication, not AgileX Revo2 ROS feedback:
  - left hand default CAN: `can0`;
  - right hand default CAN: `can1`;
  - CAN bitrate: `1000000`;
  - left hand CAN ID: `0x28`;
  - right hand CAN ID: `0x27`.
- Expected serials from the local README:
  - left: `LHL6-03-253-L-B-1-C`;
  - right: `LHL6-03-240-R-B-1-C`.
- LinkerHand L6 pose/state order is
  `[thumb_flex, thumb_abduct, index, middle, ring, pinky]`, each `0..255`.
- The local wrapper provides `get_state`, `get_current`, `get_torque`,
  `get_temperature`, `get_fault`, and `get_serial_number`.

Updated S14.3 decision:

- Replace the Revo2 hand-read-only gate with `S14.3L LinkerHand read-only
  identification`.
- Stop using AgileX Revo2 ROS `feedback/hand_status` as the primary evidence for
  these hands.
- Do not run `find_linker_hand.sh` blindly because it scans every CAN interface
  and sends `0FF#C0`; arm CAN interfaces may also be present.
- Identify actual hand CAN interfaces first, preferably using targeted
  interface checks against known hand CAN ports.
- Do not run `test_hand.py`, `gestures.py`, `diagnose.py`, or `dual_gui.py`
  before a separate S14.4 motion gate; those tools can command finger movement.

S14.3L is accepted only after LinkerHand read-only evidence records:

- detected left/right CAN interface mapping;
- serial numbers matching the expected left/right devices;
- firmware/version data;
- state/current/temperature/fault data;
- no active hand fault condition.

Field update on 2026-06-29:

- Operator reported the available hand-side cable has been connected.
- Next action is to identify the hand CAN interface without scanning arm CAN
  interfaces.
- Use `scripts/s14_linkerhand_identify_can.sh <can_iface>` for targeted
  LinkerHand identification after the candidate hand CAN interface is known and
  UP at `1000000` bitrate.
- The script refuses to run on `can_arm_a` or `can_arm_b` unless
  `--allow-arm-can` is explicitly supplied. Do not use that override before a
  documented bus review.

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
