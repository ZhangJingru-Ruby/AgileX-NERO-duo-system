#!/usr/bin/env python3
"""Publish RViz-only joint states anchored to the accepted S11 visual posture."""

import argparse
import math
from typing import Dict, Iterable, List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [f"joint{i}" for i in range(1, 8)]

# S11 accepted post-TF read-only snapshot:
# docs/evidence/ros_snapshots/20260626_055339/*_joint_states_once.txt
S11_REFERENCE_RAD = {
    "arm_a": [
        0.02429498318776107,
        1.5603068979904107,
        0.8192226443010985,
        0.023963370629882144,
        1.5049799607021903,
        0.47738245700548904,
        -0.5311560512594343,
    ],
    "arm_b": [
        -0.03469714552964727,
        1.567340574875948,
        -0.6806784082777885,
        0.09948376736367678,
        0.4568573850020357,
        -0.17996089917313532,
        0.4485147111775028,
    ],
}


def rad_to_deg(values: Iterable[float]) -> List[float]:
    return [round(math.degrees(value), 3) for value in values]


def positions_by_name(msg: JointState) -> Dict[str, float]:
    return {
        name: float(msg.position[index])
        for index, name in enumerate(msg.name)
        if index < len(msg.position)
    }


class ArmAnchor:
    def __init__(self, node: Node, arm: str, input_topic: str, output_topic: str, reference: List[float]):
        self.node = node
        self.arm = arm
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.reference = dict(zip(JOINT_NAMES, reference))
        self.offset_by_name = None
        self.publisher = node.create_publisher(JointState, output_topic, 10)
        self.subscription = node.create_subscription(
            JointState,
            input_topic,
            self._on_joint_state,
            10,
        )

    def _on_joint_state(self, msg: JointState) -> None:
        raw = positions_by_name(msg)
        missing = [name for name in JOINT_NAMES if name not in raw]
        if missing:
            self.node.get_logger().warning(
                f"{self.arm}: ignoring joint state missing required joints: {missing}"
            )
            return

        if self.offset_by_name is None:
            self.offset_by_name = {
                name: self.reference[name] - raw[name]
                for name in JOINT_NAMES
            }
            self.node.get_logger().info(
                f"{self.arm}: anchored {self.input_topic} to {self.output_topic}"
            )
            self.node.get_logger().info(
                f"{self.arm}: raw_start_deg={rad_to_deg(raw[name] for name in JOINT_NAMES)}"
            )
            self.node.get_logger().info(
                f"{self.arm}: reference_visual_deg={rad_to_deg(self.reference[name] for name in JOINT_NAMES)}"
            )
            self.node.get_logger().info(
                f"{self.arm}: visual_offset_deg={rad_to_deg(self.offset_by_name[name] for name in JOINT_NAMES)}"
            )

        out = JointState()
        out.header = msg.header
        out.name = list(msg.name)
        out.velocity = list(msg.velocity)
        out.effort = list(msg.effort)
        out.position = []
        for index, name in enumerate(msg.name):
            if index >= len(msg.position):
                break
            value = float(msg.position[index])
            if name in self.offset_by_name:
                value += self.offset_by_name[name]
            out.position.append(value)
        self.publisher.publish(out)


class S15VisualAnchorNode(Node):
    def __init__(self, args: argparse.Namespace):
        super().__init__("s15_joint_state_visual_anchor")
        self.get_logger().warning(
            "RViz visual anchoring is for observation only. Do not use visual "
            "joint-state topics for control, planning, limits, or calibration."
        )
        self.anchors = [
            ArmAnchor(
                self,
                "arm_a",
                args.arm_a_input,
                args.arm_a_output,
                S11_REFERENCE_RAD["arm_a"],
            ),
            ArmAnchor(
                self,
                "arm_b",
                args.arm_b_input,
                args.arm_b_output,
                S11_REFERENCE_RAD["arm_b"],
            ),
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Publish RViz-only visual joint states by anchoring the current live "
            "joint-state sample to the accepted S11 dual-arm visual posture."
        )
    )
    parser.add_argument("--arm-a-input", default="/arm_a/feedback/joint_states")
    parser.add_argument("--arm-b-input", default="/arm_b/feedback/joint_states")
    parser.add_argument("--arm-a-output", default="/arm_a/visual/joint_states")
    parser.add_argument("--arm-b-output", default="/arm_b/visual/joint_states")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rclpy.init()
    node = S15VisualAnchorNode(args)
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
