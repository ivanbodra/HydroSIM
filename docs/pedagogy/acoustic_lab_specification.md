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

- **IHO S-5A Ed. 2.0.0, H2.1a and H2.4a** — requires understanding transducer-array design, sidelobes, effect of transducer design on beam characteristics, side-lobe suppression, TX/RX array construction, and explicitly assessing **aperture size and element spacing on array performance**: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OCW 2.682 Acoustical Oceanography, Lecture 11** — simple line-array beamformer and grating-lobe equation; useful first-principles bridge from element spacing/wavelength to D6 steering: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/resources/mit2_682s12_lec11/>
- **Hughes Clarke (2017), “Multibeam Echosounders”** — practical bathymetric resolution depends on pulse bandwidth, projected beam widths/spacing, stabilization and altitude; use to prevent beamwidth-only resolution claims: <https://scholars.unh.edu/ccom/1370/>
- **de Moustier, Kraft & McGillicuddy (2008), “Multibeam Sonar Calibration Techniques”** — CCOM/UNH work explicitly relating physical element separation to acoustic wavelength and evaluating beamforming gain over steering angles: <https://scholars.unh.edu/ccom/610/>
- **Lanzoni & Weber (2010), “High Resolution Calibration of a Multibeam Echo Sounder”** — measured 3-D TX/RX beam patterns of a hydrographic MBES and provides empirical context for array directivity: <https://scholars.unh.edu/ccom/789/>
- **Kongsberg EM 2040 MkII official data** — real hydrographic example in which fixed transducer hardware exhibits different nominal beamwidths as operating frequency changes; useful validation that frequency/aperture interaction is operationally relevant: <https://www.kongsberg.com/globalassets/kongsberg/1.-what-we-do/2.-ocean-space/5.-seafloor-mapping/em-multibeams/em2040/em-2040---mkii-data-sheet.pdf>

---

## 4. Review queue

Continue **D6 -> D17**. For each lab record:
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