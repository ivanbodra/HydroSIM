# Layered SVP interface-depth sweep

## Status

Controlled numerical diagnostic. It is not an operational uncertainty model.

## Purpose

This experiment isolates the effect of placing one horizontal sound-speed interface at
the wrong depth in the processing profile while keeping the Truth profile fixed.
The adjacent layer sound speeds are unchanged; only the selected processing boundary
moves.

```text
Truth profile: fixed
processing profile: one interface depth varied
transducer sound-speed bias: 0
principal-plane array tilt: 0
Truth bottom: flat
```

The resulting reconstructed swath is evaluated with the existing layered SVP
swath-curvature diagnostic.

## Interface coordinate

For an interface after layer `i`, the Truth depth is

```text
z_i,true = bottom_depth(layers[i])
```

For each processing coordinate `z_i,proc`, HydroSIM records

```text
Delta_z_i = z_i,proc - z_i,true
```

Positive interface-depth error therefore means the processing interface is deeper than
Truth because HydroSIM uses +Z downward.

The sweep also records the existing signed edge-curvature metric

```text
C_edge = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir
```

where sounding error is calculated minus Truth and Z is positive down.

## Construction of the processing profile

Only the two layers adjacent to the selected interface change geometrically:

```text
upper.bottom = z_i,proc
lower.top    = z_i,proc
```

Their sound speeds remain unchanged, all other layers remain unchanged, and the profile
remains contiguous. The requested boundary must stay strictly inside the combined
vertical extent of those two adjacent layers.

This is deliberately a deterministic morphology experiment. It does not imply that a
sharp piecewise-constant interface is a complete physical model of a real thermocline.

## Interpretation

If `z_i,proc = z_i,true`, the processing profile equals Truth at that interface and the
controlled profile-only curvature closes to zero.

Moving the interface changes the fraction of the reconstructed path assigned to each
sound-speed layer. The resulting sounding-domain response can be nonlinear with
interface displacement, beam angle, water depth, and sound-speed contrast. HydroSIM
therefore stores the full swath response for every sweep coordinate rather than
assuming a linear error law.

The sign of `C_edge` is retained in the HydroSIM +Z/down convention and is not mapped
automatically to the informal words "smile" or "frown".

## Validation

Tests verify that:

- moving an interface preserves all layer sound speeds and all unrelated interfaces;
- the Truth interface depth reconstructs the flat bottom within numerical tolerance;
- small opposite interface displacements around Truth produce opposite curvature signs
  in the controlled reference case;
- requested sweep order is preserved;
- invalid interface indices, invalid boundary depths, and empty sweeps are rejected.

The opposite-sign test is a local controlled validation anchor for the selected profile,
not a universal monotonicity theorem for arbitrary SVPs.

## Implementation

```text
src/hydrosim/acquisition/layered_svp_interface_depth_sweep.py
tests/test_layered_svp_interface_depth_sweep.py
```

Related diagnostics:

```text
hydrosim.integration.layered_svp_swath_curvature
hydrosim.integration.layered_svp_error_family
```
