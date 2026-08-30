# Layered processing-SVP error family

## Status

Controlled deterministic diagnostic. It is not an operational uncertainty model and
its synthetic profiles are not climatology.

## Purpose

The flat-bottom swath-curvature diagnostic shows that a processing sound-speed
profile that differs from Truth can bend a reconstructed swath. This module adds a
controlled profile-family coordinate so different error morphologies can be compared
under exactly the same geometry, Truth profile, beam fan, and bottom.

Each case stores the complete processing profile used by reconstruction. HydroSIM does
not infer a physical oceanographic regime from a case name. Classification is only an
experiment descriptor.

Supported classifications are:

```text
reference
uniform_offset
layer_speed_perturbation
interface_displacement
synthetic_profile
```

The complete layered profile remains the authoritative experiment state.

## Experimental separation

For every member of the family:

```text
Truth profile = fixed
processing profile = case-specific
beam fan = fixed
flat bottom = fixed
transducer sound-speed bias = 0
principal-plane array tilt = 0
```

The response is therefore interpreted as a deterministic consequence of the supplied
finite-thickness processing profile within the controlled reference geometry.

## Typical controlled cases

A useful synthetic family can contain a reference profile together with cases such as:

- a uniform sound-speed offset applied to all layers;
- one or more layer-speed perturbations that approximate an incorrect gradient or
  contrast;
- displaced internal interfaces that represent an incorrect layer or thermocline
  depth;
- an arbitrary synthetic profile supplied explicitly for a focused experiment.

The terms above describe the experiment construction only. No case should be called a
realistic thermocline, seasonal profile, or regional water mass without separate
observational evidence and provenance.

## Response

Every case returns the existing `LayeredSvpSwathCurvature` result, including the full
signed beam response and the compact edge-versus-nadir metric

```text
C_edge = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir
```

This makes it possible to compare not only the magnitude of curvature but the complete
cross-track error signature.

## Validation properties

Tests verify that:

- the reference case closes to a flat reconstructed bottom;
- distinct explicit processing profiles can produce distinct curvature responses;
- two different case IDs carrying the same processing profile produce identical
  numerical results;
- supplied case ordering is preserved;
- empty families and duplicate case IDs are rejected.

The duplicate-profile test is important: the metadata coordinate must not alter the
physics.

## Limitations

The diagnostic does not impose a monotonic ranking among profile-error classes and does
not assume that one morphology always produces a larger error than another. Response
sign and magnitude depend on beam angle, water depth, complete layer structure, and
reconstruction geometry.

It also does not yet define continuous parameter sweeps for interface depth, sound-speed
contrast, or gradient strength. Those are natural next experiments after the discrete
family establishes the comparison architecture.

## Implementation

```text
src/hydrosim/acquisition/layered_svp_error_family.py
tests/test_layered_svp_error_family.py
```

Related diagnostic:

```text
hydrosim.integration.layered_svp_swath_curvature
```
