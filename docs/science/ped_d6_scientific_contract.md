# PED-D6 Scientific Contract — Transducer & Array Construction

Status: authoritative pedagogical-generation contract  
Experience: `PED-D6`  
Scope: production learner vertical slice

## Learning question

PED-D6 teaches how physical element size, element spacing, element count/aperture, acoustic frequency/wavelength, array layout, and deterministic aperture weighting shape the normalized directivity of an ideal transducer array. It may also show Mills Cross as a **construction geometry** made from orthogonal TX/RX linear apertures; two-way TX/RX response and electronic steering remain separate concepts.

The slice is limited to HydroSIM's authoritative far-field narrowband models. It must not introduce vendor-specific geometry, calibrated source/receive gain, near-field focusing, mutual coupling, or an independent frontend beam equation.

## Canonical Core ownership

The Scientific Core is the sole owner of the physics:

- `src/hydrosim/geometry/arrays.py` — regular centred 1-D/rectangular array geometry, element count, spacing, element dimensions, orientation and physical aperture;
- `src/hydrosim/geometry/mills_cross.py` — validated Mills-Cross construction from orthogonal TX/RX linear arrays;
- `src/hydrosim/acquisition/element_factor.py` — ideal rectangular-element one-way far-field directivity;
- `src/hydrosim/acquisition/array_factor.py` — ideal coherent one-way narrowband array factor, steering direction and complex element weights;
- `src/hydrosim/acquisition/beam_pattern.py` — physical one-way element-factor × array-factor composition and across-track scan with local half-power (-3 dB) beamwidth;
- `docs/science/array_factor.md` and `docs/science/beam_pattern.md` — canonical derivation, conventions, analytical anchors and limits.

The application/API and React layers may serialize, localize and visualize these outputs, but must not reproduce their equations.

## State semantics

### Configured

Learner controls scientifically belonging to PED-D6 are:

- acoustic frequency `f` [Hz], `f > 0`;
- sound speed `c` [m/s], `c > 0`;
- element count on the active axis `N >= 1`;
- inter-element centre spacing `d` [m], with `d > 0` for `N > 1`;
- physical element face dimension on the active axis `a` [m], `a > 0`;
- array geometry: regular linear baseline, with rectangular 2-D geometry permitted through canonical `TransducerArray` parameters;
- deterministic aperture weighting selector, initially `uniform` or `hann`;
- Mills-Cross construction selector when the experience is showing array architecture rather than two-way response.

Steering may remain fixed at broadside in PED-D6; interactive steering belongs primarily to PED-D7.

### Derived

Core-derived learner outputs include:

- wavelength `lambda = c / f` [m];
- element-centre positions [m];
- physical aperture [m], using canonical `TransducerArray.aperture_*` properties;
- normalized one-way element-factor response;
- normalized one-way array-factor response;
- normalized one-way physical beam pattern `element factor × array factor`;
- normalized power versus angle;
- peak angle and peak normalized power;
- local half-power (-3 dB) beamwidth when both crossings lie inside the sampled angular interval;
- visible side-lobe / grating-lobe structure present in the computed normalized pattern;
- for Mills Cross, TX/RX principal-axis geometry in their common sensor frame.

These quantities are `Derived`. PED-D6 does not create `Observed`, `Estimated`, or environmental `Truth` state.

## Required cause → effect relationships

1. **Frequency / wavelength** — for fixed physical geometry and sound speed, increasing frequency decreases wavelength and changes aperture/wavelength, generally narrowing the main lobe while changing lobe structure.
2. **Element count / aperture** — when spacing and element size are fixed, adding elements increases physical aperture and generally narrows the main lobe.
3. **Spacing relative to wavelength** — changing `d / lambda` changes the interference pattern. Large spacing can create additional coherent maxima (grating lobes / spatial aliasing); these must be shown as computed results, not hidden by the UI.
4. **Finite element size** — the rectangular element factor forms an angular envelope independent of the array-factor calculation; element size and spacing remain separate learner concepts.
5. **Beamwidth** — the authoritative scalar beamwidth is the local half-power width returned by the canonical scan. If a crossing falls outside the scan interval, beamwidth is unavailable; no extrapolation is permitted.
6. **Aperture weighting** — deterministic non-uniform weighting changes the relative coherent contributions across the aperture. In the normalized pattern this can reduce sidelobes while broadening the main lobe; it is not an absolute acoustic-gain calculation.

Approximate textbook rules such as beamwidth proportional to `lambda / aperture` may be shown only as qualitative intuition or clearly labelled approximations. The configured Core pattern is authoritative.

## Side lobes, grating lobes and gain language

The present outputs are normalized pressure/amplitude-like and normalized-power responses. They are not calibrated acoustic gain, source level, receive sensitivity, directivity index, or a two-way sonar response.

Learner-facing text may discuss relative main-lobe width, side lobes and grating lobes. A dB display is permissible only relative to the normalized pattern peak (`dB re peak`). Do not label normalized pattern values as absolute `gain [dB]`.

## Aperture weighting / apodization

`array_factor()` already accepts arbitrary complex element weights, so no new array-factor physics is required. PED-D6 needs only a canonical deterministic generator for the named learner selector.

Minimum production selector:

- `uniform`: `w_n = 1`;
- `hann`: for a one-dimensional aperture with `N > 1`, `w_n = 0.5 * [1 - cos(2*pi*n/(N-1))]`, `n = 0 ... N-1`.

For `N = 1`, both selectors reduce to the single unit weight `w_0 = 1` so normalization remains defined. Weights are real, non-negative and applied in deterministic element order. For a rectangular 2-D array, a future separable 2-D taper may be added explicitly; the minimum PED-D6 production requirement is the active 1-D aperture.

Because `array_factor()` normalizes by `sum(abs(w_n))`, these weights alter normalized directivity but do **not** define absolute gain loss. Any learner-visible `gain loss` in the old atom wording must therefore be interpreted as a **relative normalized-pattern consequence**, or deferred until a calibrated gain/power contract exists.

## Mills Cross boundary

`MillsCrossConfiguration` is already authoritative Core capability. PED-D6 may expose Mills Cross strictly as a construction/geometry comparison: two orthogonal linear TX/RX apertures, each retaining its own local frame and role. This satisfies the array-construction learning objective without introducing new physics.

PED-D6 must not use Mills Cross to imply that all MBES systems use this geometry, nor calculate a two-way TX×RX response as part of this atom. Two-way composition and electronic steering remain PED-D7/PED-D8/integrated-sonar concerns.

## Eccentricity disposition

The current product atom inventory lists `eccentricity` as a PED-D6 input, but neither the pedagogical plan nor the Scientific Core defines a physical quantity, unit, frame, or causal model with that name for transducer-array construction. It is therefore **not a scientifically actionable PED-D6 control** and must not be invented by Engineering or UX.

Authoritative recommendation: remove this atom from PED-D6 unless Technical Lead can identify a specific intended physical quantity. If the intended concept is a sensor/transducer installation offset relative to a vessel/reference point, it belongs to PED-D11/A2 installation/lever-arm geometry, where source→target offsets and frames are explicit. If it means element-position perturbation or array manufacturing tolerance, that would require a separate future fidelity contract and is outside the present PED-D6 learning objective.

This is a roadmap/inventory correction, not a request to shrink implemented science silently; the denominator must be changed only by Technical Lead/coordination authority.

## Coordinate and angle convention

For the canonical across-track scan:

- array/sensor `+Z` is the normal/down direction;
- zero across-track angle is the `+Z` normal;
- positive across-track angle points Port (`-Y`);
- negative across-track angle points Starboard (`+Y`).

The application may convert radians to degrees but must preserve the sign convention.

## Validity domain

The PED-D6 model assumes ideal regular centred geometry, deterministic element positions/dimensions, far-field plane-wave propagation, one monochromatic/narrowband frequency per evaluation, ideal identical rectangular elements, deterministic weights, no mutual coupling, no channel-calibration mismatch, no stochastic noise, no finite-bandwidth beam squint, no near-field/dynamic focusing, no calibrated absolute transmit/receive gain, and no vendor-specific beamformer behavior.

## Minimum scientific acceptance anchors

Engineering/tests should preserve at least:

- broadside uniform-array response peaks at normalized amplitude/power approximately 1;
- changing only overall complex weight scale cannot change normalized array-factor magnitude;
- two-element `d=lambda/2`, broadside steering, 30-degree source: normalized array-factor magnitude `sqrt(2)/2`, power `0.5`;
- broadside `d=lambda` exhibits the documented grating-lobe/spatial-alias anchor;
- increasing element count at fixed spacing updates aperture through `TransducerArray`, not an adapter formula;
- half-power beamwidth is reported only when both Core crossings exist;
- Hann weights are symmetric (`w_n = w_(N-1-n)`) and non-negative; for `N>2`, endpoints are zero;
- Mills-Cross geometry is accepted only when TX/RX principal axes are orthogonal under the existing Core tolerance.

## Remaining PED-D6 atom disposition

For completion of Technical Lead handoff #198:

| Inventory atom | Scientific disposition |
| --- | --- |
| `array geometry` | **Existing canonical capability.** Use `TransducerArray` regular linear/rectangular geometry; no new equation. |
| `Mills Cross` | **Existing canonical capability.** Use `MillsCrossConfiguration` as construction geometry only; no new two-way model. |
| `shading/apodization` | **Minimal missing capability.** Add a small canonical weight generator for `uniform` and `hann`, feeding existing `array_factor(weights=...)`; no array-factor change. |
| `eccentricity` | **Inventory reallocation/removal recommended.** Undefined in current D6 science; do not invent. Installation offset, if intended, belongs to PED-D11/A2. |

## First production payload boundary

The PED-D6 adapter may return configuration metadata/units, wavelength/aperture, element positions/count, sampled normalized amplitude/power pattern, peak, half-power beamwidth or unavailable state, factor decomposition when shown, selected deterministic weights, and Mills-Cross TX/RX construction geometry when selected.

No new beam equation is required.

## References / traceability

Primary HydroSIM scientific sources:

- `docs/science/array_factor.md`;
- `docs/science/beam_pattern.md`;
- `src/hydrosim/geometry/arrays.py`;
- `src/hydrosim/geometry/mills_cross.py`;
- `src/hydrosim/acquisition/element_factor.py`;
- `src/hydrosim/acquisition/array_factor.py`;
- `src/hydrosim/acquisition/beam_pattern.py`.

PED-D6 reuses those implemented reference models rather than defining a parallel pedagogical formulation. The Hann weighting definition is the standard raised-cosine Hann window applied here only as deterministic aperture weights; it does not alter the canonical coherent-sum equation.