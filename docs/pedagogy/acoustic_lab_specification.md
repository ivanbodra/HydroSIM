# HydroSIM Acoustic Lab — Pedagogical Specification

Status: **next-version development specification — iterative**  
Former name: **Didactic Module**  
Audience: AI/software/UX/science agents implementing the next HydroSIM version

This is the **canonical lab-by-lab pedagogical contract for the Acoustic Lab**. It complements the general pedagogical framework and Scientific Registry; it does not redefine physics.

Related:
- [`didactic_module_pedagogical_framework.md`](didactic_module_pedagogical_framework.md) — general pedagogy (read as Acoustic Lab framework);
- [`pedagogical_reference_index.md`](pedagogical_reference_index.md) — source index;
- [`hydrosim_pedagogical_plan.md`](hydrosim_pedagogical_plan.md) — broader curriculum/history;
- [`../architecture/didactic_explorer_foundation.md`](../architecture/didactic_explorer_foundation.md) — Scientific Core boundary.

## 1. Product and teaching contract

HydroSIM is a hydrographic acquisition simulator. The Acoustic Lab develops the physical, signal-processing, geometric and operational intuition required to understand, tune and diagnose hydrographic acquisition.

```text
SEE -> UNDERSTAND -> PREDICT -> TUNE / DECIDE -> DIAGNOSE / JUSTIFY
```

```text
CONTROL
  -> PHYSICAL / SIGNAL / GEOMETRIC CHANGE
  -> OBSERVABLE CONSEQUENCE
  -> BOTTOM-DETECTION / SOUNDING CONSEQUENCE
  -> BENEFIT + COST
  -> ACQUISITION DECISION
```

Rules:
- one dominant discovery per lab;
- few primary controls; secondary controls use progressive disclosure;
- deterministic immediate response;
- fixed/shared plot scales when autoscaling would hide the concept;
- mechanism before operational rule;
- show benefit and cost of tunable parameters;
- permit poor configurations when their consequence is useful;
- UI consumes the Scientific Core; no parallel physics;
- vendor behavior is evidence, not universal law.

## 2. Source hierarchy

1. **IHO S-5A, Ed. 2.0.0 (Aug 2026)** — competence anchor.
2. **MIT OCW 2.682 Acoustical Oceanography** — first-principles acoustics.
3. **CCOM/UNH and UNB/OMG** — hydrographic/ocean-mapping science and integrated-system interpretation.
4. **DHN** — Brazilian operational relevance.
5. **Authoritative manufacturer documentation** — real controls/modes/trade-offs.

## 3. Active lab map

| ID | Lab | Status |
|---|---|---|
| D1 | Acoustic Wave & Frequency | **Mapped** |
| D2 | Pulse & Signal Processing | **Mapped** |
| D3 | Sonar Equation & Propagation Loss | **Mapped** |
| D4 | Sound Speed & Refraction | **Mapped** |
| D5 | Transducer & Array Construction | **Mapped** |
| D6 | Beamforming & Electronic Steering | **Mapped** |
| D7 | Echosounders — SBES vs MBES | Pending |
| D8 | Bottom Detection | Pending |
| D9 | Multisector MBES | Pending |
| D10 | Vessel & Sensor Configuration | Pending |
| D11 | Vessel Motion | Pending |
| D12 | PU & Sensor Integration | Pending |
| D13 | Timing, Synchronization & Latency | Pending |
| D14 | Sounding Formation | Pending |
| D15 | Survey Planning | Pending |
| D16 | Survey Coverage & Acquisition Trade-offs | Pending |
| D17 | Uncertainty / TPU | Pending |

The old standalone `Acoustic Detection Fundamentals` lesson is retired. Its SNR/detectability objective is carried by D3; threshold-driven bottom detection belongs to D8.

---

# D1 — Acoustic Wave & Frequency

**Decision:** `KEEP + REFINE`  
**Current:** `web/pedagogical-explorer/src/WaveLab.tsx`

## Purpose
Build the minimum wave intuition reused later.

**Dominant discovery**
```text
frequency ↑ -> period ↓
frequency ↑ at fixed c -> wavelength ↓
```

## Inputs
Primary: **frequency `f`**.  
Secondary: normalized amplitude, initial phase, sound speed `c`.

Period and wavelength are derived outputs, never independent controls.

## Outputs
- `p(t)` on fixed time scale;
- `p(x)` on fixed/shared distance scale;
- period `T=1/f`;
- wavelength `λ=c/f`;
- wavelength/cycle markers;
- optional current/baseline overlay on identical axes.

## Interaction
Change frequency first; plots and derived values respond immediately. Then use amplitude/phase to distinguish magnitude/phase from frequency. Reveal sound speed only as a secondary `λ=c/f` experiment.

## Forward intuition
`frequency -> wavelength`, reused for absorption/range (D3), array/beamwidth (D5) and acquisition trade-offs (D16).

## Guardrails
No propagation loss, sonar equation, transducer response or bottom detection. Normalized amplitude is not source level/power. Conceptual wave graphics are not a general wavefield solver.

## Implementation delta
Keep current WaveLab/API. Replace adaptive spatial x-domain with fixed/shared domain; make frequency dominant; retain fixed amplitude axis and period/wavelength outputs.

## References
- IHO S-5A Ed. 2.0.0, H2.1 underwater acoustics: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- MIT OCW 2.682 Acoustical Oceanography: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>

---

# D2 — Pulse & Signal Processing

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/SignalLab.tsx`

## Purpose
Move from continuous-wave intuition to finite sonar transmissions: CW pulses and FM/LFM chirps. Build intuition for pulse duration, bandwidth, signal energy, matched filtering and range resolution.

**Dominant discovery**
```text
CW: longer pulse -> more energy but poorer raw range resolution
LFM: long pulse + bandwidth + matched filter -> energetic transmission + compressed response
bandwidth ↑ -> compressed response narrows -> range resolution improves
```

## Inputs
Primary: pulse type CW/LFM, pulse duration `τ`, LFM bandwidth `B`, centre frequency `fc`.  
Secondary: chirp direction; envelope/window only when its sidelobe consequence is visible.

## Outputs
- finite TX waveform;
- instantaneous frequency vs time;
- matched-filter/pulse-compressed response;
- visible duration and bandwidth extents;
- Scientific-Core-derived range resolution;
- relative pulse-energy indicator at fixed normalized amplitude;
- optional ideal delayed-return timeline before filtering.

## Interaction
Start with short CW; increase `τ`. Switch to LFM. Increase `τ` at fixed `B`, then increase `B`; compare on fixed/shared axes. Advanced chirp/window controls follow only after the main relationship is clear.

## Operational intuition
- `τ ↑`: more energy; longer TX occupancy; CW range resolution worsens.
- `B ↑`: narrower compressed response / better range resolution, subject to system bandwidth and processing.
- CW→LFM: permits longer energetic transmission with pulse compression.
- frequency consequences on propagation and array geometry are deferred to D3/D5.

## Guardrails
Do not teach `pulse length = actual minimum range`, pulse length as sole ping-rate determinant, or centre frequency alone as range resolution. Threshold/detection belongs to D8. Do not duplicate D3 propagation/noise physics merely to decorate the return.

## Implementation delta
Retain existing CW/LFM, frequency, duration, bandwidth, direction, envelope, waveform, instantaneous-frequency and matched-filter elements. Add explicit range-resolution and relative-energy/occupancy outputs; use fixed/shared comparison domains; add delayed-return bridge only if scientifically simple.

## References
- IHO S-5A Ed. 2.0.0, H2.1/H2.2: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- Schock, LeBlanc & Mayer (2000), *The Development of Chirp Sonar Technology and Its Applications*: <https://scholars.unh.edu/ccom/541/>
- Hughes Clarke (2017), *Multibeam Echosounders*: <https://scholars.unh.edu/ccom/1370/>
- Kongsberg EM 2040 MkII: <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>

---

# D3 — Sonar Equation & Propagation Loss

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/SonarEquationLab.tsx`

## Purpose
Build acoustic-budget intuition: the transmitted signal must survive two-way propagation and bottom interaction and remain sufficiently above noise to support detection.

**Dominant discovery**
```text
source level ↑ -> received level / SNR margin ↑
range ↑ -> two-way transmission loss ↑ -> received level / SNR ↓
frequency ↑ -> generally absorption ↑ -> long-range margin ↓
noise ↑ -> SNR ↓ while received signal level is unchanged
```

## Inputs
Primary: range `R`, source level `SL`, frequency `f`, noise level `NL`.  
Secondary: controlled bottom-return term; model-specific absorption environment; required/reference SNR. `% power` is allowed only through a documented system model mapping it to source level.

## Outputs
- RL vs range and SNR vs range on fixed scales;
- shared selected-range marker;
- two-way TL separated into spreading and absorption;
- `SL -> TL -> bottom return -> TL -> RL -> NL -> SNR` contribution budget;
- explicit positive/negative detection margin relative to a clearly labeled SNR reference;
- same-scale frequency comparison.

## Interaction
Increase range first; then independently vary SL and NL so the learner sees that SL changes RL/SNR while NL changes only SNR. Compare two frequencies at fixed geometry/environment. Optionally vary bottom-return strength.

## Operational intuition
Power/SL can recover SNR/range but does not intrinsically improve resolution. Longer/slanted ranges cost SNR. Higher hydrographic frequencies generally sacrifice range through higher absorption. Noise reduces detectability without changing propagation loss.

## Guardrails
Use registered absorption/spreading models and correct one-/two-way conventions. D3's SNR reference is not D8's bottom detector. Do not turn simplified bottom response into a backscatter module or teach frequency as a single-variable resolution rule.

## Implementation delta
Retain current fixed RL/SNR axes, range marker and frequency comparison. Separate spreading/absorption, add detection margin, make range the first experiment and reduce raw-card emphasis. Bottom scattering and beam gains remain fixed by default.

## References
- IHO S-5A Ed. 2.0.0, H2.1b–d: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- MIT OCW 2.682 Acoustical Oceanography: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- Hughes Clarke (2017), *Multibeam Echosounders*: <https://scholars.unh.edu/ccom/1370/>
- Schmidt, Weber & Lurton (2012), *Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems*: <https://scholars.unh.edu/ccom/848/>

---

# D4 — Sound Speed & Refraction

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/RefractionLab.tsx`

## Purpose
Build intuition for **why the water-column sound-speed profile matters to sounding position**. Connect profile/gradient to ray bending, then connect a wrong/stale processing profile to systematic spatial error in reconstructed soundings.

**Dominant discovery**
```text
sound-speed gradient -> refraction -> acoustic path changes
wrong processing SVP -> wrong reconstructed ray -> sounding endpoint error
same SVP mismatch -> error generally grows with obliquity / outer-swath geometry
```

## Inputs
Primary:
- launch/beam angle from vertical;
- reference/Truth sound-speed profile;
- Processing sound-speed profile, matched by default then deliberately mismatched.

Secondary: layer/gradient parameters, target depth, profile presets. Surface/transducer sound speed appears only in a clearly separated experiment because its steering role differs from the water-column SVP role.

## Outputs
- explicit `c(z)` plot;
- Truth/reference and Processing/reconstructed rays on same fixed geometry;
- visible bottom/target;
- reference and reconstructed endpoints;
- error vector with `Δx`, `Δz`;
- supporting travel time/path values;
- recommended error-vs-angle curve or small swath fan from the same Scientific Core.

## Interaction
Start constant; vary angle. Introduce a gradient; vary it while geometry stays fixed. Then compare identical Truth/Processing profiles, deliberately mismatch Processing only, and increase beam angle to expose how endpoint error evolves. Reset to matched profiles.

## Operational intuition
Representative SVP supports faithful reconstruction; stale/sparse sampling can generate coherent refraction errors, often more evident toward outer swath. Wider angular coverage gains area but generally increases sensitivity to propagation/profile error. Surface sound speed measurement does not replace the water-column profile.

## Guardrails
Use the registered ray tracer and sign/angle convention. Never let Processing SVP modify Truth propagation. Do not state a universal `Δx/Δz` sign without specified geometry/model. Layered profiles are pedagogical simplifications. Do not expand into physical oceanography or formal uncertainty propagation.

## Implementation delta
Retain current scenario progression and endpoint-error comparison. Add `c(z)` plot and bottom reference; preserve fixed geometry and explicit Truth/Processing semantics; add optional error-vs-angle view; reduce prominence of ray-parameter/per-layer diagnostics.

## References
- IHO S-5A Ed. 2.0.0, H2.1e: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- MIT OCW 2.682 Acoustical Oceanography: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- Beaudoin (2010), *Real-time Monitoring of Uncertainty due to Refraction in Multibeam Echo Sounding*: <https://scholars.unh.edu/ccom/1050/>
- Beaudoin, Calder, Hiebert & Imahori (2009), *Estimation of Sounding Uncertainty from Measurements of Water Mass Variability*: <https://scholars.unh.edu/ccom/481/>
- Beaudoin, Hughes Clarke & Bartlett (2004), *Application of surface sound speed measurements in post-processing for multi-sector multibeam echosounders*: <https://scholars.unh.edu/ccom/1335/>

---

# D5 — Transducer & Array Construction

**Decision:** `KEEP + REFINE + MOVE`  
**Current:** `web/pedagogical-explorer/src/ArrayDirectivityLab.tsx`

## Purpose
Build physical intuition for how **wavelength, aperture, number/spacing of elements and aperture weighting create directivity**. The learner should understand that narrow MBES beams do not come from an abstract software setting: they arise from coherent radiation/reception by a finite array.

**Dominant discovery**
```text
larger aperture in wavelengths -> narrower main lobe
frequency ↑ at fixed physical aperture -> aperture/λ ↑ -> narrower beam
poor / excessive element spacing -> unwanted lobes / ambiguous angular response
aperture weighting -> lower sidelobes ↔ broader main lobe / reduced effective gain
```

The lab succeeds when the learner can inspect a physical array and predict the qualitative beam-pattern consequence before changing it.

## Inputs

### Primary
- **frequency `f`** (reuses D1 wavelength intuition);
- **element count `N`**;
- **element spacing `d`**;
- or, preferably as an alternate construction mode, **physical aperture `L`** with `N`/`d` visibly derived so the learner can reason in both metres and wavelengths.

### Secondary / advanced
- element face/element factor;
- aperture weighting/shading (`uniform` vs one registered taper such as Hann);
- rectangular 2-D array dimensions;
- Mills Cross architecture as a named advanced construction example.

### Move out of the core D5 interaction
- TX↔RX eccentricity/lever-arm controls (`rxX`, `rxY`, `rxZ`) belong to **D10 Vessel & Sensor Configuration**. D5 may show TX/RX arrays spatially separated only as a fixed schematic when explaining Mills Cross; do not make installation offsets an array-directivity control.
- steering/delay/phase belongs to **D6 Beamforming & Electronic Steering**.

## Expected outputs / visual response

Required:
- physical element layout on a **fixed spatial scale**;
- wavelength `λ` and spacing explicitly shown both as distance and `d/λ`;
- physical/effective aperture shown as distance and `L/λ`;
- one-way angular response on a fixed dB/angle scale;
- main-lobe peak and **−3 dB beamwidth**;
- sidelobes visibly identified; if a grating lobe exists within the visible field, make it unmistakable rather than merely another peak;
- optional separate `element factor`, `array factor`, and combined response, but combined response is the principal learner view.

Recommended:
- a compact far-field polar view synchronized with the Cartesian dB plot;
- baseline/current overlay when changing one variable;
- 2-D footprint/directivity preview only as a bridge to D7; full seafloor footprint belongs later.

## Interaction contract

1. Start with a **simple uniform linear array** at fixed sound speed and broadside, with sensible spacing near `λ/2`.
2. Increase element count while holding spacing/frequency fixed: physical aperture grows and the main lobe narrows.
3. Reset. Increase frequency while physical geometry stays fixed: `λ` shrinks, `L/λ` grows and directivity changes. This explicitly reuses D1.
4. Reset. Increase element spacing through the scientifically valid range until the response develops unwanted/grating lobes; keep the same angle/dB axes.
5. Return to a valid spacing and compare **uniform vs tapered weighting**: sidelobes fall while the main lobe broadens / effective sensitivity changes. This is the principal trade-off experiment.
6. Only after the 1-D concept is understood, expose rectangular-array and Mills-Cross construction as advanced views. Do not require the learner to understand steering here.

## Operational intuition / trade-offs

| Design / condition | Gain | Cost / risk to retain |
|---|---|---|
| Larger aperture | narrower angular response; potentially smaller projected footprint / better angular discrimination | larger physical transducer; installation constraints |
| Higher frequency with same geometry | smaller `λ`, therefore larger aperture in wavelengths and typically narrower beam | propagation range is reduced by absorption (D3); frequency is not a free resolution control |
| More elements at fixed spacing | larger aperture and narrower beam | greater hardware/channel complexity; do not imply element count alone matters independently of aperture |
| Larger spacing | can increase aperture for fixed `N` | excessive spacing permits grating/ambiguous lobes; exact condition depends on steering and model |
| Stronger aperture taper/shading | lower sidelobes; less response to off-axis energy | broader main lobe and changed array gain/effective aperture |
| Narrow beam | better angular discrimination / smaller footprint at a given range | actual seafloor resolution still depends on range, pulse bandwidth, geometry, beam spacing and detection; defer integrated resolution to D7/D16 |

Desired operator intuition: **“beamwidth and sidelobes are consequences of physical/acoustic array design. Frequency, aperture and weighting interact; a narrow nominal beam is not an isolated software parameter.”**

## Scope boundaries / scientific guardrails

- D5 is **array construction/directivity**, not D6 steering. Keep the default beam at broadside; no learner-controlled phase/delay steering in the core sequence.
- Use Scientific-Core element factor, array factor and weighting definitions. UI must not draw a decorative beam independent of computed response.
- Grating-lobe statements must respect actual `d/λ`, scan/steering angle and the registered array model. Do not teach a universal threshold detached from steering conditions; broadside `λ/2` is a safe pedagogical starting point, not the only physically valid spacing.
- `beamwidth ≈ λ/L` is useful intuition, not a universal exact formula. Display exact/core-derived −3 dB beamwidth.
- Distinguish one-way TX/RX directivity from two-way combined sonar response. D5 should label exactly which pattern is plotted.
- Do not equate narrow beam directly with final bathymetric resolution. Hughes Clarke shows practical resolution also depends on pulse bandwidth, projected beam widths/spacing, stabilization and platform altitude.
- Element face size may affect the element factor but should remain secondary unless its consequence is visible.
- Piezoelectric material/device physics may be mentioned as context but should not expand D5 into transducer electrical design.
- Mills Cross explains orthogonal TX/RX apertures; its installation geometry/lever arms are deferred to D10.

## Dependencies / concepts passed forward

Consumes:
- D1: `λ=c/f` and frequency/wavelength intuition;
- D3: frequency has a propagation-range cost, preventing “higher frequency is always better” reasoning.

Passes forward:
- `array geometry -> directivity -> beamwidth/sidelobes` to D6 Beamforming & Steering;
- TX/RX array roles and Mills Cross concept to D7 SBES vs MBES and D9 Multisector MBES;
- beamwidth as one contributor to seafloor footprint/spatial resolution in D7/D16;
- shading trade-off to D6/D9;
- array/directivity contribution to acoustic gain/SNR when later integrated with D3.

## Current implementation delta

`ArrayDirectivityLab.tsx` already exposes linear/rectangular/Mills modes, frequency, sound speed, element count/spacing/face size, uniform/Hann weighting, physical layout, wavelength, aperture, beamwidth, element factor, array factor and combined pattern. This is a strong scientific base.

Next-version changes:
- **make linear array the dominant guided experience**; hide rectangular/Mills under advanced progression;
- expose `d/λ` and `L/λ` directly next to the physical dimensions;
- keep array geometry and directivity plots on fixed/shared scales so aperture/frequency comparisons remain perceptible;
- explicitly classify/label main lobe, sidelobes and grating lobes from Scientific-Core results;
- add baseline/current overlay for one-control experiments if simple;
- retain weighting comparison but show the main-lobe-width ↔ sidelobe suppression trade-off explicitly;
- **remove interactive TX↔RX eccentricity (`rxX/rxY/rxZ`) from D5** and transfer that concept to D10 Vessel & Sensor Configuration;
- avoid presenting rectangular-array weighting as arbitrarily disabled unless that restriction is scientific/model-driven; either support the registered model or state the scope;
- preserve `element factor -> array factor -> combined pattern`, but make the combined response visually primary and the factor decomposition explanatory.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2.1a and H2.4a** — transducer-array design, beam characteristics, sidelobes, TX/RX arrays, aperture size and element spacing: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OCW 2.682 Acoustical Oceanography, Lecture 11** — simple line-array beamformer and grating-lobe equation: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/resources/mit2_682s12_lec11/>
- **Hughes Clarke (2017), “Multibeam Echosounders”**: <https://scholars.unh.edu/ccom/1370/>
- **de Moustier, Kraft & McGillicuddy (2008), “Multibeam Sonar Calibration Techniques”**: <https://scholars.unh.edu/ccom/610/>
- **Lanzoni & Weber (2010), “High Resolution Calibration of a Multibeam Echo Sounder”**: <https://scholars.unh.edu/ccom/789/>
- **Kongsberg EM 2040 MkII**: <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>

---

# D6 — Beamforming & Electronic Steering

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/BeamformingLab.tsx`

## Purpose
Build first-principles intuition for **how an array forms and electronically points a beam by compensating relative arrival/transmission timing or phase across fixed elements**, then show that steering away from broadside changes usable array response and can introduce penalties.

**Dominant discovery**
```text
oblique wavefront -> different arrival time / phase at each element
matched relative delay / phase -> channels align -> coherent sum increases
change delay gradient -> beam direction changes without moving the array
larger steering angle -> usable response generally degrades / beam geometry changes
```

The learner should finish able to predict which channel needs relatively more/less delay for a chosen arrival direction and understand steering as **electronic compensation**, not physical rotation of the transducer.

## Inputs

### Primary
- **arrival/source angle `θsource`** for RX experiment;
- **steering angle `θsteer`** or equivalent relative-delay gradient;
- **RX / TX view** only after the receive-side mechanism is understood.

The array geometry, frequency and sound speed should remain fixed in the core experiment so the learner isolates beamforming from D5 array construction.

### Secondary / advanced
- delay-gradient versus angle control mode;
- aperture weighting/apodization, reusing D5 only when its steering consequence is shown;
- frequency for a narrowband phase-steering comparison, only if the Scientific Core explicitly distinguishes phase steering from true time-delay steering;
- near-field/dynamic focusing as an advanced concept, not a primary control.

## Expected outputs / visual response

Required:
- fixed physical array and incoming wavefront/arrival direction;
- per-channel **relative arrival offset**;
- per-channel **applied compensation delay/phase**;
- residual timing/phase after compensation;
- aligned/misaligned channel representation before summation;
- coherent-sum magnitude or normalized response at the tested direction;
- one-way array/physical beam pattern on a fixed angle scale;
- requested/effective steering direction and actual beam peak;
- −3 dB beamwidth where defined;
- explicit warning/markers for grating/ambiguous lobes when the registered model predicts them.

Recommended:
- baseline broadside pattern overlaid with current steered pattern;
- a simple seafloor/target bridge showing that larger steering angle also implies more oblique look/slant range, without duplicating D7 footprint geometry;
- a compact **steering penalty** indicator derived from the Scientific Core (for example relative peak response/gain versus broadside), rather than a generic warning.

## Interaction contract

1. **RX broadside baseline:** set source=0°, steer=0°. All arrival offsets/compensation offsets are zero or symmetric by convention; channels sum coherently.
2. Move **source angle only** while keeping steering at 0°. Arrival offsets appear across the fixed array; residuals grow and coherent response at that direction falls.
3. Set **steering angle equal to source angle**. Applied counter-delays cancel relative arrival offsets; channels realign and coherent response returns toward the modelled steered maximum. This is the central discovery.
4. Move steering away from source. Residual timing/phase reappears and coherent sum decreases. The learner should be able to predict the sign/direction before moving the control.
5. Keep source matched to steering and progressively increase absolute steering angle. Overlay broadside/current patterns and expose modelled changes in peak response, beamwidth and sidelobes/grating behavior. This introduces the operational cost of large steering.
6. Only after RX is clear, switch to **TX** and show the reciprocal concept: programmed relative timing/phase causes constructive interference in a selected direction. Do not require a separate new mathematical model in the UI.
7. Advanced: compare angle control with equivalent relative-delay gradient. Phase-only versus true-time-delay and dynamic focusing are optional only when explicitly supported and pedagogically visible.

## Operational intuition / trade-offs

| Control / condition | Gain | Cost / risk to retain |
|---|---|---|
| Steering away from broadside | directs TX/RX sensitivity to off-nadir portions of the swath without rotating hardware | effective aperture/element response and gain can degrade; beam shape/sidelobes can change; slant range and projected footprint grow later in D7 |
| Correct RX compensation for arrival angle | coherent channel summation and strong directional response | requires correct geometry/timing and steering convention |
| Steering mismatch | none | residual phase/timing lowers coherent response and can weaken detection margin |
| True time delay | steering relationship can remain valid over broader bandwidth | implementation complexity; do not conflate with narrowband phase shifts |
| Phase steering at one frequency | simpler narrowband representation | phase settings are frequency-dependent; not broadband-equivalent to time delay |
| Stronger apodization | can suppress sidelobes | broadens main lobe / changes effective gain, as already established in D5 |

Desired operator intuition: **“steering lets the system look away from broadside electronically, but outer beams are not free: the array response and later the seafloor geometry become less favorable as steering/obliquity increases.”**

## Scope boundaries / scientific guardrails

- D6 explains **beam formation/steering**, not physical array design (D5), footprint/swath geometry (D7), multisector sequencing (D9), or motion stabilization (D11).
- Use the Scientific Core for delay, phase, coherent sum, array factor, physical element response, beam peak, beamwidth and aliasing/grating-lobe conditions. UI must not infer steering penalties from angle alone if the core does not compute them.
- Follow the registered sign convention for port/starboard, element indexing, delay sign and reference channel. Never teach a universal “left channel delayed first” statement without that convention.
- MIT distinguishes **time-delay beamforming**, which can support broadband signals, from fixed phase-shift beamforming, which is inherently frequency-specific. Do not present the two as interchangeable across bandwidth.
- A steered beam is not guaranteed to have exactly the broadside shape. MIT's simple derivation uses that as an approximation; the HydroSIM physical beam should show the actual registered element × array response.
- Grating-lobe behavior depends on `d/λ`, steering and scan geometry; reuse D5's scientifically computed conditions.
- Do not claim steering intrinsically changes pulse/range resolution. Its dominant penalties are directional response and later projected spatial geometry/SNR consequences.
- “Dynamic focusing” is not required for the core D6 learning objective. Keep it advanced until the Scientific Core can show a distinct, validated consequence.

## Dependencies / concepts passed forward

Consumes:
- D1: frequency, wavelength and phase;
- D5: element spacing, aperture, array factor, beamwidth, sidelobes and grating lobes.

Passes forward:
- electronic TX/RX beam direction to D7 SBES vs MBES geometry;
- steering angle and steering penalty to D7 footprint/outer-beam resolution and D16 trade-offs;
- TX/RX directional formation to D8 bottom detection;
- sector-specific TX steering to D9 multisector MBES;
- stabilization as time-varying steering correction to D11 Vessel Motion;
- coherent-response consequences to D3/D16 SNR intuition.

## Current implementation delta

`BeamformingLab.tsx` already has a scientifically useful causal chain: fixed six-element array; RX/TX view; steering by angle or delay gradient; source angle; per-channel arrival offsets, compensation delays and residuals; coherent sum; physical beam and array factor; peak angle; −3 dB beamwidth; aliasing regime and grating-lobe angles.

Next-version changes:
- preserve the **fixed array**: D6 should not reopen D5 geometry controls in the primary experience;
- make the guided order explicit: `source moves -> residual appears -> steer to source -> residual closes -> coherent sum recovers`;
- visualize the incoming wavefront/channel alignment more strongly than numeric tables alone;
- make **RX the default first experience**; TX follows as reciprocal application;
- add broadside/current beam-pattern overlay and a Scientific-Core-derived steering-loss/relative-peak indicator if available;
- show beam response on a dB scale or another representation that makes sidelobe/steering degradation perceptible; normalized linear power alone can hide penalties;
- keep angle and delay-gradient modes, but treat delay-gradient as the explanatory/advanced representation after steering-by-angle intuition;
- retain aliasing/grating diagnostics, but do not let them dominate the normal valid-spacing experiment;
- remove or defer dynamic focusing unless a distinct validated near-field interaction exists;
- add only a lightweight bridge to oblique slant range/footprint; the full geometric consequence belongs to D7.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2.4** — multibeam transducers/arrays, beam characteristics, beam steering and hydrographic use: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OCW 2.682 Acoustical Oceanography, Lecture 11 Notes — Simple Beamformer Equations** — plane-wave arrival offset across a line array, electronic counter-delay/time-delay beamforming, phase beamforming, focused beamforming and grating-lobe equation: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/resources/mit2_682s12_lec11/>
- **Hughes Clarke (2017), “Multibeam Echosounders”** — integrated interpretation of projected beamwidth, beam spacing, stabilization and bathymetric resolution: <https://scholars.unh.edu/ccom/1370/>
- **de Moustier, Kraft & McGillicuddy (2008), “Multibeam Sonar Calibration Techniques”** — evaluates beamforming gain over steering angles in a multibeam context: <https://scholars.unh.edu/ccom/610/>
- **Kongsberg EM 304 official documentation** — operational evidence of transmit beam steering stabilized for roll/pitch/yaw and receive beam steering stabilized for roll; shows steering is an active MBES mechanism rather than a purely theoretical array topic: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/427620_em304_installation_manual_en.pdf>
- **Kongsberg ME70 official product description** — configurable beam directions/opening angles within explicit steering limits, demonstrating real-system steering constraints: <https://www.kongsberg.com/what-we-do/ocean-space/ocean-science/me70/>

---

## 4. Review queue

Continue **D7 -> D17**. For each lab record:
1. purpose + dominant discovery;
2. primary/secondary inputs;
3. outputs/visual response;
4. interaction sequence;
5. operational intuition and trade-offs;
6. scientific guardrails;
7. dependencies/forward reuse;
8. implementation delta (`KEEP`, `REFINE`, `MERGE / MOVE`, `ADD EXPERIENCE`);
9. exact recognized references.

A lab is mapped only when an implementation agent can identify **what the learner changes, what must visibly change, why, what intuition is retained, and where that intuition is reused in acquisition decisions**.