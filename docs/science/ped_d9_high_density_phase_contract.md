# PED-D9 High Density Phase Contract

Status: authoritative pedagogical-generation scientific contract  
Experience: `PED-D9`  
Scope: minimum sourced phase-based High Density learner slice

## Purpose

HydroSIM `High Density` is a phase-based extension of bottom detection. It uses split-aperture receive-phase information to resolve additional time/angle bottom detections **inside the finite footprint of one steered receive beam**, so one beam may contribute more than one bottom point to a ping.

This is scientifically distinct from the generic multiple-detection contract in `ped_d9_detection_extension_contract.md`. Generic multiple detection retains more than one independent matched-filter peak/echo candidate. High Density instead extracts additional bottom samples from the **phase trajectory associated with one bottom interaction / beam footprint**.

The first HydroSIM model is a transparent, source-grounded reference model, not a reproduction of proprietary Kongsberg processing and not a claim that every MBES implements High Density identically.

## Scientific basis

Split-aperture phase bottom detection is established practice. The receive aperture is divided into two sub-apertures; their phase difference varies with arrival direction. The conventional phase detection uses the zero-phase crossing to estimate the arrival time at the steered beam centre.

Kongsberg's EM 2040 documentation explicitly states that, in High Density mode, the phase curve for one beam is used to derive more than one detection rather than only the beam-centre detection, with sounding spacing chosen to obtain approximately equidistant bottom sampling. The same documentation notes that phase detection becomes unreliable when too few phase samples exist or the phase curve is too noisy, commonly near normal incidence/shallow geometry.

Peer-reviewed work on split-beam phase bottom detection likewise describes the phase difference between sub-apertures, the zero crossing at the beam-axis arrival, and the need for a sufficiently coherent/approximately linear phase trend around the bottom interaction.

Primary references:

- Kongsberg Maritime, *EM 2040 Multibeam Echosounder Instruction Manual*, document 346210, section `Bottom detection`.
- Trenkel, V. M. et al. (2009), `Methodological developments for improved bottom detection with the ME70 multibeam echosounder`, *ICES Journal of Marine Science*, 66(6), 1015–1022.

Evidence level:

- split-aperture phase difference and beam-centre zero crossing: `direct_source`;
- more than one detection from one beam phase curve in High Density mode: `direct_source` from the Kongsberg manual;
- the explicit HydroSIM inversion/decimation algorithm below: `derived_from_source`, chosen to make the source-described behavior transparent and deterministic without reproducing proprietary processing.

## Canonical geometry and phase convention

Reuse HydroSIM's existing receive-array convention from `docs/science/array_factor.md`.

Direction unit vectors point from the receive-array centre toward the acoustic source / bottom-scatter direction. Across-track angle is:

- `0`: array-local `+Z` normal;
- positive: Port (`-Y`);
- negative: Starboard (`+Y`).

For carrier frequency `f` [Hz], sound speed `c` [m/s], wavelength

`lambda = c / f`

and wavenumber

`k = 2*pi/lambda`,

let:

- `u(theta)` be the unit source-direction vector for across-track angle `theta`;
- `u0` be the configured steering direction of the receive beam;
- `b` [m] be the effective split-aperture phase-centre baseline vector expressed in the same receive-array frame.

The ideal differential phase relative to the steered direction is

`Delta_phi(theta) = k * (u(theta) - u0) dot b`.

This is the same residual spatial-phase relation already used by HydroSIM's canonical array-factor model, applied here to the two effective split-aperture phase centres.

At the steered direction,

`u(theta) = u0  =>  Delta_phi = 0`.

For an observed unwrapped differential phase sample `Delta_phi_j`, the phase-derived arrival angle `theta_j` is the unique solution inside the configured receive-beam angular support of

`k * (u(theta_j) - u0) dot b = Delta_phi_j`.

The implementation should solve this bounded one-dimensional equation numerically rather than introduce a second scalar sign convention. If no unique solution exists inside the beam support, the sample is not a valid High Density candidate.

## Inputs

### Configured

- `high_density_enabled`: boolean learner selector;
- receive beam steering angle / direction `u0`;
- receive-beam angular support or canonical finite footprint boundary;
- effective split-aperture phase-centre baseline vector `b` [m] in the declared receive-array frame;
- carrier frequency `f` [Hz], `f > 0`;
- sound speed `c` [m/s], `c > 0`;
- sample times / arrival offsets for the configured detection window [s];
- phase-validity window within that detection window;
- ordinary-beam reference footprint width `W_ref` [m] when spatial decimation is requested.

`W_ref` must come from HydroSIM's canonical footprint/beam geometry for the same beam and range/depth scenario. It must not be invented in the frontend.

### Observed / supplied signal state

For each sample in the phase-validity window:

- split-aperture differential phase `Delta_phi_j` [rad], locally unwrapped around the bottom interaction;
- corresponding signal/correlation magnitude used only to retain the already-established bottom-support window and reject undefined/zero-support samples.

The phase series is an acoustic observation/synthetic observation supplied by the scientific model. React must not synthesize it from display geometry.

## Reference High Density algorithm

### 1. Establish the ordinary phase-centre detection

The ordinary phase detection is the zero crossing of the locally fitted/unwrapped differential phase curve nearest the established bottom-support amplitude maximum. This yields the conventional centre detection `(t0, theta0)`.

`theta0` equals the configured steering direction within numerical tolerance for the ideal reference case.

### 2. Form phase-derived time/angle candidates

For each valid phase sample `j` inside the bottom-support window:

1. recover `theta_j` from the bounded inverse phase relation above;
2. retain only candidates inside the configured beam angular support;
3. preserve the sample arrival time `t_j` as the detection timing coordinate.

Each retained pair `(t_j, theta_j)` is a **phase-derived detection candidate**. The phase value changes the estimated arrival direction; it is not converted into a second matched-filter peak.

### 3. Convert to a pedagogical bottom coordinate only under the explicit homogeneous reference geometry

For the minimum High Density learner slice, a Cartesian comparison is permitted only in the existing straight-ray homogeneous-water reference case with monostatic timing and constant `c`.

Then:

`r_j = c * TWTT_j / 2`

and the local derived point is

`p_j = r_j * u(theta_j)`

relative to the acoustic reference origin, with the existing HydroSIM frame transform applied when a containing frame is needed.

These Cartesian points are **Derived**. The underlying time/angle `BottomDetection` remains **Observed**.

Do not use `c*TWTT/2` for a refracting or otherwise non-straight propagation case; such a case must use the canonical propagation/reconstruction chain instead.

### 4. Spatial decimation — do not equate raw sample rate with sounding density

High Density sounding count must not simply equal the number of digitized phase samples. Neighboring signal samples are not independent physical footprints.

The minimum HydroSIM reference rule therefore selects an approximately equidistant subset of valid phase-derived bottom candidates using a target across-bottom spacing

`s_HD = W_ref / 2`.

This choice is a transparent `derived_from_source` reference rule motivated by the Kongsberg documentation statement that the High Density footprint is typically about twice the across-track sampling distance. It is **not** a universal manufacturer invariant.

Selection is deterministic:

1. retain the valid candidate nearest the ordinary beam-centre detection;
2. progress outward toward Port and Starboard independently in increasing ground-distance from that centre;
3. retain the next candidate when its local bottom-point separation from the most recently retained candidate on that side is at least `s_HD`;
4. never retain a candidate outside the original configured beam footprint/support.

If the valid phase trajectory and footprint are too short to satisfy the spacing rule, High Density may legitimately produce only the ordinary centre detection.

## Output/state semantics

### Observed

Each High Density time/angle result is a `BottomDetection`-like observation containing at minimum:

- parent receive beam identity;
- stable detection index;
- method identifier `phase_high_density` (a new explicit method label; do not mislabel non-centre samples as ordinary `phase_zero_crossing`);
- arrival/TWTT;
- phase-derived across-track angle;
- source phase sample / quality metadata when exposed by the Python model.

One receive beam may therefore own multiple High Density detections.

### Derived

- Cartesian bottom points under the explicit reference propagation geometry;
- High Density detection count;
- along/across-bottom spacing between retained points;
- comparison against ordinary one-detection-per-beam output;
- density multiplier/count ratio for the displayed ping, clearly labeled as a **Derived scenario result**, not a guaranteed system specification.

No new `Truth` or `Estimated` state is created by enabling High Density.

## Distinction from generic multiple detection

The two concepts must remain separate:

**Generic multiple detection**
- starts from multiple distinct local maxima / echo candidates in the matched-filter response;
- may represent more than one physical reflector/return opportunity in one beam;
- candidate identity comes from separate amplitude/correlation peaks.

**High Density**
- starts from one beam's coherent split-aperture phase trajectory over the bottom-support window;
- uses phase-derived direction information at multiple times inside the finite beam footprint;
- increases bottom sampling of that one footprint even when there is only one ordinary bottom-return peak.

High Density must therefore not call the generic local-peak detector repeatedly and must not be implemented as an alias for `multiple_detection=true`.

## Validity / fidelity boundary

The first High Density slice assumes:

- far-field split-aperture receive geometry;
- one dominant coherent bottom interaction inside the selected detection window;
- locally unwrapped differential phase;
- a phase curve sufficiently coherent to support a unique direction inversion;
- known effective split-aperture baseline vector;
- narrowband carrier phase for the direction inversion;
- no stochastic phase-noise model;
- no phase-wrap ambiguity outside the chosen local window;
- no multipath or unresolved competing bottom interfaces inside the same phase-support interval;
- no claim of reproducing Kongsberg proprietary filtering, fitting, quality weighting, footprint adaptation, or exact sounding-count logic.

When phase support is insufficient, non-monotonic/ambiguous, or yields no unique angle inside the beam support, the High Density result is **unavailable for that beam**. The implementation must not fabricate extra detections. A separate ordinary amplitude detector may still produce a valid bottom detection according to its own contract.

## Minimum acceptance anchors

1. **Beam-centre anchor:** `Delta_phi = 0` in the ideal model recovers the configured steering direction `u0`.
2. **Forward/inverse closure:** phase generated from a known in-support `theta_test` through the canonical residual-phase equation is inverted back to `theta_test` within numerical tolerance.
3. **Sign preservation:** a known Port/Starboard test direction round-trips without reversing HydroSIM's positive-Port / negative-Starboard convention.
4. **Footprint containment:** no High Density detection is emitted outside the parent receive beam's configured angular/footprint support.
5. **Distinctness from multi-peak detection:** a signal scenario with one matched-filter bottom peak but a valid phase trajectory can yield more than one High Density detection; the generic multiple-detection algorithm still sees one amplitude peak.
6. **No synthetic density from sample rate:** doubling phase sample rate without changing the physical phase trajectory and footprint must not approximately double retained High Density detections; spatial decimation controls the retained count.
7. **Spacing anchor:** when geometry supplies sufficiently dense valid candidates, adjacent retained same-side points are separated by approximately at least `W_ref/2` under the reference rule.
8. **Disabled anchor:** `high_density_enabled=false` emits no High Density-only detections.
9. **Insufficient-phase anchor:** no unique bounded inverse / insufficient valid phase support yields an unavailable High Density state rather than invented points.
10. **State boundary:** time/angle High Density detections are Observed; any Cartesian sounding position is Derived through the configured propagation/platform geometry.

## Implementation boundary

The Scientific Core must own:

- phase-to-angle inversion;
- phase-validity checks;
- reference spatial decimation;
- High Density detection objects and metadata;
- optional reference-geometry bottom coordinates.

The application/API may serialize these outputs. React may visualize them but must not invert phase, create additional points, compute sounding spacing, or manufacture fallback detections.

The existing generic threshold/multiple-detection/false-missed logic remains governed by `docs/science/ped_d9_detection_extension_contract.md` and should not be rewritten as part of High Density.
