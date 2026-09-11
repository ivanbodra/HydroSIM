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

A recurring spatial chain must also be preserved across D5-D7:

```text
PHYSICAL ARRAY GEOMETRY
  -> 2-D / 3-D DIRECTIVITY
  -> BEAMFORMING
  -> STEERING / MULTIPLE RX LOOK DIRECTIONS
  -> TX × RX TWO-WAY RESPONSE
  -> SEAFLOOR FOOTPRINT / SAMPLING CELL
  -> SOUNDING / SWATH CONSEQUENCE
```

The learner must not leave with the impression that a beam is a 2-D decorative cone or that all MBES beams sample the bottom with the same geometry. Array dimensions in the vessel longitudinal and transverse axes create different beamwidths in orthogonal planes; TX and RX patterns have distinct roles; and each steered receive direction produces a different slant range, incidence geometry and projected footprint across the swath.

Rules:
- one dominant discovery per lab;
- few primary controls; secondary controls use progressive disclosure;
- deterministic immediate response;
- fixed/shared plot scales when autoscaling would hide the concept;
- mechanism before operational rule;
- show benefit and cost of tunable parameters;
- permit poor configurations when their consequence is useful;
- prefer connected 3-D geometry when a 2-D section would hide an essential mechanism;
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
| D7 | Echosounders — SBES vs MBES | **Mapped** |
| D8 | Bottom Detection | **Mapped** |
| D9 | Multisector MBES | **Mapped** |
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

**Decision:** `KEEP + REFINE + MOVE + ADD 2-D EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/ArrayDirectivityLab.tsx`

## Purpose
Build physical intuition for how **wavelength, aperture, element distribution and weighting in two physical axes create a three-dimensional directional response**. The learner must understand that a sonar beam has both along-track and across-track beamwidths and that each is rooted in the corresponding physical/effective aperture.

**Dominant discovery**
```text
larger aperture in one array axis -> narrower beam in that angular plane
frequency ↑ at fixed physical aperture -> aperture/λ ↑ -> beam narrows
longitudinal and transverse aperture can be different -> beam is anisotropic in 3-D
poor / excessive element spacing -> unwanted / ambiguous lobes
aperture weighting -> lower sidelobes ↔ broader main lobe / changed gain
```

The lab succeeds when the learner can inspect the element layout in plan view and qualitatively predict the beam shape in both orthogonal planes before changing a parameter.

## Inputs

### Primary — guided progression
1. **frequency `f`**;
2. **linear-array element count `N` and spacing `d`** for the first-principles 1-D experiment;
3. after that is understood, **longitudinal aperture `L_along`** and **transverse aperture `L_across`** or equivalent 2-D element counts/spacings.

Always expose the derived ratios `L_along/λ`, `L_across/λ`, `d_along/λ`, `d_across/λ` where applicable.

### Secondary / advanced
- element face / element factor;
- aperture weighting/shading;
- rectangular 2-D element grid;
- orthogonal TX/RX or Mills-Cross-like construction as a named architecture example.

### Move out of the core D5 interaction
- TX↔RX eccentricity/lever-arm controls belong to **D10 Vessel & Sensor Configuration**;
- learner-controlled steering/delay/phase belongs to **D6**.

## Expected outputs / visual response

Required:
- element layout in plan view on a fixed spatial scale;
- explicit vessel **along-track** and **across-track** axes;
- wavelength and element spacing in metres and wavelengths;
- physical/effective aperture in both axes;
- synchronized directivity cuts in the along-track and across-track planes;
- 3-D or pseudo-3-D main-lobe visualization derived from the same Scientific Core;
- −3 dB beamwidth in both orthogonal planes;
- sidelobes/grating lobes identified from computed response.

Recommended:
- physically reshape the array while the 3-D beam reshapes immediately;
- baseline/current overlay for one-axis changes;
- simple conceptual bottom plane only to preview how an anisotropic beam can create an anisotropic footprint; full footprint belongs to D7.

## Interaction contract

1. Start with a simple broadside **linear array** and reproduce the established `aperture/λ -> beamwidth` intuition.
2. Introduce a **rectangular 2-D array** with independent along/across apertures.
3. Increase **longitudinal aperture only**: only the corresponding angular cut should narrow according to the Scientific Core. Keep the other aperture fixed.
4. Reset; increase **transverse aperture only** and observe the orthogonal change.
5. Make one aperture much larger than the other. The learner should see a beam that is narrow in one plane and broad in the other rather than a symmetric cone.
6. Change frequency while physical geometry remains fixed; both aperture-in-wavelength ratios change.
7. Change element spacing to expose sidelobe/grating-lobe consequences without losing the 2-D orientation.
8. Compare weighting only after aperture intuition is established.
9. Advanced: show orthogonal TX/RX arrays / Mills-Cross-like construction as preparation for D7, emphasizing complementary directional patterns rather than installation offsets.

## Operational intuition / trade-offs

| Design / condition | Gain | Cost / risk to retain |
|---|---|---|
| Larger aperture in one axis | narrower response in the associated angular plane | larger physical installation / array complexity |
| Unequal along/across apertures | intentionally different beamwidths in orthogonal planes | footprint becomes anisotropic; orientation matters |
| Higher frequency at same geometry | greater aperture in wavelengths; typically narrower beams | greater absorption / less range from D3 |
| More elements at fixed spacing | larger aperture if physical extent grows | hardware/channel complexity; `N` alone is not the causal variable |
| Larger spacing | larger physical aperture for fixed `N` | grating/ambiguous lobes depending on `d/λ` and steering |
| Stronger taper | lower sidelobes | broader main lobe / changed gain |

Desired operator intuition: **“the beam shape is a consequence of the physical array in both vessel axes. A long aperture in one direction makes the beam narrow in that plane; the other axis can remain broad. The MBES TX and RX patterns later exploit this deliberately.”**

## Scope boundaries / scientific guardrails

- D5 is array construction/directivity, not D6 steering.
- Use Scientific-Core element factor, array factor and weighting definitions. Do not draw an arbitrary 3-D cone disconnected from computed orthogonal responses.
- Preserve the distinction among **physical aperture**, **effective aperture**, **beamwidth** and **final seafloor resolution**.
- `beamwidth ≈ λ/L` is intuition, not a universal exact formula; display the core-derived response and −3 dB widths.
- The mapping between physical array axis and angular cut must follow the project coordinate/frame conventions. Avoid ambiguous “horizontal/vertical beamwidth” labels when along/across is intended.
- A typical MBES may use complementary TX/RX apertures, often yielding a TX pattern narrow along-track and broad across-track and RX beams narrow across-track, but this is an architecture pattern, not a universal geometry for every sonar.
- Distinguish one-way TX/RX directivity from the two-way combined response used in D7.
- Mills Cross explains orthogonal apertures; installation lever arms remain D10.

## Dependencies / concepts passed forward

Consumes D1 wavelength and D3 frequency/range trade-off.  
Passes forward:
- `2-D array geometry -> 3-D directivity -> along/across beamwidth` to D6;
- distinct TX and RX directional patterns to D7;
- beamwidth/footprint contributors to D16;
- array gain/directivity context back into SNR reasoning.

## Current implementation delta

Retain the strong existing linear/rectangular/Mills scientific base. Next version must:
- keep the linear array as the first guided experiment;
- then make **independent along-track and across-track aperture** a required 2-D experiment;
- label the vessel axes unambiguously;
- synchronize plan-view element geometry, orthogonal beam cuts and a core-derived 3-D/pseudo-3-D response;
- expose `d/λ` and `L/λ` for each relevant axis;
- preserve fixed/shared angular and spatial scales;
- remove installation eccentricity from D5;
- prepare, but do not yet fully teach, the TX×RX combination used in D7.

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
Build first-principles intuition for **beamforming as coherent spatial combination** and **beam steering as the specific act of changing the formed beam's look direction electronically**. Then show how one physical RX array can form many simultaneous virtual receive directions from the same element-channel data.

**Dominant discovery**
```text
oblique wavefront -> different arrival time / phase at each element
beamforming: compensate + weight + sum channels -> directional sensitivity
beam steering: change the compensation pattern -> move that sensitivity direction
same RX element data + many delay/weight sets -> many simultaneous receive beams
```

The learner must not leave treating beamforming and beam steering as synonyms.

## Inputs

### Primary
- **arrival/source angle `θsource`**;
- **steering angle `θsteer`** or equivalent delay gradient;
- RX first, then TX reciprocal view.

Keep array geometry/frequency fixed in the core experiment so D6 isolates processing from D5 construction.

### Secondary / advanced
- delay-gradient vs angle control;
- aperture weighting;
- number of simultaneously demonstrated RX steering directions;
- phase-only vs true-time-delay comparison only if explicitly supported by the Scientific Core;
- near-field/dynamic focusing only as advanced validated material.

## Expected outputs / visual response

Required:
- fixed physical array and incoming wavefront;
- per-channel relative arrival offsets;
- applied compensation delays/phases and residuals;
- aligned/misaligned channel traces before summation;
- coherent summed response;
- actual directional beam pattern with requested/effective peak;
- broadside/current overlay and steering penalty where computed.

Required bridge to D7:
- a mode that takes the **same captured RX channel data** and shows several parallel beamforming paths, each using a different delay/weight set;
- each path yields a different virtual receive look direction;
- do not represent these as physically separate receivers.

## Interaction contract

1. RX broadside baseline: source=steer=0°.
2. Move source while steering remains fixed; arrival offsets and residuals appear, coherent response falls.
3. Steer to source; compensation closes the residuals and coherent sum recovers.
4. Mis-steer deliberately; learner predicts the loss before moving the control.
5. Increase steering magnitude while source follows it; show actual pattern/gain/beam-shape changes.
6. Duplicate the same RX channel snapshot into **multiple delay sets** and display several simultaneous virtual RX beams. This is the conceptual bridge to the MBES fan.
7. Only then show TX reciprocity: programmed relative timing/phase produces constructive radiation in a chosen direction.

## Operational intuition / trade-offs

| Control / condition | Gain | Cost / risk to retain |
|---|---|---|
| Beamforming | directional sensitivity / coherent array gain | depends on correct channel geometry/timing/weights |
| Steering | moves that directional sensitivity electronically | beam shape/gain/element response can degrade away from broadside |
| Multiple RX beamformers | many simultaneous look directions from one physical receive aperture | more processing; each direction has different seafloor geometry later |
| True time delay | broadband-consistent steering behavior | implementation complexity |
| Phase-only steering | simple narrowband representation | frequency dependent; not broadband-equivalent |
| Apodization | lower sidelobes | broader main lobe / changed gain |

Desired operator intuition: **“beamforming creates directional sensitivity from the array; steering tells that formed beam where to look. An MBES receiver can apply many steering solutions to the same element data and therefore observe many directions simultaneously.”**

## Scope boundaries / scientific guardrails

- Beamforming is broader than steering; keep the vocabulary explicit in UI and code.
- Multiple RX beams are separate processing outputs from shared physical channels, not separate physical transducers.
- Use the Scientific Core for delays, weights, coherent sum, array response, peak, beamwidth and grating-lobe behavior.
- Follow registered sign, port/starboard, element-index and delay conventions.
- Do not claim steering intrinsically changes range resolution.
- Do not yet compute the full seafloor footprint from decorative beam cones; that belongs to D7.

## Dependencies / concepts passed forward

Consumes D1 phase/wavelength and D5 2-D array/directivity.  
Passes forward:
- multiple virtual RX look directions to D7 MBES fan;
- steering penalties/outer-angle geometry to D7/D16;
- sector-specific steering to D9;
- stabilization as time-varying steering correction to D11.

## Current implementation delta

Preserve the existing causal chain and fixed array. Next version must:
- make `beamforming ≠ steering` explicit;
- make RX the first experience;
- strengthen wavefront/channel alignment visualization;
- add the **same channels -> multiple delay sets -> multiple RX beams** bridge;
- retain angle/delay-gradient modes and broadside/current pattern comparison;
- keep full footprint geometry in D7.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2.4** — multibeam arrays, beam characteristics and steering: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OCW 2.682 Acoustical Oceanography, Lecture 11** — time-delay/phase beamforming, focused beamforming and grating lobes: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/resources/mit2_682s12_lec11/>
- **Hughes Clarke (2017), “Multibeam Echosounders”**: <https://scholars.unh.edu/ccom/1370/>
- **de Moustier, Kraft & McGillicuddy (2008), “Multibeam Sonar Calibration Techniques”**: <https://scholars.unh.edu/ccom/610/>
- **Kongsberg EM 304 official documentation**: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/427620_em304_installation_manual_en.pdf>

---

# D7 — Echosounders: SBES vs MBES

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/EchosounderLab.tsx`

## Purpose
Turn D5/D6 into **actual MBES observation geometry**. The learner must understand that a characteristic multibeam fan is not simply a set of identical rays: a transmitted acoustic pulse insonifies a region, the receiver forms many look directions from one physical aperture, and each TX×RX combination has its own two-way directional response and projected seafloor footprint.

**Dominant discovery**
```text
TX pulse / TX directional pattern -> insonified sector
same RX array -> many simultaneous steered receive directions
TX response × RX response -> one two-way directional sampling cell per RX direction
many TX×RX cells -> MBES fan
beam angle changes across fan -> slant range + incidence + projected footprint change
```

The lab succeeds when the learner can select nadir, intermediate and outer beams and explain why they do **not** sample identical areas of seafloor.

## Inputs

### Primary
- system: SBES / MBES;
- depth / sonar-to-bottom separation;
- TX along-track and across-track beamwidths or a registered representative TX pattern;
- RX beamwidth and number of formed RX directions;
- MBES angular sector / steering limit;
- beam-spacing mode.

### Secondary / advanced
- pulse duration when the registered footprint model includes pulse-limited extent;
- bottom slope/incidence;
- frequency only through a physically linked transducer model, not as an isolated footprint knob.

## Expected outputs / visual response

Required views must be synchronized:

### A. Water-column / array view
- physical TX and RX apertures with vessel axes;
- one TX pulse / transmit directional envelope;
- multiple RX look directions generated from the same RX aperture;
- selected receive direction highlighted.

### B. Directional-response view for selected beam
- TX one-way directional response;
- selected RX one-way directional response;
- **combined two-way TX×RX response** computed by the Scientific Core under its defined amplitude/power convention;
- do not imply hard-edged geometric intersection when the model is a continuous directional response.

### C. Seafloor view
For every represented beam, and especially the selected one:
- beam centre / steering angle;
- slant range;
- incidence angle;
- along-track and across-track footprint dimensions or footprint polygon/ellipse from the registered model;
- sounding/detection location kept distinct from footprint area;
- top-down footprint field showing how shape and size vary across the fan.

The user must be able to compare **nadir vs intermediate vs outer beam** on the same physical scale.

## Interaction contract

1. Start with SBES and finite footprint; establish that even one beam samples an area, not a mathematical point.
2. Switch to MBES. Show a **single TX event** and multiple virtual RX directions simultaneously. The learner should recognize D6's `same RX channels -> many beamformers` mechanism.
3. Select the nadir RX beam. Show TX pattern, RX pattern and resulting two-way directional response; project its footprint on the bottom.
4. Select progressively more oblique RX beams **without changing the TX event**. Show steering, slant range, incidence and footprint changing.
5. Display the whole fan and footprint field. The learner should now see that the fan is a set of different TX×RX observation geometries, not copies of one beam shifted sideways.
6. Increase sector angle at fixed depth/beam count: coverage grows, but outer-beam geometry becomes more expensive.
7. Increase depth on fixed/shared axes: slant ranges and projected footprints grow.
8. Compare equiangular vs equidistant spacing while keeping the physical beam/footprint widths visible.
9. Increase beam count at fixed sector: centre spacing becomes denser, but the underlying physical TX/RX response does not automatically become narrower.
10. Advanced: alter pulse duration/beamwidth and let the Scientific Core identify beam-limited versus pulse-limited footprint contributions.

## Operational intuition / trade-offs

| Control / condition | Gain | Cost / risk to retain |
|---|---|---|
| Many RX beams | many simultaneous bottom look directions / swath coverage | each direction has different projection, slant range and incidence |
| Wider TX across-track insonified sector | more of the swath can be illuminated | energy/directivity and sector architecture constraints; not all systems use one identical TX sector |
| Narrow TX along-track response | smaller along-track sampling extent | requires adequate physical aperture/frequency; inherited from D5 |
| Narrow RX across-track response | finer directional discrimination across swath | array/steering/sidelobe trade-offs from D5/D6 |
| Wider angular sector | greater coverage | larger outer-beam slant range, footprint projection and generally less favorable detection geometry |
| Greater depth/range | larger covered width for same angles | larger projected footprints and spacing; less practical seafloor detail |
| More formed RX beams | denser directional sampling | does not independently reduce the physical resolution cell |
| Equidistant spacing | more uniform centre spacing over reference geometry | requires nonuniform angles and is terrain/model dependent |

Desired operator intuition: **“the MBES fan comes from one or more transmitted insonified sectors combined with many receive look directions. Each sounding has its own TX×RX geometry; nadir and outer beams therefore have different slant range, incidence and footprint.”**

## Scope boundaries / scientific guardrails

- **Do not model TX×RX as literal multiplication of two hard-edged polygons.** The Scientific Core must define the one-way patterns and two-way combination convention; visualization may show an intuitive overlap only when clearly labeled conceptual.
- Typical MBES architecture often uses a TX response narrow in the fore-aft plane and broad across-track plus RX responses narrow across-track, but actual transducer/sector architecture varies. Teach the mechanism, not one vendor geometry as universal.
- Multisector TX timing/frequency sequencing belongs to D9; D7 may state “one or more TX sectors” but use a single-sector case first.
- Keep beam centre, footprint and accepted bottom detection distinct. Detection mechanics belong to D8.
- Footprint depends on TX/RX beam shapes, slant range, incidence, pulse duration/bandwidth where applicable and bottom geometry. Do not collapse it to one generic constant ellipse.
- Outer beams do not intrinsically have worse **range resolution**; their projected spatial geometry, range, SNR and incidence are what usually become less favorable.
- Beam count/sounding density is not equivalent to independent acoustic resolution.
- Use 3-D or linked orthogonal views whenever a 2-D cross-section would hide the TX-along-track × RX-across-track mechanism.

## Dependencies / concepts passed forward

Consumes:
- D2 pulse duration/bandwidth;
- D3 range/SNR intuition;
- D5 2-D TX/RX aperture and directivity;
- D6 beamforming, steering and multiple virtual RX directions.

Passes forward:
- per-beam echo/footprint context to D8 Bottom Detection;
- sector architecture to D9 Multisector MBES;
- installation orientation to D10;
- stabilization consequence to D11;
- range + beam angle to D14 Sounding Formation;
- footprint/spacing/swath intuition to D15/D16;
- across-track geometry to D17 TPU.

## Current implementation delta

`EchosounderLab.tsx` already provides SBES/MBES, depth, beam count, angular sector, spacing mode, pulse duration, TX/RX beamwidths, beam endpoints/incidence, swath and footprint outputs. Next version must add the missing causal bridge:

- show **one TX pulse / TX response and many RX receive directions simultaneously**;
- connect the RX directions explicitly to D6's shared-array beamforming mechanism;
- for a selected beam, show `TX one-way -> RX one-way -> two-way combined response -> seafloor footprint`;
- make independent along/across footprint geometry visible;
- compare nadir/intermediate/outer footprints on a fixed physical scale;
- retain top-down footprint field and cross-section as synchronized views;
- make per-beam variation primary, not a single representative footprint;
- preserve core-derived footprint dimensions and clearly label any qualitative normalization.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2 hydrographic acoustics / echo sounding / multibeam competence** — SBES/MBES principles, transducer/beam geometry, footprint, spacing and acoustic tuning: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Hughes Clarke (2017), “Multibeam Echosounders”** — MBES beam/swath geometry and practical resolution dependence on pulse bandwidth, projected beamwidth, beam spacing, stabilization and altitude: <https://scholars.unh.edu/ccom/1370/>
- **UNB Ocean Mapping Group — Publications / Multibeam Sonar Theory class reports**: <https://www.omg.unb.ca/publications/>
- **Kongsberg EM beam-spacing technical note, “Sector Coverage / Beam Spacing Modes”**: <https://www.kongsberg.com/contentassets/058cd4fb2f1d417dab5f444f8f5cbf9a/em-sector-coverage-beam-spacing-modes.pdf>
- **Kongsberg EM 710 Mk2 product specification**: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/390849-em710mk2_product_specification.pdf>
- **Kongsberg EM 2040 MkII**: <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>

---

# D8 — Bottom Detection

**Decision:** `KEEP + REFINE + EXPAND PHASE-DETECTION EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/BottomDetectionLab.tsx`

## Purpose
Teach how an MBES turns the received acoustic return into one or more **bottom detections**. The learner must understand that the sonar does not receive a bathymetric point directly: it receives time-varying amplitude and, where coherent split-aperture information exists, differential phase. A detection algorithm interprets those observables and estimates one or more valid `(t, θ)` pairs that are passed downstream to sounding formation.

D8 deliberately separates two levels of processing:

```text
CONVENTIONAL DETECTION
  amplitude OR phase estimator
  -> one retained detection for that beam / direction
```

and

```text
ADVANCED INFORMATION EXPLOITATION
  richer phase / inter-beam structure
  -> additional valid (t, θ) detections
  -> denser / more complete seafloor representation
```

**Dominant discovery**
```text
physical return
  -> received amplitude + phase information
  -> is a usable phase ramp available?
  -> amplitude OR conventional phase estimator
  -> one retained conventional detection
  -> optional advanced exploitation of phase / inter-beam structure
  -> additional valid (t, θ) detections
  -> more complete bottom sampling
```

The lab succeeds when the learner can explain **why amplitude and conventional phase are alternative/competing estimators of the same conventional detection**, identify when phase information is or is not sufficiently defined, explain how a phase ramp can carry angular information beyond its zero crossing, and distinguish conventional phase, High Density/enhanced phase exploitation, BDI and PDI.

## Inputs

Inputs use progressive disclosure; the learner must not begin with the complete parameter wall.

### Primary — conventional bottom detection
- **scene / echo scenario** tied to physical geometry rather than only arbitrary traces: flat bottom, slope, weak return, noisy return, competing returns, small discontinuity, narrow/vertical target, good phase-ramp geometry and degraded phase-ramp geometry;
- **detection method**: `Amplitude` / `Phase`; later `Automatic / Combined` only if a validated Scientific-Core selection algorithm exists;
- **detection window / range gate**: start and end;
- **detection threshold / quality criterion**, with exact Scientific-Core semantics.

Amplitude and phase are initially treated as **alternative estimators of one conventional bottom detection**, not as two soundings to retain simultaneously merely because both produced candidates.

### Phase-specific
Reveal only after amplitude detection is understood:
- selected RX beam / steering direction;
- split-aperture geometry or baseline, normally fixed in the guided lesson;
- minimum phase-support / coherence / quality criterion from the Scientific Core;
- phase-ramp fit/support interval where the registered model uses one;
- frequency and sound speed only where required by the validated phase-to-angle mapping, preferably inherited rather than exposed as new primary controls.

### Advanced
After conventional amplitude/phase behavior is understood:
- `Conventional` / `Enhanced phase or High Density` / `BDI` / `PDI` comparison mode;
- single vs multiple retained detections where scientifically appropriate;
- optional integrated-detector view showing which method proposed each candidate and which detections were finally accepted.

TX delay is a timing reference/offset experiment, not the teaching centre of D8.

## Expected outputs / visual response

All principal views must be synchronized to the **same physical return**.

### A. Received amplitude / envelope
Show `A(t)` on a fixed time/range scale with:
- received or matched-filter magnitude;
- detection gate;
- threshold/quality criterion where meaningful;
- amplitude candidates;
- actual amplitude estimator used by the Scientific Core: peak, centroid, matched-filter maximum, etc.;
- conventional amplitude estimate `t_A`;
- accepted / rejected / false / missed state against pedagogical Truth.

The learner must be able to point to the signal and see **where the amplitude estimator put the detection**.

### B. Differential phase
Show split-aperture differential phase `Δφ(t)` on the same temporal support with:
- phase samples computed by the Scientific Core;
- usable/coherent support interval;
- visibly degraded or unsupported regions;
- phase ramp;
- fitted phase ramp where the registered estimator uses one;
- zero crossing or equivalent registered conventional phase estimator;
- conventional phase estimate `t_φ`;
- a visible phase-quality/support measure with defined scientific meaning.

If the phase ramp becomes insufficiently defined, the failure must be visible in the data. The UI must not merely disable the method without showing why.

### C. Phase -> physical angle
This output is required for the advanced lesson. For every valid phase sample used by the model, expose the Scientific-Core mapping:

```text
Δφ_i -> θ_i
```

and therefore:

```text
(t_i, Δφ_i) -> (t_i, θ_i)
```

The learner must see that the zero crossing is one particular use of the phase structure, while other valid parts of a sufficiently coherent ramp may carry direction information when a validated phase-to-angle relation exists.

### D. Conventional-method comparison
On the same echo and the same axes show:
- amplitude candidate `t_A`;
- phase candidate `t_φ` when valid;
- **one retained conventional detection** after the method/selection rule is applied.

Required visual logic:

```text
Amplitude candidate --\
                      > selection -> ONE conventional detection
Phase candidate ------/
```

Do not plot two final soundings merely because both estimators produced candidates.

### E. Seafloor / footprint view
Reuse D7 geometry without re-teaching footprint formation. Show:
- selected beam footprint / observation support;
- conventional retained detection;
- when enhanced phase is enabled, additional phase-supported `(t, θ)` detections projected inside the same physical observation support;
- footprint boundary kept visible so `more detections != more physical beams` and `more detections != smaller footprint` remain explicit.

### F. Beam × time matrix for advanced detection
Provide a matrix or equivalent water-column representation:
- horizontal axis: beam / angle;
- vertical axis: time / range;
- amplitude layer `A(beam,t)`;
- phase layer `Δφ(beam,t)` where available.

The same matrix must support two pedagogical cuts:

```text
fixed beam -> inspect time-series
```

and

```text
fixed time -> inspect angle-series
```

This is the required bridge to BDI/PDI.

### G. Downstream handoff
Every accepted result remains a detection candidate expressed as `(t, θ)` or equivalent Scientific-Core representation, with an explicit arrow:

```text
detection(s) -> TWTT + direction -> D14 Sounding Formation
```

D8 does not silently turn these detections into fully georeferenced soundings.

## Interaction contract

### Stage 1 — What is a bottom detection?
Start with one beam, one simple physical scene and one clear echo. Show the received information before activating an estimator. The learner must first confront the question: **where, in this return, is the bottom?**

### Stage 2 — Amplitude detection
Activate the amplitude estimator:

```text
A(t) -> amplitude estimator -> t_A -> one conventional detection
```

Move from a clean return to a slightly distorted/weak return so the learner sees that the estimated time is a processing result, not Truth itself. Then introduce gate and threshold.

### Stage 3 — False and missed detections
Use weak, competing and gated scenarios to create:
- true detection;
- false detection;
- missed detection.

The learner must distinguish **physical echo -> candidate -> eligible candidate -> retained detection**.

### Stage 4 — Conventional phase detection
On the same physical return show `A(t)` and `Δφ(t)` simultaneously. Highlight the coherent phase ramp and the conventional zero crossing / registered estimator:

```text
usable phase ramp -> zero crossing / fitted estimator -> t_φ
```

Compare `t_A` and `t_φ`, but retain only the solution selected by the conventional detector. The intended lesson is **Amplitude OR Phase -> one conventional detection**, not amplitude plus phase equals two soundings.

### Stage 5 — When phase works and when it does not
Provide at least one controlled scenario with a well-defined phase ramp and one in which coherence/support deteriorates.

Expected causal response:

```text
good coherent phase support
  -> stable phase ramp
  -> phase solution available
```

versus

```text
insufficient / noisy / decorrelated phase support
  -> unstable or absent usable ramp
  -> phase solution rejected / unavailable
  -> amplitude may still provide a conventional solution if its information is adequate
```

Do not encode a universal hard rule such as `nadir = amplitude` and `outer = phase`; the usable information and the registered detector determine availability/selection.

### Stage 6 — Reveal that the phase ramp contains more than the zero crossing
Freeze a good phase ramp. First show only its conventional zero-crossing use, producing one detection. Then reveal additional valid phase samples and their physical-angle mapping:

```text
Δφ_1 -> θ_1
Δφ_2 -> θ_2
Δφ_3 -> θ_3
...
```

so that:

```text
(t_1, θ_1), (t_2, θ_2), (t_3, θ_3), ...
```

can be projected onto the seafloor where the Scientific Core supports those solutions.

This is the conceptual transition from **using the phase ramp to choose one conventional point** to **using more of the phase information to recover additional valid directions from the same ping support**.

### Stage 7 — High Density / enhanced phase exploitation
Enable an advanced phase mode only after Stage 6 is understood. Compare, for the same pulse and receive-beam support:

```text
Conventional phase: one retained point
Enhanced / High Density: multiple validated phase-supported points
```

Show:
- ordinary detection count;
- enhanced detection count;
- angular and seafloor spacing;
- phase-support region;
- physical footprint boundary.

The learner must understand the mechanism as:

```text
usable phase structure
  -> phase-to-angle mapping
  -> additional (t, θ) solutions
  -> denser bottom sampling
```

not as `more beams` or an automatically smaller acoustic resolution cell.

### Stage 8 — BDI
Introduce the `beam × time` data field. Show that independent one-detection-per-beam processing does not exhaust the spatial structure of the received data. Use a scientifically registered BDI implementation/example to demonstrate how inter-beam structure can support additional or better-localized bottom interpretation.

The learner need not memorize implementation details; the retained concept is:

> information distributed across adjacent beams can contain bottom geometry that independent conventional picks do not fully express.

### Stage 9 — PDI / angle-series analysis
Use the same `beam × time` matrix and explicitly contrast:

```text
conventional / beam-centric:
fixed beam -> inspect signal through time
```

with:

```text
PDI / angle-series:
fixed time slice -> inspect amplitude + phase across beams / angles
```

For a selected time slice, show the candidate amplitude envelope across directions, the phase behavior across beams, and the phase zero crossing(s) or registered PDI criterion that produce angle estimates. Each accepted solution yields a `(t, θ)` pair.

Use scenes where this distinction is visible: narrow/vertical targets, discontinuities, small angular features or water-column returns. PDI is presented as an additional way to interrogate the same data, not as a universal replacement for conventional detection.

### Stage 10 — Integrated comparison on one Truth scene
Close D8 with one scene containing a smooth bottom plus at least one discontinuity or narrow/vertical feature. Run the same received dataset through:
- amplitude conventional detection;
- conventional phase detection where valid;
- enhanced phase / High Density;
- BDI;
- PDI.

Overlay each method's detections against optionally revealed Truth. The learner should see which structures each method recovers, misses or represents differently, and why a suitable integrated algorithm can increase detection density/completeness by exploiting the strengths of the available information.

The final visual message is:

```text
more usable information + appropriate processing
  -> more valid detections
  -> denser / more complete representation of the terrain
```

without implying that the physical beam or footprint itself became narrower.

## Operational intuition / trade-offs

| Method / control | Strength / gain | Limitation / risk to retain |
|---|---|---|
| Amplitude detection | provides a conventional solution from echo-energy structure even when usable phase information is absent | localization depends on echo shape, footprint and estimator; can be ambiguous or spatially averaged |
| Conventional phase detection | uses a coherent phase ramp to localize the detection in time/direction with high precision under suitable geometry | requires a minimally defined/coherent phase ramp, adequate support/SNR and a valid split-aperture model |
| Gate / threshold | rejects unrelated or weak candidates and can stabilize tracking | can exclude the true return and create missed detections |
| Enhanced phase / High Density | exploits more of the usable phase ramp to derive additional directions/detections from the same ping support | depends on valid `Δφ -> θ` mapping and phase quality; more points are not automatically independent resolution cells |
| BDI | exploits spatial structure distributed across beams rather than treating each conventional pick in isolation | requires a validated inter-beam model/algorithm and adequate support across beams |
| PDI | interrogates amplitude/phase as an angle-series at fixed time and can recover detections that beam-centric time-series processing may under-represent | requires sufficient angular/phase support; not every scene produces additional valid detections |
| Integrated detector | can select/combine the strengths of available estimators and advanced treatments | selection logic must remain scientifically traceable; more candidates can increase ambiguity and QC burden |

Desired operator intuition:

> **A bottom detector does not merely find an echo peak. It decides which amplitude, phase, temporal and angular information is trustworthy enough to convert into one or more valid bottom detections. Conventional amplitude and phase compete to provide a single beam/direction solution; advanced processing can exploit more of the available structure to increase bottom-detection density and completeness.**

## Scope boundaries / scientific guardrails

- D8 teaches **bottom detection**, not D3 acoustic-budget physics, D7 footprint formation, D9 sector sequencing or D14 coordinate transformation.
- Keep **physical echo**, **candidate**, **eligible candidate**, **retained detection**, and **final sounding** as distinct states.
- **Amplitude and conventional phase are alternative/competing estimators for a conventional detection.** Do not retain two final conventional soundings solely because both estimators returned candidates.
- A phase solution requires a **minimally defined/coherent phase ramp or equivalent validated phase support**. Phase detection must visibly fail/degrade when that support is insufficient.
- Do not teach `amplitude = nadir` and `phase = outer beams` as a universal hard cutoff. Actual method selection depends on signal/geometry and the registered detector.
- For amplitude detection, display the estimator actually implemented by the Scientific Core. Do not silently equate all amplitude detection with the single largest raw sample.
- For phase detection, use the registered split-aperture/phase estimator. Never draw a decorative zero crossing disconnected from computed phase data.
- The mapping `Δφ -> θ` must live in the Scientific Core and respect baseline geometry, wavelength/frequency, sound speed where applicable, steering convention, sign/frame convention, ambiguity limits and calibration assumptions.
- **The conventional zero crossing is one use of the phase ramp, not proof that every phase sample is an independent valid sounding.** Additional detections require explicit validation/support criteria.
- High Density/enhanced phase is **not more physical beams** and does not automatically shrink the acoustic footprint.
- Higher point density/detail is not identical to increased independent acoustic resolution. Preserve footprint, sounding density, detection completeness and independent resolution as separate concepts.
- BDI/PDI are advanced treatments that exploit more of the available data; do not portray them as generic enhancement filters or guaranteed bottom finders.
- Preserve PDI's key distinction between **time-series / fixed-beam analysis** and **angle-series / fixed-time analysis**.
- Truth labels are pedagogical/validation aids. Operational detectors do not know the true seabed echo a priori.
- Formal uncertainty propagation belongs to D17; D8 may expose phase residual/coherence/detection quality only when scientifically defined.
- D8 outputs `(t, θ)` detections or the registered equivalent. D14 remains responsible for full sounding formation/georeferencing.

## Dependencies / concepts passed forward

Consumes:
- D2 matched filtering, pulse compression and range-resolution intuition;
- D3 SNR/detectability context;
- D5 array/sidelobe context where it affects received phase/amplitude structure;
- D6 receive beamforming, steering and split-aperture/phase context;
- D7 per-beam footprint, slant range, incidence and swath geometry.

Passes forward:
- accepted `(t, θ)` / TWTT-direction detections to D14 Sounding Formation;
- detection-method quality/residual/coherence contribution to D17 TPU;
- additional detection density/completeness to D16 Acquisition Trade-offs;
- sector-specific detection/TX-epoch association to D9 Multisector MBES.

## Current implementation delta

`BottomDetectionLab.tsx` already provides a useful scaffold: clean/late/competing echo scenarios, TX delay, steering angle, amplitude-peak vs phase-zero-crossing method selector, detection window, threshold, single/multiple retention, true/false/missed classification, TWTT, candidate separation and a first High Density comparison.

Next-version changes required by this specification:
- preserve the existing `echo -> candidate -> eligible -> retained -> timing` chain, but place it inside the broader `received amplitude + phase -> estimator -> detection(s)` story;
- show **synchronized amplitude and differential-phase traces** from the same Scientific-Core return;
- implement a validated conventional phase estimator and visibly mark its coherent support, phase ramp and zero crossing / fitted solution;
- compare `t_A` and `t_φ` while retaining **one conventional detection** according to the active/registered selection rule;
- add a phase-quality/support indicator and scenarios in which the phase ramp is good, degraded and unusable;
- implement/expose the Scientific-Core **phase-to-physical-angle mapping `Δφ -> θ`**;
- make the transition `zero crossing -> one point` to `usable ramp -> multiple validated (t, θ) points` explicit;
- retain High Density as an advanced mode but replace hard-coded UI-side support with Scientific-Core-generated phase scenarios/solutions;
- keep the D7 footprint visible while plotting additional detections so that density is never confused with additional beams or a smaller footprint;
- add a `beam × time` amplitude/phase matrix or equivalent water-column representation;
- add fixed-beam/time-series and fixed-time/angle-series views;
- implement BDI/PDI only through scientifically registered core algorithms or clearly labelled validated pedagogical slices; do not approximate them heuristically in React;
- add a common Truth scene for side-by-side method comparison and optional Truth reveal;
- connect all accepted detections explicitly to D14 as `(t, θ)` / TWTT-direction outputs rather than implying they are already georeferenced soundings.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2.2a and H2.4a** — bottom detection, matched filtering, thresholding, range resolution, amplitude and phase bottom detection, multiple returns and relation to depth uncertainty: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Hughes Clarke (2017), “Multibeam Echosounders”** — integrated MBES treatment of phase/amplitude bottom detection, projected footprint, pulse bandwidth and practical sounding resolution: <https://scholars.unh.edu/ccom/1370/>
- **Araujo, Leonardo Gomes (2020), “Potential for Non-Conventional Use of Split-Beam Phase Data in Bottom Detection”** — UNH thesis; develops PDI from prior beam-deviation concepts, contrasts time-series and angle-series interrogation, and demonstrates non-conventional use of split-beam phase information to increase detection capability in difficult geometries: <https://scholars.unh.edu/thesis/1421/>
- **Hamel (UNH thesis, 2020)** — split-aperture phase-ramp behavior and propagation of phase noise into bottom-detection uncertainty: <https://scholars.unh.edu/thesis/1425/>
- **Kongsberg EM 302 official data sheet / product documentation** — real-system evidence for split-beam/phase-based processing heritage, multiple/high-density soundings and operational MBES detection architecture: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/data-sheet---echosounder-multibeam-em-302/>
- **IHO International Hydrographic Review, “Usability of multibeam echosounder for wreck investigations…”** — operational discussion of amplitude/phase bottom-detection combination and water-column use in MBES: <https://ihr.iho.int/articles/usability-of-multibeam-echosounder-for-wreck-investigations-using-backscatter-and-water-column-data-in-shallow-waters/>

---

# D9 — Multisector MBES

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/MultisectorLab.tsx`  
**Historical implementation alias:** `PED-D10` / `D10Multisector*` in current API naming; pedagogical numbering here is authoritative.

## Purpose
Teach why a modern MBES may divide one swath into **multiple transmit sectors** and why sector identity matters downstream. The learner must distinguish TX sectors from the many RX beams already learned in D6/D7: a sector is a transmit event/configuration with its own angular support, steering, timing and potentially frequency/pulse characteristics; RX beams/detections are later associated with the appropriate transmitted sector.

**Dominant discovery**
```text
one swath / ping
  -> one or more distinct TX sectors
  -> sector-specific angle + TX epoch + signal configuration
  -> RX beams/detections must reference the correct TX sector
  -> sector design changes coverage / sounding distribution / interference behavior
```

The lab succeeds when the learner can look at a multi-sector ping and identify **which parts belong to transmit architecture versus receive beamforming**, predict what changes when sector timing/frequency/coverage changes, and explain why the correct sector TX epoch is required for a valid TWTT.

## Inputs

### Primary
- **TX sector count/layout** using a simple one-sector baseline then a three-sector example;
- each sector's **centre / angular support**;
- **TX timing / delay / transmit group** so simultaneous and staggered events can be compared;
- **per-sector frequency** where the selected registered architecture supports frequency-coded sectors.

### Secondary / advanced
- pulse duration per sector;
- relative/source-level setting only when the Scientific Core maps it to an acoustic consequence;
- along-track sector steering / yaw-pitch stabilization when later connected to D11;
- sector focusing/range only if a validated near-field/focusing model exists;
- surface sound speed as a steering input only as a bridge from D4, not as a new SVP lesson.

Sound speed should not remain a primary D9 knob merely because wavelength is convenient to calculate; D1/D4 already own wavelength and steering sound-speed concepts.

## Expected outputs / visual response

Required synchronized views:

### A. TX sector geometry
- physical TX aperture/reference at the vessel;
- each **TX sector** visibly distinct, with centre and angular support;
- gaps and overlaps between sector supports made explicit;
- a faint RX-beam/fan context may be overlaid only to reinforce `TX sectors ≠ RX beams`.

### B. Transmit timeline
- one ping shown as one or more TX epochs;
- pulse start/end for every sector;
- simultaneous sectors grouped explicitly;
- staggered sectors visibly separated in time;
- selected sector's TX epoch available for downstream TWTT reasoning.

### C. Sector configuration / identity
For each sector:
- frequency and wavelength when physically configured;
- pulse duration;
- configured relative power/source-level quantity only with exact semantics;
- sector identifier preserved so later receive detections can be associated with the correct TX event.

Recommended:
- selected RX beam/detection from D7/D8 mapped to its parent TX sector once the Scientific Core supports that association;
- a small seafloor coverage strip showing how sector boundaries contribute to the total swath without re-teaching footprint;
- current/baseline comparison for one-sector versus multi-sector architecture.

## Interaction contract

1. Start with a **single TX sector** covering a modest swath. Keep one TX epoch and one frequency so the learner has the D7 baseline.
2. Split the same overall swath into **three TX sectors** while keeping the receive fan conceptually unchanged. This is the central distinction: more TX sectors do **not** mean more physical RX arrays or simply “three groups of beams”.
3. Change the sector centres/widths to create a deliberate **gap**, then an **overlap**. Show coverage supports on the same angular scale and let the learner diagnose the geometry.
4. Put all sectors at the same TX epoch and label them **simultaneous**. If the selected architecture is frequency-coded, assign different frequencies and show that the signal identity can separate concurrent sector transmissions; do not invent a crosstalk calculation unless the core has one.
5. Stagger one sector with a TX delay. The water-column geometry need not change, but the timeline must. Show that a detection associated with that sector requires its own TX epoch to recover TWTT correctly.
6. Vary frequency per sector in the registered architecture. Reuse D1/D3 intuition: wavelength and propagation behavior differ, but D9's discovery is **sector identity/configuration**, not a new frequency lesson.
7. Vary pulse duration per sector and show only the timing/configuration consequence currently supported. Defer SNR/range-resolution consequences to the existing D2/D3 models unless the core explicitly integrates them here.
8. Advanced: show sector-specific along-track steering/stabilization or focusing only when a validated Scientific-Core response is available. Use this to bridge toward D11 rather than silently encoding vendor behavior.

## Operational intuition / trade-offs

| Control / condition | Gain | Cost / risk to retain |
|---|---|---|
| Multiple TX sectors | allows different steering/signal treatment across the swath and can support stable, efficient wide-swath operation | sector boundaries, timing and identity must remain correct downstream |
| Frequency-coded simultaneous sectors | permits near-simultaneous sector transmission with signal separation in architectures designed for it; can mitigate inter-sector/multipath interference | frequency-dependent propagation/response differs across sectors; architecture-specific filters/waveforms are required |
| Staggered sector timing | separates TX events in time and supports architectures/modes that cannot or should not transmit them together | lengthens the transmit sequence and makes the correct sector TX epoch essential for TWTT |
| Wider/moved sector support | reallocates transmit coverage toward a desired part of the swath | poor configuration can create gaps, excessive overlap or unfavorable steering |
| Sector-specific pulse/frequency | adapts signal characteristics to sector/range objectives | creates nonuniform acoustic characteristics across the swath; exact benefit follows D2/D3 and the registered system model |
| More sectors | finer control of transmit geometry/configuration | more scheduling/association complexity; sector count is not sounding density or RX beam count |

Desired operator intuition: **“a multisector MBES is coordinating several transmit configurations inside one swath. Every sector has an identity and TX epoch; receive beams and detections are only physically meaningful when tied back to the correct sector.”**

## Scope boundaries / scientific guardrails

- A **TX sector is not an RX beam**. Keep sector count, receive-beam count and sounding count visually and conceptually separate.
- Multisector does not universally mean “three sectors”, “different frequencies” or “simultaneous transmission”. Those are real architectures/modes, especially in Kongsberg EM systems, but HydroSIM must teach the general mechanism first.
- The current Scientific Core slice computes configured angular supports, sector wavelength, TX start/end and transmit groups. It explicitly **does not** model vendor scheduling, crosstalk, interference suppression, source-level/SNR consequences or automatic sector-to-RX-beam association.
- Do not infer acoustic power from UI opacity. A configured `relative_power` may be displayed as a setting, but visual brightness must not be interpreted as insonified intensity unless the Scientific Core computes that field.
- Do not claim that different frequencies inherently improve coverage or resolution. Reuse D3/D5 trade-offs and the actual registered sonar model.
- Sector TX delay is a timing reference. Any downstream TWTT must use the correct sector transmit epoch; D13/D14 later own general synchronization/latency and sounding formation.
- Surface sound speed can affect electronic steering and sector geometry in real systems; water-column SVP controls propagation. Preserve D4's distinction and do not collapse them into one “sound speed” effect.
- Along-track yaw/pitch stabilization and motion-driven sector steering belong primarily to D11. D9 may establish the sector structure that stabilization acts upon.
- Near-field transmit focusing is advanced and should appear only if the Scientific Core has a validated focusing model.

## Dependencies / concepts passed forward

Consumes:
- D1 frequency/wavelength;
- D2 pulse duration/signal identity;
- D3 frequency/range and source-level/SNR trade-offs;
- D4 distinction between transducer/surface sound speed and water-column propagation profile;
- D6 steering and virtual RX beams;
- D7 TX×RX swath geometry;
- D8 detection/TWTT and the need for the correct TX epoch.

Passes forward:
- sector installation/orientation context to D10;
- sector steering/stabilization architecture to D11;
- multiple TX epochs to D13 Timing, Synchronization & Latency;
- correct sector TX epoch/identity to D14 Sounding Formation;
- sector-dependent coverage/sounding distribution to D15/D16.

## Current implementation delta

`MultisectorLab.tsx` plus `multisector_api.py` already expose three configurable sectors, centre/width, per-sector frequency, pulse duration, TX delay and relative power; the Scientific Core returns angular coverage supports, wavelength, absolute TX start/end and simultaneous transmit groups. The API correctly labels this as a **vendor-neutral first slice** and keeps TX sectors distinct from RX beams.

Next-version changes:
- begin with a **one-sector baseline**, then reveal the three-sector configuration; do not start with the full parameter wall;
- make `TX SECTORS ≠ RX BEAMS` the dominant visual distinction, ideally by overlaying a faint receive fan from D7 behind the colored TX sectors;
- make gap/overlap consequences explicit when centre/width controls move;
- make the timeline and **sector-specific TX epoch** equally prominent with the angular geometry;
- reduce sound speed and relative power from primary controls; wavelength is a derived reminder, not the teaching objective;
- do not use opacity as a physical proxy for power unless an acoustic-level model is integrated;
- add a visible one-sector ↔ multisector comparison and preserve fixed angular/time scales;
- if sector-to-RX/detection association is added, implement it in the Scientific Core/API rather than assigning sectors heuristically in React;
- keep simultaneous/different-frequency operation as a labelled real-system example, not the universal default rule;
- defer yaw/pitch stabilization and transmit focusing until D11 or until a validated integrated core slice is available.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2.4a/H2.4b** — MBES content explicitly includes **beam sectors** and beam shading; learners must explain/assess the impact of beam sectors on sounding distribution: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Beaudoin, Hughes Clarke & Bartlett (2004), “Application of surface sound speed measurements in post-processing for multi-sector multibeam echosounders”** — demonstrates why changing sector timing/boundaries and associating receive beams with the correct transmit sector matter to sounding reconstruction: <https://scholars.unh.edu/ccom/1335/>
- **Beaudoin, Weber et al. (2013), “Multibeam Echosounder System Optimization for Water Column Mapping of Undersea Gas Seeps”** — institutional evidence that frequency-encoded multi-sector systems are used to stabilize bathymetric imaging geometry and sounding spacing/density: <https://scholars.unh.edu/ccom/693/>
- **Kongsberg EM 2040 Instruction Manual, System overview** — architecture-specific example: three TX sectors per swath, normally separate frequencies and simultaneous transmission, sector steering/focusing and filtering to reduce crosstalk; use as real-system evidence rather than universal behavior: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/346210_em2040_instruction_manual.pdf>
- **Kongsberg EM 2040 MKII current product documentation** — current evidence for a three-sector broadband transmitter with sectors transmitted simultaneously at separate frequencies: <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>

---

## 4. Review queue

Continue **D10 -> D17**. For each lab record:
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