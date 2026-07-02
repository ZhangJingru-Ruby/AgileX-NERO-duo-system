#!/usr/bin/env python3
"""S15 human-like elbow-curl/fist demo using verified joint deltas.

This script is for the field-discovered demo mapping:

- left side defaults to Arm B + left LinkerHand
- arm motion defaults to J1 -2 deg and J4 +2 deg for a small probe
- formal demo can use J1 -10 deg and J4 +10 deg after the probe is accepted

It defaults to dry-run and returns the arm to the starting posture after execute.
"""

from __future__ import annotations

import argparse
import math
import threading
import time
from typing import Any

import rclpy

from ros_s15_arm_hand_sequence import (  # noqa: E402
    ARMS,
    JOINT_LIMITS_DEG,
    PRESETS,
    SIDE_TO_ARM,
    SIDE_TO_CAN_DEFAULT,
    S15ArmHandNode,
    S15SafetyError,
    build_waypoints,
    close_sdk_bus,
    deg_list,
    format_status,
    query_hand_health,
    require_arm_status_ok,
    require_can_interface,
    LinkerHandApi,
)


DEMO_JOINTS = ("joint1", "joint4")
MAX_DEMO_DELTA_DEG = 25.0
J1_LAB_WORLD_X_TO_RAW_SIGN = {
    # The arms face each other. Operator validation showed that the same raw
    # J1 sign rotates Arm A and Arm B in opposite lab_world X directions.
    "arm_a": -1.0,
    "arm_b": 1.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side", choices=["left", "right", "both"], default="left")
    parser.add_argument("--arm-a-namespace", default="arm_a")
    parser.add_argument("--arm-b-namespace", default="arm_b")
    parser.add_argument("--left-can", default=SIDE_TO_CAN_DEFAULT["left"])
    parser.add_argument("--right-can", default=SIDE_TO_CAN_DEFAULT["right"])
    parser.add_argument("--j1-delta-deg", type=float, default=-2.0)
    parser.add_argument("--j1-delta-frame", choices=["lab-world-x", "raw-joint"], default="lab-world-x")
    parser.add_argument("--j4-delta-deg", type=float, default=2.0)
    parser.add_argument("--left-j1-delta-deg", type=float)
    parser.add_argument("--right-j1-delta-deg", type=float)
    parser.add_argument("--left-j4-delta-deg", type=float)
    parser.add_argument("--right-j4-delta-deg", type=float)
    parser.add_argument("--arm-profile", choices=["segmented", "single-target"], default="segmented")
    parser.add_argument("--max-step-deg", type=float, default=2.0)
    parser.add_argument("--waypoint-dwell", type=float, default=0.5)
    parser.add_argument("--wide-motion-threshold-deg", type=float, default=5.0)
    parser.add_argument("--allow-wide-motion", action="store_true")
    parser.add_argument("--feedback-timeout", type=float, default=5.0)
    parser.add_argument("--command-subscriber-timeout", type=float, default=2.0)
    parser.add_argument("--motion-timeout", type=float, default=20.0)
    parser.add_argument("--target-tolerance-deg", type=float, default=1.2)
    parser.add_argument("--passive-tolerance-deg", type=float, default=1.0)
    parser.add_argument("--non-commanded-tolerance-deg", type=float, default=1.5)
    parser.add_argument("--hold-seconds", type=float, default=1.5)
    parser.add_argument("--skip-hand", action="store_true")
    parser.add_argument("--hand-speed", type=int, default=20)
    parser.add_argument("--hand-dwell", type=float, default=1.2)
    parser.add_argument("--hand-timing", choices=["after-curl", "during-curl"], default="after-curl")
    parser.add_argument("--hand-start-delay", type=float, default=0.4)
    parser.add_argument("--hand-close-fraction", type=float, default=0.5)
    parser.add_argument("--allow-full-fist", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-clearance", action="store_true")
    parser.add_argument("--confirm-rviz-visible", action="store_true")
    return parser.parse_args()


def selected_sides(args: argparse.Namespace) -> list[str]:
    if args.side == "both":
        return ["left", "right"]
    return [args.side]


def side_j1_delta_deg(args: argparse.Namespace, side: str) -> float:
    if side == "left" and args.left_j1_delta_deg is not None:
        return args.left_j1_delta_deg
    if side == "right" and args.right_j1_delta_deg is not None:
        return args.right_j1_delta_deg
    return args.j1_delta_deg


def side_j4_delta_deg(args: argparse.Namespace, side: str) -> float:
    if side == "left" and args.left_j4_delta_deg is not None:
        return args.left_j4_delta_deg
    if side == "right" and args.right_j4_delta_deg is not None:
        return args.right_j4_delta_deg
    return args.j4_delta_deg


def side_can(args: argparse.Namespace, side: str) -> str:
    return args.left_can if side == "left" else args.right_can


def require_safe_args(args: argparse.Namespace) -> None:
    if args.max_step_deg <= 0 or args.max_step_deg > 5:
        raise SystemExit("--max-step-deg must be in (0, 5] for the slow elbow-curl demo.")
    if args.waypoint_dwell < 0:
        raise SystemExit("--waypoint-dwell must be >= 0.")
    for side in selected_sides(args):
        if abs(side_j1_delta_deg(args, side)) > MAX_DEMO_DELTA_DEG:
            raise SystemExit(f"{side} J1 delta must be <= {MAX_DEMO_DELTA_DEG:g} deg for this demo script.")
        if abs(side_j4_delta_deg(args, side)) > MAX_DEMO_DELTA_DEG:
            raise SystemExit(f"{side} J4 delta must be <= {MAX_DEMO_DELTA_DEG:g} deg for this demo script.")
    if args.hand_start_delay < 0:
        raise SystemExit("--hand-start-delay must be >= 0.")
    if args.hand_speed < 10 or args.hand_speed > 50:
        raise SystemExit("--hand-speed must be in 10..50.")
    if args.hand_dwell < 0:
        raise SystemExit("--hand-dwell must be >= 0.")
    if args.hand_close_fraction < 0 or args.hand_close_fraction > 1:
        raise SystemExit("--hand-close-fraction must be in 0..1.")
    if args.execute and args.hand_close_fraction > 0.5 and not args.allow_full_fist:
        raise SystemExit("Full/near-full fist requires --allow-full-fist.")
    if args.execute and not args.confirm_clearance:
        raise SystemExit("Execution requires --confirm-clearance.")
    if args.execute and not args.confirm_rviz_visible:
        raise SystemExit("Execution requires --confirm-rviz-visible.")


def require_joint_limits_deg(target_summary: dict[str, float], margin_deg: float = 3.0) -> None:
    for joint, value in target_summary.items():
        low, high = JOINT_LIMITS_DEG[joint]
        if value < low + margin_deg or value > high - margin_deg:
            raise S15SafetyError(
                f"{joint} target {value:.2f} deg outside margin "
                f"[{low + margin_deg:.2f}, {high - margin_deg:.2f}]"
            )


def j1_raw_delta_deg(args: argparse.Namespace, arm: str, side: str) -> float:
    requested = side_j1_delta_deg(args, side)
    if args.j1_delta_frame == "raw-joint":
        return requested
    return J1_LAB_WORLD_X_TO_RAW_SIGN[arm] * requested


def build_demo_target(
    sample: Any,
    args: argparse.Namespace,
    arm: str,
    side: str,
) -> tuple[list[float], list[int], dict[str, float], dict[str, float]]:
    missing = [joint for joint in DEMO_JOINTS if joint not in sample.names]
    if missing:
        raise SystemExit(f"feedback is missing demo joints: {missing}")

    target = list(sample.positions)
    summary = {}
    indices = []
    command_delta_by_joint = {
        "joint1": j1_raw_delta_deg(args, arm, side),
        "joint4": side_j4_delta_deg(args, side),
    }
    for joint_name in DEMO_JOINTS:
        idx = sample.names.index(joint_name)
        target[idx] += math.radians(command_delta_by_joint[joint_name])
        indices.append(idx)
        summary[joint_name] = math.degrees(target[idx])
    require_joint_limits_deg(summary)
    return target, indices, summary, command_delta_by_joint


def max_demo_delta_deg(args: argparse.Namespace) -> float:
    max_delta = 0.0
    for side in selected_sides(args):
        max_delta = max(max_delta, abs(side_j1_delta_deg(args, side)), abs(side_j4_delta_deg(args, side)))
    return max_delta


def plan_waypoints(
    starts: dict[str, list[float]],
    targets: dict[str, list[float]],
    indices: dict[str, list[int]],
    active_arms: list[str],
    args: argparse.Namespace,
) -> list[dict[str, list[float]]]:
    if args.arm_profile == "single-target":
        return [{arm: list(targets[arm]) for arm in active_arms}]
    return build_waypoints(starts, targets, indices, active_arms, args.max_step_deg)


def print_plan(
    args: argparse.Namespace,
    active_sides: list[str],
    active_arms: list[str],
    passive_arms: list[str],
    samples: dict[str, Any],
    targets: dict[str, list[float]],
    target_summaries: dict[str, dict[str, float]],
    command_delta_by_arm: dict[str, dict[str, float]],
    waypoints: list[dict[str, list[float]]],
) -> None:
    print("S15 NERO elbow-curl/fist demo")
    print(f"execute={args.execute} side={args.side}")
    for side in active_sides:
        arm = SIDE_TO_ARM[side]
        print(f"{side}_mapping={arm}/{side_can(args, side)}")
    print("gesture_delta_definition=joint1_lab_world_x_delta + joint4_raw_delta")
    print(f"j1_delta_frame={args.j1_delta_frame}")
    print(
        "requested_delta_deg="
        f"{ {side: {'joint1': side_j1_delta_deg(args, side), 'joint4': side_j4_delta_deg(args, side)} for side in active_sides} }"
    )
    print(f"command_delta_deg={command_delta_by_arm}")
    print(f"arm_profile={args.arm_profile}")
    print(f"waypoint_count={len(waypoints)} max_step_deg={args.max_step_deg} waypoint_dwell={args.waypoint_dwell}")
    print(f"hand_sequence={'skipped' if args.skip_hand else 'open -> close -> open'}")
    if not args.skip_hand:
        print(f"hand_timing={args.hand_timing} hand_start_delay={args.hand_start_delay}")
        for side in active_sides:
            open_pose, close_pose = hand_poses(args, side)
            print(f"{side}_hand_open_pose={open_pose}")
            print(f"{side}_hand_close_fraction={args.hand_close_fraction}")
            print(f"{side}_hand_close_pose={close_pose}")
    for item in ARMS:
        print(f"{item}_current_deg={deg_list(samples[item].positions)}")
    for arm in active_arms:
        print(f"{arm}_target_summary_deg={target_summaries[arm]}")
        print(f"{arm}_target_full_deg={deg_list(targets[arm])}")
    print(f"passive_arms={passive_arms}")
    if max_demo_delta_deg(args) > args.wide_motion_threshold_deg:
        print(
            f"wide_motion_required=true threshold_deg={args.wide_motion_threshold_deg} "
            "add --allow-wide-motion for execute"
        )


def hand_poses(args: argparse.Namespace, side: str) -> tuple[list[int], list[int]]:
    open_pose = list(PRESETS["open"][side])
    fist_pose = list(PRESETS["fist"][side])
    close_pose = [
        int(round(open_value + args.hand_close_fraction * (fist_value - open_value)))
        for open_value, fist_value in zip(open_pose, fist_pose)
    ]
    return open_pose, close_pose


def prepare_hand_api(args: argparse.Namespace, side: str) -> Any:
    can_iface = side_can(args, side)
    require_can_interface(can_iface, side)
    api = LinkerHandApi(hand_type=side, hand_joint="L6", can=can_iface)
    time.sleep(0.3)
    temp, fault, current = query_hand_health(api)
    print(f"pre_{side}_hand_health temperature={temp} fault={fault} current_raw={current}")
    if any(value != 0 for value in fault):
        raise S15SafetyError(f"{side} hand has nonzero fault before demo: {fault}")

    speed = [args.hand_speed] * 6
    print(f"setting_{side}_hand_speed={speed}")
    api.set_joint_speed(speed)
    time.sleep(0.2)
    return api


def check_hand_post_health(args: argparse.Namespace, side: str, api: Any) -> None:
    temp, fault, current = query_hand_health(api)
    print(f"post_{side}_hand_health temperature={temp} fault={fault} current_raw={current}")
    if any(value != 0 for value in fault):
        raise S15SafetyError(f"{side} hand has nonzero fault after demo: {fault}")


def send_hand_open(args: argparse.Namespace, side: str, api: Any, label: str) -> None:
    open_pose, _ = hand_poses(args, side)
    print(f"{label}_{side}_hand_open={open_pose}")
    api.finger_move(open_pose)
    time.sleep(args.hand_dwell)


def send_hand_close_then_open(args: argparse.Namespace, side: str, api: Any) -> None:
    open_pose, close_pose = hand_poses(args, side)
    print(f"sending_{side}_hand_close={close_pose}")
    api.finger_move(close_pose)
    time.sleep(args.hand_dwell)

    print(f"returning_{side}_hand_open={open_pose}")
    api.finger_move(open_pose)
    time.sleep(args.hand_dwell)
    check_hand_post_health(args, side, api)


def run_hand_sequence(args: argparse.Namespace, side: str) -> None:
    api = None
    try:
        api = prepare_hand_api(args, side)
        send_hand_open(args, side, api, "sending")
        send_hand_close_then_open(args, side, api)
    finally:
        if api is not None:
            close_sdk_bus(api)


def execute_waypoints(
    args: argparse.Namespace,
    node: S15ArmHandNode,
    active_arms: list[str],
    passive_arms: list[str],
    names: dict[str, list[str]],
    starts: dict[str, list[float]],
    indices: dict[str, list[int]],
    waypoints: list[dict[str, list[float]]],
    label: str,
) -> None:
    for number, waypoint in enumerate(waypoints, start=1):
        print(f"Publishing {label} waypoint {number}/{len(waypoints)}")
        node.publish_targets(active_arms, names, waypoint)
        node.wait_for_waypoint(
            active_arms,
            passive_arms,
            waypoint,
            starts,
            indices,
            math.radians(args.target_tolerance_deg),
            math.radians(args.passive_tolerance_deg),
            math.radians(args.non_commanded_tolerance_deg),
            args.motion_timeout,
        )
        for arm in active_arms:
            sample = node.samples[arm]
            if sample is not None:
                print(f"after_{label}_waypoint_{number}_{arm}_deg={deg_list(sample.positions)}")
        time.sleep(args.waypoint_dwell)


def main() -> int:
    args = parse_args()
    require_safe_args(args)

    active_sides = selected_sides(args)
    active_arms = [SIDE_TO_ARM[side] for side in active_sides]
    passive_arms = [item for item in ARMS if item not in active_arms]

    rclpy.init()
    node = S15ArmHandNode(args.arm_a_namespace, args.arm_b_namespace)
    hand_apis: dict[str, Any] = {}
    hand_threads: list[threading.Thread] = []
    try:
        samples = node.wait_samples(args.feedback_timeout)
        node.spin_for_status(0.5)
        for item in ARMS:
            require_arm_status_ok(item, node.statuses[item])

        starts = {item: list(samples[item].positions) for item in ARMS}
        names = {item: samples[item].names for item in ARMS}
        targets = {}
        indices = {}
        target_summaries = {}
        command_delta_by_arm = {}
        for side in active_sides:
            arm = SIDE_TO_ARM[side]
            target, joint_indices, target_summary, command_delta_by_joint = build_demo_target(
                samples[arm],
                args,
                arm,
                side,
            )
            targets[arm] = target
            indices[arm] = joint_indices
            target_summaries[arm] = target_summary
            command_delta_by_arm[arm] = command_delta_by_joint

        waypoints = plan_waypoints(starts, targets, indices, active_arms, args)

        print_plan(
            args,
            active_sides,
            active_arms,
            passive_arms,
            samples,
            targets,
            target_summaries,
            command_delta_by_arm,
            waypoints,
        )
        for item in ARMS:
            print(f"{item}_status={format_status(node.statuses[item])}")
        print(f"command_subscriber_counts={node.command_subscription_counts()}")

        if not args.execute:
            print("Dry run only. Add --execute plus required safety confirmations after review.")
            return 0

        if max_demo_delta_deg(args) > args.wide_motion_threshold_deg and not args.allow_wide_motion:
            raise SystemExit(
                f"Demo delta requires {max_demo_delta_deg(args):.2f} deg max joint change. "
                "Add --allow-wide-motion after clearance review."
            )

        counts = node.wait_command_subscribers(active_arms, args.command_subscriber_timeout)
        print(f"execute_command_subscriber_counts={counts}")

        hand_errors: list[BaseException] = []
        if not args.skip_hand and args.hand_timing == "during-curl":
            for side in active_sides:
                hand_apis[side] = prepare_hand_api(args, side)
                send_hand_open(args, side, hand_apis[side], "prepositioning")

            def hand_worker(side: str, api: Any) -> None:
                try:
                    if args.hand_start_delay:
                        time.sleep(args.hand_start_delay)
                    send_hand_close_then_open(args, side, api)
                except BaseException as exc:  # pragma: no cover - operator-facing guard
                    hand_errors.append(exc)

            for side, api in hand_apis.items():
                thread = threading.Thread(target=hand_worker, args=(side, api), name=f"s15_{side}_hand_worker", daemon=True)
                hand_threads.append(thread)
                thread.start()

        execute_waypoints(args, node, active_arms, passive_arms, names, starts, indices, waypoints, "curl")
        print(f"Holding curl posture for {args.hold_seconds:.1f}s.")
        time.sleep(args.hold_seconds)

        if hand_threads:
            for thread in hand_threads:
                thread.join()
            if hand_errors:
                raise hand_errors[0]
        if hand_apis:
            for api in hand_apis.values():
                close_sdk_bus(api)
            hand_apis.clear()
        elif not args.skip_hand:
            for side in active_sides:
                run_hand_sequence(args, side)

        return_targets = {arm: starts[arm] for arm in active_arms}
        return_waypoints = plan_waypoints(targets, return_targets, indices, active_arms, args)
        execute_waypoints(args, node, active_arms, passive_arms, names, starts, indices, return_waypoints, "return")

        node.spin_for_status(0.5)
        for item in ARMS:
            print(f"final_{item}_status={format_status(node.statuses[item])}")
        print("S15 elbow-curl/fist demo completed.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted by operator.")
        return 130
    except Exception as exc:
        print(f"S15 elbow-curl/fist demo failed: {exc}")
        return 1
    finally:
        for thread in hand_threads:
            if thread.is_alive():
                thread.join(timeout=3.0)
        for api in hand_apis.values():
            close_sdk_bus(api)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
