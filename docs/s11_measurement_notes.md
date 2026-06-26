# S11 Measurement Notes

Status: partially measured; static TF yaw pending RViz validation.

Use this file to record the measured transforms from the shared lab frame to
each robot base. Do not fill estimated or convenient values as facts.

## Measurement Session

| Item | Value |
| --- | --- |
| Date/time | 2026-06-26 |
| Operator | User/operator report |
| Git commit | `233bf6a` before this measurement-record update |
| Table/fixture unchanged from S10 | No base movement reported after S10 closure |
| Measurement tool | Not reported; measured value provided as `260 mm` |
| Photo directory | `docs/pics/s11_measurement_20260626/` |

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
| roll | `0` | rad; tabletop upright assumption |
| pitch | `0` | rad; tabletop upright assumption |
| yaw | `0` | rad; Arm A is the reference orientation candidate |
| Translation uncertainty | Not quantified | physical center projection convention |
| Rotation uncertainty | Pending | yaw reference still requires RViz validation |
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
| roll | `0` | rad; tabletop upright assumption |
| pitch | `0` | rad; tabletop upright assumption |
| yaw | `3.1415926` candidate | rad; inferred from A/B Web-frame observation as a 180 deg vertical-axis difference; requires RViz validation |
| Translation uncertainty | Not quantified | measured value reported; exact tool/uncertainty not yet recorded |
| Rotation uncertainty | Pending | yaw candidate must be validated in RViz |
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
  `180 deg` around the vertical `lab_world +Z` axis.
- This supports the first static-TF candidate `arm_b/base_link yaw = pi`
  relative to Arm A.
- Because Web coordinate axes may not be identical to ROS `base_link`, this is
  a validation candidate, not final acceptance evidence.

## Acceptance Notes

- [x] `lab_world` origin is defined as Arm A base center projection.
- [x] Arm A base transform is recorded by first-baseline convention.
- [ ] Arm B full transform is accepted; translation is measured, yaw is still an RViz-validation candidate.
- [ ] Translation uncertainty is about `5 mm` or better, or the limitation is documented.
- [ ] Yaw uncertainty is about `1 deg` or better, or the limitation is documented.
- [ ] Roll/pitch are set to `0` only if the table/base level assumption is acceptable.
- [x] Photos/screenshots and engineering drawings are saved under `docs/pics/s11_measurement_20260626/`.

## Deviations

- Translation uncertainty and measurement tool were not reported yet.
- Yaw is derived from Web-frame observation and must be checked in RViz before
  S11 acceptance.
