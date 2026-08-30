# Principal-plane array tilt: depth-normalized sounding response

## Status

Controlled diagnostic. This document does not define an operational uncertainty model.

## Purpose

The preceding HydroSIM diagnostics connect transducer sound-speed bias and explicit
principal-plane array tilt to a ray-parameter mismatch and then to final sounding
error. This diagnostic adds bottom depth as a controlled coordinate and reports the
final calculated-minus-Truth error normalized by the physical sensor-to-bottom
vertical separation.

For vertical separation `H > 0`, the reported dimensionless responses are

```text
e_y = Delta_y / H
e_z = Delta_z / H
e_norm = ||Delta_r|| / H
```

where `Delta_y` is across-track error, `Delta_z` is vertical error in the HydroSIM
+Z/down convention, and `||Delta_r||` is the Euclidean sounding-error norm.

## Why normalize by vertical separation

The normalization separates two questions that should not be conflated:

1. How large is the final error in metres at a given depth?
2. Does the controlled response scale approximately with depth?

In a homogeneous profile with otherwise fixed geometry, the present geometric and
travel-time problem is scale-similar. The normalized response is therefore expected
to remain constant with depth, subject to numerical tolerance. That property is used
as an analytical/numerical validation anchor.

A layered profile introduces fixed physical interface depths. Changing bottom depth
then changes the fraction of the acoustic path spent in each layer. The problem is
no longer geometrically scale-similar, so HydroSIM deliberately imposes no law that
`Delta_y/H`, `Delta_z/H`, or `||Delta_r||/H` must remain constant.

## Controlled variables

The diagnostic sweeps:

- configured across-track beam angle;
- transducer sound-speed sensor bias;
- explicit principal-plane array tilt; and
- flat-bottom depth.

The processing profile remains equal to Truth. Platform attitude remains aligned
with the horizontal profile frame. The same finite sound-speed profile is used for
all requested depths and must cover every target depth.

## Denominator definition

Depth normalization uses

```text
H = z_bottom - z_sensor
```

in the HydroSIM +Z/down frame. It is not absolute NED Z, slant range, ray-path
length, or two-way acoustic distance.

## Validation properties

The implementation is tested against these controlled properties:

- homogeneous-profile normalized response is depth-invariant within numerical tolerance;
- a layered profile is not forced to obey depth invariance;
- zero bias or zero array tilt retains the narrow controlled closure after normalization;
- output ordering is deterministic: angle, bias, tilt, depth;
- empty depth axes and non-positive vertical separation are rejected.

The homogeneous scaling property validates the complete numerical chain rather than
introducing a new physical law. Failure of depth invariance in a layered profile can
be physically meaningful because the fixed interface depths break scale similarity.

## Interpretation limits

These normalized quantities are dimensionless response diagnostics. They are not:

- Total Vertical Uncertainty or Total Horizontal Uncertainty;
- confidence intervals;
- stochastic sensor-error models;
- operational accuracy limits;
- evidence that sound-speed errors are universally proportional to depth.

The current experiment remains stationary, monostatic, reciprocal, principal-plane,
horizontally layered, and flat-bottom. It uses one common TX/RX principal-plane array
orientation and excludes vessel dynamics, independent TX/RX installation rotations,
multi-sector association, and full 3-D Mills-cross geometry.

## Implementation

Primary implementation:

```text
src/hydrosim/acquisition/principal_plane_array_tilt_depth_normalized_response.py
```

Validation:

```text
tests/test_principal_plane_array_tilt_depth_normalized_response.py
```

Related diagnostics:

```text
docs/science/principal_plane_array_tilt.md
docs/science/principal_plane_array_tilt_sensitivity.md
docs/science/principal_plane_array_tilt_sensitivity_map.md
docs/science/principal_plane_array_tilt_sounding_error_map.md
```
