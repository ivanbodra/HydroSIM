# Principal-plane array tilt as a controlled symmetry break

Status: controlled reference experiment for the HydroSIM sound-speed-at-transducer model.

## Purpose

The aligned sound-speed-at-transducer reference case can close numerically even when the transducer sound-speed sensor is biased. HydroSIM therefore needs controlled geometry changes that test where that closure stops being valid rather than treating it as a universal rule.

The first such coordinate is `principal_plane_array_tilt_rad`.

This parameter is deliberately reduced to one principal plane. It is not a complete vessel-attitude model, a complete Mills-cross installation model, or a multi-sector transmit model. Platform pose remains aligned with the horizontal sound-speed profile so array orientation is the only added geometry coordinate.

## Coordinate meaning

Let `theta_cfg` be the configured beam angle measured relative to the array principal-plane normal, and let `tau` be the principal-plane array tilt relative to the profile vertical. Positive `tau` is defined in the same signed direction as positive across-track angle.

The sonar constructs its steering law using `c_used`. Truth propagates with local sound speed `c_true`. In array coordinates,

```text
p_array = sin(theta_cfg) / c_used

theta_phys_array = asin(c_true * p_array)
```

The physical launch angle used by the horizontally layered Truth profile is then

```text
theta_phys_profile = tau + theta_phys_array
```

For reciprocal reception, the physical arrival is first interpreted in array coordinates. The sonar estimates

```text
p_observed_array = sin(theta_phys_array) / c_true

theta_est_array = asin(c_used * p_observed_array)
```

and the estimated direction is rotated back into the profile frame:

```text
theta_est_profile = tau + theta_est_array
```

The zero-thickness processing boundary then establishes the profile-frame ray parameter from

```text
p_processing = sin(theta_est_profile) / c_used
```

while Truth follows

```text
p_truth = sin(theta_phys_profile) / c_true
```

## Why tilt breaks the aligned closure

When `tau = 0`, the ideal reciprocal reference gives

```text
p_processing = p_truth
```

for a transducer-value perturbation used consistently in TX steering, RX angle mapping, and the processing boundary. This is the existing narrow closure case.

When `tau != 0`, sound-speed scaling is performed in array coordinates but Snell propagation is referenced to the horizontal profile frame. In general,

```text
sin(tau + asin(k * sin(theta)))
```

cannot be reduced to a form that makes the array-frame sound-speed factors cancel after rotation. Rotation and sound-speed angular mapping do not generally commute. Therefore `p_processing` and `p_truth` can differ even when the finite-thickness Truth and processing profiles are identical.

This is the specific symmetry break being tested.

## Validation strategy

The implementation preserves the previous zero-tilt tests unchanged in physical meaning. A new analytical test independently computes:

```text
theta_phys_array

theta_phys_profile

theta_est_profile

p_truth

p_processing
```

from elementary trigonometric relations and verifies that the implementation reproduces the angle states while the two profile-frame ray parameters separate for non-zero tilt and biased transducer sound speed.

The parameterized A/B/C/D study now accepts a tilt axis. With zero tilt, the transducer-only case remains a closure diagnostic. With non-zero tilt, the same A/B/C/D construction measures departure from that closure without changing the finite-thickness profile error definitions.

## Scope and limitations

The current model assumes:

- stationary and reciprocal propagation;
- one principal plane;
- horizontal piecewise-constant sound-speed layers;
- a flat bottom;
- aligned platform pose;
- one common principal-plane array orientation used for the TX/RX angular-coordinate experiment;
- no multi-sector timing, sector association, or three-dimensional array geometry.

The parameter should therefore be interpreted as a diagnostic orientation coordinate. A later full MBES model should represent TX and RX array frames independently in 3-D and should not infer full installation behavior from this 2-D experiment.

## Relationship to the broader sound-speed model

This experiment does not alter the existing separation between:

```text
Truth != Observed != Configured != Estimated != Derived
```

It also does not change the zero-thickness boundary representation or the finite-thickness processing SVP. The only new operation is an explicit coordinate rotation between array-angle semantics and the horizontal profile frame.

See also `docs/science/sound_speed_at_transducer.md` and the Scientific Registry entry `hydrosim.integration.principal_plane_array_tilt_symmetry_break`.
