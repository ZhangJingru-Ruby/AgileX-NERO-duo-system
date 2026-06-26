# S11 Operator Guide

Status: prepared for field execution; S11 accepted values are recorded in
`docs/s11_measurement_notes.md` and `docs/s11_static_tf_plan.md`.

This guide explains S11 in operator terms. S11 is a measurement and validation
phase. It is not a motion phase.

## 1. What S11 Is Trying To Prove

For dual-arm manipulation, the software must know where the two arm bases are in
one shared coordinate frame. Otherwise a later algorithm cannot know whether a
target is near Arm A, near Arm B, between the two arms, or outside the safe
workspace.

S11 produces three facts:

- A shared frame named `lab_world`.
- A measured transform from `lab_world` to `arm_a/base_link`.
- A measured transform from `lab_world` to `arm_b/base_link`.

A transform has two parts:

- Translation: `x`, `y`, `z`, in meters.
- Rotation: `roll`, `pitch`, `yaw`, normally in radians for ROS commands.

For table-mounted arms, the most important first baseline values are usually
`x`, `y`, and `yaw`. If both bases are fixed on the same level tabletop,
`z`, `roll`, and `pitch` can often be recorded as `0`, but the assumption must
be written down.

## 2. Safety State

S11 does not require robot motion.

Before measuring:

- Do not run SDK/ROS/Web motion commands.
- Do not enable a new motion mode.
- Keep the workspace clear.
- If the arms are powered, keep them in read-only/idle state.
- If the arms are unpowered or disabled, make sure gravity cannot make a link
  drop into a person, laptop, tool, or cable.

The base relationship can be measured with the robot powered off, as long as the
base mounting has not moved since S10.

## 3. Recommended First `lab_world` Choice

Unless there is already an external camera, table fixture, or lab coordinate
standard, use this first baseline:

- `lab_world` origin: Arm A base center projected onto the tabletop.
- `lab_world +X`: a marked table direction that is easy to repeat later.
- `lab_world +Y`: left of `+X`, forming a right-handed table frame.
- `lab_world +Z`: upward.

This makes Arm A easy to record:

```text
lab_world -> arm_a/base_link:
x=0, y=0, z=0, orientation to be verified in RViz
```

This is acceptable for the first dual-arm baseline because the critical fact is
Arm B's measured pose relative to Arm A. If the project later adds external
cameras, fixtures, calibration boards, or object workcells, define a new
table/fixture `lab_world` and redo S11.

For the accepted S11 runtime TF, use the values in
`docs/s11_static_tf_plan.md`. The final RViz-valid transform is published to
`arm_*/world`, not directly to `arm_*/base_link`.

## 4. How To Identify Base Centers

Use the physical base mounting geometry as the repeatable measurement reference.

From the user manual image already archived in this project, the base mounting
pattern uses four holes on a `70 mm x 70 mm` pattern. The practical center of
the base is the intersection of the diagonals between those four hole centers.

Use this point as the x/y measurement proxy for `base_link`.

Why this is reasonable for S11:

- The current URDF has `world_to_base_link` at zero.
- The current `base_link` mesh extends upward from approximately `z=0` to
  `z=0.086 m`.
- `joint1` is at `z=0.138 m` relative to `base_link`.
- For a table-upright base without spacers, `base_link` is therefore treated as
  lying on the base/table reference plane for this first baseline.

Record this as a measurement convention, not as a new factory specification.

## 5. Tools

Recommended:

- Masking tape or painter's tape.
- Fine marker.
- Tape measure or ruler.
- Caliper if available.
- Right-angle square if available.
- Phone camera.
- Optional bubble level.

Minimum acceptable:

- A tape measure/ruler, tape marks, and clear photos.

## 6. Physical Measurement Procedure

### Step 1: Mark Arm A Center

1. Locate the four base mounting holes or their visible fasteners.
2. Mark the approximate center by crossing the two diagonals.
3. Project that center to the tabletop with tape/marker.
4. Label it `A_CENTER / lab_world origin`.

If the actual center is hidden by the base, mark two perpendicular table lines
aligned to the hole pattern and draw their intersection next to the base. State
that this is a projected center.

### Step 2: Define `+X`

Choose one repeatable direction and mark it with tape as `lab_world +X`.

Good choices:

- A straight table edge.
- A rail/fixture edge.
- The line from Arm A center toward Arm B center, if the two arms are intended
  to face each other across a shared workspace.

Do not choose a vague direction such as "roughly forward" without a physical
mark.

### Step 3: Define `+Y`

Mark `+Y` as the left direction when facing `+X`. If possible, use a square to
make it perpendicular to `+X`.

### Step 4: Mark Arm B Center

Repeat the same base-center method for Arm B. Label the mark `B_CENTER`.

### Step 5: Measure Translation

Measure Arm B relative to Arm A:

- `x_b`: distance from Arm A center to Arm B center along `+X`.
- `y_b`: distance from the `+X` axis to Arm B center along `+Y`.
- `z_b`: height difference between the two base reference planes.

Use meters in the file:

```text
100 mm = 0.100 m
500 mm = 0.500 m
```

Sign convention:

- Positive `x`: in the marked `+X` direction.
- Positive `y`: left of `+X`.
- Negative `y`: right of `+X`.
- Positive `z`: upward.

For Arm A, if using the recommended first baseline:

```text
x_a=0
y_a=0
z_a=0
```

### Step 6: Measure Yaw

Yaw is the rotation around the vertical `+Z` axis.

For the first baseline, record yaw as the angle from `lab_world +X` to each arm
base's chosen forward/reference direction.

Acceptable reference directions:

- A marked line on the base mounting pattern.
- A repeatable physical feature on the base.
- The intended robot-facing direction, if it is clearly marked in photos.

Common conversions for ROS static TF:

```text
0 deg   = 0 rad
90 deg  = 1.5708 rad
180 deg = 3.1416 rad
-90 deg = -1.5708 rad
```

If you cannot confidently identify the URDF base +X direction from the physical
base, do not guess silently. Record the physical reference you used, then use
RViz in S11 validation to confirm whether the displayed arm layout matches the
real layout. If RViz is rotated by 90 or 180 degrees, correct yaw and document
the correction.

### Step 7: Roll And Pitch

For a normal tabletop setup:

```text
roll=0
pitch=0
```

This is acceptable only if the bases are installed upright on a reasonably level
table. If there are wedges, uneven spacers, tilted fixtures, or visible base
tilt, measure or document the limitation.

## 7. Photos To Capture

Save photos under a clear directory, for example:

```text
docs/pics/s11_measurement_20260626/
```

Capture at least:

- Whole table overview showing both arms.
- Arm A base center mark.
- Arm B base center mark.
- `lab_world +X` and `+Y` tape arrows.
- Tape/ruler reading for Arm B `x`.
- Tape/ruler reading for Arm B `y`.
- Any yaw reference marks.
- Any spacer/height feature if `z` is not zero.

## 8. What To Fill In

Fill `docs/s11_measurement_notes.md`.

For the recommended first baseline, Arm A should look like:

```text
x=0
y=0
z=0
roll=0
pitch=0
yaw=0
```

Arm B should contain the measured values:

```text
x=<measured meters>
y=<measured meters>
z=<measured meters or 0 with reason>
roll=0
pitch=0
yaw=<measured radians or degrees, unit stated>
```

Do not copy these as final values until the measurements are actually made.

## 9. What To Send Back For Review

After measuring, send:

- The chosen `lab_world` origin and `+X/+Y` definitions.
- Arm A values.
- Arm B values.
- Whether yaw is in degrees or radians.
- Measurement tool and uncertainty estimate.
- Photo directory path.

Then we will convert the values into static TF commands and run the read-only
ROS/RViz validation.
