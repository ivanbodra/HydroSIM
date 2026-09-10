# HydroSIM Acoustic Lab — Pedagogical Specification

Status: **next-version development specification — iterative**  
Former name: **Didactic Module**  
Audience: AI/software/UX/science agents implementing the next HydroSIM version

This is the **canonical lab-by-lab pedagogical contract for the Acoustic Lab**. It complements the general framework and Scientific Registry; it does not redefine physics.

Related:
- [`didactic_module_pedagogical_framework.md`](didactic_module_pedagogical_framework.md) — general pedagogy (to be read as Acoustic Lab framework);
- [`pedagogical_reference_index.md`](pedagogical_reference_index.md) — source index;
- [`hydrosim_pedagogical_plan.md`](hydrosim_pedagogical_plan.md) — broader HydroSIM curriculum history;
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
| D5 | Transducer & Array Construction | Pending |
| D6 | Beamforming & Electronic Steering | Pending |
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
Keep current WaveLab/API. Replace adaptive spatial x-domain with a fixed/shared domain; make frequency dominant; retain fixed amplitude axis and period/wavelength outputs.

## References
- IHO S-5A Ed. 2.0.0, H2 acoustic foundations: <https://iho.int/standards-and-specifications>
- MIT OCW 2.682 Acoustical Oceanography: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/pages/lecture-notes/>

---

# D2 — Pulse & Signal Processing

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/SignalLab.tsx`

## Purpose
Move from continuous wave intuition to finite sonar transmissions: CW pulses and FM/LFM chirps. Build intuition for pulse duration, bandwidth, signal energy, matched filtering and range resolution.

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
- recommended: ideal delayed-return timeline before filtering.

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
Retain existing CW/LFM, frequency, duration, bandwidth, direction, envelope, waveform, instantaneous-frequency and matched-filter elements. Add explicit range-resolution and relative-energy/occupancy outputs; use fixed/shared comparison domains; add delayed-return bridge if it remains scientifically simple.

## References
- IHO S-5A Ed. 2.0.0, H2 acoustic systems: <https://iho.int/standards-and-specifications>
- Schock, LeBlanc & Mayer (2000), *The Development of Chirp Sonar Technology and Its Applications*: <https://scholars.unh.edu/ccom/541/>
- Hughes Clarke (2017), *Multibeam Echosounders*: <https://scholars.unh.edu/ccom/1370/>
- Kongsberg EM 2040 family: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040-Mk2/>

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
- IHO S-5A Ed. 2.0.0, H2 acoustic-system outcomes: <https://iho.int/standards-and-specifications>
- MIT OCW 2.682 Acoustical Oceanography: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- Hughes Clarke (2017), *Multibeam Echosounders*: <https://scholars.unh.edu/ccom/1370/>
- Schmidt, Weber & Lurton (2012), *Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems*: <https://scholars.unh.edu/ccom/848/>
- Kongsberg EM 2040 family: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040C-MkII/>

---

# D4 — Sound Speed & Refraction

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/RefractionLab.tsx`

## Purpose
Build hydrographic intuition for **why the water-column sound-speed profile matters to sounding position**. The learner should connect a profile/gradient to ray bending and then connect a wrong or stale processing profile to a systematic spatial error in reconstructed soundings.

**Dominant discovery**
```text
sound-speed gradient -> refraction -> acoustic path changes
wrong processing SVP -> wrong reconstructed ray -> sounding endpoint error
same SVP mismatch -> error generally grows with obliquity / outer-swath geometry
```

The lab is successful when the learner stops thinking of SVP as a correction file and starts thinking: **“the measured travel time and angle are converted into position through a propagation model; if my water-column model is wrong, my sounding moves.”**

## Inputs

### Primary
- **Launch / beam angle from vertical** — exposes angular sensitivity and prepares outer-swath reasoning.
- **Reference (Truth) sound-speed profile** — initially a simple 2–3 layer profile or gradient preset; later editable if needed.
- **Processing sound-speed profile** — matched to Truth by default, then deliberately offset/stale for comparison.

### Secondary / advanced
- layer-interface depth or gradient magnitude;
- target/bottom depth;
- selectable profile presets representing weak vs strong stratification;
- surface/transducer sound speed only in a clearly separated experiment that explains its distinct role in beam steering; do **not** silently conflate it with the water-column SVP.

Do not make temperature, salinity and pressure independent primary controls here. They are causes/measurement inputs to sound speed, not the acquisition intuition D4 is trying to teach.

## Expected outputs / visual response

Required:
- **sound-speed profile `c(z)`** plotted next to the water column;
- reference/Truth ray path and processing/reconstructed ray path on the **same fixed geometry**;
- visible bottom/target surface, not only an abstract target depth;
- reference and reconstructed endpoints;
- **endpoint error vector decomposed into `Δx` and `Δz`**;
- travel time and horizontal range/path outputs as supporting values;
- angle-at-layer / Snell-law response may be shown as a compact derived annotation, not the dominant output.

Recommended:
- a small **across-track error vs beam angle** curve or fan preview computed by the same Scientific Core. This is the bridge from a single ray to MBES intuition: near-nadir error may look small while outer beams diverge strongly.
- optional Truth-vs-processing swath endpoints over a flat seafloor, without yet introducing full beamforming or bottom detection.

## Interaction contract

1. **Constant profile:** vary launch angle; rays remain straight. Establish geometry/travel-time baseline.
2. **Reference gradient/layers:** introduce one sound-speed change. The ray bends according to the registered propagation model; keep axes fixed so the geometric difference is visible.
3. Vary the gradient/profile while holding launch angle and target depth fixed; learner predicts the direction/magnitude trend before moving the control.
4. Switch to **Truth vs Processing**. Begin with identical profiles so endpoints coincide.
5. Offset the processing lower layer/profile while Truth remains fixed. Show the reconstructed path and endpoint separating immediately.
6. Increase beam angle while keeping the same profile mismatch. Show how the endpoint error changes; if supported by the core, expose the full across-track error fan/curve.
7. Reset to matched Truth/Processing profiles.

The UI should make Truth and Processing unmistakable. Never let changing the processing profile also mutate the simulated Truth propagation.

## Operational intuition / trade-offs

| Condition / choice | Useful consequence | Cost / risk learner must understand |
|---|---|---|
| Representative/recent SVP | more faithful ray reconstruction and sounding position | requires adequate water-column sampling in space/time |
| Sparse/stale SVP sampling | less acquisition interruption/effort | may miss water-mass variability and create coherent refraction error, especially toward outer swath |
| Wider/steeper beam angle | wider coverage | increases sensitivity to refraction/profile error and later also incurs range/footprint/SNR penalties |
| Near-nadir geometry | often less sensitive to lateral refraction error | does not imply SVP is unimportant or that vertical/travel-time effects vanish |
| Surface/transducer SV measurement | supports correct sonar steering/angle handling in applicable MBES systems | is **not a substitute** for the water-column profile used for ray tracing |

The desired operator thought is: **“outer-swath disagreement may be a water-column/refraction problem; before changing power or detector settings, check whether the SVP represents the water through which the sound propagated.”**

## Scope boundaries / scientific guardrails

- D4 teaches **geometric-acoustic ray tracing**, not a full finite-wavefield solver. Label the visualization accordingly.
- Use the Scientific Core's registered ray tracer and documented angle/sign convention. The UI must not implement its own Snell-law shortcut.
- Separate **Truth/reference propagation** from **processing/reconstruction propagation**. Wrong processing SVP must not alter simulated Truth travel time/path.
- Do not claim a universal sign for `Δx`/`Δz` from “SV too high/low” without specifying profile, geometry, convention and reconstruction method. Let the Scientific Core show the result.
- Layered/constant-gradient models are pedagogical simplifications. Do not imply the ocean is piecewise constant because the teaching visualization is.
- Surface sound speed at the transducer and water-column SVP have different operational roles in multibeam systems. Preserve that distinction for D6/D9/D14.
- Do not expand D4 into physical oceanography, CTD instrumentation, water-mass classification or survey-planning optimization. Sampling strategy is previewed here and synthesized in D15/D16/D17.
- Refraction error contributes to uncertainty, but formal uncertainty propagation belongs to D17.

## Dependencies / concepts passed forward

Consumes:
- D1: sound speed and wavelength vocabulary;
- D3: longer/slanted paths are acoustically more demanding, though D4 focuses on geometry rather than SNR.

Passes forward:
- `SVP -> ray path -> range/angle reconstruction -> sounding position` to D14 Sounding Formation;
- `profile mismatch + beam angle -> outer-swath error` to D7/D9/D16/D17;
- distinction between **surface SV** and **water-column SVP** to beam steering/multisector/sounding-formation labs;
- operational diagnosis of coherent cross-track/refraction artifacts to the Acquisition Simulator.

## Current implementation delta

The current `RefractionLab.tsx` already has the correct scientific/pedagogical seed: constant, two-layer and wrong-processing-profile scenarios; launch angle; lower-layer and processing sound speeds; reference vs reconstructed ray; travel-time/path values; and explicit endpoint `Δx/Δz`.

Next-version changes:
- **retain** the three-step scenario progression and current endpoint-error comparison;
- add an explicit **`c(z)` profile plot** synchronized with the water-column geometry;
- draw a simple bottom/target reference so endpoint error is immediately recognizable as a sounding-position error;
- keep Truth/reference and Processing visually distinct and semantically fixed;
- add an optional **error-vs-angle / swath fan** using the same Scientific Core, because Beaudoin's hydrographic work shows that refraction uncertainty must be understood across the potential sounding space, not from one ray alone;
- reduce prominence of `ray parameter` and per-layer numeric strips; they are useful derived diagnostics but not primary learner outcomes;
- keep layer count small for the basic lab; progressive disclosure may later allow more realistic profiles/presets;
- preserve common/fixed geometry scales across comparisons so profile-error growth cannot be hidden by autoscaling.

## Recognized references

- **IHO S-5A, Ed. 2.0.0 (Aug 2026)** — current competence standard. H2 includes sound-speed profile/gradient, ray-tracing theory and an applied outcome to use an SVP to compute the sound-ray path: <https://iho.int/standards-and-specifications>
- **MIT OpenCourseWare 2.682 Acoustical Oceanography, James Lynch** — first-principles propagation/refraction foundation: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- **Beaudoin, J. (2010), “Real-time Monitoring of Uncertainty due to Refraction in Multibeam Echo Sounding”** — key pedagogical reference for showing refraction consequence across the potential sounding space and for linking profile-sampling regime to sounding uncertainty: <https://scholars.unh.edu/ccom/1050/>
- **Beaudoin, J.; Calder, B.R.; Hiebert, J.; Imahori, G. (2009), “Estimation of Sounding Uncertainty from Measurements of Water Mass Variability”** — connects water-mass variability/SVP representativeness to potential sounding uncertainty: <https://scholars.unh.edu/ccom/481/>
- **Hamilton, T.; Beaudoin, J. (2010), “Modeling the Effect of Oceanic Internal Waves on the Accuracy of Multibeam Echosounders”** — shows how spatial/temporal SV structure can create MBES error and interact with survey geometry: <https://scholars.unh.edu/ccom/784/>
- **Beaudoin, J.D.; Hughes Clarke, J.E.; Bartlett, J.E. (2004), “Application of surface sound speed measurements in post-processing for multi-sector multibeam echosounders”** — supports the required distinction between transducer/surface sound speed and water-column propagation information: <https://scholars.unh.edu/ccom/1335/>
- **Kongsberg EM 2040 instruction manual** — operational description: bottom detection supplies TWTT/angle; transducer-depth sound speed, water-column SVP and vessel attitude are then used to compute sounding coordinates, with refraction calculated using Snell's law through the SVP layers: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/346210_em2040_instruction_manual.pdf>
- **Kongsberg EM 2040C MkII official documentation** — confirms water-column sound-speed profile as a real-time correction input and the separate transducer sound-speed sensor context: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040C-MkII/>

---

## 4. Review queue

Continue D5 -> D17. For each lab record:
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