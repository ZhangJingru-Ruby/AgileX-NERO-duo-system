# NERO Upstream Repository Analysis

Date: 2026-06-24

Purpose: verify the ROS/SDK strategy from the cloned upstream repositories rather
than relying on assumptions from earlier GitHub references.

## Local Clones

| Repository | Local path | Branch | Commit | Role |
| --- | --- | --- | --- | --- |
| `agilexrobotics/agx_arm_ros` | `upstream/agx_arm_ros` | `ros2` | `c73d33f` | Current AgileX ROS driver workspace for Piper/Nero and related arms. |
| `agilexrobotics/pyAgxArm` | `upstream/pyAgxArm` | `master` | `a226840` | Python SDK used by the ROS driver and usable standalone over CAN. |
| `agilexrobotics/piper_ros` | `upstream/piper_ros` | `humble_beta1` | `2dc30fc` | Reference source for the NERO description package supplied by the user. |
| `agilexrobotics/agx_arm_urdf` submodule | `upstream/agx_arm_ros/src/agx_arm_description/agx_arm_urdf` | submodule | `f6642ce` | Current URDF/Xacro/mesh model set used by `agx_arm_ros`. |

## Evidence From `agx_arm_ros`

- `README.md` identifies the package as `AgileX 机械臂 ROS2 驱动`.
- The README shows Humble and Jazzy as passing ROS targets.
- The overview says it provides ROS2 interfaces for AgileX arms including
  Piper and Nero.
- The quick-start clone command is `git clone -b ros2 --recurse-submodules`.
- Dependencies are ROS2 dependencies: `ros2-control`, `ros2-controllers`,
  `controller-manager`, `xacro`, MoveIt2, and `python3-colcon-common-extensions`.
- Runtime commands use `ros2 launch` and `ros2 run`.
- `src/agx_arm_ctrl/package.xml` depends on `rclpy`, `launch_ros`, and exports
  `ament_python`.
- `src/agx_arm_ctrl/launch/start_single_agx_arm.launch.py` provides
  `arm_type` choices including `nero`, and `effector_type` choices
  `none`, `agx_gripper`, and `revo2`.

Conclusion: this repository is the official current ROS route for NERO in our
workspace, and it is ROS2, not ROS1/Noetic.

## Evidence From `piper_ros`

- The requested path
  `src/robot_description/nero_description` exists on branch `humble_beta1`.
- `package.xml` uses `ament_cmake`, `rviz2`, and `xacro`.
- `CMakeLists.txt` uses `ament_cmake` and installs `launch`, `meshes`, `rviz`,
  and `urdf`.
- This path is a NERO model/description package, not the current NERO control
  driver.

Conclusion: this repository supports the Humble-oriented model evidence, but it
does not justify choosing ROS1/Noetic for control.

## Evidence From `pyAgxArm`

- `README.md` describes a Python SDK for AgileX arms and end effectors, including
  Nero, over CAN.
- Supported Ubuntu versions are listed as `18.04 / 20.04 / 22.04 / 24.04`.
- Supported Python is `3.6` and above, documented as compatible up to `3.14`.
- `setup.py` requires `python-can>=3.3.4`.
- Quick-start examples use Linux `interface="socketcan"` and `channel="can0"`.
- Firmware selectors include Nero `DEFAULT`, `V111`, `V112`, and `V120`.

Conclusion: the current Ubuntu 20.04 host can be used for SDK/CAN-only read
checks after installing compatible Python dependencies, but this does not make
Noetic the preferred ROS route.

## Evidence From `agx_arm_urdf`

- The submodule contains NERO URDF/Xacro assets, including bare arm, gripper,
  and left/right Revo2 dexterous hand variants.
- Its README includes standalone ROS2 and ROS1 packaging examples.
- The ROS1 note is for packaging URDF assets in a catkin workspace; it is not a
  ROS1 NERO control driver.

Conclusion: ROS1 can display/package model assets if needed, but the current
control stack evidence remains ROS2.

## ROS Strategy Decision

Recommended deployment strategy:

1. Use Ubuntu 22.04 + ROS2 Humble for the main NERO ROS bring-up.
2. Ubuntu 24.04 + ROS2 Jazzy is a valid alternative if we deliberately choose
   Jazzy and verify the workspace on that host.
3. Keep the current Ubuntu 20.04 machine available for SDK-only CAN/status work,
   using a clean Python environment with `python-can>=3.3.4`.
4. Do not choose Noetic as the default route. Noetic is ROS1 and does not match
   the current `agx_arm_ros` driver path. It should only be used for a hard
   legacy ROS1 integration requirement, with a separate porting/validation plan.

Current blocker:

- S2 ROS setup is not complete until the host strategy is selected and a
  supported ROS2 environment is available.
- SDK-only preparation can proceed on the current Ubuntu 20.04 host, but should
  not be treated as equivalent to completing the ROS2 deployment environment.
