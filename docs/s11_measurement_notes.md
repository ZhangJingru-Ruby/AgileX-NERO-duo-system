# S11 Measurement Notes

Status: accepted / closed for the S11 first engineering baseline.

Use this file to record the measured transforms from the shared lab frame to
each robot base. Do not fill estimated or convenient values as facts.

## Measurement Session

| Item | Value |
| --- | --- |
| Date/time | 2026-06-26 |
| Operator | User/operator report |
| Git commit | Pre-closure visual-validation commit `829224c`; closure commit records this evidence update |
| Table/fixture unchanged from S10 | No base movement reported after S10 closure |
| Measurement tool | Not reported; measured value provided as `260 mm` |
| Photo directory | `docs/pics/s11_measurement_20260626/` |
| Accepted RViz screenshot | `docs/pics/S11_RViz_accepted_dual_arm_layout.png` |
| Post-TF ROS snapshot | `docs/s9_ros_snapshots/20260626_055339/` |

## lab_world Convention

| Axis / item | Definition |
| --- | --- |
| Origin | Arm A base center projected onto the tabletop |
| +X | From Arm A base center toward Arm B base center |
| +Y | Left-hand direction when facing `+X` |
| +Z | Up |
| Reason for convention | First dual-arm baseline; makes Arm B relative position easy to validate and reproduce |

Recommended default:

- Origin: a marked table/fixture point that can be found again.
- +X: forward direction of the experiment table.
- +Y: left direction when facing +X.
- +Z: up.

## Arm A Transform

Measured transform: `lab_world -> arm_a/base_link`

Runtime static TF target for RViz/model validation: `lab_world -> arm_a/world`,
because the NERO URDF already contains a fixed `world -> base_link` joint.

| Field | Value | Unit / note |
| --- | --- | --- |
| x | `0.000` | meters; by `lab_world` origin convention |
| y | `0.000` | meters; by `lab_world` origin convention |
| z | `0.000` | meters; same tabletop/base reference plane assumed |
| roll | `0` accepted for S11 baseline | rad; inferred from Web-frame observation and accepted by RViz visual validation |
| pitch | `-1.5707963` accepted for S11 baseline | rad; maps observed Arm A local `+X` to `lab_world +Z` |
| yaw | `0` accepted for S11 baseline | rad; inferred from Web-frame observation and accepted by RViz visual validation |
| Translation uncertainty | Not quantified | physical center projection convention |
| Rotation uncertainty | Visual validation only | accepted for S11 baseline; refine if future metrology is required |
| Reference points used | Arm A base center projection; `docs/pics/s11_measurement_20260626/` |

## Arm B Transform

Measured transform: `lab_world -> arm_b/base_link`

Runtime static TF target for RViz/model validation: `lab_world -> arm_b/world`,
using the same numeric values as the measured base pose.

| Field | Value | Unit / note |
| --- | --- | --- |
| x | `0.260` | meters; user measured `260 mm` from Arm A center toward Arm B center |
| y | `0.000` | meters; user reported `y_b = 0` |
| z | `0.000` | meters; user reported `z_b = 0`, same tabletop/base reference plane assumed |
| roll | `3.1415926` accepted for S11 baseline | rad; inferred from Web-frame observation and accepted by RViz visual validation |
| pitch | `-1.5707963` accepted for S11 baseline | rad; maps observed Arm B local `+X` to `lab_world +Z` |
| yaw | `0` accepted for S11 baseline | rad; inferred from Web-frame observation and accepted by RViz visual validation |
| Translation uncertainty | Not quantified | measured value reported; exact tool/uncertainty not yet recorded |
| Rotation uncertainty | Visual validation only | accepted for S11 baseline; refine if future metrology is required |
| Reference points used | Arm A and Arm B base center projections; `docs/pics/s11_measurement_20260626/` |

## Web Frame Observation

The operator observed the Web 3D/control coordinate axes in the natural hanging
posture. These observations are useful for deciding the first RViz validation
candidate, but they are not yet treated as a verified ROS `base_link` transform.

Reported mapping from Web axes to `lab_world` axes:

| Arm | Web axis observation in `lab_world` |
| --- | --- |
| Arm A | `+x_web = +Z`, `+y_web = +Y`, `+z_web = -X` |
| Arm B | `+x_web = +Z`, `+y_web = -Y`, `+z_web = +X` |

Interpretation:

- The Web-frame observations imply Arm A and Arm B differ by approximately
  `180 deg`, but the difference is not represented correctly by a pure
  `lab_world +Z` yaw once RViz/ROS root frames are considered.
- The first pure-yaw RViz candidate placed the two models horizontally in the
  table plane and did not match the physical natural hanging posture.
- The revised candidate maps the reported Web axes into `lab_world`:
  - Arm A: `roll=0`, `pitch=-1.5707963`, `yaw=0`.
  - Arm B: `roll=3.1415926`, `pitch=-1.5707963`, `yaw=0`.
- The revised 3D root rotations were accepted by operator RViz visual
  validation on 2026-06-26: the simulated layout matched the real dual-arm
  layout, and moving each arm was reflected in RViz feedback.

## Acceptance Notes

- [x] `lab_world` origin is defined as Arm A base center projection.
- [x] Arm A base transform is recorded by first-baseline convention.
- [x] Arm B full transform is accepted for S11 baseline by operator RViz visual validation.
- [x] Translation uncertainty is about `5 mm` or better, or the limitation is documented.
- [x] Orientation is accepted for S11 baseline by RViz visual validation.
- [x] Roll/pitch values are explicitly non-zero where required to map the robot root frames into `lab_world`.
- [x] Photos/screenshots and engineering drawings are saved under `docs/pics/s11_measurement_20260626/`.

## Deviations

- Translation uncertainty and measurement tool were not reported; this limitation is accepted for the S11 first engineering baseline and must be revisited before high-precision dual-arm manipulation.
- The first RViz visual check with pure Arm B yaw `pi` did not match reality.
- The revised 3D root rotations matched reality by operator report on
  2026-06-26.
- The S11 post-TF read-only snapshot `docs/s9_ros_snapshots/20260626_055339/`
  is clean: `Failed capture commands: 0`, A/B joint states at about 200 Hz,
  A/B `err_status: 0`, and no joint-limit or joint-communication flags.
