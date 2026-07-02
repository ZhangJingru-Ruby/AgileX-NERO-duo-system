#!/usr/bin/env python3
"""Stable public entry point for returning arms and hands to the initial pose."""

from __future__ import annotations

import os
import sys


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(script_dir, "ros_s15_return_to_initial.py")
    os.execv(sys.executable, [sys.executable, target, *sys.argv[1:]])


if __name__ == "__main__":
    main()
