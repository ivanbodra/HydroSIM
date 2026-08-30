# Layered SVP compensated full-swath response

Status: **controlled numerical diagnostic; not operational uncertainty**.

## Purpose

The interface/contrast compensation curve identifies processing-SVP coordinates for
which the edge-minus-nadir vertical curvature is approximately zero:

```text
C_edge = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir ~= 0
```

That scalar condition does not require the complete reconstructed swath to equal Truth.
This diagnostic therefore re-evaluates every compensation-curve point across the full
configured signed beam fan and records the calculated-minus-Truth beamwise response.

## Beamwise quantities

For every configured beam angle, the inherited swath model reports:

```text
Delta_y(theta)
Delta_z(theta)
||Delta_r(theta)||
```

where `Delta_y` is across-track error, `Delta_z` is vertical error, and the error
convention is calculated minus Truth. HydroSIM uses a right-handed NED-like frame, so
positive Y is starboard and positive Z is down.

## Aggregate deterministic summaries

For each compensated swath, HydroSIM additionally reports:

```text
max |Delta_y|
RMS(Delta_y)
max |Delta_z|
RMS(Delta_z)
max ||Delta_r||
RMS(||Delta_r||)
```

The RMS values are simple summaries over the explicitly configured beam samples. They
are not standard deviations, confidence intervals, TVU/THU estimates, or stochastic
uncertainty measures.

## Scientific interpretation

The principal question is whether a processing-profile pair satisfying

```text
C_edge ~= 0
```

can still produce non-zero beamwise error. In the controlled reference experiment,
the Truth coordinate closes the complete swath, while off-Truth compensated coordinates
can retain non-zero vertical and across-track sounding errors even though the scalar
edge-curvature metric is essentially zero.

This is a direct demonstration of metric non-uniqueness: a single curvature indicator
can be insensitive to structured error that remains visible in the full swath.

The result does **not** imply that every off-Truth compensated point must have the same
hidden-error pattern or magnitude. The response depends on the complete Truth profile,
processing profile, beam fan, bottom depth, interface location, and sound-speed contrast.

## Relationship to the compensation curve

The compensation curve is authoritative for the numerical root coordinates. This
module does not re-fit or alter those roots. It evaluates the existing full swath at
each located depth/contrast pair and preserves the requested interface-depth order and
configured beam order.

## Controlled validity domain

The inherited experiment remains:

- stationary and monostatic;
- reciprocal;
- horizontally layered and piecewise constant;
- flat-bottom;
- aligned pose;
- ideal transducer sound-speed measurement;
- zero principal-plane array tilt;
- one signed across-track principal plane.

## Limitations

This diagnostic is not an oceanographic inversion, operational SVP correction method,
uncertainty model, or proof that `C_edge` is inadequate for every purpose. It shows only
that the chosen scalar curvature metric does not, by itself, guarantee full-swath
closure in the controlled model. The aggregate summaries also depend on the chosen beam
sampling and therefore must not be interpreted as sampling-independent physical norms.

## Implementation

Module:

```text
hydrosim.acquisition.layered_svp_interface_contrast_compensated_swath_response
```

Primary function:

```text
run_layered_svp_compensated_swath_response
```

Related models:

```text
hydrosim.integration.layered_svp_interface_contrast_compensation_curve
hydrosim.integration.layered_svp_interface_contrast_map
hydrosim.integration.layered_svp_swath_curvature
```
