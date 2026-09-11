# D8 — Bottom Detection

Status: **Mapped**

**Decision:** `KEEP + REFINE + EXPAND PHASE-DETECTION EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/BottomDetectionLab.tsx`

## Purpose
Teach how an MBES transforms the received acoustic return into one or more bottom detections. The learner must understand that the sonar does not directly receive a bathymetric point: it receives signals containing amplitude and phase information. Detection algorithms interpret those signals and estimate one or more `(t, θ)` pairs passed downstream to sounding formation.

Two processing levels must remain distinct:

```text
CONVENTIONAL:
Amplitude OR Phase -> one retained detection for that beam/direction

ADVANCED EXTRACTION:
richer amplitude/phase structure -> multiple valid (t, θ) solutions
```

## Dominant discovery

A bottom detection is an estimate made from the received signal. Amplitude and phase can compete to determine a conventional solution; when additional spatial/phase information is sufficiently reliable, advanced algorithms can extract more valid bottom detections from the same acquired data.

```text
PHYSICAL RETURN
  -> RECEIVED AMPLITUDE + PHASE
  -> QUALITY / SUPPORT TESTS
  -> AMPLITUDE OR CONVENTIONAL PHASE DETECTION
  -> ONE RETAINED (t, θ)
  -> OPTIONAL ADVANCED EXPLOITATION
  -> PHASE-RAMP / BDI / PDI INFORMATION
  -> ADDITIONAL VALID (t, θ) DETECTIONS
  -> MORE COMPLETE SEAFLOOR SAMPLING
```

## Inputs

### Primary — conventional detection
- echo / scene scenario: clean planar bottom, sloping bottom, weak return, noisy return, competing returns, discontinuity, narrow/vertical object, good phase-ramp geometry, degraded phase-ramp geometry;
- detection method: `Amplitude` or `Phase`; later `Automatic/Combined` only if backed by a defined Scientific-Core selector;
- range gate / detection window start and end;
- threshold / quality criterion with exact semantics.

Amplitude and phase are initially competing estimators for the same conventional detection, not two soundings from the same beam merely because both estimates exist.

### Phase-specific
- selected beam / steering direction;
- split-aperture geometry, initially fixed;
- minimum phase-support criterion;
- phase quality/coherence criterion;
- phase-ramp fitting/support interval when required by the registered model.

### Advanced
- mode: `Conventional`, `Enhanced phase / High Density`, `BDI`, `PDI`;
- optional integrated detector only after each constituent method is understood;
- scene geometry that exposes differences between methods.

TX delay is only a timing-reference experiment and must not dominate D8.

## Core outputs / visual response

### 1. Received amplitude `A(t)`
Show envelope/energy, range gate, threshold, candidate returns, amplitude estimator and selected `t_A`. The learner must see where the amplitude method placed the detection in the echo.

### 2. Differential phase `Δφ(t)`
Show actual/calculated split-aperture phase samples, valid-support region, phase ramp, regions without reliable phase, zero crossing, fitted ramp where applicable, and conventional phase estimate `t_φ`. If the ramp becomes incoherent or unsupported, phase detection must visibly lose validity.

### 3. Phase -> physical angle
Show the Scientific-Core mapping

```text
Δφ_i -> θ_i
```

so that a valid phase sample can be understood as a physical directional estimate. For each usable sample:

```text
(t_i, Δφ_i) -> (t_i, θ_i)
```

This mapping must follow the validated array/baseline/frequency/sign convention, not a decorative UI approximation.

### 4. Retained conventional detection
Show `t_A` and `t_φ` when both candidates exist, but retain only the selected conventional solution according to the active detector/selector.

### 5. Seafloor / footprint projection
Synchronize the signal plots with a simple footprint/seafloor view. Conventional mode shows one retained point. Enhanced phase mode may show several valid points inside the same receive-beam support. More detections must not be drawn as more physical beams or a narrower footprint.

### 6. Beam × time matrix
For BDI/PDI experiences, show a common data matrix with:
- X = beam / direction / angle;
- Y = time / range;
- amplitude and phase as selectable/synchronized layers.

Teach the distinction:

```text
fixed beam -> inspect time-series
fixed time -> inspect angle-series
```

### 7. Truth comparison
Optional/teaching-only Truth overlay classifies retained detections as true/false/missed and allows method comparison against the same physical scene.

## Interaction sequence

1. **What is a detection?** Show one beam, one echo and corresponding terrain with no detector active. Ask where the bottom is in the signal.
2. **Amplitude detection.** Activate amplitude estimator: `A(t) -> t_A`; immediately project the retained point. Then modify echo shape slightly.
3. **Gate / threshold failure modes.** Introduce weak/noisy/competing returns. Move gate and threshold to create true, false and missed detections. Preserve candidate vs eligible vs retained states.
4. **Conventional phase detection.** Show `A(t)` and `Δφ(t)` on the same time base. Highlight the usable phase ramp and zero crossing. Compute `t_φ`. Compare `t_A` and `t_φ`, but retain only one conventional solution.
5. **When phase works and when it does not.** Move between good and degraded phase-ramp scenarios. A coherent/supportable ramp yields a stable phase solution; inadequate support/coherence makes phase unavailable or unreliable while amplitude may remain usable.
6. **Key transition: the phase ramp contains more than its zero crossing.** Freeze a good ramp. First use only `Δφ=0` -> one conventional point. Then reveal additional valid phase samples and their `Δφ_i -> θ_i` mapping.
7. **High Density / enhanced phase.** Convert several valid `(t_i, Δφ_i)` into `(t_i, θ_i)` and project multiple bottom detections from the same pulse/receive-beam support. Compare conventional vs enhanced detection count and spacing.
8. **BDI.** Show the beam×time intensity structure and demonstrate that information distributed between beams can reveal geometry lost by independent one-detection-per-beam treatment.
9. **PDI.** On the same matrix, freeze a time slice and inspect amplitude/phase across directions. Find valid cross-beam phase zero crossing(s) / angle solution(s) under the registered method to form additional `(t, θ)` candidates. Emphasize `fixed time -> angle-series` versus conventional `fixed beam -> time-series`.
10. **Final same-scene comparison.** Use one Truth scene containing smooth bottom plus a discontinuity and narrow/vertical feature. Overlay what amplitude, conventional phase, enhanced phase/High Density, BDI and PDI recover, then show accepted combined detections if an integrated selector exists.

## Operational intuition / trade-offs

| Method / control | Strength | Limitation / cost |
|---|---|---|
| Narrower gate | rejects unrelated echoes | may miss real bottom when range changes |
| Higher threshold / stricter quality | suppresses weak/noisy candidates | may reject weak true returns |
| Amplitude detection | works without a usable phase ramp; derives timing from echo-energy structure | localization depends on echo/footprint geometry and chosen estimator |
| Conventional phase | uses coherent split-aperture phase ramp for precise timing/direction estimate | requires sufficient coherent phase support, SNR and appropriate geometry |
| High Density / enhanced phase | converts more phase structure into multiple directional detections | requires valid phase-to-angle mapping and quality support; more points are not smaller beams |
| BDI | exploits cross-beam spatial/intensity structure | depends on coherent multi-beam structure and algorithmic interpretation |
| PDI | exploits amplitude/phase as an angle-series at fixed time | requires valid spatial/phase support; complements but does not guarantee detection in every scene |

Desired learner message: **the bottom detector decides how much of the amplitude, phase, temporal and angular information available in the received field can be trusted and converted into valid bottom detections.**

## Scientific guardrails

- Conventional amplitude and phase may be competing estimators for one retained detection. Do not emit two conventional soundings merely because both produced candidates.
- A usable phase ramp is a prerequisite for reliable phase detection.
- The zero crossing must come from computed phase data, not a decorative curve.
- `Δφ -> θ` belongs to the Scientific Core and must respect split-aperture baseline, frequency/wavelength, geometry, steering, sign and phase ambiguities.
- High Density is not “more beams”. It exploits additional phase-supported solutions within the observation support of a formed receive beam.
- More detections can increase density, terrain detail and completeness when supported by the data, but do not automatically imply smaller footprint or greater independent acoustic resolution.
- BDI/PDI are not generic enhancement filters. Preserve their defined data dimensions and algorithmic assumptions.
- PDI must preserve the distinction between time-series and angle-series analysis.
- Keep physical echo, candidate, eligible candidate, retained detection and final sounding separate.
- Truth labels are teaching/validation aids only.
- D8 outputs `(t, θ)` or equivalent detection observables; D14 owns full sounding formation and coordinate transformation.
- Formal uncertainty propagation belongs to D17.

## Dependencies / forward reuse
Consumes D2 matched filtering/pulse compression, D3 SNR context, D5 array/sidelobe context, D6 receive beamforming/split-aperture phase, D7 footprint/slant range/incidence.

Passes valid/invalid `(t, θ)` detections to D14; detection-method/quality contribution to D17; additional sounding density to D16; sector-specific detection behavior to D9.

## Implementation delta
The current `BottomDetectionLab.tsx` already has echo scenarios, gate, threshold, amplitude-peak vs phase-zero-crossing selector, true/false/missed classification, TWTT, multiple retention and a High Density comparison. Next version must:
- make amplitude and differential phase synchronized primary views;
- show zero crossing and phase-ramp quality/support explicitly;
- expose validated `Δφ -> θ` mapping;
- compare `t_A` and `t_φ` but retain only one conventional detection;
- expand usable phase-ramp samples into multiple `(t, θ)` detections in enhanced mode;
- project those detections inside the same receive-beam support;
- add beam×time amplitude/phase matrix;
- show vertical time-series and horizontal angle-series cuts;
- add BDI/PDI method comparison over the same Truth scene;
- keep UI free of parallel hard-coded physics.

## Recognized references
- **IHO S-5A Ed. 2.0.0 (Aug 2026), H2.2a/H2.4a** — bottom detection, matched filtering, thresholding, amplitude/phase methods and multiple returns: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Hughes Clarke, John E. (2017), “Multibeam Echosounders”** — hydrographic bottom-detection and resolution context: <https://scholars.unh.edu/ccom/1370/>
- **Kongsberg (2013), “Sector coverage and beam spacing modes for multibeam echosounders”** — architecture-specific evidence for High Density Equidistant operation with several soundings per beam: <https://www.kongsberg.com/contentassets/058cd4fb2f1d417dab5f444f8f5cbf9a/em-sector-coverage-beam-spacing-modes.pdf>
- **Gomes de Araujo, Leonardo (2020), “Potential for Non-Conventional Use of Split-Beam Phase Data in Bottom Detection”**, University of New Hampshire M.S. thesis — PDI, angle-series analysis and complementary time-angle detections: <https://scholars.unh.edu/thesis/1421/>
- **Hamel, Jonathan (2020), “Effects of Transmission Side Lobe Interference on Multibeam Echosounder Phase Ramps”**, University of New Hampshire M.S. thesis — phase-ramp noise/support and direct coupling to bottom-detection uncertainty: <https://scholars.unh.edu/thesis/1425/>
