#!/usr/bin/env python3
"""Run one S12 control-isolation joint step while monitoring both arms.

Default mode is dry-run. Add --execute only after the S12 safety gate is
confirmed and the active/passive driver pair is running.
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


@dataclass
class Sample:
    names: list[str]
    positions: list[float]
    stamp: float


class IsolationError(RuntimeError):
    pass


class S12IsolationStep(Node):
    def __init__(self, arm_a_ns: str, arm_b_ns: str, target: str) -> None:
        super().__init__("nero_s12_isolation_step")
        self.namespaces = {
            "arm_a": arm_a_ns.strip("/"),
            "arm_b": arm_b_ns.strip("/"),
        }
        self.target = target
        self.passive = "arm_b" if target == "arm_a" else "arm_a"
        self.samples: dict[str, Optional[Sample]] = {"arm_a": None, "arm_b": None}
        self.statuses: dict[str, object] = {"arm_a": None, "arm_b": None}

        self.publishers = {}
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
            self.estop_clients[arm] = self.create_client(Empty, f"{prefix}/emergency_stop")
            if arm == self.target:
                self.publishers[arm] = self.create_publisher(
                    JointState, f"{prefix}/control/move_j", 1
                )

    def _make_joint_cb(self, arm: str):
        def cb(msg: JointState) -> None:
            if len(msg.name) == len(msg.position) and len(msg.position) >= 7:
                self.samples[arm] = Sample(list(msg.name), list(msg.position), time.monotonic())

        return cb

    def _make_status_cb(self, arm: str):
        def cb(msg) -> None:
            self.statuses[arm] = msg

        return cb

    def wait_samples(self, timeout: float) -> tuple[Sample, Sample]:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.samples["arm_a"] is not None and self.samples["arm_b"] is not None:
                return self.samples["arm_a"], self.samples["arm_b"]
        missing = [arm for arm, sample in self.samples.items() if sample is None]
        raise TimeoutError(f"No valid joint sample for {missing} within {timeout:.1f}s")

    def spin_for_status(self, duration: float) -> None:
        deadline = time.monotonic() + duration
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)

    def publish_target(self, names: list[str], positions: list[float], repeats: int = 3) -> None:
        msg = JointState()
        msg.name = names
        msg.position = positions
        pub = self.publishers[self.target]
        for _ in range(max(1, repeats)):
            msg.header.stamp = self.get_clock().now().to_msg()
            pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.05)
            time.sleep(0.05)

    def wait_target_and_passive(
        self,
        joint_name: str,
        target_rad: float,
        passive_start: list[float],
        target_tolerance_rad: float,
        passive_tolerance_rad: float,
        timeout: float,
    ) -> tuple[Sample, Sample, float]:
        deadline = time.monotonic() + timeout
        max_passive_dev = 0.0
        last_target = None
        last_passive = None

        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            target_sample = self.samples[self.target]
            passive_sample = self.samples[self.passive]
            if target_sample is None or passive_sample is None:
                continue

            last_target = target_sample
            last_passive = passive_sample

            passive_dev = max(
                abs(current - start)
                for current, start in zip(passive_sample.positions, passive_start)
            )
            max_passive_dev = max(max_passive_dev, passive_dev)
            if max_passive_dev > passive_tolerance_rad:
                raise IsolationError(
                    f"Passive {self.passive} moved "
                    f"{math.degrees(max_passive_dev):.3f} deg, "
                    f"limit={math.degrees(passive_tolerance_rad):.3f} deg"
                )

            idx = target_sample.names.index(joint_name)
            if abs(target_sample.positions[idx] - target_rad) <= target_tolerance_rad:
                return target_sample, passive_sample, max_passive_dev

        if last_target is not None:
            idx = last_target.names.index(joint_name)
            raise TimeoutError(
                f"{self.target} {joint_name} did not reach target. "
                f"last={math.degrees(last_target.positions[idx]):.3f} deg "
                f"target={math.degrees(target_rad):.3f} deg "
                f"max_passive_dev={math.degrees(max_passive_dev):.3f} deg"
            )
        raise TimeoutError(f"No samples while waiting for {self.target} {joint_name}")

    def emergency_stop_all(self) -> None:
        for arm, client in self.estop_clients.items():
            if client.wait_for_service(timeout_sec=0.3):
                future = client.call_async(Empty.Request())
                rclpy.spin_until_future_complete(self, future, timeout_sec=0.8)
                print(f"Called {arm} emergency_stop service.", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["arm_a", "arm_b"], required=True)
    parser.add_argument("--arm-a-namespace", default="arm_a")
    parser.add_argument("--arm-b-namespace", default="arm_b")
    parser.add_argument("--joint", default="joint1")
    parser.add_argument("--delta-deg", type=float, required=True)
    parser.add_argument("--max-delta-deg", type=float, default=30.0)
    parser.add_argument("--feedback-timeout", type=float, default=5.0)
    parser.add_argument("--motion-timeout", type=float, default=15.0)
    parser.add_argument("--target-tolerance-deg", type=float, default=0.7)
    parser.add_argument("--passive-tolerance-deg", type=float, default=1.0)
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
    if abs(args.delta_deg) > args.max_delta_deg:
        raise SystemExit(
            f"Refusing delta {args.delta_deg} deg; max allowed is {args.max_delta_deg} deg"
        )
    if args.passive_tolerance_deg <= 0:
        raise SystemExit("--passive-tolerance-deg must be positive")
    if not args.return_to_start:
        raise SystemExit("S12 first isolation tests must return to start; do not use --no-return")


def deg_list(values: list[float]) -> list[float]:
    return [math.degrees(v) for v in values]


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


def main() -> int:
    args = parse_args()
    require_safe_args(args)

    rclpy.init()
    node = S12IsolationStep(args.arm_a_namespace, args.arm_b_namespace, args.target)
    try:
        print("S12 NERO ROS control-isolation step")
        print(f"target={args.target} passive={node.passive} execute={args.execute}")
        print(f"joint={args.joint} delta_deg={args.delta_deg}")
        print(
            "limits: "
            f"max_delta_deg={args.max_delta_deg} "
            f"target_tolerance_deg={args.target_tolerance_deg} "
            f"passive_tolerance_deg={args.passive_tolerance_deg}"
        )

        arm_a_sample, arm_b_sample = node.wait_samples(args.feedback_timeout)
        samples = {"arm_a": arm_a_sample, "arm_b": arm_b_sample}
        target_sample = samples[args.target]
        passive_sample = samples[node.passive]

        if args.joint not in target_sample.names:
            raise SystemExit(f"{args.joint} not found in {args.target}: {target_sample.names}")

        idx = target_sample.names.index(args.joint)
        target_positions = list(target_sample.positions)
        target_positions[idx] += math.radians(args.delta_deg)

        node.spin_for_status(0.5)
        print(f"target_current_deg={deg_list(target_sample.positions)}")
        print(f"target_goal_deg={deg_list(target_positions)}")
        print(f"passive_current_deg={deg_list(passive_sample.positions)}")
        print(f"target_status: {format_status(node.statuses[args.target])}")
        print(f"passive_status: {format_status(node.statuses[node.passive])}")

        if not args.execute:
            print("Dry run only. Add --execute after the S12 safety gate is confirmed.")
            return 0

        passive_start = list(passive_sample.positions)
        target_start = list(target_sample.positions)
        target_goal = target_positions[idx]

        print("Publishing target-arm move_j step...")
        node.publish_target(target_sample.names, target_positions)
        after_target, after_passive, max_passive_dev = node.wait_target_and_passive(
            args.joint,
            target_goal,
            passive_start,
            math.radians(args.target_tolerance_deg),
            math.radians(args.passive_tolerance_deg),
            args.motion_timeout,
        )
        print(f"after_step_target_deg={deg_list(after_target.positions)}")
        print(f"after_step_passive_deg={deg_list(after_passive.positions)}")
        print(f"max_passive_dev_deg={math.degrees(max_passive_dev):.3f}")

        print("Returning target arm to original joint angle...")
        node.publish_target(target_sample.names, target_start)
        back_target, back_passive, max_passive_dev_return = node.wait_target_and_passive(
            args.joint,
            target_start[idx],
            passive_start,
            math.radians(args.target_tolerance_deg),
            math.radians(args.passive_tolerance_deg),
            args.motion_timeout,
        )
        max_passive_dev = max(max_passive_dev, max_passive_dev_return)
        print(f"after_return_target_deg={deg_list(back_target.positions)}")
        print(f"after_return_passive_deg={deg_list(back_passive.positions)}")
        print(f"max_passive_dev_total_deg={math.degrees(max_passive_dev):.3f}")

        node.spin_for_status(0.5)
        print(f"final_target_status: {format_status(node.statuses[args.target])}")
        print(f"final_passive_status: {format_status(node.statuses[node.passive])}")
        print("S12 isolation step completed.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted by operator.", file=sys.stderr)
        if args.execute and args.estop_on_error:
            node.emergency_stop_all()
        return 130
    except Exception as exc:
        print(f"S12 isolation step failed: {exc}", file=sys.stderr)
        if args.execute and args.estop_on_error:
            node.emergency_stop_all()
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
