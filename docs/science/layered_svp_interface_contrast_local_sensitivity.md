# Layered SVP interface/contrast local sensitivity

## Status

Controlled numerical diagnostic. This model is not an operational uncertainty estimate and does not assert a universal oceanographic law.

## Purpose

The 2-D interface-depth/contrast map shows how the flat-bottom edge-minus-nadir curvature changes when two processing-SVP coordinates are varied together. This diagnostic extracts the local response around the Truth coordinate with a centered 3 x 3 finite-difference stencil.

The two coordinates are:

- processing interface depth `z`;
- lower-minus-upper adjacent-layer sound-speed contrast `dc`.

The response is the existing calculated-minus-Truth vertical swath-curvature metric:

```text
C(z, dc) = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir
```

The Truth profile, bottom, sensor state, and beam fan remain fixed.

## Centered stencil

Let the Truth coordinate be `(z0, dc0)`. The user supplies positive finite-difference steps `h` and `k`. HydroSIM evaluates:

```text
z  = z0 - h, z0, z0 + h
dc = dc0 - k, dc0, dc0 + k
```

This produces nine complete swath reconstructions through the existing interface/contrast map implementation.

## Local first derivatives

The centered numerical sensitivities are:

```text
dC/dz ~= [C(z0+h, dc0) - C(z0-h, dc0)] / (2 h)
```

and

```text
dC/ddc ~= [C(z0, dc0+k) - C(z0, dc0-k)] / (2 k)
```

Their units are deliberately kept distinct:

- `dC/dz`: metres of curvature per metre of interface-depth error;
- `dC/ddc`: metres of curvature per metre-per-second of contrast error.

HydroSIM does not combine these values into a Euclidean gradient norm because the two coordinates have different physical units. Any nondimensionalization would require an explicit scale choice and would itself become part of the experiment definition.

## Local compensation slope

If `dC/ddc` is numerically resolvable, the first-order tangent to the local zero-curvature contour is:

```text
d(dc)/dz = -(dC/dz) / (dC/ddc)
```

This quantity is reported as `contrast_compensation_slope_mps_per_m`.

It means only that, sufficiently close to the reference coordinate, a contrast change following this slope cancels the first-order change in the selected curvature metric. It does **not** imply that the full reconstructed swath is correct, that the compensation remains valid for large perturbations, or that one SVP error physically corrects another.

This distinction matters: different erroneous profiles can produce similar edge-curvature signatures while retaining different beam-by-beam errors.

## Second derivatives and interaction

The centered second derivatives are also reported:

```text
d2C/dz2 ~= [C(z0+h,dc0) - 2 C(z0,dc0) + C(z0-h,dc0)] / h^2
```

```text
d2C/ddc2 ~= [C(z0,dc0+k) - 2 C(z0,dc0) + C(z0,dc0-k)] / k^2
```

The mixed derivative is:

```text
d2C/(dz ddc) ~= [C(+h,+k) - C(+h,-k) - C(-h,+k) + C(-h,-k)] / (4 h k)
```

A non-zero mixed derivative is a local indication that depth and contrast coordinates interact in the curvature response. HydroSIM therefore does not assume a separable model such as:

```text
C(z,dc) = C_z(z) + C_c(dc)
```

A complementary corner interaction residual is evaluated as:

```text
R_int = C(z,dc) - C(z,dc0) - C(z0,dc) + C(z0,dc0)
```

and the maximum absolute residual over the four stencil corners is reported. This is a finite-step diagnostic and should not be confused with the mixed derivative itself.

## Scientific interpretation

The diagnostic is useful for identifying three distinct local behaviours:

1. **sensitivity** — how rapidly the selected swath-curvature metric responds to each coordinate near Truth;
2. **compensation** — the local direction in parameter space along which first-order curvature can remain approximately zero;
3. **interaction/nonlinearity** — whether changing one coordinate changes the response to the other.

The compensation direction creates an important identifiability warning. A nearly flat reconstructed bottom does not uniquely determine the processing SVP. Multiple combinations of interface-depth and contrast errors may produce similar curvature while differing elsewhere in the sounding solution.

## Validity domain

The inherited controlled experiment assumes:

- stationary monostatic reciprocal geometry;
- horizontal piecewise-constant layers;
- flat bottom;
- aligned pose;
- ideal transducer sound-speed sensor;
- zero principal-plane array tilt;
- one selected interior interface;
- lower adjacent layer speed parameterized relative to the unchanged upper-layer speed.

## Limitations

- The derivative values depend on the chosen finite-difference steps `h` and `k`.
- Convergence with decreasing step size is not automatically assumed; it should be checked when derivative accuracy matters.
- A sharp horizontal interface is a controlled morphology, not a continuous thermocline model.
- The local compensation slope applies only to the selected edge-minus-nadir curvature metric, not the complete swath-error vector.
- No global linearity, monotonicity, separability, or uniqueness is assumed.
- The diagnostic is not TVU, THU, confidence, or stochastic uncertainty.
- No lateral gradients, sloping terrain, vessel dynamics, independent TX/RX rotations, or multi-sector effects are represented here.

## Implementation

Module:

```text
hydrosim.acquisition.layered_svp_interface_contrast_local_sensitivity
```

Primary function:

```text
run_layered_svp_interface_contrast_local_sensitivity
```
