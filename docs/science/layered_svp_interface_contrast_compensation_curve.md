# Layered SVP interface-contrast compensation curve

Status: **controlled numerical diagnostic; not operational uncertainty**.

## Purpose

This diagnostic follows the zero-curvature contour of the existing controlled
processing-SVP experiment. Truth remains fixed while the processing interface depth
is prescribed and the lower-minus-upper sound-speed contrast is solved numerically so
that the edge-minus-nadir vertical curvature is approximately zero.

Let

```text
C_edge = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir
```

and define

```text
Delta_z_i = z_i,proc - z_i,true
Delta_Delta_c = Delta_c_proc - Delta_c_true
```

The compensation curve is the numerical family of pairs satisfying

```text
C_edge(Delta_z_i, Delta_Delta_c) ~= 0
```

within the requested root-finding tolerance.

## Root search

For every processing interface depth, the caller supplies one contrast bracket. The
implementation evaluates the curvature at both bracket ends and uses bisection only
when those values bracket a sign change. An endpoint already inside the curvature
tolerance is accepted directly. HydroSIM does not extrapolate a root outside the
supplied bracket.

Bisection is deliberately used here because it is simple, deterministic, and does not
require derivative smoothness or a particular local polynomial model.

## Relationship to the local sensitivity tangent

The existing local sensitivity diagnostic gives the first-order compensation slope at
Truth:

```text
d(Delta_c)/dz = -(dC/dz) / (dC/d(Delta_c))
```

when the contrast derivative is numerically resolvable. For every compensation-curve
point, HydroSIM also records the contrast error predicted by that local tangent and the
residual between the numerical root and the tangent prediction.

The tangent is a comparison diagnostic only. It is not used to force the root or to
assume global linearity.

## Scientific interpretation

A zero value of `C_edge` means only that the chosen edge-minus-nadir scalar curvature
metric is compensated. It does **not** imply that:

- the processing SVP equals Truth;
- every beam reconstructs the correct sounding;
- across-track error is zero;
- the complete swath is flat in every possible metric; or
- the processing-profile error is uniquely determined.

Consequently, the curve explicitly demonstrates one form of non-uniqueness: different
processing interface depths and sound-speed contrasts can produce the same scalar
curvature signature.

## Controlled validity domain

The underlying experiment remains:

- stationary and monostatic;
- reciprocal;
- horizontally layered and piecewise constant;
- flat-bottom;
- aligned pose;
- ideal transducer sound-speed measurement;
- zero principal-plane array tilt;
- one signed across-track principal plane.

## Limitations

The curve is not an oceanographic inversion, thermocline estimator, uncertainty model,
or operational correction algorithm. Root existence depends on the supplied contrast
bracket and on the controlled geometry. Multiple roots may exist in a broader domain;
this implementation returns the root associated with the supplied sign-changing
bracket and does not claim uniqueness beyond that bracket.

## Implementation

Module:

```text
hydrosim.acquisition.layered_svp_interface_contrast_compensation_curve
```

Primary function:

```text
run_layered_svp_interface_contrast_compensation_curve
```

Related models:

```text
hydrosim.integration.layered_svp_interface_contrast_map
hydrosim.integration.layered_svp_interface_contrast_local_sensitivity
hydrosim.integration.layered_svp_interface_contrast_sensitivity_convergence
```
