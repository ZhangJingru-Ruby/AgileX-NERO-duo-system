# S3 Model Validation

Date: 2026-06-24

Scope: offline NERO model validation in the Docker ROS2 Humble environment. No
real robot, CAN device, or motion command was used.

## Runtime Source

Current runtime model source:

- Package: `agx_arm_description`
- Workspace: `~/agx_arm_ws`
- Repository: `agx_arm_ros`
- Commit: `c73d33f`
- URDF submodule: `agx_arm_urdf`
- URDF submodule commit: `f6642ce`

The initial bare-arm configuration remains:

- `arm_type:=nero`
- `effector_type:=none`
- `tcp_offset:=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`

## Model Files Checked

All of these models expand with `xacro` and pass `check_urdf`:

| Model | Result | Notes |
| --- | --- | --- |
| `nero_description.urdf` | Pass | Bare arm, current S3/S8 default. |
| `nero_with_gripper_description.xacro` | Pass | For later gripper route, not active now. |
| `nero_with_left_revo2_description.xacro` | Pass | For later left Revo2/dexterous hand route. |
| `nero_with_right_revo2_description.xacro` | Pass | For later right Revo2/dexterous hand route. |
| `nero_with_revo2_flange_description.xacro` | Pass | Revo2 flange-only model. |

Bare-arm parsed structure:

- Robot name: `nero`
- Links: `9`
- Joints: `8`
- Kinematic chain: `world -> base_link -> link1 -> link2 -> link3 -> link4 -> link5 -> link6 -> link7`
- Mesh references: `16`
- Missing mesh references: `0`

`robot_state_publisher` successfully loaded the bare-arm model and reported
segments `world`, `base_link`, and `link1` through `link7`.

## URDF Joint Summary

| Joint | Parent -> Child | Axis | Origin xyz | Origin rpy | URDF lower/upper |
| --- | --- | --- | --- | --- | --- |
| `joint1` | `base_link -> link1` | `0 0 1` | `0 0 0.138` | `0 0 0` | `-155.00..155.00 deg` |
| `joint2` | `link1 -> link2` | `0 0 1` | `0 0 0` | `1.5707963 3.1415926 0` | `-99.69..99.69 deg` |
| `joint3` | `link2 -> link3` | `0 0 1` | `0 -0.31 0` | `-1.5707963 0 3.1415926926` | `-157.56..157.56 deg` |
| `joint4` | `link3 -> link4` | `0 0 1` | `0 0 0` | `-1.5707963 0 3.1415926926` | `-57.87..122.61 deg` |
| `joint5` | `link4 -> link5` | `0 0 1` | `0 -0.27001 0` | `1.5707963 -1.5707963 0` | `-157.56..157.56 deg` |
| `joint6` | `link5 -> link6` | `0 0 1` | `0 0 0` | `1.5707963 -1.5707963 0` | `-41.83..54.43 deg` |
| `joint7` | `link6 -> link7` | `0 0 1` | `0 -0.0235 0` | `1.5707963 0 0` | `-90.00..90.00 deg` |

## Important Finding

Most URDF joint limits are close to the manual limits, but `joint2` is expressed
as `-99.69..99.69 deg` in the runtime URDF, while the local manual records J2 as
`-15..190 deg`.

Do not treat this as resolved by assumption. The likely cause is a different
zero/offset convention between the URDF and the manual/mechanical joint angle
definition, but this must be confirmed later by comparing Web/CAN/SDK/ROS joint
feedback on the real arm.

For safety, the manual limits remain the safety source until live feedback
confirms the mapping.

## RViz Status

`display.launch.py` was tested with:

```bash
ros2 launch agx_arm_description display.launch.py \
  arm_type:=nero \
  effector_type:=none \
  gui:=false \
  control:=true
```

Initial RViz retry from the non-desktop shell failed because that shell could
not access the desktop X11 display:

- `No protocol specified`
- `Unable to open display: :1`
- `RenderingAPIException: Couldn't open X display :1`

This was an X11 authorization/display-session issue, not a URDF parsing failure.

The real desktop terminal retry succeeded with:

```bash
bash scripts/run_humble_container.sh --allow-xhost \
  ros2 launch agx_arm_description display.launch.py \
  arm_type:=nero \
  effector_type:=none \
  gui:=false \
  control:=true
```

Observed successful evidence:

- `xhost +local:root` was applied by `--allow-xhost`.
- `joint_state_publisher`, `robot_state_publisher`, and `rviz2` started.
- `robot_state_publisher` reported `base_link`, `link1` through `link7`, and
  `world`.
- `rviz2` reported OpenGL `4.5`.
- The launch was stopped with Ctrl-C.
- `joint_state_publisher`, `robot_state_publisher`, and `rviz2` finished
  cleanly.
- Temporary X11 permission was revoked with:

```bash
xhost -local:root
```

Final `xhost` output allowed only:

```text
SI:localuser:lv-robotics
```

Result: S3 RViz GUI validation is complete.
