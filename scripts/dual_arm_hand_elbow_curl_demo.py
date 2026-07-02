#!/usr/bin/env python3
"""Stable public entry point for the accepted dual-arm dual-hand demo."""

from __future__ import annotations

import os
import sys


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(script_dir, "ros_s15_elbow_curl_demo.py")
    os.execv(sys.executable, [sys.executable, target, *sys.argv[1:]])


if __name__ == "__main__":
    main()
