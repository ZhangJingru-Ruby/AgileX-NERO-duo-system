#!/usr/bin/env python3
"""Run one low-risk S13 dual-arm joint-space step.

Default mode is dry-run: read both arms, print both target vectors, and monitor
a short hold period. Add --execute only after the S13 safety gate is confirmed
and the dual-active driver pair is running.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from dataclasses import dataclass
from typing import Optional

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import Empty

try:
    from agx_arm_msgs.msg import AgxArmStatus
except Exception:  # pragma: no cover - script is run inside ROS container
    AgxArmStatus = None


ARMS = ("arm_a", "arm_b")


@dataclass
class Sample:
    names: list[str]
    positions: list[float]
    stamp: float


class S13SafetyError(RuntimeError):
    pass


class S13DualJointStep(Node):
    def __init__(self, arm_a_ns: str, arm_b_ns: str) -> None:
        super().__init__("nero_s13_dual_joint_step")
        self.namespaces = {
            "arm_a": arm_a_ns.strip("/"),
            "arm_b": arm_b_ns.strip("/"),
        }
        self.samples: dict[str, Optional[Sample]] = {arm: None for arm in ARMS}
        self.statuses: dict[str, object] = {arm: None for arm in ARMS}
        self.command_publishers = {}
        self.estop_clients = {}

        for arm, ns in self.namespaces.items():
            prefix = f"/{ns}" if ns else ""
            self.create_subscription(
                JointState,
                f"{prefix}/feedback/joint_states",
                self._make_joint_cb(arm),
                1,
            )
            if AgxArmStatus is not None:
                self.create_subscription(
                    AgxArmStatus,
                    f"{prefix}/feedback/arm_status",
                    self._make_status_cb(arm),
                    1,
                )
            self.command_publishers[arm] = self.create_publisher(
                JointState, f"{prefix}/control/move_j", 1
            )
            self.estop_clients[arm] = self.create_client(Empty, f"{prefix}/emergency_stop")

    def _make_joint_cb(self, arm: str):
        def cb(msg: JointState) -> None:
            if len(msg.name) == len(msg.position) and len(msg.position) >= 7:
                self.samples[arm] = Sample(list(msg.name), list(msg.position), time.monotonic())

        return cb

    def _make_status_cb(self, arm: str):
        def cb(msg) -> None:
            self.statuses[arm] = msg

        return cb

    def wait_samples(self, timeout: float) -> dict[str, Sample]:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if all(self.samples[arm] is not None for arm in ARMS):
                return {arm: self.samples[arm] for arm in ARMS}  # type: ignore[return-value]
        missing = [arm for arm, sample in self.samples.items() if sample is None]
        raise TimeoutError(f"No valid joint sample for {missing} within {timeout:.1f}s")

    def spin_for_status(self, duration: float) -> None:
        deadline = time.monotonic() + duration
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)

    def monitor_hold(
        self,
        starts: dict[str, list[float]],
        seconds: float,
        tolerance_rad: float,
    ) -> dict[str, float]:
        max_dev = {arm: 0.0 for arm in ARMS}
        deadline = time.monotonic() + seconds
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            for arm in ARMS:
                sample = self.samples[arm]
                if sample is None:
                    continue
                dev = max(
                    abs(current - start)
                    for current, start in zip(sample.positions, starts[arm])
                )
                max_dev[arm] = max(max_dev[arm], dev)
                if max_dev[arm] > tolerance_rad:
                    raise S13SafetyError(
                        f"{arm} moved during hold: "
                        f"{math.degrees(max_dev[arm]):.3f} deg, "
                        f"limit={math.degrees(tolerance_rad):.3f} deg"
                    )
        return max_dev

    def publish_targets(
        self,
        names: dict[str, list[str]],
        positions: dict[str, list[float]],
        repeats: int = 3,
    ) -> None:
        msgs = {}
        for arm in ARMS:
            msg = JointState()
            msg.name = names[arm]
            msg.position = positions[arm]
            msgs[arm] = msg

        for _ in range(max(1, repeats)):
            stamp = self.get_clock().now().to_msg()
            for arm in ARMS:
                msgs[arm].header.stamp = stamp
                self.command_publishers[arm].publish(msgs[arm])
            rclpy.spin_once(self, timeout_sec=0.05)
            time.sleep(0.05)

    def wait_dual_targets(
        self,
        joint_name: str,
        targets: dict[str, float],
        starts: dict[str, list[float]],
        target_tolerance_rad: float,
        non_target_tolerance_rad: float,
        timeout: float,
    ) -> tuple[dict[str, Sample], dict[str, float]]:
        deadline = time.monotonic() + timeout
        max_non_target_dev = {arm: 0.0 for arm in ARMS}
        last_samples: dict[str, Optional[Sample]] = {arm: None for arm in ARMS}

        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if any(self.samples[arm] is None for arm in ARMS):
                continue

            reached = {}
            for arm in ARMS:
                sample = self.samples[arm]
                assert sample is not None
                last_samples[arm] = sample
                idx = sample.names.index(joint_name)

                non_target_dev = max(
                    abs(current - start)
                    for joint_idx, (current, start) in enumerate(
                        zip(sample.positions, starts[arm])
                    )
                    if joint_idx != idx
                )
                max_non_target_dev[arm] = max(max_non_target_dev[arm], non_target_dev)
                if max_non_target_dev[arm] > non_target_tolerance_rad:
                    raise S13SafetyError(
                        f"{arm} non-target joint moved "
                        f"{math.degrees(max_non_target_dev[arm]):.3f} deg, "
                        f"limit={math.degrees(non_target_tolerance_rad):.3f} deg"
                    )

                reached[arm] = abs(sample.positions[idx] - targets[arm]) <= target_tolerance_rad

            if all(reached.values()):
                return {arm: self.samples[arm] for arm in ARMS}, max_non_target_dev  # type: ignore[return-value]

        details = []
        for arm in ARMS:
            sample = last_samples[arm]
            if sample is None:
                details.append(f"{arm}=no sample")
                continue
            idx = sample.names.index(joint_name)
            details.append(
                f"{arm} last={math.degrees(sample.positions[idx]):.3f} deg "
                f"target={math.degrees(targets[arm]):.3f} deg"
            )
        raise TimeoutError("Dual target wait timed out: " + "; ".join(details))

    def emergency_stop_all(self) -> None:
        for arm, client in self.estop_clients.items():
            if client.wait_for_service(timeout_sec=0.3):
                future = client.call_async(Empty.Request())
                rclpy.spin_until_future_complete(self, future, timeout_sec=0.8)
                print(f"Called {arm} emergency_stop service.", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm-a-namespace", default="arm_a")
    parser.add_argument("--arm-b-namespace", default="arm_b")
    parser.add_argument("--joint", default="joint1")
    parser.add_argument("--arm-a-delta-deg", type=float, default=30.0)
    parser.add_argument("--arm-b-delta-deg", type=float, default=-30.0)
    parser.add_argument("--max-delta-deg", type=float, default=30.0)
    parser.add_argument("--feedback-timeout", type=float, default=5.0)
    parser.add_argument("--hold-seconds", type=float, default=3.0)
    parser.add_argument("--hold-tolerance-deg", type=float, default=1.0)
    parser.add_argument("--motion-timeout", type=float, default=15.0)
    parser.add_argument("--target-tolerance-deg", type=float, default=0.7)
    parser.add_argument("--non-target-tolerance-deg", type=float, default=1.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--no-return", dest="return_to_start", action="store_false")
    parser.add_argument("--no-estop-on-error", dest="estop_on_error", action="store_false")
    parser.set_defaults(return_to_start=True, estop_on_error=True)
    return parser.parse_args()


def require_safe_args(args: argparse.Namespace) -> None:
    if not args.joint.startswith("joint"):
        raise SystemExit("--joint must be like joint1")
    if args.max_delta_deg <= 0:
        raise SystemExit("--max-delta-deg must be positive")
    for label, delta in {
        "arm_a": args.arm_a_delta_deg,
        "arm_b": args.arm_b_delta_deg,
    }.items():
        if abs(delta) > args.max_delta_deg:
            raise SystemExit(
                f"Refusing {label} delta {delta} deg; "
                f"max allowed is {args.max_delta_deg} deg"
            )
    if args.hold_seconds < 0:
        raise SystemExit("--hold-seconds must be non-negative")
    if args.hold_tolerance_deg <= 0:
        raise SystemExit("--hold-tolerance-deg must be positive")
    if args.non_target_tolerance_deg <= 0:
        raise SystemExit("--non-target-tolerance-deg must be positive")
    if not args.return_to_start:
        raise SystemExit("S13 first dual-arm step must return to start; do not use --no-return")


def deg_list(values: list[float]) -> list[float]:
    return [math.degrees(v) for v in values]


def deg_dict(values: dict[str, float]) -> dict[str, float]:
    return {arm: math.degrees(value) for arm, value in values.items()}


def format_status(status: object) -> str:
    if status is None:
        return "None"
    return (
        f"ctrl_mode={getattr(status, 'ctrl_mode', None)} "
        f"arm_status={getattr(status, 'arm_status', None)} "
        f"mode_feedback={getattr(status, 'mode_feedback', None)} "
        f"motion_status={getattr(status, 'motion_status', None)} "
        f"err_status={getattr(status, 'err_status', None)}"
    )


def build_targets(
    samples: dict[str, Sample],
    joint_name: str,
    arm_a_delta_deg: float,
    arm_b_delta_deg: float,
) -> tuple[dict[str, list[float]], dict[str, int]]:
    deltas = {
        "arm_a": math.radians(arm_a_delta_deg),
        "arm_b": math.radians(arm_b_delta_deg),
    }
    targets = {}
    indices = {}
    for arm in ARMS:
        sample = samples[arm]
        if joint_name not in sample.names:
            raise SystemExit(f"{joint_name} not found in {arm}: {sample.names}")
        idx = sample.names.index(joint_name)
        indices[arm] = idx
        target = list(sample.positions)
        target[idx] += deltas[arm]
        targets[arm] = target
    return targets, indices


def main() -> int:
    args = parse_args()
    require_safe_args(args)

    rclpy.init()
    node = S13DualJointStep(args.arm_a_namespace, args.arm_b_namespace)
    try:
        print("S13 NERO ROS dual-arm joint-space step")
        print(f"execute={args.execute}")
        print(
            f"joint={args.joint} "
            f"arm_a_delta_deg={args.arm_a_delta_deg} "
            f"arm_b_delta_deg={args.arm_b_delta_deg}"
        )
        print(
            "limits: "
            f"max_delta_deg={args.max_delta_deg} "
            f"hold_seconds={args.hold_seconds} "
            f"hold_tolerance_deg={args.hold_tolerance_deg} "
            f"target_tolerance_deg={args.target_tolerance_deg} "
            f"non_target_tolerance_deg={args.non_target_tolerance_deg}"
        )

        samples = node.wait_samples(args.feedback_timeout)
        targets, indices = build_targets(
            samples,
            args.joint,
            args.arm_a_delta_deg,
            args.arm_b_delta_deg,
        )
        starts = {arm: list(samples[arm].positions) for arm in ARMS}
        target_joint_goals = {
            arm: targets[arm][indices[arm]]
            for arm in ARMS
        }

        node.spin_for_status(0.5)
        for arm in ARMS:
            print(f"{arm}_current_deg={deg_list(samples[arm].positions)}")
            print(f"{arm}_target_deg={deg_list(targets[arm])}")
            print(f"{arm}_status: {format_status(node.statuses[arm])}")

        hold_dev = node.monitor_hold(
            starts,
            args.hold_seconds,
            math.radians(args.hold_tolerance_deg),
        )
        print(f"hold_max_dev_deg={deg_dict(hold_dev)}")

        if not args.execute:
            print("Dry run only. Add --execute after the S13 safety gate is confirmed.")
            return 0

        print("Publishing dual-arm move_j step...")
        names = {arm: samples[arm].names for arm in ARMS}
        node.publish_targets(names, targets)
        after_step, max_non_target_step = node.wait_dual_targets(
            args.joint,
            target_joint_goals,
            starts,
            math.radians(args.target_tolerance_deg),
            math.radians(args.non_target_tolerance_deg),
            args.motion_timeout,
        )
        for arm in ARMS:
            print(f"after_step_{arm}_deg={deg_list(after_step[arm].positions)}")
        print(f"max_non_target_dev_step_deg={deg_dict(max_non_target_step)}")

        print("Returning both arms to original joint angles...")
        node.publish_targets(names, starts)
        start_joint_goals = {arm: starts[arm][indices[arm]] for arm in ARMS}
        after_return, max_non_target_return = node.wait_dual_targets(
            args.joint,
            start_joint_goals,
            starts,
            math.radians(args.target_tolerance_deg),
            math.radians(args.non_target_tolerance_deg),
            args.motion_timeout,
        )
        max_non_target_total = {
            arm: max(max_non_target_step[arm], max_non_target_return[arm])
            for arm in ARMS
        }
        for arm in ARMS:
            print(f"after_return_{arm}_deg={deg_list(after_return[arm].positions)}")
        print(f"max_non_target_dev_total_deg={deg_dict(max_non_target_total)}")

        node.spin_for_status(0.5)
        for arm in ARMS:
            print(f"final_{arm}_status: {format_status(node.statuses[arm])}")
        print("S13 dual-arm joint-space step completed.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted by operator.", file=sys.stderr)
        if args.execute and args.estop_on_error:
            node.emergency_stop_all()
        return 130
    except Exception as exc:
        print(f"S13 dual-arm joint-space step failed: {exc}", file=sys.stderr)
        if args.execute and args.estop_on_error:
            node.emergency_stop_all()
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
