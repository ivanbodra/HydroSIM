# PED-D7 Scientific Contract — Beamforming & Electronic Steering

Status: authoritative pedagogical-generation contract  
Experience: `PED-D7`  
Scope: first production learner vertical slice

## Learning question

PED-D7 teaches how relative propagation phase across an array is compensated so that element contributions add coherently in a selected direction, and how changing the steering direction moves and reshapes the normalized beam pattern.

The first slice is deliberately limited to the already-authoritative HydroSIM ideal far-field narrowband array model. It does not introduce vendor-specific beamformer logic, near-field/dynamic focusing, finite-bandwidth beam squint, adaptive beamforming, channel mismatch, or an independent frontend steering equation.

## Canonical Core ownership

The Scientific Core is the sole owner of the numerical physics:

- `src/hydrosim/geometry/arrays.py` — deterministic centred array geometry and element positions;
- `src/hydrosim/acquisition/array_factor.py` — steering direction, residual phase, coherent summation, complex element weights and normalized one-way array response;
- `src/hydrosim/acquisition/element_factor.py` — ideal rectangular-element directivity;
- `src/hydrosim/acquisition/beam_pattern.py` — one-way physical element-factor × array-factor pattern and across-track scan;
- `docs/science/array_factor.md` and `docs/science/beam_pattern.md` — canonical equations, direction convention, analytical anchors and validity limits.

The application/API and React layers may serialize, localize and visualize these outputs, but must not reproduce the steering, phase, delay or beam equations.

## State semantics

### Configured

Minimum learner controls for the first slice:

- acoustic frequency `f` [Hz], `f > 0`;
- sound speed `c` [m/s], `c > 0`;
- one regular array geometry already supported by `TransducerArray` (element count, spacing and element dimensions);
- steering angle `theta_0` in the canonical across-track plane;
- scan/source angle interval used to evaluate the normalized pattern;
- beamformer role: `TX` or `RX` may be presented as a pedagogical mode, but both use the same ideal normalized one-way static steering law in this first slice;
- weights are uniform unit weights in the first slice.

The steering control is the pedagogical distinction from PED-D6. PED-D6 may hold steering at broadside; PED-D7 makes steering direction an explicit learner-controlled quantity.

### Derived

The Core-derived learner outputs are:

- wavelength `lambda = c / f` [m];
- steering direction unit vector in the array frame;
- per-element positions;
- per-element residual phase for each evaluated source/field direction;
- per-element complex coherent contributions;
- coherent complex sum and normalization;
- normalized one-way array-factor magnitude and power;
- normalized one-way physical beam pattern including element directivity;
- sampled normalized power versus across-track angle;
- peak angle and peak normalized power;
- local half-power (-3 dB) beamwidth when both crossings are present in the requested scan interval;
- relative steering delay/phase interpretation as defined below.

These are `Derived`. The first PED-D7 slice creates no `Observed`, `Estimated`, or stochastic `Truth` state.

## Direction and steering convention

PED-D7 inherits the HydroSIM array-frame convention exactly:

- array/sensor `+Z` is the normal/down direction;
- zero across-track angle is the `+Z` normal;
- positive across-track angle points Port (`-Y`);
- negative across-track angle points Starboard (`+Y`);
- both source direction `u` and steering direction `u0` point from the array centre toward the acoustic source/field direction.

For an element at position `r_i`, the canonical residual phase is

`phi_i = k (u - u0) . r_i`, with `k = 2*pi/lambda`.

The application layer may display degrees instead of radians but must preserve the sign convention.

## Relative delay and phase representation

The canonical scientific interpretation is the one already documented in `docs/science/array_factor.md`:

- far-field arrival offset from direction `u`: `Delta t_i = -(u . r_i) / c`;
- steering compensation delay toward `u0`: `tau_i = (u0 . r_i) / c`;
- under `s(t) = exp(i 2*pi f t)`, the combined residual phase is `k (u - u0) . r_i`.

For learner visualization, relative delays or phases may be shown per element after subtracting any common offset/reference-element value. A common delay added equally to all channels does not change the normalized static beam direction and should not be presented as a distinct steering effect.

The authoritative numerical response remains the Core `array_factor()` / `one_way_beam_pattern()` output. The frontend must not independently reconstruct the beam from displayed delays or phases.

## TX / RX boundary for the first slice

The first PED-D7 slice teaches **static one-way beamforming**. Under the ideal reciprocal narrowband array assumptions represented by the present Core, the same spatial phasing relationship can illustrate either:

- TX: relative excitation timing/phase selected so contributions add coherently toward `u0`; or
- RX: relative receive compensation selected so a plane wave arriving from `u0` adds coherently.

Therefore a TX/RX selector may change explanation, timing arrows or signal-flow visualization, but it must not produce two different numerical beam equations in this first slice.

A combined two-way TX × RX response, distinct TX/RX array geometries, Mills Cross composition, receive-window timing, dynamic receive steering/focusing, and ping-dependent beamformer behavior are outside this first slice and require their own explicit contract before learner-facing implementation.

## Required cause → effect relationships

The first production experience must make these effects observable using canonical Core outputs:

1. **Coherent steering** — when source/evaluation direction equals steering direction, residual spatial phases align and the normalized array factor reaches its coherent maximum for uniform ideal elements.
2. **Beam motion** — changing `theta_0` moves the principal response away from broadside according to the canonical steering direction; the UI must preserve Port-positive / Starboard-negative sign.
3. **Residual phase away from steer angle** — when `u != u0`, element contributions acquire relative residual phase and the coherent sum changes, producing the angular interference pattern.
4. **Steering and finite element directivity** — the physical beam is element factor × array factor. At larger steering angles, the array-factor peak may remain coherently steered while the finite element envelope reduces the physical normalized response; this is a steering-loss mechanism within the present ideal model.
5. **Spatial aliasing remains visible** — if array spacing permits grating lobes, steering does not authorize the UI to suppress them.
6. **Beamwidth is computed, not guessed** — the scalar half-power width is authoritative only when returned by `scan_across_track_beam_pattern()`; no extrapolation or textbook approximation substitutes for a missing crossing.

## Weighting / apodization boundary

`array_factor()` already supports arbitrary deterministic complex weights, but HydroSIM still has no canonical learner-facing generator for named taper families or their parameterization.

Therefore the first PED-D7 production slice uses **uniform unit weights**. Named Hann, Hamming, Taylor, Chebyshev or other apodization controls are deferred until a dedicated canonical weight-generation contract is introduced and independently validated.

Arbitrary frontend-created complex weights are not allowed merely because the Core function accepts them.

## Dynamic focusing / receive timing boundary

Dynamic focusing and dynamic receive steering require range/time-dependent delays and a near-field or time-varying observation model that is not represented by the present static far-field `array_factor()` contract.

They are therefore explicitly deferred from the first PED-D7 slice. The learner experience may state that operational MBES receivers can update steering/focusing with receive time, but it must not simulate that behavior until the Scientific Core contains an authoritative model for it.

Likewise, the first slice does not model receive gates, pulse timing, sample timing, bandwidth-dependent steering, or vendor-specific beamformer implementation.

## Gain and steering-loss language

The present responses are normalized one-way pressure/amplitude-like and normalized-power quantities. They are not calibrated source level, receive sensitivity, directivity index, or absolute gain.

`Steering loss` in this first slice may describe a **relative reduction of the normalized physical beam peak caused by the finite element directivity envelope when steering away from the element normal**. It must not be labelled as an absolute dB loss budget unless a later calibrated contract introduces the required quantities.

A relative dB display is permissible only when clearly labelled relative to a stated normalization/reference and numerically bounded near zero.

## Validity domain

The first PED-D7 model assumes:

- deterministic regular array geometry;
- far-field plane waves;
- one monochromatic/narrowband frequency per evaluation;
- ideal identical rectangular elements;
- static steering direction during one evaluation;
- uniform unit weights;
- ideal coherent channels;
- no mutual coupling;
- no channel calibration mismatch or phase noise;
- no adaptive beamforming;
- no finite-bandwidth beam squint;
- no near-field/dynamic focusing;
- no receive-time-dependent steering;
- no calibrated absolute gain;
- no vendor-specific behavior.

These are scientific limits and must not be silently corrected by another layer.

## Minimum scientific acceptance anchors

Engineering/tests for the PED-D7 adapter should preserve at least these properties:

- with source/evaluation direction equal to steering direction and uniform weights, all residual spatial phases are zero within numerical precision and normalized array-factor magnitude/power are approximately `1`;
- broadside steering (`theta_0 = 0`) reproduces the PED-D6 broadside pattern for the same array/frequency/sound-speed configuration;
- the sign convention is preserved: positive steering angle is Port (`-Y`), negative is Starboard (`+Y`);
- for the documented two-element `d = lambda/2` broadside case and a +30 degree source direction, normalized array-factor magnitude is `sqrt(2)/2` and normalized power is `0.5`;
- for +30 degree source direction steered to -30 degrees in that documented two-element case, ideal equal-element contributions cancel and normalized response approaches zero;
- changing only a common multiplicative complex scale on all weights cannot change normalized array-factor magnitude;
- the physical beam curve is obtained from canonical element-factor × array-factor composition rather than by relabelling the array factor;
- half-power beamwidth is unavailable when the Core scan lacks either crossing.

## First production payload boundary

A minimal PED-D7 application adapter is scientifically sufficient if it accepts the Configured controls above and returns, from canonical Core calls:

- configuration metadata and units;
- steering angle/direction with explicit sign convention;
- element positions;
- relative steering delay/phase information suitable for coherent-summation visualization;
- per-element residual phase/contribution data for at least the currently evaluated source/field direction;
- sampled normalized array-factor and physical one-way beam-pattern outputs versus angle;
- peak angle/power and half-power beamwidth or explicit unavailable state;
- a `TX`/`RX` pedagogical role indicator whose numerical static one-way response is intentionally identical under the first-slice reciprocal idealization.

No new physical beamforming equation is required for this adapter. If Engineering needs a reusable helper for serialization of the already-defined steering delay/phase values, that is an application/API concern and must delegate the actual convention/math to the canonical scientific definitions rather than creating a competing model.

## References / traceability

Primary HydroSIM scientific sources for this contract:

- `docs/science/ped_d6_scientific_contract.md`;
- `docs/science/array_factor.md`;
- `docs/science/beam_pattern.md`;
- `src/hydrosim/geometry/arrays.py`;
- `src/hydrosim/acquisition/array_factor.py`;
- `src/hydrosim/acquisition/element_factor.py`;
- `src/hydrosim/acquisition/beam_pattern.py`.

PED-D7 deliberately reuses the implemented HydroSIM array physics and advances only the learner-controlled steering dimension required by the pedagogical plan.