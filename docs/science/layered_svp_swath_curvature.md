# Layered SVP swath-curvature diagnostic

## Status

Controlled numerical diagnostic. It is not an operational uncertainty model.

## Purpose

A processing sound-speed profile that differs from Truth can reconstruct a physically
flat bottom as a curved cross-track swath. Hydrographic operators often describe such
signatures informally as a bottom that "smiles" or "frowns". HydroSIM quantifies the
underlying geometry without assigning those informal labels to a sign, because plot
orientation, depth-axis direction, and usage can differ.

This diagnostic isolates the finite-thickness processing-profile contribution:

```text
Truth profile != processing profile
transducer sound-speed bias = 0
principal-plane array tilt = 0
Truth bottom = flat
```

The A/B/C/D reference architecture is reused and the `profile_only` case is extracted.

## Reported response

For each signed configured beam angle `theta`, HydroSIM records calculated-minus-Truth:

```text
Delta_y(theta)
Delta_z(theta)
||Delta_r(theta)||
```

with Y positive starboard and Z positive down.

A compact edge-curvature diagnostic is

```text
C_edge = 0.5 * (Delta_z_port_edge + Delta_z_starboard_edge) - Delta_z_nadir
```

`C_edge` is useful for comparing controlled experiments. Its sign is retained in the
HydroSIM +Z/down convention; the implementation deliberately does not map positive or
negative values to the words "smile" or "frown".

## Expected symmetry in the controlled reference geometry

For a horizontal layered profile, flat bottom, aligned pose, and symmetric signed beam
angles, the reduced principal-plane experiment is mirror symmetric. Therefore the
validation expects approximately

```text
Delta_z(-theta) = Delta_z(+theta)
Delta_y(-theta) = -Delta_y(+theta)
```

This is a property of this controlled geometry, not a universal MBES swath-symmetry
law. Vessel attitude, sloping terrain, lateral sound-speed structure, independent TX/RX
frames, sector geometry, timing, or other errors can break it.

## Scientific interpretation

The visual curvature is a final sounding-domain response. It must not be confused with
one scalar sound-speed error or with the initial Snell ray-parameter mismatch alone.
Its magnitude and sign depend on the complete Truth and processing profiles, interface
depths, beam angle, water depth, and reconstruction geometry.

A uniform or layer-specific perturbation can therefore generate different swath shapes.
The next useful experimental family is to vary profile morphology explicitly, including
constant offsets, gradient approximations, thermocline-like layers, and displaced
interfaces.

## Validation

Tests verify:

- identical Truth and processing profiles reconstruct the flat bottom;
- a profile mismatch produces a nonzero edge-versus-nadir vertical response;
- the controlled flat/horizontal geometry has even vertical and odd across-track error;
- reversing a controlled profile perturbation changes the curvature response sign in
  the tested reference case;
- the angle axis must contain nadir and both sides of the swath.

## Implementation

```text
src/hydrosim/acquisition/layered_svp_swath_curvature.py
tests/test_layered_svp_swath_curvature.py
```

Related documents:

```text
docs/science/sound_speed_at_transducer.md
docs/science/principal_plane_array_tilt_sounding_error_map.md
docs/science/principal_plane_array_tilt_depth_normalized_response.md
```
