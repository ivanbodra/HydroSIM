# PED-D17 Coverage and Density Contract

Status: authoritative minimum scientific contract  
Experience: `PED-D17`  
Scope: vendor-neutral reference acquisition-strip consequences for `PED-D17-O03` and `PED-D17-O04`

## Purpose

PED-D17 teaches how acquisition geometry and settings determine the spatial sampling pattern produced by a multibeam survey. This contract defines only the minimum deterministic consequences needed for learner-visible coverage/gaps and along/across spacing/density.

It reuses the canonical D8 beam/footprint geometry, D9 bottom-detection and High Density behavior, and D10 sector/transmit geometry. It does not define a parallel sonar, detector, or propagation model.

A central distinction is mandatory:

> **insonified coverage is not sounding density.**

A region may be acoustically insonified without containing a retained bottom detection, and High Density may increase the number of retained soundings inside an existing footprint without increasing that footprint's physical insonified area.

## Reference acquisition strip

The minimum PED-D17 reference case assumes:

- straight survey line;
- constant vessel speed `v >= 0` [m/s];
- constant effective ping rate `f_p > 0` [Hz];
- locally horizontal reference bottom at constant depth for the minimum 2-D spacing/coverage display;
- fixed sonar configuration during the displayed strip;
- canonical D8/D10 beam centres, sectors, swath and finite footprint geometry;
- canonical D9 retained detections, including High Density when enabled;
- no line-to-line overlap calculation: that belongs to PED-D16 survey planning;
- no stochastic missed detections unless explicitly supplied by the D9 detector state.

The strip is expressed in a local survey frame:

- `x`: along-track, positive in vessel travel direction;
- `y`: across-track, positive Starboard for the survey-display coordinate;
- bottom positions are Derived from the canonical HydroSIM geometry before spacing metrics are computed.

The survey-display `y` convention must not be confused with D8/D9's positive-Port beam-angle convention. Geometry must be transformed to positions first; spacing uses physical point coordinates and is therefore non-negative.

## Along-track ping spacing

For constant speed and effective ping rate,

`Delta_x_ping = v / f_p` [m].

Equivalent form using ping interval `T_p = 1/f_p`:

`Delta_x_ping = v * T_p`.

This is the distance between successive ping origins along the reference straight track.

Validity:

- `v >= 0`;
- `f_p > 0` and finite;
- constant speed/rate over the displayed interval.

At `v = 0`, successive ping origins have zero along-track separation; this does **not** imply infinite independent spatial information. The UI/API must report zero geometric ping spacing, not an infinite density claim.

If ping rate is unavailable, non-positive or non-finite, along-track spacing is `unavailable/invalid`; do not divide by zero or fabricate a fallback.

For a retained sounding belonging to beam/detection identity `j` whose across-track geometry is fixed from ping to ping, the first-slice along-track spacing between successive soundings of the same identity is also `Delta_x_ping`. This statement does not apply when sectors/detections alternate irregularly or the identity is absent from a ping.

## Across-track sounding spacing

For one ping, obtain the ordered set of **retained Derived bottom positions** from the canonical D8/D9/D10 chain:

`P = {p_1, ..., p_N}`.

Order them by across-track coordinate `y` from Port to Starboard (or vice versa, provided the API declares the order consistently).

For adjacent retained points,

`Delta_y_i = |y_(i+1) - y_i|` [m],  i = 1 ... N-1.

These are the canonical local across-track sounding spacings for PED-D17.

Do not infer across-track spacing from `swath_width / beam_count` unless the canonical geometry actually produces equally spaced bottom points. Equiangular beams on a flat bottom are generally not equidistant on the seabed; D8 already owns that distinction.

If fewer than two retained bottom points exist, adjacent across-track spacing is unavailable rather than zero.

Useful render-ready summaries may include:

- `min_across_spacing_m`;
- `max_across_spacing_m`;
- `mean_across_spacing_m`;
- ordered `adjacent_across_spacing_m[]`.

They are Derived summaries of the actual retained geometry, not configured beam spacing.

## Sounding density

PED-D17 uses geometric sample density, not statistical independence and not a manufacturer sounding-density specification.

### Along-track linear density

For `v > 0` and regular pings,

`rho_ping_x = 1 / Delta_x_ping = f_p / v` [pings/m].

At `v = 0`, this spatial-density quantity is **undefined/unavailable**, even though `Delta_x_ping = 0`, because repeated pings at one location do not define samples per travelled metre.

For one stable retained detection identity per ping, the same numerical relation may be labeled sounding samples per along-track metre for that identity.

### Across-track local linear density

For adjacent retained soundings with `Delta_y_i > 0`,

`rho_y_i = 1 / Delta_y_i` [soundings/m].

Coincident points (`Delta_y_i = 0`) do not yield infinite useful spatial density; report the coincidence/zero spacing explicitly and mark reciprocal density unavailable.

### Reference areal sampling density

For the regular reference strip only, a local sampling-cell approximation may be reported as

`rho_A_i = 1 / (Delta_x_ping * Delta_y_i)` [soundings/m^2]

when `Delta_x_ping > 0` and `Delta_y_i > 0`.

This is a **Derived geometric sampling-density proxy**, not an IHO coverage-quality metric, not an independent-footprint count, and not a probability of detection.

## Insonified coverage and gaps

Coverage/gap for PED-D17-O03 is defined from the union of canonical finite **insonified footprint intervals/areas**, not from the mere presence of beam-centre soundings.

For the minimum flat-bottom across-track display, each valid beam/detection parent supplies a canonical footprint interval

`F_i = [y_i_left, y_i_right]`

from D8/D10 finite-footprint geometry.

Sort valid intervals by left edge and merge overlapping/touching intervals. The merged union is the **insonified coverage** for that ping.

For two consecutive merged intervals `C_k=[a_k,b_k]` and `C_(k+1)=[a_(k+1),b_(k+1)]`, an internal across-track gap exists when

`a_(k+1) > b_k`,

with gap width

`G_k = a_(k+1) - b_k` [m].

Touching intervals (`a_(k+1) == b_k` within numerical tolerance) are continuous coverage with zero gap.

The outer region beyond the configured Port/Starboard swath limits is not an `internal gap`; it is simply outside the configured instantaneous swath.

A learner-visible result should expose at minimum:

- merged coverage intervals;
- total covered width (sum of merged interval widths, without double-counting overlap);
- internal gap intervals and widths;
- classification `continuous` when there is no internal gap, otherwise `gapped`;
- configured geometric swath extent separately from covered width.

Thus `geometric swath extent` and `insonified covered width` are not automatically identical.

### Along-track footprint continuity

When the canonical geometry supplies an along-track footprint length `L_x > 0`, consecutive pings provide continuous idealized along-track insonification for that footprint identity when

`Delta_x_ping <= L_x`

within numerical tolerance. If

`Delta_x_ping > L_x`,

the idealized gap between consecutive footprint intervals is

`G_x = Delta_x_ping - L_x`.

If canonical along-track footprint length is unavailable, PED-D17 must not infer along-track insonified coverage from ping spacing alone. It may still show ping/sounding spacing.

## High Density consequence

High Density is governed by `docs/science/ped_d9_high_density_phase_contract.md`.

For PED-D17:

- High Density may add multiple retained phase-derived bottom detections inside one parent receive-beam footprint;
- these additional points enter the ordered sounding set `P` and therefore can reduce local `Delta_y_i` and increase the Derived sounding-density metrics;
- the parent beam's physical footprint interval/area is unchanged by the mere act of retaining more phase-derived detections;
- therefore High Density **does not increase instantaneous physical insonified coverage** in this reference model;
- High Density can improve spatial sampling inside already insonified support, subject to the D9 phase-validity and spatial-decimation rules.

If High Density is enabled but D9 reports insufficient/ambiguous phase support, no additional soundings are fabricated and coverage remains that of the parent ordinary beam geometry.

The UI must not depict High Density as creating extra beams, widening the swath, or illuminating previously uninsonified seabed unless a separate canonical sonar configuration actually changes those quantities.

## Multisector and multiple detections

### Multisector

Use D10's actual canonical transmit-sector/beam geometry. Combine footprint intervals by physical union; overlapping sectors must not double-count insonified coverage. Retained sounding positions from all sectors may contribute to spacing/density after they are transformed to the same bottom/survey frame.

If sector transmit times differ enough that platform motion materially changes their spatial origin, use their canonical sector-specific geometry/timing rather than pretending all sector soundings are simultaneous. The minimum static reference may use the existing D10 render-ready positions when that effect is already resolved upstream.

### Generic multiple detection

D9 generic multiple detections may add retained sounding points, but a secondary detection does not by itself create a new parent acoustic footprint. Density is computed from retained bottom positions; physical coverage remains governed by the canonical insonified footprint geometry.

## State semantics

### Configured

- frequency and beam/footprint configuration;
- beam spacing mode/configuration;
- High Density enabled/disabled;
- swath/sector configuration;
- reference depth/scenario geometry;
- ping rate;
- vessel speed;
- multisector/detection settings.

### Observed

- D9 bottom detections, including valid High Density or generic multiple detections, retain their existing Observed semantics.

### Derived

- ping-origin spacing;
- retained bottom positions used by this contract;
- adjacent across-track sounding spacing;
- linear/areal sampling-density summaries;
- footprint union;
- covered width;
- gap intervals/widths;
- continuous/gapped classification;
- High Density ordinary-vs-HD density comparison.

No new Truth or Estimated state is created by these display consequences.

## Invalid and unsupported states

Return explicit unavailable/invalid status rather than synthetic values when:

- `f_p <= 0` or non-finite;
- `v < 0` or non-finite in this scalar-speed reference model;
- fewer than two retained soundings for an adjacent across-spacing metric;
- reciprocal density is requested for zero spacing;
- footprint support is absent for a coverage/gap calculation;
- required bottom positions are invalid/non-intersecting;
- mixed positions/footprints are not expressed in a common declared frame;
- High Density phase inversion is unavailable under the D9 contract.

A gap caused by a valid geometric footprint union is a legitimate Derived result and must not be labeled an invalid state.

## Minimum acceptance anchors

1. `v=5 m/s`, `f_p=10 Hz` -> `Delta_x_ping=0.5 m` and `rho_ping_x=2 pings/m`.
2. Doubling ping rate at fixed positive speed halves along-track ping spacing.
3. Doubling speed at fixed ping rate doubles along-track ping spacing.
4. `v=0` -> zero ping-origin displacement but unavailable spatial density per travelled metre.
5. Across-track spacing is computed from actual retained bottom positions, not `swath/beam_count`.
6. Overlapping footprint intervals are unioned without double-counting covered width.
7. Two separated footprint unions expose the exact internal gap between adjacent merged edges.
8. Touching footprint intervals are continuous coverage within numerical tolerance.
9. Enabling High Density with valid D9 phase support may increase retained sounding count/density while leaving parent insonified coverage unchanged.
10. Enabling High Density with insufficient phase support does not fabricate soundings or coverage.
11. Multiple detections may increase retained point count without automatically increasing footprint coverage.
12. If `Delta_x_ping > L_x`, the reference along-track footprint gap is `Delta_x_ping-L_x`; if `L_x` is unavailable, no along-track coverage claim is made.

## Implementation boundary

Scientific Core / canonical Python geometry owns the physical positions, footprint geometry and D9/D10 detection/sector consequences. The PED-D17 Core/application adapter may compute the deterministic spacing, union, gap and density summaries defined here and serialize them as render-ready outputs.

React may visualize those outputs and classifications but must not derive spacing, union footprints, infer High Density points, or invent coverage rules.

This contract intentionally stops before PED-D16 line planning, overlap between adjacent survey lines, IHO feature-detection requirements, probabilistic coverage, acoustic detectability, uncertainty/TPU, terrain-dependent survey-quality assessment, or vendor-specific sounding-density specifications.

## Reused authority

- `docs/science/ped_d9_high_density_phase_contract.md` — High Density phase-derived detections and spatial decimation.
- canonical PED-D8 beam-centre/finite-footprint geometry and equiangular/equidistant behavior.
- canonical PED-D9 bottom-detection semantics.
- canonical PED-D10 sector geometry/timing.
- `docs/conventions.md` — HydroSIM frames, units and state conventions.
