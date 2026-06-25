#!/usr/bin/env python3
"""Run a bounded single-joint ROS move_j step for NERO.

Default mode is dry-run: read feedback, print target, and do not publish a
control command. Add --execute to publish /control/move_j.
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


class RosSingleJointStep(Node):
    def __init__(self, namespace: str) -> None:
        super().__init__("nero_ros_single_joint_step")
        ns = namespace.strip("/")
        prefix = f"/{ns}" if ns else ""
        self.joint_topic = f"{prefix}/feedback/joint_states"
        self.status_topic = f"{prefix}/feedback/arm_status"
        self.command_topic = f"{prefix}/control/move_j"
        self.estop_service = f"{prefix}/emergency_stop"

        self._joint_sample: Optional[Sample] = None
        self._status = None
        self._publisher = self.create_publisher(JointState, self.command_topic, 1)
        self.create_subscription(JointState, self.joint_topic, self._joint_cb, 1)
        if AgxArmStatus is not None:
            self.create_subscription(AgxArmStatus, self.status_topic, self._status_cb, 1)
        self._estop_client = self.create_client(Empty, self.estop_service)

    def _joint_cb(self, msg: JointState) -> None:
        if len(msg.name) == len(msg.position) and len(msg.position) >= 7:
            self._joint_sample = Sample(list(msg.name), list(msg.position), time.monotonic())

    def _status_cb(self, msg) -> None:
        self._status = msg

    def wait_sample(self, timeout: float) -> Sample:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self._joint_sample is not None:
                return self._joint_sample
        raise TimeoutError(f"No valid joint sample from {self.joint_topic} within {timeout:.1f}s")

    def wait_status(self, timeout: float) -> object:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self._status is not None:
                return self._status
        return None

    def publish_target(self, names: list[str], positions: list[float], repeats: int = 3) -> None:
        msg = JointState()
        msg.name = names
        msg.position = positions
        for _ in range(max(1, repeats)):
            msg.header.stamp = self.get_clock().now().to_msg()
            self._publisher.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.05)
            time.sleep(0.05)

    def wait_joint_target(
        self,
        joint_name: str,
        target: float,
        tolerance_rad: float,
        timeout: float,
    ) -> Sample:
        deadline = time.monotonic() + timeout
        last = None
        while rclpy.ok() and time.monotonic() < deadline:
            sample = self.wait_sample(timeout=0.2)
            last = sample
            idx = sample.names.index(joint_name)
            if abs(sample.positions[idx] - target) <= tolerance_rad:
                return sample
        if last is not None:
            idx = last.names.index(joint_name)
            raise TimeoutError(
                f"{joint_name} did not reach target. "
                f"last={math.degrees(last.positions[idx]):.3f} deg "
                f"target={math.degrees(target):.3f} deg"
            )
        raise TimeoutError(f"No samples while waiting for {joint_name}")

    def emergency_stop(self) -> None:
        if self._estop_client.wait_for_service(timeout_sec=0.5):
            future = self._estop_client.call_async(Empty.Request())
            rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="arm_a")
    parser.add_argument("--joint", default="joint1")
    parser.add_argument("--delta-deg", type=float, default=2.0)
    parser.add_argument("--max-delta-deg", type=float, default=2.0)
    parser.add_argument("--feedback-timeout", type=float, default=5.0)
    parser.add_argument("--motion-timeout", type=float, default=8.0)
    parser.add_argument("--tolerance-deg", type=float, default=0.3)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--no-return", dest="return_to_start", action="store_false")
    parser.add_argument("--no-estop-on-ctrl-c", dest="estop_on_ctrl_c", action="store_false")
    parser.set_defaults(return_to_start=True, estop_on_ctrl_c=True)
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


def deg_list(values: list[float]) -> list[float]:
    return [math.degrees(v) for v in values]


def format_status(status: object) -> str:
    if status is None:
        return "None"
    return (
        f"ctrl_mode={getattr(status, 'ctrl_mode', None)} "
        f"arm_status={getattr(status, 'arm_status', None)} "
        f"mode_feedback={getattr(status, 'mode_feedback', None)} "
        f"motion_status={getattr(status, 'motion_status', None)}"
    )


def main() -> int:
    args = parse_args()
    require_safe_args(args)

    rclpy.init()
    node = RosSingleJointStep(args.namespace)
    try:
        print("S10.3 NERO ROS single-joint step")
        print(f"namespace={args.namespace} execute={args.execute}")
        print(f"joint={args.joint} delta_deg={args.delta_deg}")
        sample = node.wait_sample(args.feedback_timeout)
        if args.joint not in sample.names:
            raise SystemExit(f"{args.joint} not found in feedback names: {sample.names}")

        idx = sample.names.index(args.joint)
        target = list(sample.positions)
        target[idx] += math.radians(args.delta_deg)

        print(f"feedback_topic={node.joint_topic}")
        print(f"command_topic={node.command_topic}")
        print(f"current_deg={deg_list(sample.positions)}")
        print(f"target_deg={deg_list(target)}")
        print(f"pre_status: {format_status(node.wait_status(0.5))}")

        if not args.execute:
            print("Dry run only. Add --execute after the S10.3 safety gate is confirmed.")
            return 0

        print("Publishing ROS move_j step...")
        node.publish_target(sample.names, target)
        after = node.wait_joint_target(
            args.joint,
            target[idx],
            math.radians(args.tolerance_deg),
            args.motion_timeout,
        )
        print(f"after_step_deg={deg_list(after.positions)}")

        if args.return_to_start:
            print("Returning to original joint angle...")
            node.publish_target(sample.names, sample.positions)
            back = node.wait_joint_target(
                args.joint,
                sample.positions[idx],
                math.radians(args.tolerance_deg),
                args.motion_timeout,
            )
            print(f"after_return_deg={deg_list(back.positions)}")

        print(f"final_status: {format_status(node.wait_status(0.5))}")
        print("S10.3 ROS single-joint step completed.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted by operator.", file=sys.stderr)
        if args.execute and args.estop_on_ctrl_c:
            print("Calling ROS emergency_stop service due to Ctrl-C.", file=sys.stderr)
            node.emergency_stop()
        return 130
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
