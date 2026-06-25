# S11 Measurement Notes

Status: template, awaiting physical measurement.

Use this file to record the measured transforms from the shared lab frame to
each robot base. Do not fill estimated or convenient values as facts.

## Measurement Session

| Item | Value |
| --- | --- |
| Date/time | TBD |
| Operator | TBD |
| Git commit | TBD |
| Table/fixture unchanged from S10 | TBD |
| Measurement tool | TBD |
| Photo directory | TBD |

## lab_world Convention

| Axis / item | Definition |
| --- | --- |
| Origin | TBD |
| +X | TBD |
| +Y | TBD |
| +Z | Up, unless explicitly changed |
| Reason for convention | TBD |

Recommended default:

- Origin: a marked table/fixture point that can be found again.
- +X: forward direction of the experiment table.
- +Y: left direction when facing +X.
- +Z: up.

## Arm A Transform

Transform: `lab_world -> arm_a/base_link`

| Field | Value | Unit / note |
| --- | --- | --- |
| x | TBD | meters |
| y | TBD | meters |
| z | TBD | meters |
| roll | TBD | degrees or radians, specify |
| pitch | TBD | degrees or radians, specify |
| yaw | TBD | degrees or radians, specify |
| Translation uncertainty | TBD | meters |
| Rotation uncertainty | TBD | degrees or radians |
| Reference points used | TBD | text/photos |

## Arm B Transform

Transform: `lab_world -> arm_b/base_link`

| Field | Value | Unit / note |
| --- | --- | --- |
| x | TBD | meters |
| y | TBD | meters |
| z | TBD | meters |
| roll | TBD | degrees or radians, specify |
| pitch | TBD | degrees or radians, specify |
| yaw | TBD | degrees or radians, specify |
| Translation uncertainty | TBD | meters |
| Rotation uncertainty | TBD | degrees or radians |
| Reference points used | TBD | text/photos |

## Acceptance Notes

- [ ] `lab_world` origin is physically marked or otherwise repeatable.
- [ ] Arm A base transform is measured, not assumed.
- [ ] Arm B base transform is measured, not assumed.
- [ ] Translation uncertainty is about `5 mm` or better, or the limitation is documented.
- [ ] Yaw uncertainty is about `1 deg` or better, or the limitation is documented.
- [ ] Roll/pitch are set to `0` only if the table/base level assumption is acceptable.
- [ ] Photos show the reference points and measurement method.

## Deviations

Record any deviation from the recommended convention or measurement accuracy:

- TBD
