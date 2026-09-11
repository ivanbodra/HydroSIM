# D8 Phase Detection Scientific Contract

Status: authoritative minimum contract for the Didactic Explorer D8 phase-detection experience.

## Scope

This contract defines the minimum scientifically defensible split-aperture phase path required by D8. It does not reproduce a vendor bottom detector and does not claim that BDI, PDI, or proprietary High Density algorithms are universal.

D8 preserves two levels:

1. **conventional phase detection** — phase information contributes one retained `(twtt, across_track_angle)` observation for a formed receive-beam support;
2. **enhanced phase exploitation** — additional phase-supported samples may yield additional valid `(twtt_i, across_track_angle_i)` observations inside that same acquired/formed support.

Additional detections are not additional physical beams and do not imply a smaller acoustic footprint.

## Canonical geometry and sign

Use HydroSIM's existing across-track convention from `docs/conventions.md`:

- zero receive angle = nominal transducer normal in the across-track plane;
- positive across-track angle = port;
- negative across-track angle = starboard.

Let:

- `b` = effective split-aperture phase-centre baseline [m];
- `f` = acoustic frequency [Hz];
- `c` = sound speed used for the phase-angle conversion [m/s];
- `lambda = c/f` [m];
- `k = 2*pi/lambda` [rad/m];
- `theta_s` = formed receive-beam steering/reference angle [rad], using the HydroSIM across-track sign;
- `delta_phi` = unwrapped residual differential phase [rad] relative to the steering/reference direction.

For the canonical HydroSIM subarray ordering, define positive differential phase so that increasing `delta_phi` maps to increasing HydroSIM across-track angle. The reference relation is

`delta_phi = k*b*(sin(theta) - sin(theta_s))`.

Therefore

`sin(theta) = sin(theta_s) + delta_phi/(k*b)`

and

`theta = asin(sin(theta_s) + delta_phi/(k*b))`.

This is the canonical internal mapping. Any instrument/datagram whose subarray order or phase sign differs must convert explicitly at its adapter boundary; the UI must not introduce an independent sign convention.

### Validity of the inverse

The phase-to-angle result is valid only when:

- `b > 0`, `f > 0`, and `c > 0`;
- the phase sample belongs to a support interval accepted by the phase-quality model;
- phase unwrapping/branch selection is defined for that support;
- the inverse argument `sin(theta_s) + delta_phi/(k*b)` lies in `[-1, +1]` within numerical tolerance;
- the selected branch is consistent with the formed receive-beam support.

A wrapped phase value alone is not sufficient to select a unique physical angle when spatial phase ambiguity exists. HydroSIM must preserve an explicit invalid/ambiguous state rather than silently selecting an arbitrary branch.

## Required phase input state

The minimum render/processing state for one selected receive beam is:

- common time/TWTT sample axis;
- complex split-aperture channel or equivalent already-derived differential-phase samples;
- `delta_phase_wrapped_rad`;
- `delta_phase_unwrapped_rad` where unwrapping is valid;
- phase-support mask;
- phase-quality/coherence measure with documented normalization;
- effective baseline `b`;
- frequency `f` and sound speed `c` used for the mapping;
- steering/reference angle `theta_s`;
- explicit phase-sign/subarray-order convention.

If the current Core does not expose complex split-aperture data, an adapter may expose the already-derived differential phase, but it must remain a canonical Python/Core result rather than a React reconstruction.

## Support and quality semantics

D8 must distinguish:

- **sample exists** — a differential-phase value can be computed;
- **supported** — the sample lies inside the configured temporal/echo support used by the estimator;
- **quality-valid** — the sample passes the registered phase-quality/coherence criterion;
- **angle-valid** — supported + quality-valid + unambiguous phase-to-angle inversion;
- **retained** — selected by the active detector/selector as an observation.

These states must not be collapsed into a single `valid` flag if doing so hides why phase detection failed.

For the first slice, the exact numerical coherence/quality estimator may remain a configured Core model. The UI may expose its threshold but must not invent the estimator. A threshold value has meaning only together with the named/normalized quality quantity it thresholds.

## Conventional phase estimator

The conventional phase lesson uses a locally coherent phase ramp within the accepted echo support.

The canonical estimator must return at minimum:

- phase support interval;
- fitted or otherwise registered phase-ramp representation;
- zero/reference crossing time `t_phi` when valid;
- phase quality/support state;
- detected across-track angle associated with the retained phase observation.

For a residual phase defined relative to the formed beam steering direction, the zero crossing `delta_phi = 0` corresponds to `theta = theta_s`. The estimator's time localization is the time at which the accepted phase ramp crosses that reference.

A zero crossing drawn from decorative/synthetic frontend geometry is prohibited. If support/coherence is insufficient, the phase candidate must become unavailable/invalid rather than returning a plausible-looking estimate.

The conventional phase candidate competes with the amplitude candidate for the one conventional retained observation. The existence of both candidates does not by itself create two soundings.

## Enhanced phase / High Density boundary

The scientifically reusable part of the existing HydroSIM High Density concept is the principle that richer phase information within the support of a formed receive beam can yield multiple directional bottom detections from one ping/beam support.

For each additional accepted phase sample or locally estimated solution:

`(t_i, delta_phi_i) -> (twtt_i, theta_i)`

using the same canonical phase-to-angle mapping and quality/ambiguity checks above.

Minimum enhanced output:

- parent ping and receive-beam identity;
- multiple ordered detection observations;
- for each detection: `twtt_seconds`, `detected_across_track_angle_rad`, phase-support/quality metadata, and stable detection index;
- explicit parent-beam association.

HydroSIM must not teach that High Density creates new receive beams, narrows the footprint, or guarantees independent acoustic resolution equal to point spacing.

Manufacturer documentation may be used as evidence that specific systems expose multiple soundings per beam, but manufacturer-specific extraction details must not be generalized unless separately documented.

## BDI and PDI boundary

### PDI

The Gomes de Araujo work provides a defensible research basis for a **PDI teaching/research slice** in which phase/intensity information is inspected across direction at fixed time. The essential distinction is:

- conventional beam-series view: fixed beam/direction, vary time;
- PDI-style view: fixed time, vary beam/direction/angle.

For D8, PDI may be represented only when the Core exposes the actual beam-by-time phase/intensity matrix and a documented cross-direction estimator. A generic frontend zero crossing across interpolated display pixels is not scientifically acceptable.

### BDI

BDI may be shown as a named advanced/research comparison only when a specific registered algorithm and source are implemented. The present contract does **not** define a universal BDI estimator. Until such an algorithm exists in the Core, BDI is staged/deferred rather than approximated decoratively.

### Integrated selector

No universal `Automatic/Combined` detector is defined here. Combining amplitude, conventional phase, enhanced phase, BDI, or PDI requires a separately documented selector/acceptance policy.

## State semantics

The phase samples and retained `(twtt, angle)` tuple are **Observed** measurement state when produced from the simulated received field/detector path.

Configured baseline, frequency, sound speed, steering reference, support threshold, quality threshold, and detector mode remain **Configured** unless their owning model defines another state.

A Cartesian seabed point reconstructed from the retained observation plus processing geometry remains **Derived**, consistent with `docs/science/d8_observation_state_contract.md`.

Truth may label a detection as true/false/missed for teaching or validation but must not enter the estimator objective or candidate selection.

## Required implementation invariants

1. `delta_phi = 0` maps exactly to `theta_s` under the canonical residual-phase definition.
2. With fixed `b`, `f`, `c`, and `theta_s`, increasing valid unwrapped `delta_phi` must not decrease HydroSIM across-track angle on the selected monotonic branch.
3. Reversing an external instrument's subarray ordering must be corrected at the adapter boundary; it must not reverse HydroSIM's port-positive angle convention.
4. Unsupported or quality-invalid phase samples cannot become retained phase detections.
5. An inverse argument outside `[-1,+1]` is invalid, not clipped into a valid-looking angle except for documented floating-point tolerance at the boundary.
6. Conventional amplitude and phase candidates do not automatically produce two retained conventional observations.
7. Enhanced detections preserve their parent receive-beam identity.
8. Enhanced detection count/spacing must not be reported as beam count or beamwidth.
9. Truth cannot be used to choose the retained detector solution.
10. BDI/PDI cannot be synthesized in React from decorative display geometry.

## References

- `lurton_2003_acoustical_measurement_accuracy` — time/angle bathymetry and amplitude/phase measurement accuracy.
- `lurton_2010_underwater_acoustics` — array phase, beamforming and underwater-acoustic measurement foundations.
- `bourguignon_et_al_2009_me70_bottom_detection` — multibeam bottom detection and split-beam phase-difference/zero-crossing methods.
- `kongsberg_em2040_instruction_manual_346210` — manufacturer-specific evidence for split-aperture phase bottom detection and High Density/multiple-sounding behavior.
- Gomes de Araujo, Leonardo (2020), *Potential for Non-Conventional Use of Split-Beam Phase Data in Bottom Detection*, University of New Hampshire M.S. thesis — research basis for angle-series/PDI exploitation: https://scholars.unh.edu/thesis/1421/
- Hamel, Jonathan (2020), *Effects of Transmission Side Lobe Interference on Multibeam Echosounder Phase Ramps*, University of New Hampshire M.S. thesis — phase-ramp support/noise and bottom-detection implications: https://scholars.unh.edu/thesis/1425/

The two UNH theses above should be registered by stable bibliography IDs before their claims are reused outside D8.