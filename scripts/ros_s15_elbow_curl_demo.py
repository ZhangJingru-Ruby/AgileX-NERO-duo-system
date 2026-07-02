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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side", choices=["left", "right"], default="left")
    parser.add_argument("--arm-a-namespace", default="arm_a")
    parser.add_argument("--arm-b-namespace", default="arm_b")
    parser.add_argument("--left-can", default=SIDE_TO_CAN_DEFAULT["left"])
    parser.add_argument("--right-can", default=SIDE_TO_CAN_DEFAULT["right"])
    parser.add_argument("--j1-delta-deg", type=float, default=-2.0)
    parser.add_argument("--j4-delta-deg", type=float, default=2.0)
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


def require_safe_args(args: argparse.Namespace) -> None:
    if args.max_step_deg <= 0 or args.max_step_deg > 5:
        raise SystemExit("--max-step-deg must be in (0, 5] for the slow elbow-curl demo.")
    if args.waypoint_dwell < 0:
        raise SystemExit("--waypoint-dwell must be >= 0.")
    if abs(args.j1_delta_deg) > 15 or abs(args.j4_delta_deg) > 15:
        raise SystemExit("J1/J4 deltas must be <= 15 deg for this first demo script.")
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


def build_demo_target(sample: Any, args: argparse.Namespace) -> tuple[list[float], list[int], dict[str, float]]:
    missing = [joint for joint in DEMO_JOINTS if joint not in sample.names]
    if missing:
        raise SystemExit(f"feedback is missing demo joints: {missing}")

    target = list(sample.positions)
    summary = {}
    indices = []
    delta_by_joint = {
        "joint1": args.j1_delta_deg,
        "joint4": args.j4_delta_deg,
    }
    for joint_name in DEMO_JOINTS:
        idx = sample.names.index(joint_name)
        target[idx] += math.radians(delta_by_joint[joint_name])
        indices.append(idx)
        summary[joint_name] = math.degrees(target[idx])
    require_joint_limits_deg(summary)
    return target, indices, summary


def max_demo_delta_deg(args: argparse.Namespace) -> float:
    return max(abs(args.j1_delta_deg), abs(args.j4_delta_deg))


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
    arm: str,
    passive_arms: list[str],
    samples: dict[str, Any],
    target: list[float],
    target_summary: dict[str, float],
    waypoints: list[dict[str, list[float]]],
) -> None:
    side_can = args.left_can if args.side == "left" else args.right_can
    print("S15 NERO elbow-curl/fist demo")
    print(f"execute={args.execute} side={args.side} arm={arm} hand_can={side_can}")
    print("gesture_delta_definition=joint1_delta + joint4_delta, discovered by operator Web test")
    print(f"j1_delta_deg={args.j1_delta_deg} j4_delta_deg={args.j4_delta_deg}")
    print(f"arm_profile={args.arm_profile}")
    print(f"waypoint_count={len(waypoints)} max_step_deg={args.max_step_deg} waypoint_dwell={args.waypoint_dwell}")
    print(f"hand_sequence={'skipped' if args.skip_hand else 'open -> close -> open'}")
    if not args.skip_hand:
        print(f"hand_timing={args.hand_timing} hand_start_delay={args.hand_start_delay}")
        open_pose = list(PRESETS["open"][args.side])
        fist_pose = list(PRESETS["fist"][args.side])
        close_pose = [
            int(round(open_value + args.hand_close_fraction * (fist_value - open_value)))
            for open_value, fist_value in zip(open_pose, fist_pose)
        ]
        print(f"hand_open_pose={open_pose}")
        print(f"hand_close_fraction={args.hand_close_fraction}")
        print(f"hand_close_pose={close_pose}")
    for item in ARMS:
        print(f"{item}_current_deg={deg_list(samples[item].positions)}")
    print(f"{arm}_target_summary_deg={target_summary}")
    print(f"{arm}_target_full_deg={deg_list(target)}")
    print(f"passive_arms={passive_arms}")
    if max_demo_delta_deg(args) > args.wide_motion_threshold_deg:
        print(
            f"wide_motion_required=true threshold_deg={args.wide_motion_threshold_deg} "
            "add --allow-wide-motion for execute"
        )


def hand_poses(args: argparse.Namespace) -> tuple[list[int], list[int]]:
    open_pose = list(PRESETS["open"][args.side])
    fist_pose = list(PRESETS["fist"][args.side])
    close_pose = [
        int(round(open_value + args.hand_close_fraction * (fist_value - open_value)))
        for open_value, fist_value in zip(open_pose, fist_pose)
    ]
    return open_pose, close_pose


def prepare_hand_api(args: argparse.Namespace) -> Any:
    can_iface = args.left_can if args.side == "left" else args.right_can
    require_can_interface(can_iface, args.side)
    api = LinkerHandApi(hand_type=args.side, hand_joint="L6", can=can_iface)
    time.sleep(0.3)
    temp, fault, current = query_hand_health(api)
    print(f"pre_{args.side}_hand_health temperature={temp} fault={fault} current_raw={current}")
    if any(value != 0 for value in fault):
        raise S15SafetyError(f"{args.side} hand has nonzero fault before demo: {fault}")

    speed = [args.hand_speed] * 6
    print(f"setting_{args.side}_hand_speed={speed}")
    api.set_joint_speed(speed)
    time.sleep(0.2)
    return api


def check_hand_post_health(args: argparse.Namespace, api: Any) -> None:
    temp, fault, current = query_hand_health(api)
    print(f"post_{args.side}_hand_health temperature={temp} fault={fault} current_raw={current}")
    if any(value != 0 for value in fault):
        raise S15SafetyError(f"{args.side} hand has nonzero fault after demo: {fault}")


def send_hand_open(args: argparse.Namespace, api: Any, label: str) -> None:
    open_pose, _ = hand_poses(args)
    print(f"{label}_{args.side}_hand_open={open_pose}")
    api.finger_move(open_pose)
    time.sleep(args.hand_dwell)


def send_hand_close_then_open(args: argparse.Namespace, api: Any) -> None:
    open_pose, close_pose = hand_poses(args)
    print(f"sending_{args.side}_hand_close={close_pose}")
    api.finger_move(close_pose)
    time.sleep(args.hand_dwell)

    print(f"returning_{args.side}_hand_open={open_pose}")
    api.finger_move(open_pose)
    time.sleep(args.hand_dwell)
    check_hand_post_health(args, api)


def run_hand_sequence(args: argparse.Namespace) -> None:
    api = None
    try:
        api = prepare_hand_api(args)
        send_hand_open(args, api, "sending")
        send_hand_close_then_open(args, api)
    finally:
        if api is not None:
            close_sdk_bus(api)


def execute_waypoints(
    args: argparse.Namespace,
    node: S15ArmHandNode,
    arm: str,
    passive_arms: list[str],
    names: dict[str, list[str]],
    starts: dict[str, list[float]],
    indices: dict[str, list[int]],
    waypoints: list[dict[str, list[float]]],
    label: str,
) -> None:
    for number, waypoint in enumerate(waypoints, start=1):
        print(f"Publishing {label} waypoint {number}/{len(waypoints)}")
        node.publish_targets([arm], names, waypoint)
        node.wait_for_waypoint(
            [arm],
            passive_arms,
            waypoint,
            starts,
            indices,
            math.radians(args.target_tolerance_deg),
            math.radians(args.passive_tolerance_deg),
            math.radians(args.non_commanded_tolerance_deg),
            args.motion_timeout,
        )
        sample = node.samples[arm]
        if sample is not None:
            print(f"after_{label}_waypoint_{number}_{arm}_deg={deg_list(sample.positions)}")
        time.sleep(args.waypoint_dwell)


def main() -> int:
    args = parse_args()
    require_safe_args(args)

    arm = SIDE_TO_ARM[args.side]
    passive_arms = [item for item in ARMS if item != arm]

    rclpy.init()
    node = S15ArmHandNode(args.arm_a_namespace, args.arm_b_namespace)
    hand_api = None
    hand_thread = None
    try:
        samples = node.wait_samples(args.feedback_timeout)
        node.spin_for_status(0.5)
        for item in ARMS:
            require_arm_status_ok(item, node.statuses[item])

        starts = {item: list(samples[item].positions) for item in ARMS}
        names = {item: samples[item].names for item in ARMS}
        target, joint_indices, target_summary = build_demo_target(samples[arm], args)
        targets = {arm: target}
        indices = {arm: joint_indices}
        waypoints = plan_waypoints(starts, targets, indices, [arm], args)

        print_plan(args, arm, passive_arms, samples, target, target_summary, waypoints)
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

        counts = node.wait_command_subscribers([arm], args.command_subscriber_timeout)
        print(f"execute_command_subscriber_counts={counts}")

        hand_errors: list[BaseException] = []
        if not args.skip_hand and args.hand_timing == "during-curl":
            hand_api = prepare_hand_api(args)
            send_hand_open(args, hand_api, "prepositioning")

            def hand_worker() -> None:
                try:
                    if args.hand_start_delay:
                        time.sleep(args.hand_start_delay)
                    send_hand_close_then_open(args, hand_api)
                except BaseException as exc:  # pragma: no cover - operator-facing guard
                    hand_errors.append(exc)

            hand_thread = threading.Thread(target=hand_worker, name="s15_hand_worker", daemon=True)
            hand_thread.start()

        execute_waypoints(args, node, arm, passive_arms, names, starts, indices, waypoints, "curl")
        print(f"Holding curl posture for {args.hold_seconds:.1f}s.")
        time.sleep(args.hold_seconds)

        if hand_thread is not None:
            hand_thread.join()
            if hand_errors:
                raise hand_errors[0]
        if hand_api is not None:
            close_sdk_bus(hand_api)
            hand_api = None
        elif not args.skip_hand:
            run_hand_sequence(args)

        return_waypoints = plan_waypoints(targets, {arm: starts[arm]}, indices, [arm], args)
        execute_waypoints(args, node, arm, passive_arms, names, starts, indices, return_waypoints, "return")

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
        if hand_thread is not None and hand_thread.is_alive():
            hand_thread.join(timeout=3.0)
        if hand_api is not None:
            close_sdk_bus(hand_api)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
