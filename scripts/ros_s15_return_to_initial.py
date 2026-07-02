#!/usr/bin/env python3
"""Return S15 NERO arms and LinkerHand L6 hands to the initial posture.

The default arm target is the operator-accepted joint zero posture:
joint1..joint7 = 0 deg for both arms. This is a commanded joint-space posture,
not a Web zero calibration or automatic zero-setting operation.

The earlier S15 field ``park`` posture is still available as ``--pose s15-park``
for reproducing older S15 checks.
"""

from __future__ import annotations

import argparse
import math
import time
from typing import Any

import rclpy

from ros_s15_arm_hand_sequence import (  # noqa: E402
    ARMS,
    PRESETS,
    SIDE_TO_CAN_DEFAULT,
    S15ArmHandNode,
    S15SafetyError,
    build_waypoints,
    call_hands,
    close_sdk_bus,
    deg_list,
    query_hand_health,
    require_arm_status_ok,
    require_can_interface,
    format_status,
    LinkerHandApi,
)


S15_PARK_DEG = {
    # Recorded from the accepted S15 left dry-run/current posture on 2026-07-02.
    "arm_a": [2.651, -0.774, -95.039, -6.746, 92.13, -2.174, 9.687],
    "arm_b": [0.824, 0.132, 101.705, -1.078, -91.63, 0.259, -3.628],
}
ZERO_DEG = {
    "arm_a": [0.0] * 7,
    "arm_b": [0.0] * 7,
}
POSE_TARGETS_DEG = {
    "zero": ZERO_DEG,
    "s15-park": S15_PARK_DEG,
}
POSE_DEFINITIONS = {
    "zero": "all arm joints commanded to 0 deg; not Web zero calibration",
    "s15-park": "legacy S15 field park posture; not factory zero calibration",
}

JOINT_NAMES = [f"joint{i}" for i in range(1, 8)]
SIDES = ("left", "right")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=["both", "arm_a", "arm_b"], default="both")
    parser.add_argument("--pose", choices=sorted(POSE_TARGETS_DEG), default="zero")
    parser.add_argument("--arm-a-namespace", default="arm_a")
    parser.add_argument("--arm-b-namespace", default="arm_b")
    parser.add_argument("--left-can", default=SIDE_TO_CAN_DEFAULT["left"])
    parser.add_argument("--right-can", default=SIDE_TO_CAN_DEFAULT["right"])
    parser.add_argument("--skip-arms", action="store_true")
    parser.add_argument("--skip-hands", action="store_true")
    parser.add_argument("--hand-speed", type=int, default=30)
    parser.add_argument("--hand-dwell", type=float, default=1.0)
    parser.add_argument("--max-step-deg", type=float, default=10.0)
    parser.add_argument("--wide-motion-threshold-deg", type=float, default=30.0)
    parser.add_argument("--allow-wide-motion", action="store_true")
    parser.add_argument("--feedback-timeout", type=float, default=5.0)
    parser.add_argument("--command-subscriber-timeout", type=float, default=2.0)
    parser.add_argument("--motion-timeout", type=float, default=20.0)
    parser.add_argument("--target-tolerance-deg", type=float, default=1.2)
    parser.add_argument("--passive-tolerance-deg", type=float, default=1.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-clearance", action="store_true")
    parser.add_argument("--confirm-rviz-visible", action="store_true")
    return parser.parse_args()


def selected_arms(arm_arg: str) -> list[str]:
    if arm_arg == "both":
        return list(ARMS)
    return [arm_arg]


def require_safe_args(args: argparse.Namespace) -> None:
    if args.skip_arms and args.skip_hands:
        raise SystemExit("Nothing to do: do not combine --skip-arms and --skip-hands.")
    if args.max_step_deg <= 0 or args.max_step_deg > 15:
        raise SystemExit("--max-step-deg must be in (0, 15] for S15 return-to-initial.")
    if args.hand_speed < 10 or args.hand_speed > 50:
        raise SystemExit("--hand-speed must be in 10..50 for S15 return-to-initial.")
    if args.execute and not args.confirm_clearance:
        raise SystemExit("Execution requires --confirm-clearance.")
    if args.execute and not args.confirm_rviz_visible:
        raise SystemExit("Execution requires --confirm-rviz-visible.")


def max_delta_deg(starts: dict[str, list[float]], targets: dict[str, list[float]], arms: list[str]) -> float:
    value = 0.0
    for arm in arms:
        for current, target in zip(starts[arm], targets[arm]):
            value = max(value, abs(math.degrees(target - current)))
    return value


def build_targets(
    samples: dict[str, Any],
    arms: list[str],
    pose: str,
) -> tuple[dict[str, list[float]], dict[str, list[int]]]:
    targets: dict[str, list[float]] = {}
    indices: dict[str, list[int]] = {}
    pose_targets = POSE_TARGETS_DEG[pose]
    for arm in arms:
        sample = samples[arm]
        missing = [joint for joint in JOINT_NAMES if joint not in sample.names]
        if missing:
            raise SystemExit(f"{arm} feedback is missing joints: {missing}")
        target = list(sample.positions)
        arm_indices = []
        for joint_name, target_deg in zip(JOINT_NAMES, pose_targets[arm]):
            idx = sample.names.index(joint_name)
            target[idx] = math.radians(target_deg)
            arm_indices.append(idx)
        targets[arm] = target
        indices[arm] = arm_indices
    return targets, indices


def print_plan(
    args: argparse.Namespace,
    arms: list[str],
    samples: dict[str, Any] | None,
    targets: dict[str, list[float]] | None,
    max_delta: float,
    waypoint_count: int,
) -> None:
    print("S15 NERO return-to-initial")
    print(f"execute={args.execute} pose={args.pose} arms={arms} skip_arms={args.skip_arms} skip_hands={args.skip_hands}")
    print(f"pose_definition={POSE_DEFINITIONS[args.pose]}")
    print(f"hand_open_left={list(PRESETS['open']['left'])}")
    print(f"hand_open_right={list(PRESETS['open']['right'])}")
    if samples is not None and targets is not None:
        for arm in arms:
            print(f"{arm}_current_deg={deg_list(samples[arm].positions)}")
            print(f"{arm}_target_deg={deg_list(targets[arm])}")
    print(f"max_planned_joint_delta_deg={max_delta:.3f}")
    print(f"waypoint_count={waypoint_count} max_step_deg={args.max_step_deg}")
    if max_delta > args.wide_motion_threshold_deg:
        print(
            f"wide_motion_required=true threshold_deg={args.wide_motion_threshold_deg} "
            "add --allow-wide-motion for execute"
        )


def open_hands(args: argparse.Namespace) -> None:
    can_by_side = {"left": args.left_can, "right": args.right_can}
    apis: dict[str, LinkerHandApi] = {}
    try:
        for side in SIDES:
            require_can_interface(can_by_side[side], side)
        for side in SIDES:
            apis[side] = LinkerHandApi(hand_type=side, hand_joint="L6", can=can_by_side[side])
        time.sleep(0.3)

        for side, api in apis.items():
            temp, fault, current = query_hand_health(api)
            print(f"pre_{side}_hand_health temperature={temp} fault={fault} current_raw={current}")
            if any(value != 0 for value in fault):
                raise S15SafetyError(f"{side} hand has nonzero fault before open: {fault}")

        speed = [args.hand_speed] * 6
        for side, api in apis.items():
            print(f"setting_{side}_hand_speed={speed}")
            api.set_joint_speed(speed)
        time.sleep(0.2)

        open_poses = {side: list(PRESETS["open"][side]) for side in SIDES}
        print(f"sending_hand_open={open_poses}")
        send_times = call_hands(
            "return_to_initial_hand_open",
            {side: (lambda api=api, pose=open_poses[side]: api.finger_move(pose)) for side, api in apis.items()},
        )
        if len(send_times) == 2:
            print(f"hand_open_send_delta_ms={abs(send_times['left'] - send_times['right']) * 1000.0:.3f}")
        time.sleep(args.hand_dwell)

        for side, api in apis.items():
            temp, fault, current = query_hand_health(api)
            print(f"post_{side}_hand_health temperature={temp} fault={fault} current_raw={current}")
            if any(value != 0 for value in fault):
                raise S15SafetyError(f"{side} hand has nonzero fault after open: {fault}")
    finally:
        for api in apis.values():
            close_sdk_bus(api)


def execute_arm_return(
    args: argparse.Namespace,
    node: S15ArmHandNode,
    arms: list[str],
    samples: dict[str, Any],
    targets: dict[str, list[float]],
    indices: dict[str, list[int]],
) -> None:
    starts = {arm: list(samples[arm].positions) for arm in ARMS}
    names = {arm: samples[arm].names for arm in ARMS}
    passive_arms = [arm for arm in ARMS if arm not in arms]
    waypoints = build_waypoints(starts, targets, indices, arms, args.max_step_deg)

    node.wait_command_subscribers(arms, args.command_subscriber_timeout)
    for number, waypoint in enumerate(waypoints, start=1):
        print(f"Publishing return waypoint {number}/{len(waypoints)}")
        node.publish_targets(arms, names, waypoint)
        node.wait_for_waypoint(
            arms,
            passive_arms,
            waypoint,
            starts,
            indices,
            math.radians(args.target_tolerance_deg),
            math.radians(args.passive_tolerance_deg),
            math.radians(args.target_tolerance_deg),
            args.motion_timeout,
        )
        for arm in arms:
            sample = node.samples[arm]
            if sample is not None:
                print(f"after_return_waypoint_{number}_{arm}_deg={deg_list(sample.positions)}")


def main() -> int:
    args = parse_args()
    require_safe_args(args)
    arms = [] if args.skip_arms else selected_arms(args.arm)

    rclpy.init()
    node = S15ArmHandNode(args.arm_a_namespace, args.arm_b_namespace)
    try:
        samples = node.wait_samples(args.feedback_timeout)
        node.spin_for_status(0.5)
        for arm in ARMS:
            require_arm_status_ok(arm, node.statuses[arm])

        targets = None
        indices = None
        max_delta = 0.0
        waypoint_count = 0
        if arms:
            targets, indices = build_targets(samples, arms, args.pose)
            starts = {arm: list(samples[arm].positions) for arm in ARMS}
            max_delta = max_delta_deg(starts, targets, arms)
            waypoint_count = len(build_waypoints(starts, targets, indices, arms, args.max_step_deg))

        print_plan(args, arms, samples, targets, max_delta, waypoint_count)
        for arm in ARMS:
            print(f"{arm}_status={format_status(node.statuses[arm])}")
        print(f"command_subscriber_counts={node.command_subscription_counts()}")

        if not args.execute:
            print("Dry run only. Add --execute plus required safety confirmations after review.")
            return 0

        if max_delta > args.wide_motion_threshold_deg and not args.allow_wide_motion:
            raise SystemExit(
                f"Planned return requires {max_delta:.2f} deg max joint change. "
                "Add --allow-wide-motion only after clearance review."
            )

        if not args.skip_hands:
            open_hands(args)
        if arms and targets is not None and indices is not None:
            execute_arm_return(args, node, arms, samples, targets, indices)

        node.spin_for_status(0.5)
        for arm in ARMS:
            print(f"final_{arm}_status={format_status(node.statuses[arm])}")
        print("S15 return-to-initial completed.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted by operator.")
        return 130
    except Exception as exc:
        print(f"S15 return-to-initial failed: {exc}")
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
