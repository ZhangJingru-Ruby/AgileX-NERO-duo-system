#!/usr/bin/env python3
"""Run a bounded single-joint NERO SDK step.

Default mode is dry-run: connect, read current state, print the target, and do
not send motion. Add --execute to enable the arm and send move_j.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
from typing import Any, Sequence


def import_sdk() -> Any:
    try:
        from pyAgxArm import AgxArmFactory, ArmModel, NeroFW, create_agx_arm_config
    except Exception as exc:  # pragma: no cover - operator-facing script
        print(f"Failed to import pyAgxArm: {exc}", file=sys.stderr)
        print("Use the project SDK venv, for example: .venv/nero-sdk/bin/python")
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


def parse_args() -> argparse.Namespace:
    default_channel = os.environ.get(
        "NERO_ARM_A_CAN_PORT",
        os.environ.get("NERO_CAN_PORT", "can_arm_a"),
    )
    firmware_default = os.environ.get("NERO_FW", "v112")
    if firmware_default not in {"default", "v111", "v112", "v120"}:
        firmware_default = "v112"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default=os.environ.get("NERO_CAN_INTERFACE", "socketcan"))
    parser.add_argument("--channel", default=default_channel)
    parser.add_argument("--firmware", default=firmware_default, choices=["default", "v111", "v112", "v120"])
    parser.add_argument("--joint", type=int, default=7, choices=range(1, 8))
    parser.add_argument("--delta-deg", type=float, default=1.0)
    parser.add_argument("--max-delta-deg", type=float, default=2.0)
    parser.add_argument("--speed-percent", type=int, default=5)
    parser.add_argument("--feedback-timeout", type=float, default=5.0)
    parser.add_argument("--enable-timeout", type=float, default=3.0)
    parser.add_argument("--motion-timeout", type=float, default=8.0)
    parser.add_argument("--poll-period", type=float, default=0.05)
    parser.add_argument("--settle-time", type=float, default=0.25)
    parser.add_argument("--execute", action="store_true", help="Actually enable and send move_j.")
    parser.add_argument(
        "--no-return",
        dest="return_to_start",
        action="store_false",
        help="Do not command the joint back to its original angle after the step.",
    )
    parser.add_argument(
        "--no-estop-on-ctrl-c",
        dest="estop_on_ctrl_c",
        action="store_false",
        help="Do not send SDK electronic_emergency_stop() on Ctrl-C.",
    )
    parser.set_defaults(return_to_start=True, estop_on_ctrl_c=True)
    return parser.parse_args()


def require_safe_args(args: argparse.Namespace) -> None:
    if args.max_delta_deg <= 0:
        raise SystemExit("--max-delta-deg must be positive")
    if abs(args.delta_deg) > args.max_delta_deg:
        raise SystemExit(
            f"Refusing delta {args.delta_deg} deg; max allowed is {args.max_delta_deg} deg"
        )
    if args.speed_percent < 0 or args.speed_percent > 10:
        raise SystemExit("For S10.2, --speed-percent must be in [0, 10]")


def wait_joint_feedback(robot: Any, timeout: float, poll_period: float) -> list[float]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if hasattr(robot, "has_comm_error") and robot.has_comm_error():
            raise RuntimeError(f"SDK communication error: {robot.get_comm_error()}")
        joint_state = robot.get_joint_angles()
        if joint_state is not None and getattr(joint_state, "hz", 0) > 0:
            joints = list(joint_state.msg)
            if len(joints) == 7:
                return joints
        time.sleep(poll_period)
    raise TimeoutError(f"No valid 7-joint feedback within {timeout:.1f}s")


def status_has_error(status: Any) -> bool:
    if status is None:
        return True
    err = getattr(status.msg, "err_status", None)
    if err is None:
        return False
    for name in dir(err):
        if name.startswith("_"):
            continue
        value = getattr(err, name)
        if isinstance(value, bool) and value:
            return True
    return False


def print_status(label: str, status: Any) -> None:
    if status is None:
        print(f"{label}: None")
        return
    msg = status.msg
    print(
        f"{label}: ctrl_mode={getattr(msg, 'ctrl_mode', None)} "
        f"arm_status={getattr(msg, 'arm_status', None)} "
        f"mode_feedback={getattr(msg, 'mode_feedback', None)} "
        f"motion_status={getattr(msg, 'motion_status', None)}"
    )


def wait_motion_done(robot: Any, timeout: float, poll_period: float) -> bool:
    time.sleep(0.25)
    deadline = time.monotonic() + timeout
    last_status = None
    while time.monotonic() < deadline:
        status = robot.get_arm_status()
        last_status = status
        if status_has_error(status):
            print_status("error_status", status)
            return False
        motion_status = getattr(status.msg, "motion_status", None) if status else None
        if motion_status == 0:
            return True
        time.sleep(poll_period)
    print_status("last_status", last_status)
    return False


def enable_all(robot: Any, timeout: float) -> bool:
    try:
        return bool(robot.enable(timeout=timeout))
    except TypeError:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if robot.enable():
                return True
            time.sleep(0.01)
        return False


def deg_list(values: Sequence[float]) -> list[float]:
    return [math.degrees(v) for v in values]


def main() -> int:
    args = parse_args()
    require_safe_args(args)
    AgxArmFactory, ArmModel, NeroFW, create_agx_arm_config = import_sdk()

    cfg = create_agx_arm_config(
        robot=ArmModel.NERO,
        firmeware_version=firmware_value(NeroFW, args.firmware),
        interface=args.interface,
        channel=args.channel,
    )

    print("S10.2 NERO SDK single-joint step")
    print(f"channel={args.channel} firmware={args.firmware} execute={args.execute}")
    print(f"joint=J{args.joint} delta_deg={args.delta_deg} speed_percent={args.speed_percent}")

    robot = AgxArmFactory.create_arm(cfg)
    print("Connecting...")
    robot.connect()
    try:
        firmware = robot.get_firmware()
        print(f"firmware={firmware}")
        current = wait_joint_feedback(robot, args.feedback_timeout, args.poll_period)
        target = list(current)
        target[args.joint - 1] += math.radians(args.delta_deg)

        joint_name = f"joint{args.joint}"
        lo, hi = cfg["joint_limits"][joint_name]
        if target[args.joint - 1] < lo or target[args.joint - 1] > hi:
            raise SystemExit(
                f"Target {math.degrees(target[args.joint - 1]):.3f} deg is outside "
                f"{joint_name} configured limits [{math.degrees(lo):.3f}, {math.degrees(hi):.3f}] deg"
            )

        print(f"current_deg={deg_list(current)}")
        print(f"target_deg={deg_list(target)}")
        print_status("pre_status", robot.get_arm_status())

        if not args.execute:
            print("Dry run only. Add --execute after the S10.2 safety gate is confirmed.")
            return 0

        print("Setting speed percent...")
        robot.set_speed_percent(args.speed_percent)
        print("Enabling all joints...")
        if not enable_all(robot, args.enable_timeout):
            raise RuntimeError("Enable timed out or failed")

        print_status("enabled_status", robot.get_arm_status())
        if status_has_error(robot.get_arm_status()):
            raise RuntimeError("Arm status has error flags after enable")

        print("Sending move_j step...")
        robot.move_j(target)
        if not wait_motion_done(robot, args.motion_timeout, args.poll_period):
            raise RuntimeError("Step motion did not finish cleanly")
        time.sleep(args.settle_time)
        print(f"after_step_deg={deg_list(wait_joint_feedback(robot, args.feedback_timeout, args.poll_period))}")

        if args.return_to_start:
            print("Returning to original joint angle...")
            robot.move_j(current)
            if not wait_motion_done(robot, args.motion_timeout, args.poll_period):
                raise RuntimeError("Return motion did not finish cleanly")
            time.sleep(args.settle_time)
            print(f"after_return_deg={deg_list(wait_joint_feedback(robot, args.feedback_timeout, args.poll_period))}")

        print_status("final_status", robot.get_arm_status())
        if status_has_error(robot.get_arm_status()):
            raise RuntimeError("Final arm status has error flags")
        print("S10.2 SDK single-joint step completed.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted by operator.", file=sys.stderr)
        if args.execute and args.estop_on_ctrl_c:
            print("Sending SDK electronic_emergency_stop() due to Ctrl-C.", file=sys.stderr)
            robot.electronic_emergency_stop()
        return 130
    finally:
        if hasattr(robot, "disconnect"):
            robot.disconnect()
            print("Disconnected.")


if __name__ == "__main__":
    raise SystemExit(main())
