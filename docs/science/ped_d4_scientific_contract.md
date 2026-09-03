# PED-D4 Scientific Contract — Sound Speed & Refraction

Status: active pedagogical scientific contract

## Purpose

`PED-D4` teaches why a sound-speed profile bends an acoustic ray and why using an incorrect processing profile produces a different reconstructed path. It reuses HydroSIM's existing layered Snell model; it does not introduce a parallel propagation model.

The pedagogical question is:

> How do sound-speed structure and launch angle change acoustic path, travel time and inferred geometry?

## Canonical scientific source

PED-D4 shall consume the existing reference model:

- Registry: `hydrosim.propagation.layered_snell_piecewise_constant`
- Implementation: `src/hydrosim/acquisition/layered_propagation.py`
- Transducer/profile boundary semantics: `docs/science/sound_speed_at_transducer.md`

No propagation equation is to be reimplemented in the presentation layer.

## Reference formulation

For horizontally stratified, piecewise-constant sound-speed layers, the conserved ray parameter is

```text
p = sin(theta_i) / c_i
```

where `theta_i` is measured from the local downward vertical and `c_i` is the sound speed in layer `i`.

Within each layer:

```text
theta_i = asin(p c_i)
dx_i    = dz_i tan(theta_i)
ds_i    = dz_i / cos(theta_i)
dt_i    = ds_i / c_i
```

The current HydroSIM reference implementation is 2-D, downward-propagating and rejects critical/turning conditions explicitly.

## State semantics

For the basic learner experiment:

- learner-selected launch angle: **Configured**;
- learner-selected sound-speed profile used for a ray: **Configured**;
- ray parameter, refracted angles, path segments, horizontal offset, path length and travel time: **Derived**.

For the incorrect-profile comparison:

- a designated reference profile may be treated as exercise **Truth** only when the lesson explicitly declares it as the hidden/reference environment;
- the profile used to reconstruct/process the same travel-time observation is **Configured**;
- the resulting reconstructed path/endpoint is **Derived**;
- the difference between reconstruction and the declared Truth result is a **Derived simulation-truth error**, not an Observed uncertainty estimate.

The UI must not relabel a Configured processing profile as an observation.

## Minimum PED-D4 experiments

### 1. Constant sound speed anchor

A constant-c profile must reduce to straight-line geometry. Changing sound speed while preserving the same launch angle changes travel time for a fixed path geometry but does not create refraction in a homogeneous medium.

### 2. Two-layer refraction

For two horizontal layers with different `c`, the learner must be able to see:

- the angle change at the interface;
- conservation of `p = sin(theta)/c`;
- the resulting horizontal displacement, path length and travel time.

The visualization should make the cause/effect link explicit rather than presenting only final numbers.

### 3. Launch-angle sensitivity

For the same profile, increasing the launch angle away from vertical generally increases horizontal displacement and path length. The experience must remain inside the validity domain of the current model and must not silently cross a critical/turning condition.

### 4. Correct vs incorrect processing profile

Use one declared reference/Truth layered profile to generate a ray/travel time. Reconstruct the same travel time with a different Configured processing profile using the canonical time-driven solver. Compare:

- reference path;
- processing/reconstructed path;
- endpoint horizontal/depth differences where defined;
- path-length/travel-time consistency.

This comparison is pedagogical error formation, not a full survey uncertainty model.

## Required learner-visible quantities

The minimal scientific outputs are:

- depth and sound speed of each profile layer;
- launch angle from vertical, degrees in UI / radians internally;
- per-layer refracted angle;
- horizontal distance;
- acoustic path length;
- travel time;
- optional ray parameter readout for the Snell-law demonstration;
- correct-vs-processing endpoint/path difference for the incorrect-profile experiment.

Every numerical value must originate from canonical Python Core/application outputs.

## Validity and limitations

PED-D4 v0.1 is deliberately limited to the current reference model:

- geometrical acoustics;
- horizontally stratified medium;
- finite piecewise-constant layers;
- downward propagation;
- 2-D propagation plane;
- no critical/turning branch;
- no range-dependent environment;
- no absorption, scattering, diffraction or multipath in ray geometry.

A plotted polyline through layer segments is a representation of the piecewise-constant reference solution, not a continuously curved gradient ray.

The previously specified environmental T/S/P profile-extension concept remains deferred post-v0.1 and is not required for PED-D4 completion.

## Scientific invariants for tests

1. Constant-c profile gives straight-ray geometry within numerical tolerance.
2. In traversed layers, `sin(theta_i)/c_i` is constant within numerical tolerance.
3. Sum of segment travel times equals total travel time.
4. Sum of segment path lengths equals total path length.
5. Depth-driven and time-driven solutions close on the same ray when supplied the corresponding travel time.
6. Critical/turning conditions are rejected explicitly rather than extrapolated silently.
7. A finite supplied SVP is not silently extended beyond its declared depth domain.

Existing Core tests already cover the principal mathematical anchors; PED-D4 integration tests should verify that the learner-facing adapter preserves these semantics rather than duplicating the solver.

## Non-goals

PED-D4 does not add:

- environmental sound-speed prediction from temperature/salinity/pressure;
- oceanographic climatology or profile extrapolation;
- multipath or turning rays;
- absorption/TL (covered by PED-D3);
- surface-sound-speed installation errors beyond the already documented boundary model;
- full sounding reconstruction chain (covered later by PED-D15).

## Traceability

- `scientific_registry/models/propagation/layered_snell_piecewise_constant.yaml`
- `src/hydrosim/acquisition/layered_propagation.py`
- `docs/science/sound_speed_at_transducer.md`
- `docs/pedagogy/hydrosim_pedagogical_plan.md`
- `tests/test_layered_propagation.py`
