# PED-D6 Steering / Source / Peak Interpretation

Status: authoritative scientific disposition for learner-facing D6  
Scope: steering/source/peak semantics, relative delay/phase reference, coherent-sum interpretation, and aliasing regime

## Disposition

The current Core equations are scientifically consistent. A large difference between requested steering angle and reported `peak_angle_deg` can be physically valid when the array is spatially aliased (grating lobes) and the **physical one-way beam** has a stronger global maximum at another angle. No sign correction or Core beamforming rewrite is required by issue #371.

The current API's `peak_angle_deg` is the angle of the **global maximum of the physical one-way beam pattern inside the configured scan interval**, not a restatement of the configured steering angle.

Therefore a case such as requested steering near `+43 deg` with a global physical peak near broadside can be valid when element spacing is too large in wavelength units for unambiguous steering at the selected frequency. The element factor can further change which aliased array-factor lobe becomes the strongest physical-beam lobe.

## Canonical angular convention

Reuse HydroSIM's canonical receive/transducer array frame:

- zero across-track angle: array normal `+Z`;
- positive angle: Port (`-Y`);
- negative angle: Starboard (`+Y`).

`steering_angle_deg` and `source_angle_deg` use this same convention.

For across-track angle `theta`,

`u(theta) = [0, -sin(theta), cos(theta)]`.

No frontend-local sign inversion is scientifically permitted. Display transforms may rotate SVG graphics as needed, but labels, rays, controls, plot axes, source direction, steering direction, and peak readout must all represent this same convention.

## Meaning of the principal quantities

### `steering_angle_deg`

Configured processing direction `theta_0`.

It selects the relative phase/delay law applied across the fixed physical array. It is **not** an assertion that the strongest physical lobe must always occur at exactly that angle.

### `source_angle_deg`

Configured evaluation direction `theta_s` used to ask: "what response does the current fixed beamformer produce for a wave arriving from / field direction at this angle?"

In the RX teaching path, changing source angle while keeping steering fixed demonstrates directional selectivity. The beamformer does not automatically retune to the source.

### Evaluated array-factor power

For uniform unit weights and `N` elements,

`AF = (1/N) * sum_i exp(j * k * (u_s - u_0) dot r_i)`

and

`evaluated_array_factor_power = |AF|^2`.

It is a normalized one-way spatial-coherence response. Perfect phase alignment gives 1. It is not absolute acoustic power or source level.

### Evaluated physical-beam power

The current one-way physical response is

`B(theta_s) = E(theta_s) * AF(theta_s; theta_0)`

where `E` is the canonical element factor.

Thus

`evaluated_physical_beam_power = |B(theta_s)|^2`.

It can be lower than the array-factor power because the individual element directivity attenuates that direction.

### Coherent sum

The API's complex coherent sum is the unnormalized spatial array sum before division by `N`:

`C = sum_i exp(j * k * (u_s - u_0) dot r_i)`

for the current uniform-weight model.

Therefore `|C| = N` at perfect alignment and `|C|/N = sqrt(evaluated_array_factor_power)`.

The real and imaginary parts depend on reference phase/origin and should not be taught as independent physical observables. Learner-facing coherence should primarily use magnitude or normalized magnitude.

### `peak_angle_deg`

The current Core scans the physical one-way beam over the declared angular interval and returns the angle whose `normalized_power` is largest.

Hence:

- in an unaliased well-behaved configuration, `peak_angle_deg` should lie close to `steering_angle_deg`, subject to finite angular sampling and element-factor effects;
- in an aliased configuration, another grating lobe may become the global physical maximum and `peak_angle_deg` may differ strongly from the requested steering angle;
- this difference is a valid teaching consequence when explicitly labeled as such.

## Relative arrival, delay, and phase convention

For an element at position `r_i` and a source-direction unit vector `u`, HydroSIM's canonical relative arrival-time offset is

`Delta_t_arrival_i = -(u dot r_i) / c`.

Only relative offsets matter. Choose and expose one reference channel `ref` for learner display:

`delta_t_arrival_i = Delta_t_arrival_i - Delta_t_arrival_ref`.

For steering direction `u_0`, the beamformer compensation delay is

`tau_i = (u_0 dot r_i) / c`.

Displayed relative compensation is

`delta_tau_i = tau_i - tau_ref`.

With HydroSIM's complex convention `s(t)=exp(j 2 pi f t)`, applying a positive delay `tau_i` contributes phase

`phi_steer_i = -2 pi f tau_i`.

The residual phase after compensation is therefore

`phi_res_i = k * (u_s - u_0) dot r_i`,

matching the existing Core array-factor equation.

A common delay added to all channels changes absolute latency but **does not change steering**. The learner-facing D6 must therefore show relative delay/phase with an explicit zero/reference channel.

## Why requested steering can differ from physical peak

For a uniform linear array with across-track spacing `d`, array-factor maxima repeat whenever adjacent-element residual phase differs by an integer multiple of `2 pi`.

For HydroSIM's across-track convention, equivalent array-factor maxima satisfy

`sin(theta) = sin(theta_0) + m * lambda / d`

for integer `m`, subject to a physically visible solution `|sin(theta)| <= 1`.

`m=0` is the requested steering lobe. Any visible solution with `m != 0` is a grating-lobe / spatial-alias solution.

A conservative full-visible-sector condition for avoiding grating lobes is

`d <= lambda / 2`.

For a particular steering angle and scan interval, the exact test is stronger and should be used by backend logic if a warning/status is later exposed: check whether any nonzero integer `m` yields a solution inside the active scan interval.

The element factor does not remove the array's spatial ambiguity. It weights the competing lobes. Consequently an aliased lobe closer to the element normal can have larger **physical-beam** power than the nominal steering lobe and become the returned global `peak_angle_deg`.

## Interpretation of the reported +43 / +48 -> ~2 deg case

The relationship itself is not evidence of a sign bug. It is scientifically plausible when the selected frequency makes `d/lambda` large enough to create a visible grating lobe near broadside. If the same geometry is returned to an unaliased regime (for example `d <= lambda/2`) the physical peak must return close to the requested steering angle.

The learner-facing explanation should therefore be:

- steering angle = requested processing direction;
- source angle = direction currently being evaluated;
- peak angle = strongest physical lobe across the scan;
- when spacing is unambiguous, requested steering and physical peak coincide closely;
- when spacing becomes spatially aliased, multiple directions can satisfy the same inter-element phase progression, and element directivity determines which physical lobe is strongest.

Do not explain this as the beamformer "missing" the requested direction, mechanically rotating, or following the source.

## Useful / ambiguous steering regime

For D6 Layer 1, use a fixed reference array deliberately chosen so that the normal learner interaction stays unambiguous across its advertised steering range. The simplest robust choice is `d <= lambda/2` at the highest learner-selectable frequency.

If an advanced interaction deliberately permits `d > lambda/2`, it should be presented as an aliasing/grating-lobe demonstration rather than ordinary steering failure.

Backend/API may expose a render-ready status such as:

- `unambiguous` — no nonzero grating-lobe solution in the configured scan;
- `aliased` — at least one nonzero solution exists;

but React must not derive this condition independently.

## Minimum acceptance anchors

1. At `source_angle == steering_angle`, residual phase is zero for every element and normalized array-factor power is 1 within numerical tolerance.
2. For an unaliased array, the physical peak lies at/near the steering angle within scan discretization tolerance.
3. Reversing Port/Starboard signs reverses source/steering/peak consistently; no panel may use an opposite convention.
4. Adding the same delay to all channels leaves steering and normalized array factor unchanged.
5. For an aliased array, a nonzero integer `m` satisfying the visible-lobe equation produces an additional array-factor maximum.
6. Element-factor weighting may cause an aliased lobe to become the strongest physical-beam peak.
7. `|coherent_sum|/N` equals array-factor normalized magnitude for the current uniform-weight model.

## Implementation boundary

No Core equation change is required by #371.

UX should use this interpretation for the D6 redesign in #372. If UX needs an explicit `unambiguous/aliased` flag, per-channel relative delay values, or Delay -> Steering inverse mapping, those should be exposed by Python/API; React must not reproduce the equations locally.

This disposition intentionally does not broaden into a general array/beamforming audit.
