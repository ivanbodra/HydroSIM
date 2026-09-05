# PED-D12 Scientific Contract — Vessel Motion Consequences

Status: authoritative pedagogical-generation contract  
Experience: `PED-D12`  
Scope: first learner-facing reference experiment for Roll / Pitch / Yaw / Heading / Heave consequences

## Learning question

PED-D12 teaches how vessel/sensor motion changes the instantaneous sonar geometry and therefore changes where ideal beam centre-lines intersect the seafloor. The first production slice is a controlled geometric experiment. It does not model sensor error, motion latency, uncertainty, bottom-detection noise, or reconstructed sounding error.

The Scientific Core remains the sole owner of vessel attitude/pose transforms, beam directions and terrain intersection. React must visualize returned states only.

## Canonical conventions

Reuse HydroSIM canonical conventions:

- body frame `B`: `+X` Forward, `+Y` Starboard, `+Z` Down;
- local navigation/scene frame follows the existing right-handed NED-style convention;
- positive roll: Starboard down;
- positive pitch: bow up;
- positive yaw/heading change: Starboard/clockwise viewed from above;
- heave is positive upward, therefore a positive heave decreases Down position by the same magnitude;
- column vectors and existing active rotation composition remain authoritative.

## State semantics

### Configured learner state

- roll [rad internally; degrees permitted in UI];
- pitch [rad internally; degrees permitted in UI];
- yaw/heading [rad internally; degrees permitted in UI];
- heave [m], positive upward.

For this first reference experiment, the learner controls represent the **Truth vessel/sensor pose used to generate geometry**, not an Observed/Configured-vs-Truth mismatch.

### Derived outputs

- moved vessel/sensor pose;
- transformed beam centre-line directions;
- moved beam/terrain intersections;
- swath edge/width consequence from the moved edge-beam intersections;
- sounding displacement vectors between moved and no-motion reference intersections for corresponding beams.

These are `Derived` geometric consequences of the configured Truth pose. They are not measurement error, uncertainty, or Observed soundings.

## Reference experiment

### Beam/fan definition

Use a fixed three-beam reference set sufficient to expose the directional consequence without creating a new beam-spacing model:

1. Port edge beam;
2. nadir beam;
3. Starboard edge beam.

The edge angles must be equal and opposite in the canonical across-track convention. The production adapter may use a fixed default half-swath angle already supported by the canonical ideal-fan/beam primitives; the exact numerical default is application configuration, not new physics. The scientific invariant is symmetric edge steering about nominal nadir.

If the existing Core exposes an ideal equal-angle fan and Engineering prefers to return additional intermediate beams, that is permitted provided the Port/nadir/Starboard reference identities remain explicit and no new beam equation is introduced.

### Terrain/reference geometry

Use a horizontal canonical `PlaneTerrain` at a configured constant Down coordinate/depth in the common scene/navigation frame.

The learner-facing swath consequence is purely geometric:

- Port edge intersection position;
- Starboard edge intersection position;
- swath width = Euclidean horizontal/across-track separation of those edge intersections in the reference plane.

Do not interpret this as effective acoustic coverage, detectability, footprint width, or guaranteed sounding swath.

### Installation geometry

For the first PED-D12 consequence slice:

- sonar reference point is coincident with the vessel reference point used by the motion model;
- fixed sonar alignment is zero;
- no learner-configurable lever arm or installation misalignment is introduced.

This isolates dynamic vessel motion. Lever arms and installation offsets are taught separately in PED-D11/A2 and may be integrated later through the same canonical transforms.

### No-motion reference state

For every learner state, generate a paired reference state at the same nominal reference position and same terrain with:

- roll = 0;
- pitch = 0;
- yaw deviation = 0 relative to the selected nominal heading/reference orientation;
- heave = 0.

The reference is therefore the same experiment with dynamic motion removed, not a separately processed or estimated sounding solution.

If heading is exposed as an absolute orientation control, the no-motion comparison preserves the selected nominal heading and removes only the dynamic yaw deviation. UX/API metadata must make this distinction explicit so heading is not silently equated with yaw error.

## Sounding-consequence semantics

For each corresponding beam `i`, define

`delta_p_i = p_i,moved - p_i,reference`

where both points are ideal Truth beam-centre intersections with the same horizontal terrain.

`delta_p_i` is a `Derived` geometric displacement vector in the declared common frame. Its components may be shown as along-track, across-track and Down differences.

PED-D12-O04 must use this Truth-vs-reference geometric displacement. It must **not** use `SoundingComparison` Configured-vs-Truth reconstruction residuals, because no sensor/configuration error is being introduced in this lesson. Those semantics belong to later integration/error lessons.

## Cause → effect expectations

The authoritative outputs are the Core-transformed directions/intersections; the qualitative anchors below are acceptance guidance:

- positive roll rotates the swath about the Forward axis, producing opposite vertical/lateral consequences on Port and Starboard edge beams;
- pitch rotates the fan about the Starboard axis, producing primarily along-track displacement of beam intersections on a horizontal plane;
- yaw/heading rotates the horizontal orientation of the fan/swath footprint around Down and therefore rotates where non-nadir beams intersect in plan view;
- positive heave translates the sonar upward and therefore changes all beam intersection ranges/geometric positions coherently for a fixed terrain;
- zero roll/pitch/yaw-deviation/heave must produce zero `delta_p_i` for every corresponding beam;
- Port/Starboard symmetry must be preserved for a symmetric fan on horizontal terrain under zero roll/pitch/yaw deviation.

No fixed small-angle displacement formula is canonical for the learner output; Engineering must use existing rigid-body transforms and terrain intersection.

## Fidelity boundary

Included:

- rigid-body pose transformation;
- ideal beam centre-lines;
- horizontal plane terrain;
- corresponding Truth intersection comparison;
- geometric swath-edge/width consequence.

Excluded:

- finite beam footprint/directivity changes;
- sound-speed refraction;
- moving-receiver effects;
- timing/latency;
- sensor measurement error;
- installation misalignment/lever-arm error;
- bottom-detection noise;
- uncertainty propagation;
- vendor-specific stabilization or beam-control logic.

## Minimum acceptance anchors

1. Zero-motion configuration returns identical moved/reference intersections and zero displacement vectors.
2. Pure heave changes all beam-origin vertical positions coherently and preserves symmetric fan identity.
3. Pure roll on a symmetric horizontal-plane case preserves Port/Starboard beam identity and creates opposite-sign across-track/vertical geometric consequences where expected from the canonical rotation.
4. Pure pitch creates along-track intersection displacement without inventing a heading change.
5. Pure yaw/heading rotation changes plan-view orientation while preserving beam steering angles in the sonar frame.
6. Swath width is derived from edge intersections, never from an independent UI formula.

## Traceability

PED-D12 reuses existing HydroSIM vessel-motion, rigid-transform, ideal-beam/fan and plane-terrain primitives. Dynamic-motion error/signature models such as `docs/science/dynamic_motion_residuals.md` remain scientifically distinct because PED-D12 introduces motion itself, not a motion-sensor/configuration error.
