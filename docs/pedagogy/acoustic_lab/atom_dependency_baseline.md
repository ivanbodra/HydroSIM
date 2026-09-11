# Didactic Explorer — Audited Atom & Dependency Baseline

Status: **Initial audited planning baseline**  
Authority: Product Owner > Technical Lead > specialist scope  
Source handoff: #408  
Coordination gate: #359  
Production UX history: #392  
Production truth: `main`  
Review baseline: `v0.1.0_draft`

This document is the first complete audited reference atom/dependency map for all 17 Didactic Explorer labs after pedagogical requalification.

It is a **planning baseline, not an immutable implementation contract**. Material implementation changes may later `MERGE`, `SPLIT`, `ADD`, `REMOVE`, or `RECLASSIFY` atoms, provided the change remains traceable to the treatment, the previous atom(s), and the scientific/implementation reason.

Official `READY` and atoms-satisfied numerators remain Technical Lead authority.

## 1. Global result

- Labs mapped: **17/17**
- Inputs: **103**
- Outputs: **76**
- Audited initial denominator: **x = 179 atoms**
- Previous preliminary denominator in #392: **179**
- Net denominator delta: **0**

The audit confirms the previous total while correcting several atom meanings/classifications described in §4. The retained denominator is therefore an audited result, not blind adoption of the earlier count.

## 2. Atom rules applied

An atom is one learner-facing input or output required to materially satisfy the approved treatment.

Not counted independently: headings, labels, legends, reset, language selector, decorative markers, API fields, tests, CI, duplicated readouts/annotations of the same consequence, or implementation components.

A comparison overlay, marker, numeric readout, and annotation remain part of one output atom when they communicate the same underlying learner consequence. Distinct learner consequences remain distinct even when rendered in one chart.

Canonical state distinction must be preserved throughout:

`Truth != Observed != Configured != Estimated != Derived`

## 3. Per-lab atom inventory

### D1 — Acoustic Wave & Frequency — 4 inputs / 4 outputs = 8

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D01-I01 | Input | Frequency | Changes oscillation rate; period falls and wavelength changes at fixed sound speed. |
| D01-I02 | Input | Normalized amplitude | Changes wave magnitude without changing period or wavelength. |
| D01-I03 | Input | Initial phase | Shifts phase without changing frequency-derived quantities. |
| D01-I04 | Input | Sound speed | Changes wavelength at fixed frequency. |
| D01-O01 | Output | Temporal wave `p(t)` | Makes frequency/period/amplitude/phase visible on a fixed time scale. |
| D01-O02 | Output | Spatial wave `p(x)` | Makes wavelength change visible on a fixed/shared distance scale. |
| D01-O03 | Output | Period `T` | Shows `T = 1/f` as a derived consequence, not an independent control. |
| D01-O04 | Output | Wavelength `λ` | Shows `λ = c/f`, linking frequency and sound speed to later array/propagation labs. |

Production reconciliation: **RETAIN** current requalified D1 structure; fixed/shared scale remains part of O01/O02, not a separate atom.  
Minimum dependency state: scientific/Core/API **AVAILABLE**.

### D2 — Pulse & Signal Processing — 6 inputs / 5 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D02-I01 | Input | Pulse type CW/LFM | Switches between simple finite pulse and chirped/pulse-compressed behavior. |
| D02-I02 | Input | Pulse duration `τ` | Changes transmit occupancy/relative energy and CW temporal extent. |
| D02-I03 | Input | Bandwidth `B` | Changes LFM sweep extent and compressed response width/range resolution. |
| D02-I04 | Input | Centre frequency `fc` | Places the signal spectrally without being mis-taught as range resolution by itself. |
| D02-I05 | Input | Chirp direction | Reverses the LFM frequency progression while preserving the core bandwidth lesson. |
| D02-I06 | Input | Envelope/window | Changes sidelobe/main-response behavior when that consequence is visible. |
| D02-O01 | Output | Finite TX waveform | Shows pulse duration and waveform type directly. |
| D02-O02 | Output | Instantaneous frequency | Shows CW constancy versus LFM frequency progression/bandwidth. |
| D02-O03 | Output | Matched-filter response | Shows pulse compression and response narrowing. |
| D02-O04 | Output | Range resolution | Shows the authoritative resolution consequence of the active pulse/configuration. |
| D02-O05 | Output | Relative pulse energy/occupancy | Shows why longer transmission can provide more energy without conflating it with propagation. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: current waveform/matched-filter path **AVAILABLE**; render-ready range resolution and energy/occupancy **MISSING** from production API — existing blocker **#394**, owner `software-engineering`.

### D3 — Sonar Equation & Propagation Loss — 5 inputs / 6 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D03-I01 | Input | Range | Reveals two-way propagation-loss growth and reduced received margin. |
| D03-I02 | Input | Source level | Raises received level/SNR without being taught as a resolution control. |
| D03-I03 | Input | Frequency | Changes absorption/range behavior under the registered model. |
| D03-I04 | Input | Noise level | Changes SNR without changing received signal level. |
| D03-I05 | Input | Configured SNR reference | Provides a pedagogical comparison reference, not a detector threshold. |
| D03-O01 | Output | RL vs range | Shows received-level decay with geometry/propagation. |
| D03-O02 | Output | SNR vs range | Shows detectability-budget margin evolution independently of RL. |
| D03-O03 | Output | Transmission-loss decomposition | Separates spreading and absorption in the two-way loss. |
| D03-O04 | Output | Sonar contribution budget | Shows `SL -> TL -> bottom return -> TL -> RL -> NL -> SNR`. |
| D03-O05 | Output | SNR reference margin | Shows signed margin above/equal/below the configured reference. |
| D03-O06 | Output | Same-scale frequency comparison | Makes frequency-dependent propagation consequence directly comparable. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: science semantics **AVAILABLE** on `main`; margin/API bridge **PARTIALLY_AVAILABLE / MISSING in main endpoint** under existing **#396**, owner `software-engineering`.

### D4 — Sound Speed & Refraction — 4 inputs / 5 outputs = 9

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D04-I01 | Input | Launch/beam angle | Changes obliquity and the geometric sensitivity to profile mismatch. |
| D04-I02 | Input | Truth/reference SVP | Defines the physical propagation environment used for Truth. |
| D04-I03 | Input | Processing SVP | Changes reconstruction only; a mismatch moves the derived endpoint. |
| D04-I04 | Input | Profile/geometry scenario | Provides controlled constant/layered/gradient/depth cases without exposing every model coefficient at once. |
| D04-O01 | Output | Sound-speed profile `c(z)` | Makes the water-column model itself visible. |
| D04-O02 | Output | Truth/reference acoustic path | Shows the physical ray/path through the Truth water column. |
| D04-O03 | Output | Processing/reconstructed path | Shows the path implied by the configured processing profile on the same geometry. |
| D04-O04 | Output | Endpoint displacement/error | Shows reference vs reconstructed endpoint and `Δx, Δz` as one consequence. |
| D04-O05 | Output | Obliquity/swath sensitivity | Shows how profile-mismatch consequence evolves with beam angle on a shared geometry. |

Production reconciliation: **RETAIN + MODIFY**.  
Dependencies: registered ray/endpoint science **AVAILABLE**; shared Truth/Processing semantics **AVAILABLE**. No minimum external blocker identified.

### D5 — Transducer & Array Construction — 6 inputs / 7 outputs = 13

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D05-I01 | Input | Frequency | Changes wavelength and aperture-in-wavelengths at fixed physical geometry. |
| D05-I02 | Input | Across-track element count | Changes physical/effective across aperture through array construction. |
| D05-I03 | Input | Across-track element spacing | Changes across aperture and `d/λ`, exposing lobe/alias behavior. |
| D05-I04 | Input | Along-track element count | Changes the orthogonal physical/effective aperture. |
| D05-I05 | Input | Along-track element spacing | Changes along aperture and normalized spacing. |
| D05-I06 | Input | Aperture weighting/shading | Trades sidelobe suppression against main-lobe width/gain. |
| D05-O01 | Output | Physical 2-D element layout | Makes array geometry and vessel along/across axes visible. |
| D05-O02 | Output | Wavelength and normalized spacing | Shows metres together with `d/λ` so physical geometry is interpreted in wavelengths. |
| D05-O03 | Output | Physical/effective apertures | Shows aperture in both vessel axes and its normalized `L/λ` meaning. |
| D05-O04 | Output | Across-track directivity cut | Shows the response generated by the associated aperture. |
| D05-O05 | Output | Along-track directivity cut | Shows the independent orthogonal response. |
| D05-O06 | Output | Orthogonal -3 dB beamwidths | Makes anisotropic beam width visible quantitatively. |
| D05-O07 | Output | Sidelobe/grating-lobe consequence | Shows how spacing/weighting reshape response beyond the main lobe. |

Production reconciliation: **RETAIN + MODIFY + ADD + REMOVE**; remove installation eccentricity from D5 and keep it in D10.  
Dependencies: existing array science **AVAILABLE**; second orthogonal render-ready response **MISSING** under **#399**, owner `software-engineering`.

### D6 — Beamforming & Electronic Steering — 4 inputs / 7 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D06-I01 | Input | Source/arrival angle | Changes physical arrival offsets while steering can remain fixed. |
| D06-I02 | Input | Steering command / delay gradient | Changes applied relative compensation without mechanically moving the array. |
| D06-I03 | Input | RX/TX view | Reveals receive compensation/sum first and reciprocal transmit behavior second. |
| D06-I04 | Input | Simultaneous virtual RX directions | Shows one physical channel set processed through several delay/weight sets. |
| D06-O01 | Output | Wavefront/channel arrival offsets | Shows which channels are early/late before compensation. |
| D06-O02 | Output | Applied compensation and residuals | Shows the processing correction and remaining mismatch. |
| D06-O03 | Output | Channel alignment state | Shows aligned/misaligned traces after compensation. |
| D06-O04 | Output | Coherent summed response | Shows directional sensitivity through constructive/destructive combination. |
| D06-O05 | Output | Directional response / effective peak | Distinguishes requested steering from actual physical one-way response. |
| D06-O06 | Output | Broadside/current steering consequence | Shows steering penalty/shape change on a common angular scale where computed. |
| D06-O07 | Output | Shared-channels -> multiple virtual beams | Shows multiple receive directions as parallel processing, not multiple transducers. |

Production reconciliation: **RETAIN + MODIFY + ADD**; preserve the fixed-array causal redesign rather than reintroducing D5 construction controls.  
Dependencies: steering/sign/alias science **AVAILABLE** (#371 resolved); single-beam API **AVAILABLE**; multi-beam shared-channel response **MISSING** under **#401**, owner `software-engineering`.

### D7 — Echosounders: SBES vs MBES — 6 inputs / 5 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D07-I01 | Input | System mode SBES/MBES | Switches between one finite acoustic observation and a formed receive fan. |
| D07-I02 | Input | Sonar-to-bottom separation/depth | Changes slant ranges, projected footprint and swath geometry. |
| D07-I03 | Input | TX directional-pattern configuration | Changes transmitted insonification support and along/across footprint contribution. |
| D07-I04 | Input | RX fan configuration | Changes receive beamwidth/directional sampling configuration without implying narrower beams from count alone. |
| D07-I05 | Input | Angular sector/steering limit | Changes angular coverage and outer-beam geometry. |
| D07-I06 | Input | Beam-spacing mode | Redistributes receive directions/sounding centres without changing physical beamwidth by itself. |
| D07-O01 | Output | SBES/MBES water-column geometry | Shows one TX event and the physical relationship to one/many receive directions. |
| D07-O02 | Output | Selected TX×RX directional response | Shows TX one-way, selected RX one-way and canonical two-way response as one causal chain. |
| D07-O03 | Output | Per-beam observation locations | Shows beam centre, slant range/incidence and detection location across the fan. |
| D07-O04 | Output | Finite seafloor footprint field | Shows along/across footprint support separately from point detections. |
| D07-O05 | Output | Swath/sounding-spacing consequence | Shows nadir/intermediate/outer geometry and spacing on common physical scales. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: canonical centre/incidence/spacing/finite-footprint geometry **AVAILABLE**; selected TX/RX/two-way response **MISSING** under **#402**, owner `software-engineering`.

### D8 — Bottom Detection — 6 inputs / 5 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D08-I01 | Input | Echo/scene scenario | Changes the physical return structure: clean, noisy, competing, discontinuous or phase-support cases. |
| D08-I02 | Input | Detection method | Lets amplitude and conventional phase compete as estimators for one retained solution. |
| D08-I03 | Input | Detection gate/window | Changes which echo support is eligible for detection. |
| D08-I04 | Input | Threshold/quality criterion | Trades rejection of weak/noisy candidates against missed true returns. |
| D08-I05 | Input | Phase support/beam context | Exposes when phase-ramp support/coherence is sufficient or degraded. |
| D08-I06 | Input | Extraction mode | Moves from Conventional to enhanced phase/High Density and BDI/PDI comparison without equating them to extra physical beams. |
| D08-O01 | Output | Synchronized amplitude + differential-phase evidence | Shows `A(t)` and `Δφ(t)` on one time base with gate/support/candidates. |
| D08-O02 | Output | Phase-to-angle / detection formation | Shows validated `Δφ -> θ` and how candidate `(t,θ)` estimates are formed. |
| D08-O03 | Output | Retained detection(s) on seafloor support | Shows one conventional retained point or additional valid phase-supported detections inside the same acoustic support. |
| D08-O04 | Output | Beam×time / time-series vs angle-series view | Makes BDI/PDI data orientation and method distinction visible. |
| D08-O05 | Output | Same-scene method/Truth comparison | Shows true/false/missed and method recovery differences without exposing Truth as operational data. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: amplitude/gate/threshold/multiple-detection and historical High Density slices **PARTIALLY_AVAILABLE**; canonical phase detection, validated phase-to-angle and BDI/PDI scope **BLOCKED on science** under **#403**, owner `scientific-lead`.

### D9 — Multisector MBES — 6 inputs / 4 outputs = 10

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D09-I01 | Input | TX sector count/layout | Splits one swath into identified transmit-sector configurations. |
| D09-I02 | Input | Sector centre/angular support | Creates sector coverage, gap or overlap while RX beams remain conceptually distinct. |
| D09-I03 | Input | Sector TX timing/group | Changes simultaneous/staggered transmit epochs and downstream TWTT association. |
| D09-I04 | Input | Per-sector frequency | Changes sector signal identity/propagation context only where the architecture supports it. |
| D09-I05 | Input | Per-sector pulse duration | Changes sector pulse configuration without inventing unsupported consequences. |
| D09-I06 | Input | Per-sector source-level/relative-power setting | Changes configured sector transmission only with exact registered semantics. |
| D09-O01 | Output | TX sector geometry | Shows centres/supports/gaps/overlaps and reinforces `TX sectors != RX beams`. |
| D09-O02 | Output | Transmit timeline | Shows TX epochs, pulse intervals and simultaneous/staggered groups. |
| D09-O03 | Output | Sector identity/configuration | Preserves frequency/pulse/timing identity for downstream association. |
| D09-O04 | Output | One-sector vs multisector consequence | Shows what changes in geometry/timing/configuration without implying more sectors = more receive beams/soundings. |

Production reconciliation: **RETAIN + MODIFY + REMOVE** misleading equal-weight/opacity-as-power presentation; existing UX WIP is authoritative.  
Minimum dependencies: current sector geometry/timing/config API **AVAILABLE**; parent-sector association is recommended but not a minimum blocker.

### D10 — Vessel & Sensor Configuration — 7 inputs / 4 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D10-I01 | Input | Vessel reference point / VRP | Redefines coordinates/lever arms without moving the rigid physical installation. |
| D10-I02 | Input | GNSS installation position | Moves the GNSS measurement centre physically in the common vessel frame. |
| D10-I03 | Input | IMU/MRU installation position | Moves the motion-reference centre physically and changes lever arms. |
| D10-I04 | Input | Sonar installation position | Moves the acoustic measurement centre physically and changes lever arms. |
| D10-I05 | Input | Sensor mounting orientation | Rotates sensor body axes relative to vessel axes without moving its centre. |
| D10-I06 | Input | Vessel vertical geometry | Changes waterline/static-draft/transducer geometric relationships in the vessel frame. |
| D10-I07 | Input | Hydrographic water level relative to datum | Changes the datum quantity without moving vessel-frame sensors/geometry. |
| D10-O01 | Output | Common-frame installation / lever arms | Shows physical sensor centres, vessel axes, directed offsets and invariants. |
| D10-O02 | Output | Sensor-axis orientation | Shows aligned versus physically misaligned sensor body axes. |
| D10-O03 | Output | Vertical-reference separation | Makes vessel-frame Z geometry visibly distinct from hydrographic water level/datum. |
| D10-O04 | Output | Configuration/invariant snapshot | Shows the frame/origin/offset/orientation record and equivalent-VRP invariants. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: static position/VRP/vertical API **AVAILABLE**; mounting orientation/body-axis transform **MISSING** under **#404**, owner `software-engineering`.

### D11 — Vessel Motion — 4 inputs / 4 outputs = 8

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D11-I01 | Input | Roll | Rotates the vessel/swath across-track and exposes outer-swath sensitivity. |
| D11-I02 | Input | Pitch | Rotates acoustic geometry fore-aft and moves offset sensors through rigid-body geometry. |
| D11-I03 | Input | Yaw/heading deviation | Rotates acoustic geometry horizontally relative to track/seafloor. |
| D11-I04 | Input | Heave | Translates the sonar vertically without confusing the motion with attitude. |
| D11-O01 | Output | Vessel/sensor pose | Shows neutral/current vessel, axes, VRP and transducer from authoritative rigid-body geometry. |
| D11-O02 | Output | Acoustic beam/swath motion consequence | Shows baseline/current acoustic geometry and stabilization consequence while vessel motion remains real. |
| D11-O03 | Output | Raw vs motion-compensated sounding consequence | Shows uncompensated displacement versus ideal compensated geometry on the same scene. |
| D11-O04 | Output | Time-varying motion consequence | Shows one deterministic DOF over time tied to the corresponding geometric response. |

Production reconciliation: **RETAIN + MODIFY + REMOVE + ADD**: preserve learner interaction strengths, remove CSS/synthetic geometry as scientific authority, consume existing motion Core/API.  
Minimum dependencies: rigid-body motion/science/API **AVAILABLE**. Off/Ideal compensation is a required comparison state; it is not counted separately here because the baseline allows simultaneous comparison rather than requiring another independent control. If implementation makes it an independently causal control, traceable `SPLIT/RECLASSIFY` is permitted.

### D12 — PU & Sensor Integration — 6 inputs / 4 outputs = 10

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D12-I01 | Input | Sensor/device class | Tests whether the selected PU input accepts the measurement role. |
| D12-I02 | Input | Connection/transport configuration | Changes serial/network path and applicable connection parameters. |
| D12-I03 | Input | Protocol | Tests interpretation compatibility independently of the physical/logical connection. |
| D12-I04 | Input | Message/datagram type | Tests message semantics inside an otherwise accepted protocol. |
| D12-I05 | Input | Update rate | Changes nominal cadence/period and can violate profile-specific limits. |
| D12-I06 | Input | Timestamp source | Tests time-reference compatibility without pretending that compatibility proves timing correctness. |
| D12-O01 | Output | Layered PU integration path | Shows pass/fail at sensor role -> transport -> protocol/message -> cadence -> time source -> PU input. |
| D12-O02 | Output | Stream semantics/cadence | Shows role, message identity, update rate/period and timestamp source. |
| D12-O03 | Output | Explicit rejection diagnosis | Shows the exact layer/reason for an incompatible configuration. |
| D12-O04 | Output | Sensor-to-PU integrated flow state | Shows accepted stream(s) entering acquisition inputs without implying packet simulation or scientific validity. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: compatibility evaluator **AVAILABLE**; authoritative PU input profile is currently frontend-defined and must move to Python/API — **MISSING** under **#405**, owner `software-engineering`.

### D13 — Timing, Synchronization & Latency — 5 inputs / 4 outputs = 9

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D13-I01 | Input | Selected sensor stream | Changes the cadence/latency/association stream being diagnosed. |
| D13-I02 | Input | Update rate | Changes sample spacing/sample age without changing latency. |
| D13-I03 | Input | Stream latency | Moves availability later without rewriting the physical measurement epoch. |
| D13-I04 | Input | Vessel speed | Scales the spatial consequence of the same position timing mismatch. |
| D13-I05 | Input | Synchronization / clock-offset state | Changes reported-time relation to common time independently of latency. |
| D13-O01 | Output | Common event/cadence timeline | Shows sample epochs, availability, trigger/TX/RX context and periodic cadence on one time basis. |
| D13-O02 | Output | Causal sample association / age | Shows which sample is legally available at the sonar event and why future samples are forbidden. |
| D13-O03 | Output | Clock synchronization consequence | Shows common/Truth time versus sensor-reported time and known-offset correction distinctly from latency. |
| D13-O04 | Output | Timing-to-spatial state consequence | Shows the constant-speed position-state displacement; attitude remains age/angular-state evidence until geometry is supplied downstream. |

Production reconciliation: **RETAIN + MODIFY + ADD**.  
Dependencies: cadence/latency/causal association API **AVAILABLE**; clock science is now **AVAILABLE** from resolved **#406**; render-ready clock synchronization API bridge **MISSING** under **#413**, owner `software-engineering`.

### D14 — Sounding Formation — 7 inputs / 3 outputs = 10

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D14-I01 | Input | Retained detection / TWTT | Supplies the observed acoustic timing information from D8. |
| D14-I02 | Input | Detected direction/beam angle | Supplies the observed angular direction required with range/path. |
| D14-I03 | Input | Propagation model / sound speed | Changes how travel time and direction are reconstructed into path/range. |
| D14-I04 | Input | Vessel position | Places the sensor/observation in navigation space. |
| D14-I05 | Input | Vessel attitude | Rotates the observation from vessel/sensor geometry into navigation frame. |
| D14-I06 | Input | Installation transform | Applies lever arm/mounting geometry from sensor to vessel reference. |
| D14-I07 | Input | Event/identity association | Selects the correct ping/sector/beam/detection/time provenance. |
| D14-O01 | Output | Detection -> acoustic path/range | Shows why a detection is still only an acoustic observation before spatial transforms. |
| D14-O02 | Output | Sensor -> vessel -> navigation transform chain | Shows which configured transform moves/rotates the observation. |
| D14-O03 | Output | Derived 3-D sounding | Shows final reconstructed point and optional teaching-only Truth/error evidence. |

Production reconciliation: **RETAIN + MODIFY** with progressive disclosure and explicit transform-chain visualization.  
Minimum dependencies: first-slice constant-`c`, pose, lever-arm, identity and Truth/error API **AVAILABLE**. Advanced D4 ray tracing, D10 mounting orientation, D9 sector provenance and D13 wrong-time diagnostics remain downstream enhancements, not minimum blockers for this baseline.

### D15 — Survey Planning — 7 inputs / 4 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D15-I01 | Input | Survey-area geometry | Defines the finite planning area/cross-line span. |
| D15-I02 | Input | Reference depth | Changes canonical expected swath through upstream sonar geometry. |
| D15-I03 | Input | Sonar/swath configuration | Changes the expected usable swath used by the reference planner. |
| D15-I04 | Input | Line direction | Rotates the line family and changes clipping/cross-line span. |
| D15-I05 | Input | Spacing mode | Switches between overlap-driven and explicit centreline-spacing planning. |
| D15-I06 | Input | Overlap / requested spacing | Trades nominal coverage margin against line count/effort and can intentionally create gaps. |
| D15-I07 | Input | Survey speed | Changes idealized on-line time only in the current model. |
| D15-O01 | Output | Planned line/coverage map | Shows finite centrelines and nominal strips in one local-metre view. |
| D15-O02 | Output | Gap/overlap coverage state | Shows requested/actual spacing and continuous/touching/overlapping/gapped consequence. |
| D15-O03 | Output | Acquisition effort | Shows line count, on-line length and idealized on-line time with scope limits. |
| D15-O04 | Output | Baseline/current plan comparison | Supports a defensible coverage-margin versus effort decision. |

Production reconciliation: **RETAIN + MODIFY**.  
Minimum scientific/Core/API dependencies **AVAILABLE**; treatment identifies no new minimum blocker.

### D16 — Survey Coverage & Acquisition Trade-offs — 9 inputs / 5 outputs = 14

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D16-I01 | Input | Vessel speed | Changes along-track ping spacing at fixed effective ping rate. |
| D16-I02 | Input | Effective ping rate | Changes along-track sampling cadence/spacing at fixed speed. |
| D16-I03 | Input | Angular sector/swath configuration | Changes geometric across-track support through canonical D7 geometry. |
| D16-I04 | Input | Beam count | Changes directional sample count/centre distribution, not physical beamwidth by itself. |
| D16-I05 | Input | Beam-spacing mode | Redistributes retained centres without being mis-taught as resolution. |
| D16-I06 | Input | RX beamwidth / footprint configuration | Changes finite footprint support/continuity. |
| D16-I07 | Input | Depth | Changes range/projected footprint and spacing through upstream geometry. |
| D16-I08 | Input | Bottom-detection sampling mode | Compares conventional versus additional valid/High Density detections inside existing support. |
| D16-I09 | Input | Multisector/acquisition configuration | Imports already-defined sector/acquisition consequences without inventing new local physics. |
| D16-O01 | Output | Swath/finite-footprint support | Shows physical insonified support separately from point count. |
| D16-O02 | Output | Spatial sounding pattern | Shows ping origins and retained/additional detections in the local survey frame. |
| D16-O03 | Output | Coverage union/gaps | Shows merged finite-footprint coverage and real geometric gaps rather than filling beam-centre extent. |
| D16-O04 | Output | Along/across spacing and density | Shows ping spacing and actual retained across-track spacing/density consequences. |
| D16-O05 | Output | Benefit/cost trade-off comparison | Distinguishes coverage, density, resolution and efficiency when choosing configurations. |

Production reconciliation: **RETAIN + MODIFY**; de-emphasize unsupported frequency/pulse controls and make the connected acquisition strip dominant.  
Minimum survey-density/footprint-union/High-Density invariant APIs **AVAILABLE**; no new minimum blocker identified.

### D17 — Uncertainty / TPU — 7 inputs / 4 outputs = 11

| ID | Type | Learner-facing atom | Learner-visible consequence |
|---|---|---|---|
| D17-I01 | Input | Horizontal position standard uncertainty | Adds horizontal measurement dispersion through the registered model. |
| D17-I02 | Input | Roll standard uncertainty | Adds angle/range-dependent across/down uncertainty, especially with obliquity. |
| D17-I03 | Input | Slant-range standard uncertainty | Projects along the acoustic direction and redistributes with beam angle. |
| D17-I04 | Input | Effective sound-speed standard uncertainty | Adds homogeneous-model path/range sensitivity without replacing D4 refraction physics. |
| D17-I05 | Input | Across-track installation-offset uncertainty | Adds configured installation contribution to the final covariance. |
| D17-I06 | Input | Timing standard uncertainty | Produces along-track uncertainty proportional to vessel speed in the first slice. |
| D17-I07 | Input | Water-level standard uncertainty | Adds vertical-reduction uncertainty directly in the controlled model. |
| D17-O01 | Output | Propagated sounding uncertainty geometry/components | Shows covariance-derived along/across/down dispersion on physical axes. |
| D17-O02 | Output | Horizontal/vertical standard and expanded uncertainty semantics | Distinguishes `1σ` summaries from explicitly expanded uncertainty and avoids mislabelling them as automatic S-44 compliance. |
| D17-O03 | Output | Variance-contribution ranking | Shows which input dominates and why contributions combine as variances/covariances. |
| D17-O04 | Output | Geometry/swath uncertainty variation | Shows how the same input uncertainties map differently at nadir/intermediate/outer beams; optional Truth/error/residual evidence remains semantically distinct. |

Production reconciliation: **RETAIN + MODIFY + ADD** learner framing/expanded-uncertainty experience.  
Minimum scalar/generic covariance APIs, contribution decomposition, angle sweep and coverage-factor/Truth-residual semantics **AVAILABLE**.

## 4. Reconciliation with previous #392 baseline

Previous: **179 = 103 inputs + 76 outputs**.  
Audited: **179 = 103 inputs + 76 outputs**.  
Net delta: **0**.

Material semantic corrections with no net-count change:

1. **D4:** `fixed bottom geometry` is not retained as an independent atom. Bottom/target graphics are context. The five outputs are now explicitly `c(z)`, Truth path, Processing path, endpoint-error consequence, and obliquity/swath sensitivity.
2. **D5:** weighting/shading is the counted advanced causal input; `element face` is not required as a separate minimum atom. TX/RX installation eccentricity remains moved to D10.
3. **D8:** the expanded phase treatment does not inflate the denominator by counting every plot annotation separately. Amplitude and differential phase form one synchronized evidence atom; `Δφ -> θ`/formation is one causal output; BDI/PDI share one beam×time/time-vs-angle output. The previous five-output budget is therefore retained with corrected semantics.
4. **D11:** Off/Ideal stabilization/compensation is a required comparison, but the baseline permits it to be shown simultaneously rather than forcing a separate control atom. If implementation exposes it as an independently causal learner control, that is a traceable future `SPLIT/RECLASSIFY`, not a silent denominator change.
5. **D13:** the earlier vague `timestamp/time source` concept is replaced by the now-defined `synchronization / clock-offset state` from #406. Count remains five inputs.
6. **D17:** the previous shorthand `THU/TVU/TPU` output is corrected to standard-versus-expanded horizontal/vertical uncertainty semantics. It must not imply S-44 95% compliance from `1σ` quantities.

No treatment-required learner consequence was removed solely to preserve 179; no decorative/readout item was added solely to preserve it.

## 5. Current-production reconciliation summary

| Lab | Current action | Minimum dependency status |
|---|---|---|
| D1 | RETAIN | AVAILABLE |
| D2 | RETAIN + MODIFY + ADD | PARTIALLY_AVAILABLE — #394 |
| D3 | RETAIN + MODIFY + ADD | PARTIALLY_AVAILABLE — #396 |
| D4 | RETAIN + MODIFY | AVAILABLE |
| D5 | RETAIN + MODIFY + ADD + REMOVE | PARTIALLY_AVAILABLE — #399 |
| D6 | RETAIN + MODIFY + ADD | PARTIALLY_AVAILABLE — #401 |
| D7 | RETAIN + MODIFY + ADD | PARTIALLY_AVAILABLE — #402 |
| D8 | RETAIN + MODIFY + ADD | BLOCKED/PARTIAL — #403 science first |
| D9 | RETAIN + MODIFY + REMOVE | AVAILABLE for minimum path; current UX WIP |
| D10 | RETAIN + MODIFY + ADD | PARTIALLY_AVAILABLE — #404 |
| D11 | RETAIN + MODIFY + REMOVE + ADD | AVAILABLE; current UI must consume existing Core geometry |
| D12 | RETAIN + MODIFY + ADD | PARTIALLY_AVAILABLE — #405 |
| D13 | RETAIN + MODIFY + ADD | science AVAILABLE (#406); API bridge MISSING — #413 |
| D14 | RETAIN + MODIFY | AVAILABLE for minimum path |
| D15 | RETAIN + MODIFY | AVAILABLE |
| D16 | RETAIN + MODIFY | AVAILABLE |
| D17 | RETAIN + MODIFY + ADD | AVAILABLE |

No whole-product rewrite is justified by this audit. Existing HydroSIM code remains reusable capital. No lab currently requires a second frontend. `LOCAL_REBUILD` is therefore **not imposed as a baseline decision**; Production UX may justify it later for a specific local interaction structure with traceable evidence.

## 6. Shared mechanisms and ownership

| Shared mechanism | Labs | Baseline ownership decision |
|---|---|---|
| Fixed/shared comparison scales and baseline/current overlays | D1–D7, D15–D17 | Reuse the established interaction rule. Keep lab rendering local unless a real shared component already exists; do not abstract merely for visual similarity. |
| Truth / Observed / Configured / Estimated / Derived semantics | D4, D8, D11, D14, D17 | **One shared semantic/style owner.** D14 is the best integration anchor; other labs consume the same state/provenance vocabulary. |
| Vessel/reference-frame visualization | D10, D11, D14, D17 | **One shared implementation owner should extract/refine the frame/axes/vessel/sensor primitives** because parallel reinvention risks contradictory axis/sign geometry. D10/D11 establish physical geometry; D14 consumes it. |
| Beam/directivity/footprint spatial primitives | D5, D6, D7, D8, D9, D16 | Core science remains lab-specific, but **D7 should own shared seafloor beam/footprint presentation primitives** consumed downstream by D8/D16. D5 directivity plots remain separate. |
| Causal event timeline | D9, D12, D13, D14 | **D13 should own the generic event/timestamp timeline primitive**; D9/D14 consume it for sector/provenance events. D12 cadence may reuse ticks but keeps integration semantics local. |
| High Density visual semantics | D8, D16 | D8 owns explanation/formation; D16 consumes canonical detection objects. Never implement High Density twice or redraw extra physical beams. |
| Scenario/preset + progressive disclosure pattern | Most labs | Reuse interaction convention, but keep local unless a concrete shared component prevents duplicate state/control code. |
| EN/PT-BR localization and hydrographic/naval terminology | All | Reuse the existing global language shell. **One terminology/glossary owner**; no per-lab language toggles or divergent translations. |

## 7. Existing blocker inventory

| Issue | Lab(s) | Owner | Exact missing capability | State at audit |
|---|---|---|---|---|
| #394 | D2 | software-engineering | Render-ready canonical range resolution and relative pulse-energy/occupancy | Open |
| #396 | D3 | software-engineering | Configured SNR reference + render-ready signed margin in sonar-equation API | Open; scientific semantics already resolved |
| #399 | D5 | software-engineering | Orthogonal along-track directivity pattern and -3 dB beamwidth from authoritative Core/API | Open |
| #401 | D6 | software-engineering | One shared RX channel snapshot evaluated through multiple simultaneous steering/delay sets | Open |
| #402 | D7 | software-engineering | Selected TX one-way + RX one-way + canonical two-way directional response tied to the footprint | Open |
| #403 | D8 | scientific-lead | Canonical differential-phase detection, `Δφ -> θ`, phase support/quality, enhanced phase boundary and minimum BDI/PDI scope | Open |
| #404 | D10 | software-engineering | Sensor mounting orientation/body-axis transform in canonical vessel configuration API | Open |
| #405 | D12 | software-engineering | Registered/API-owned PU input profile instead of frontend-owned acceptance rules | Open |
| #406 | D13 | scientific-lead | Clock-offset/common-time semantics | **Resolved/closed**; contract available on `main` |
| #413 | D13 | software-engineering | Expose resolved clock synchronization contract as render-ready timing API data | Open |

Historical D8 High Density work (#294/#325) is preserved as prior capital and must not be duplicated. #403 is the current broader phase-detection scientific gate.

## 8. Immediately implementable vs blocked/partial

### Immediately implementable minimum paths

- **D1** — current requalified surface can be retained/audited.
- **D4** — minimum Truth/Processing SVP and endpoint-error experience has no new external blocker.
- **D9** — minimum requalification is UX/presentation; preserve current WIP.
- **D11** — consume existing authoritative motion API instead of conceptual CSS geometry.
- **D14** — progressive observation-to-sounding transform chain is supported by current first-slice API.
- **D15** — current planner science/API already supports the minimum treatment.
- **D16** — current density/coverage APIs support the minimum trade-off lesson.
- **D17** — current uncertainty APIs support the minimum mechanism and expanded-uncertainty framing.

### Partially blocked but UX-independent work remains possible

- **D2** — comparison hierarchy/axes can progress; O04/O05 depend on #394.
- **D3** — hierarchy/decomposition can progress; D03-I05/O05 depend on #396.
- **D5** — 2-D physical layout and existing plane can progress; orthogonal cut/beamwidth depend on #399.
- **D6** — single-beam mechanism can progress; multi-virtual-beam atom D06-O07 depends on #401.
- **D7** — geometry/footprint/fixed scales can progress; D07-O02 depends on #402.
- **D10** — physical-position/VRP/vertical-reference work can progress; orientation atoms D10-I05/O02 depend on #404.
- **D12** — layered presentation can be prepared; final authority boundary depends on #405.
- **D13** — cadence/latency/causal association can progress; synchronization atom D13-I05/O03 depends on #413.

### Science-blocked slice

- **D8** — amplitude/gate/threshold/previous High Density capital remains reusable, but the approved phase/BDI/PDI treatment cannot be completed until #403 defines the canonical phase contract/scope.

## 9. Proposed implementation blocks

Blocks are planning units, not mandatory branches.

### Block A — Acoustic foundations: D1–D4
Common concepts: fixed/shared scales, wave/signal/propagation causality, baseline comparison.  
Prerequisites: none upstream.  
Blockers: #394 D2, #396 D3.  
Collision risk: low between lab files; medium if agents simultaneously refactor shared plot/comparison primitives.  
Parallelism: **yes**, provided shared comparison primitives have one owner.

### Block B — Array to observation geometry: D5–D7
Common concepts: physical array, beam response, steering, TX/RX geometry, footprint.  
Prerequisites: D1 frequency/wavelength intuition; D2/D3 conceptual dependencies need not be runtime blockers.  
Blockers: #399, #401, #402.  
Collision risk: **high** for beam/directivity/footprint shared primitives and related API types.  
Parallelism: **only after one owner is assigned for shared beam/footprint presentation**; otherwise serialize shared-component edits.

### Block C — Detection and sector architecture: D8–D9
Common concepts: echo/detection identity, TX sector provenance, timing, enhanced detections.  
Prerequisites: D7 conceptual geometry.  
Blockers: #403 for D8; D9 minimum path unblocked.  
Collision risk: medium through detection/sector provenance and High Density semantics.  
Parallelism: **yes** — D9 can proceed while #403 resolves, but D9 must not redefine D8 detection physics.

### Block D — Platform geometry and motion: D10–D11
Common concepts: vessel frame, VRP, sensor positions/orientations, rigid-body motion, stabilization/compensation.  
Prerequisites: shared vessel/reference-frame visual ownership.  
Blockers: #404 for D10 orientation; D11 minimum path unblocked.  
Collision risk: **high** if both branches independently create vessel/axes/sensor primitives.  
Parallelism: yes only after assigning one owner for the shared vessel/reference-frame component.

### Block E — Integration to sounding: D12–D14
Common concepts: stream identity, cadence/time, event association, provenance, coordinate reconstruction.  
Prerequisites: D10/D11 outputs conceptually; minimum D14 first slice already has local canonical inputs.  
Blockers: #405 D12, #413 D13; D14 minimum path unblocked.  
Collision risk: high around timeline/provenance/state semantics; medium around shared API types.  
Parallelism: **yes** after D13 owns the generic timeline and D14 owns state/provenance presentation.

### Block F — Planning, acquisition and uncertainty: D15–D17
Common concepts: survey-frame spatial views, baseline/current decision comparison, coverage/density/quality trade-offs.  
Prerequisites: consumes earlier concepts but minimum APIs already available.  
Blockers: none identified for minimum paths.  
Collision risk: medium between D15/D16 survey map/coverage styling; low with D17 if state vocabulary is reused.  
Parallelism: **yes**; this is the safest independent block for a second UX line.

## 10. Collision / parallel-work matrix

| Lab group pair | Risk | Reason / guardrail |
|---|---|---|
| D1–D4 vs D15–D17 | Low | Different production components and APIs; shared scale pattern only. |
| D5–D7 internal | High | Beam/directivity/footprint concepts and likely shared presentation/API typing. Assign one shared owner. |
| D7 ↔ D8/D16 | Medium-High | D8/D16 consume D7 footprint semantics. D7 owns footprint presentation primitives; downstream consumes. |
| D8 ↔ D16 | Medium | High Density/detection semantics must come from one canonical object/model. D8 explains; D16 compares consequences. |
| D9 ↔ D13/D14 | Medium | Shared TX epoch/sector provenance and timelines. D13 owns generic timeline; D14 consumes identity. |
| D10 ↔ D11/D14 | High | Same vessel frame, axes, lever arms and sensor geometry. One shared vessel/reference-frame owner is mandatory. |
| D12 ↔ D13 | Medium | Stream identity/update rate/timestamp semantics cross the boundary; D12 must not implement timing-error logic. |
| D13 ↔ D14 | Medium-High | Wrong-time/pose association is consumed by D14; timing math remains D13/Core authority. |
| D15 ↔ D16 | Medium | Related survey-frame/coverage views, but line planning and within-strip acquisition remain separate responsibilities. |
| D14 ↔ D17 | Medium | Provenance/state semantics and Truth/error/uncertainty distinction must remain consistent. |

Most lab components are separate production files, so the dominant merge-collision risk is not the lab file itself but shared visual primitives, shared API/type definitions, and semantic ownership. Parallel branches must not both redefine those shared surfaces.

## 11. Recommended safe allocation for two Production UX agents

### UX Line A — acoustic/sonar chain
1. Converge existing D2 WIP and consume #394 when ready.
2. D3 once #396 lands, without opening a parallel duplicate of current dependency work.
3. Then D5–D7 as Block B, with one explicit owner for beam/footprint shared primitives.
4. D8 only after #403 releases the required science; D9 remains current WIP and should be preserved rather than restarted.

### UX Line B — integration/operational chain
1. Finish/preserve existing D9 WIP if assigned by Technical Lead.
2. Move immediately to unblocked Block F (D15–D17) or D11/D14 while D10/D12/D13 bridges resolve.
3. Before D10–D14 parallel work expands, assign shared ownership: vessel/reference-frame primitive to one branch; generic timeline to D13; state/provenance presentation to D14.

Safest immediate independent pairing after the mapping gate:

- **Line A:** current D2/D3 acoustic WIP/dependencies.
- **Line B:** current D9 WIP, then D15–D17.

This pairing has low shared-file/semantic collision and keeps both agents productive while specialist blockers #394/#396/#399/#401/#402/#403/#404/#405/#413 proceed in parallel.

## 12. Planning-baseline completion statement

This audit satisfies the Stage-A planning requirement from #359/#408:

- 17/17 treatments mapped;
- every lab has stable input/output atom IDs, counts and learner consequences;
- audited denominator `x = 179` established;
- differences in interpretation from the earlier #392 summary are explicitly reconciled;
- current-production actions are classified;
- shared-component ownership is identified;
- existing blockers are reconciled without duplication, with only the newly necessary post-#406 D13 engineering bridge routed as #413;
- immediately implementable and blocked/partial labs are distinguished;
- coherent implementation blocks and collision risks are documented;
- two Production UX lines can now be assigned without rediscovering the global architecture.
