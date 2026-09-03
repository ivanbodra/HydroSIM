# PED-D8 Scientific Contract — Echosounders: SBES vs MBES

Status: authoritative pedagogical-generation contract  
Experience: `PED-D8`  
Scope: first production learner vertical slice

## Learning question

PED-D8 teaches the geometric difference between a single nadir sounding per ping and a multibeam swath formed by multiple steered receive beams, and how depth, beamwidth, incidence angle, beam count, angular sector, and beam-spacing strategy affect footprint, sounding positions, and instantaneous across-track coverage.

The first slice is deliberately geometric. It does not introduce bottom-detection algorithms, High Density/multiple detections, multisector transmission, stochastic uncertainty, vendor-specific beam layouts, calibrated gain, scattering/backscatter, or synthetic raw-data generation.

## Canonical Core ownership

The first slice must reuse the existing Scientific Core:

- `src/hydrosim/acquisition/beam_spacing.py` — canonical equiangular and equidistant receive-beam steering plans;
- `src/hydrosim/acquisition/layered_propagation.py` — canonical ray endpoints for the configured sound-speed profile;
- `src/hydrosim/acquisition/footprint.py` — reference flat-seafloor half-power/pulse rectangular footprint approximation;
- `src/hydrosim/acquisition/beam_pattern.py`, `array_factor.py`, `element_factor.py` — canonical ideal one-way directivity where a beam-pattern visualization is reused from PED-D6/PED-D7.

The application/API and React layers may compose and serialize these results but must not independently recreate beam-spacing, ray-endpoint, or footprint equations.

This PED-D8 identifier is distinct from the older `docs/science/d8_observation_state_contract.md`, which concerns the historical Sounding Formation / Detection Chain naming. That document remains authoritative for state semantics where applicable but does not define this pedagogical SBES-vs-MBES experience.

## State semantics

### Configured

Minimum controls for the first slice:

- system mode: `SBES` or `MBES`;
- vertical separation from sonar reference point to a horizontal flat seafloor `h` [m], `h > 0`;
- sound-speed profile used by the canonical propagation path; a constant profile is sufficient for the simplest anchor;
- pulse duration `tau` [s] and sound speed used by the compact footprint approximation;
- transmit along-track half-power beamwidth [rad];
- receive across-track half-power beamwidth [rad];
- for MBES only: receive beam count `N >= 2`, minimum and maximum across-track steering angles, and spacing method `equiangular` or `equidistant`;
- for equidistant MBES: target depth and start depth required by the canonical solver.

SBES first-slice geometry uses one nadir beam (`across_track_angle = 0`) and therefore has no beam-spacing mode.

### Derived

Canonical learner outputs are:

- steering angle(s) [rad/deg];
- ray endpoint across-track position(s) [m] at the configured target depth;
- adjacent sounding spacing(s) [m] across track;
- instantaneous geometric swath width [m], defined for this first slice as `max(endpoint_x) - min(endpoint_x)` for the MBES beam-centre endpoints at target depth;
- SBES instantaneous beam-centre swath width of zero (one centre point), while its finite insonified footprint remains non-zero;
- beam-limited along-track footprint width [m];
- beam-limited across-track footprint width [m];
- pulse-limited across-track width [m] when defined by the canonical footprint model;
- effective across-track footprint width, effective rectangular area, and limiting mechanism from `estimate_flat_seafloor_footprint()`;
- incidence angle from the local flat-bottom normal for each reference beam in the simplified flat-bottom case;
- optional canonical normalized directivity curves reused from PED-D6/PED-D7, if needed to explain that beamwidth is a response threshold rather than a hard physical edge.

These quantities are `Derived`. The first PED-D8 slice creates no new `Observed`, `Estimated`, or stochastic `Truth` state.

## Coordinate and sign conventions

PED-D8 inherits HydroSIM across-track geometry:

- vessel/sensor `+X`: Forward;
- `+Y`: Starboard;
- `+Z`: Down;
- zero across-track angle: nadir / `+Z`;
- positive across-track angle: Port (`-Y`);
- negative across-track angle: Starboard (`+Y`).

For display, Port and Starboard labels may accompany the signed angle/position. The sign must not be silently inverted by the frontend.

The beam-spacing Core currently returns signed across-track endpoint positions consistent with the sign of the requested steering angle. The application layer must preserve that ordering/sign convention.

## SBES first-slice boundary

SBES is represented as one co-located conceptual transmit/receive sounding direction at nadir per ping. Its pedagogical role is to provide the single-beam reference:

- one beam-centre endpoint at across-track position `0` on a level bottom;
- no receive-beam spacing strategy;
- a finite footprint determined by the configured beamwidth/pulse approximation;
- no claim that all operational SBES transducers have identical TX and RX aperture geometry.

The first slice may display TX/RX as a single conceptual channel or co-aligned beam. It must not infer a vendor-specific circular-piston response or a specific commercial transducer construction unless such a model is later added explicitly to the Scientific Core.

## MBES first-slice boundary

MBES is represented as a common ping with multiple ideal receive beam-centre directions spanning the configured across-track sector. The learner should see that multiple beam centres intersect the seafloor across a swath in one ping.

The first slice does not yet model a complete two-way Mills-Cross response. It may explain the conventional conceptual architecture — broad transmit insonification combined with multiple narrower steered receive beams — while using the existing footprint approximation (`transmit_along_track_beamwidth` × `receive_across_track_beamwidth`) for footprint geometry.

Distinct TX sectors, sector tilts, frequencies, pulse schedules, dynamic receive focusing, and vendor-specific beamforming belong to later experiences, principally PED-D10 and future higher-fidelity extensions.

## Equiangular versus equidistant beam spacing

The canonical beam-spacing behavior is already implemented in `beam_spacing.py`.

### Equiangular

`make_equiangular_beam_plan()` produces a constant steering-angle increment between configured minimum and maximum angles.

On a flat bottom, constant angular spacing does not imply constant seafloor spacing; outer-beam endpoint spacing generally differs from near-nadir spacing because the angle-to-bottom mapping is nonlinear.

### Equidistant

`make_equidistant_beam_plan()` solves steering angles so that ray endpoints are equally spaced across track at a specified target depth for the configured layered sound-speed profile.

This is stronger and more scientifically appropriate than substituting a flat, constant-sound-speed `atan(x/h)` approximation. The frontend must therefore consume the Core-generated angles/endpoints rather than deriving its own equidistant angles.

The current reference equidistant solver requires a sector spanning nadir. That validity condition must remain visible to the application; it must not be hidden by silent fallback to equiangular spacing.

## Footprint interpretation

The existing `footprint.py` model is an explicit compact approximation, not a hard physical insonification boundary.

For a horizontal flat seafloor it uses half-power beamwidth geometry and, away from nadir, a pulse-limited across-track projection. The resulting `effective_area_m2` is a rectangular effective approximation.

Therefore PED-D8 may use this model to demonstrate:

1. increasing depth increases beam-limited footprint dimensions;
2. incidence/steering away from nadir changes across-track footprint geometry;
3. pulse duration may become the across-track limiting mechanism for sufficiently oblique incidence;
4. a beam footprint is finite even though the beam-centre position is a point;
5. adjacent MBES footprints may overlap even when beam-centre soundings are distinct.

The UI must not label the -3 dB footprint boundary as the absolute edge of acoustic energy. Sidelobes and energy outside the half-power contour exist in the underlying directivity concept.

## Required cause → effect relationships

The first production experience must make these relationships observable:

1. **Single versus multiple simultaneous beam centres** — SBES presents one nadir beam centre; MBES presents multiple across-track beam centres in one ping.
2. **Depth scaling** — for fixed angular geometry on a flat bottom, greater depth expands endpoint separation/swath and beam-limited footprint dimensions.
3. **Incidence effect on footprint** — outer/oblique MBES beams have different projected across-track footprints than near-nadir beams under the canonical footprint approximation.
4. **Equiangular nonuniform bottom spacing** — equal angular increments do not in general produce equal endpoint spacing on the seafloor.
5. **Equidistant compensation** — the Core equidistant plan changes steering-angle increments so target-depth endpoint spacing is approximately constant.
6. **Beam count effect** — for a fixed sector and spacing strategy, changing beam count changes adjacent beam-centre spacing; it does not by itself change the configured outer-sector limits.
7. **Swath versus footprint distinction** — geometric swath width is an extent of beam-centre endpoints; footprint is the finite spatial support associated with an individual beam/pulse approximation. They must not be presented as the same quantity.

## Sounding-spacing boundary

PED-D8 first slice covers **instantaneous across-track beam-centre spacing within one ping** only.

Along-track sounding spacing requires vessel speed and ping rate/timing and belongs primarily to PED-D17 (Survey Coverage & Acquisition Trade-offs). The PED-D8 UI may state this dependency but must not fabricate along-track spacing from geometry alone.

Likewise, High Density multiple detections per beam and bottom-detection-dependent sounding multiplicity belong to PED-D9.

## Validity domain

The first PED-D8 slice assumes:

- horizontal flat reference seafloor for footprint comparison;
- deterministic geometry;
- one ping snapshot;
- ideal beam-centre steering directions;
- no bottom slope/roughness in the footprint approximation;
- no scattering/backscatter or target-strength physics;
- no stochastic observation noise;
- no bottom-detection algorithm;
- no multiple detections / High Density;
- no calibrated source/receive gain;
- no vendor-specific beam distribution;
- no multisector timing/frequency logic;
- no dynamic receive focusing;
- no along-track vessel-motion coverage model.

Layered sound-speed propagation may be used by the equidistant beam-spacing solver because that physics already exists in the Core. However, the compact footprint approximation remains a flat-bottom geometric approximation and must not be misrepresented as a full refracted 2-D footprint projection.

## Minimum scientific acceptance anchors

Engineering/tests for the PED-D8 adapter should preserve at least these properties:

- SBES on a horizontal bottom returns exactly one beam-centre endpoint at across-track `0` for the first-slice nadir configuration;
- a symmetric equiangular MBES sector with an odd beam count includes a nadir beam within numerical precision;
- the sign convention remains Port-positive / Starboard-negative for steering angles and endpoint positions;
- in a constant sound-speed flat-bottom reference case, symmetric `+theta` and `-theta` beams have equal-magnitude opposite-sign endpoints;
- for equiangular spacing, angular differences are constant within numerical precision while endpoint spacings need not be constant;
- for a valid equidistant case, target endpoint differences are constant within solver precision while angular differences need not be constant;
- MBES geometric swath width equals the maximum minus minimum beam-centre endpoint position at the target depth;
- increasing flat-bottom depth with fixed angular sector increases geometric swath width;
- the compact footprint output is obtained from `estimate_flat_seafloor_footprint()` rather than a duplicate frontend formula;
- footprint width/area remain positive for valid inputs, and the limiting mechanism is reported from the Core;
- equidistant requests outside the Core validity boundary fail explicitly rather than silently changing spacing strategy.

## First production payload boundary

A minimal PED-D8 application adapter is scientifically sufficient if it returns, from canonical Core calls:

- system mode and configuration metadata/units;
- signed beam steering angles;
- signed beam-centre target-depth endpoint positions;
- adjacent across-track beam-centre spacings;
- geometric beam-centre swath width;
- representative or per-beam footprint results from the canonical compact footprint model;
- explicit spacing-method metadata;
- for equidistant mode, target positions returned by the Core;
- explicit validity/error state when an unsupported configuration is requested.

The adapter may provide a synchronized SBES/MBES comparison payload for the same depth, sound-speed and beamwidth assumptions. It must not introduce a second geometry implementation in the application layer.

## References / traceability

Primary HydroSIM sources for this contract:

- `docs/pedagogy/hydrosim_pedagogical_plan.md` — PED-D8 learning scope;
- `docs/science/ped_d6_scientific_contract.md` — array/directivity construction boundary;
- `docs/science/ped_d7_scientific_contract.md` — electronic steering and sign conventions;
- `src/hydrosim/acquisition/beam_spacing.py`;
- `src/hydrosim/acquisition/layered_propagation.py`;
- `src/hydrosim/acquisition/footprint.py`;
- `src/hydrosim/acquisition/beam_pattern.py`.

PED-D8 therefore advances the learner from `how one beam is formed and steered` to `how one or many beam centres and footprints map onto the seafloor`, while leaving detection and operational multisector behavior to their dedicated experiences.