# Layered SVP interface-depth / sound-speed-contrast map

## Status

Controlled numerical diagnostic. This model is not an operational uncertainty model.

## Purpose

This diagnostic extends the one-dimensional processing-interface depth sweep into a
two-dimensional experiment. The Truth sound-speed profile, flat bottom, transducer
sound-speed measurement, and platform geometry remain fixed while two processing-SVP
coordinates are varied:

1. the depth of one selected interior horizontal interface; and
2. the sound-speed contrast across that processing interface.

The contrast coordinate is defined as

```text
Delta_c_proc = c_lower,proc - c_upper,proc
```

where the upper adjacent layer speed is held fixed and the lower adjacent layer speed
is set from the requested contrast.

## Construction

For every requested interface depth, HydroSIM first moves the selected interface while
preserving all layer speeds. For every requested contrast at that depth, it then keeps
the upper adjacent layer speed unchanged and sets

```text
c_lower,proc = c_upper,proc + Delta_c_proc
```

All unrelated layers and interfaces remain unchanged. This makes interface depth and
adjacent-layer contrast explicit, independent experiment coordinates.

The corresponding errors relative to Truth are

```text
Delta_z_i = z_i,proc - z_i,true
Delta_Delta_c = Delta_c_proc - Delta_c_true
```

with

```text
Delta_c_true = c_lower,true - c_upper,true
```

## Swath response

At each two-dimensional coordinate, HydroSIM reuses the existing controlled
`layered_svp_swath_curvature` experiment. It records the full calculated-minus-Truth
swath error and the edge-minus-nadir vertical-curvature diagnostic

```text
C_edge = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir
```

The sign follows HydroSIM's +Z/down convention. No automatic mapping from sign to the
informal terms "smile" or "frown" is imposed.

## Validation anchor

When both processing coordinates equal their Truth values, the constructed processing
profile is identical to Truth at the selected interface and adjacent layer. In the
controlled test profile this point reconstructs the flat bottom within numerical
tolerance.

This closure is a reference-model validation anchor. It does not imply linearity,
separability, monotonicity, or universal symmetry of the response away from the Truth
coordinate.

## Interpretation

The map is useful for visualizing interaction between two common profile-morphology
errors. A displaced interface and an incorrect layer contrast can reinforce, oppose,
or otherwise reshape the final swath curvature through the full layered propagation
and reconstruction geometry. Therefore the final sounding response should be
inspected numerically rather than inferred from either coordinate alone.

## Validity domain

The current model assumes a stationary monostatic reciprocal reference experiment,
horizontal piecewise-constant layers, flat bottom, aligned platform pose, ideal
transducer sound-speed sensor, zero principal-plane array tilt, and one selected
interior interface.

## Limitations

The sharp layer boundary is a controlled morphology, not a complete oceanographic
thermocline model. The model does not represent a continuous sound-speed gradient,
lateral gradients, terrain slope, vessel dynamics, independent TX/RX frames,
multisector effects, or stochastic uncertainty. No operational error limit should be
derived directly from this diagnostic.
