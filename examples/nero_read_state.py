#!/usr/bin/env python3
"""Read NERO state through pyAgxArm without sending motion commands."""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any


def import_sdk() -> Any:
    try:
        from pyAgxArm import AgxArmFactory, ArmModel, NeroFW, create_agx_arm_config
    except Exception as exc:  # pragma: no cover - used as operator-facing script
        print(f"Failed to import pyAgxArm: {exc}", file=sys.stderr)
        print("Install it first, for example: pip3 install . inside pyAgxArm")
        raise SystemExit(2)
    return AgxArmFactory, ArmModel, NeroFW, create_agx_arm_config


def firmware_value(nero_fw: Any, name: str) -> Any:
    mapping = {
        "default": nero_fw.DEFAULT,
        "v111": nero_fw.V111,
        "v112": nero_fw.V112,
        "v120": nero_fw.V120,
    }
    return mapping[name]


def compact(value: Any) -> str:
    if value is None:
        return "None"
    msg = getattr(value, "msg", value)
    hz = getattr(value, "hz", None)
    timestamp = getattr(value, "timestamp", None)
    parts = [f"msg={msg}"]
    if hz is not None:
        parts.append(f"hz={hz}")
    if timestamp is not None:
        parts.append(f"timestamp={timestamp}")
    return ", ".join(parts)


def parse_args() -> argparse.Namespace:
    firmware_default = os.environ.get("NERO_FW", "v112")
    if firmware_default not in {"default", "v111", "v112", "v120"}:
        firmware_default = "v112"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default=os.environ.get("NERO_CAN_INTERFACE", "socketcan"))
    parser.add_argument("--channel", default=os.environ.get("NERO_CAN_PORT", "can0"))
    parser.add_argument(
        "--firmware",
        default=firmware_default,
        choices=["default", "v111", "v112", "v120"],
        help="SDK firmware selector. Confirm this against the real arm firmware.",
    )
    parser.add_argument(
        "--connect",
        action="store_true",
        help="Actually connect to the CAN interface. Without this, only config is printed.",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Call robot.enable() before reading. Does not send motion commands.",
    )
    parser.add_argument(
        "--normal-mode",
        action="store_true",
        help="Call set_normal_mode() while enabling. Usually only for firmware <= 1.11.",
    )
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--period", type=float, default=0.05)
    parser.add_argument("--enable-timeout", type=float, default=5.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    AgxArmFactory, ArmModel, NeroFW, create_agx_arm_config = import_sdk()

    cfg = create_agx_arm_config(
        robot=ArmModel.NERO,
        firmeware_version=firmware_value(NeroFW, args.firmware),
        interface=args.interface,
        channel=args.channel,
    )

    print("NERO SDK config:")
    print(cfg)

    if not args.connect:
        print("Dry run only. Add --connect after CAN is active.")
        return 0

    robot = AgxArmFactory.create_arm(cfg)
    print("Connecting...")
    robot.connect()

    try:
        if args.enable:
            print("Enabling...")
            deadline = time.monotonic() + args.enable_timeout
            while time.monotonic() < deadline:
                if args.normal_mode:
                    robot.set_normal_mode()
                if robot.enable():
                    print("Enable succeeded.")
                    break
                time.sleep(0.01)
            else:
                print("Enable timed out.", file=sys.stderr)

        stop_at = time.monotonic() + args.duration
        while time.monotonic() < stop_at:
            if hasattr(robot, "has_comm_error") and robot.has_comm_error():
                print(f"comm_error={robot.get_comm_error()}")
            print(f"joint_angles: {compact(robot.get_joint_angles())}")
            if hasattr(robot, "get_tcp_pose"):
                print(f"tcp_pose: {compact(robot.get_tcp_pose())}")
            if hasattr(robot, "get_arm_status"):
                print(f"arm_status: {compact(robot.get_arm_status())}")
            print("---")
            time.sleep(args.period)
    finally:
        if hasattr(robot, "disconnect"):
            robot.disconnect()
            print("Disconnected.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
