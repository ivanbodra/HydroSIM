# PED-D6 Scientific Contract — Transducer & Array Construction

Status: authoritative pedagogical-generation contract  
Experience: `PED-D6`  
Scope: first production learner vertical slice

## Learning question

PED-D6 teaches how physical element size, element spacing, element count/aperture, acoustic frequency and wavelength shape the normalized directivity of an ideal transducer array.

The first slice is intentionally limited to the already-authoritative HydroSIM far-field narrowband models. It must not introduce vendor-specific geometry, calibrated source/receive gain, near-field focusing, mutual coupling, or an independent frontend beam equation.

## Canonical Core ownership

The Scientific Core is the sole owner of the physics:

- `src/hydrosim/geometry/arrays.py` — regular centred 1-D/rectangular array geometry, element count, spacing, element dimensions and physical aperture;
- `src/hydrosim/acquisition/element_factor.py` — ideal rectangular-element one-way far-field directivity;
- `src/hydrosim/acquisition/array_factor.py` — ideal coherent one-way narrowband array factor, steering direction and complex element weights;
- `src/hydrosim/acquisition/beam_pattern.py` — physical one-way element-factor × array-factor composition and across-track scan with local half-power (-3 dB) beamwidth;
- `docs/science/array_factor.md` and `docs/science/beam_pattern.md` — canonical derivation, conventions, analytical anchors and limits.

The application/API and React layers may serialize, localize and visualize these outputs, but must not reproduce their equations.

## State semantics

### Configured

Minimum learner controls for the first slice:

- acoustic frequency `f` [Hz], `f > 0`;
- sound speed `c` [m/s], `c > 0`;
- element count on the active axis `N >= 1`;
- inter-element centre spacing `d` [m], with `d > 0` for `N > 1`;
- physical element face dimension on the active axis `a` [m], `a > 0`;
- steering angle may be fixed at broadside for the PED-D6 baseline; interactive steering belongs primarily to PED-D7.

A simple 1-D regular array is the required baseline because it isolates the relationships PED-D6 is intended to teach. The existing rectangular 2-D `TransducerArray` remains canonical and may be exposed later without changing the science.

### Derived

The Core-derived learner outputs are:

- wavelength `lambda = c / f` [m];
- element-centre positions [m];
- physical aperture [m], using the canonical `TransducerArray.aperture_*` property;
- normalized one-way element-factor response;
- normalized one-way array-factor response;
- normalized one-way physical beam pattern `element factor × array factor`;
- normalized power versus angle;
- peak angle and peak normalized power;
- local half-power (-3 dB) beamwidth when both crossings lie inside the sampled angular interval;
- visible side-lobe / grating-lobe structure present in the computed normalized pattern.

These quantities are `Derived`. PED-D6 does not create `Observed`, `Estimated`, or environmental `Truth` state.

## Required cause → effect relationships

The first production experience must make the following effects observable through canonical Core outputs:

1. **Frequency / wavelength** — for fixed physical geometry and sound speed, increasing frequency decreases wavelength and changes the electrical/acoustic aperture (`aperture / wavelength`), generally narrowing the main lobe while changing lobe structure.
2. **Element count / aperture** — when spacing and element size are fixed, adding elements increases physical aperture and generally narrows the main lobe.
3. **Spacing relative to wavelength** — changing `d / lambda` changes the interference pattern. Large spacing can create additional coherent maxima (grating lobes / spatial aliasing); these must be shown as results of the computed pattern, not hidden by the UI.
4. **Finite element size** — the rectangular element factor forms an angular envelope independent of the array-factor calculation; element size and element spacing therefore remain separate learner concepts.
5. **Beamwidth** — the authoritative scalar beamwidth for this slice is the local half-power width returned by `scan_across_track_beam_pattern()`. If a crossing falls outside the requested scan interval, beamwidth is unavailable; the application must not extrapolate one.

Approximate textbook rules such as beamwidth proportional to `lambda / aperture` may be shown only as qualitative intuition or clearly labelled approximations. The configured array's computed Core pattern is authoritative.

## Side lobes, grating lobes and gain language

The present outputs are normalized pressure/amplitude-like and normalized-power responses. They are not calibrated acoustic gain, source level, receive sensitivity, directivity index, or a two-way sonar response.

Accordingly:

- learner-facing text may discuss relative main-lobe width, side lobes and grating lobes;
- the UI must not label normalized pattern values as absolute `gain [dB]` unless a later calibrated scientific contract explicitly introduces that quantity;
- a dB display of normalized power is permissible if it is explicitly relative to the pattern peak (for example `dB re peak`) and zero/near-zero handling is numerically bounded by the application layer without altering the Core physics.

## Shading / apodization boundary

`array_factor()` already accepts arbitrary complex element weights, so the Core can represent deterministic weighting without changing the array-factor equation. However, HydroSIM currently has no canonical scientific model that generates named learner-facing taper families or defines their parameterization.

Therefore the PED-D6 first slice uses **uniform unit weights**. Named shading/apodization controls (Hann, Hamming, Taylor, etc.) are deferred until a canonical weight-generation contract exists. PED-D7 may later consume the existing complex-weight capability when steering/apodization is explicitly specified.

This prevents the frontend or application adapter from inventing taper equations.

## Mills Cross / eccentricity boundary

The repository contains validated Mills-Cross/two-way infrastructure, but it is not required for the first PED-D6 slice. PED-D6 first establishes one-array construction and one-way directivity.

Detailed TX/RX orthogonal-array composition, Mills Cross architecture, eccentricity or installation-specific geometry must be introduced only under a dedicated scientific/learning contract where their role is explicit (principally PED-D7/PED-D8 and later integrated sonar geometry). They must not block PED-D6 production delivery.

## Coordinate and angle convention

For the canonical across-track scan:

- array/sensor `+Z` is the normal/down direction;
- zero across-track angle is the `+Z` normal;
- positive across-track angle points Port (`-Y`);
- negative across-track angle points Starboard (`+Y`).

The application layer may convert radians to degrees for learner presentation but must preserve the sign convention.

## Validity domain

The first PED-D6 model assumes:

- ideal regular centred array geometry;
- deterministic element positions and dimensions;
- far-field plane-wave propagation;
- one monochromatic/narrowband frequency per evaluation;
- ideal identical rectangular elements;
- uniform weights in the first learner slice;
- no mutual coupling;
- no element/channel calibration mismatch;
- no stochastic noise;
- no finite-bandwidth beam squint;
- no near-field/dynamic focusing;
- no calibrated absolute transmit/receive gain;
- no vendor-specific beamformer behavior.

These are model limits, not UI caveats to be silently corrected by another layer.

## Minimum scientific acceptance anchors

Engineering/tests for the adapter should preserve at least these properties:

- broadside uniform-array response peaks at normalized amplitude/power approximately 1;
- changing only overall complex weight scale cannot change normalized array-factor magnitude;
- for the existing analytical two-element case with `d = lambda/2`, broadside steering and a 30-degree source direction, normalized array-factor magnitude is `sqrt(2)/2` and normalized power is `0.5`;
- with broadside steering and `d = lambda`, the canonical model exhibits a grating-lobe/spatial-alias response at the endfire anchor documented in `docs/science/array_factor.md`;
- increasing element count at fixed spacing must update physical aperture through `TransducerArray`, not through a duplicated adapter formula;
- half-power beamwidth is reported only when the Core scan finds both threshold crossings.

## First production payload boundary

A minimal PED-D6 application adapter is scientifically sufficient if it accepts the Configured controls above and returns, from canonical Core calls:

- configuration metadata and units;
- wavelength and physical aperture;
- element positions/count;
- sampled across-track normalized amplitude/power pattern;
- peak angle/power;
- half-power beamwidth or explicit unavailable state;
- enough metadata to distinguish element factor, array factor and their combined physical one-way beam pattern if the learner visualization exposes those curves.

No new equation is required for this adapter.

## References / traceability

Primary HydroSIM scientific sources for this contract:

- `docs/science/array_factor.md`;
- `docs/science/beam_pattern.md`;
- `src/hydrosim/geometry/arrays.py`;
- `src/hydrosim/acquisition/element_factor.py`;
- `src/hydrosim/acquisition/array_factor.py`;
- `src/hydrosim/acquisition/beam_pattern.py`.

PED-D6 deliberately reuses those implemented reference models rather than defining a parallel pedagogical formulation.
