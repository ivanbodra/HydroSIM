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

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/BottomDetectionLab.tsx`

## Purpose
Turn the echo and footprint context from D2/D3/D7 into a **time/range estimate that becomes a sounding candidate**. The learner must understand that the sonar does not measure “the bottom point” directly: it receives a finite, noisy/structured echo, applies a detection method within a search region, and selects one or more return times/angles that are then passed downstream.

**Dominant discovery**
```text
received echo -> candidate response in time
search window + threshold / quality rule -> eligible candidate(s)
amplitude or phase method -> estimated bottom time / angle
wrong gate / threshold / competing echo -> missed or false detection
selected detection -> TWTT + direction passed to sounding formation
```

The lab succeeds when the learner can inspect a return trace, predict which echo will be selected, deliberately create a false or missed detection, and explain why amplitude and phase methods can behave differently across MBES geometry.

## Inputs

### Primary
- **echo scenario / return trace**: clean, weak/noisy, competing/multiple echoes;
- **detection window / range gate**;
- **detection threshold or quality criterion**;
- **detection method**: amplitude-based / phase-based when both are supported by the Scientific Core.

### Secondary / advanced
- retain single vs multiple detections;
- beam/steering angle to connect D7 geometry to detection behavior;
- phase-ramp/support length or equivalent validated quality/resolution parameter;
- **High Density** mode only after ordinary one-detection-per-beam behavior is understood.

TX delay is useful only as a timing reference/offset experiment; it must not distract from the detector itself.

## Expected outputs / visual response

Required:
- received / matched-filter magnitude versus time or lag on a fixed scale;
- highlighted detection/search window;
- threshold/quality criterion drawn directly on the trace where meaningful;
- all candidate returns, eligible candidates, retained detection(s), and rejected candidates visually distinct;
- selected TWTT / lag and derived range proxy from the Scientific Core;
- explicit classification against hidden/known scenario Truth for pedagogy: **true detection / false detection / missed detection**;
- for phase detection, a visible split-aperture/differential-phase trace and the fitted/validated zero-crossing or equivalent estimator used by the registered model;
- selected beam/direction and, when supported, the estimated angle of arrival;
- downstream arrow: `detection -> TWTT + direction -> D14 sounding formation`.

Recommended:
- synchronized ordinary vs multiple/high-density detections over the same footprint;
- confidence/quality indicator only if it has a defined Scientific-Core meaning;
- a simple seafloor strip showing where retained detections fall relative to the D7 footprint, without turning D8 into a footprint lab.

## Interaction contract

1. Start with a **single clear echo** and amplitude detection. Show the received response, the selected peak/centroid according to the core method, and the resulting TWTT.
2. Move the **detection window** so the true echo first remains inside, then falls outside. The learner should see a valid detection become a missed detection without changing the physical echo.
3. Reset and increase the **threshold / quality criterion**. A weak candidate is rejected; lower it until weak/competing responses can become eligible. The benefit/cost is explicit: suppress weak false candidates vs risk missing the real bottom.
4. Use a **competing-echo scenario**. Compare single-detection retention with multiple detections. Show that candidate generation and final retention are distinct stages.
5. Switch to **phase detection** when implemented. Visualize the split-aperture phase relation and how the zero-crossing / fitted phase estimator determines bottom timing/direction under the registered method. Compare with amplitude detection on the same echo geometry rather than treating one as universally superior.
6. Compare near-normal and oblique/outer-beam cases using a scientifically controlled scenario. Teach the common practical pattern that amplitude information is often effective near specular/nadir returns while phase methods are heavily used away from nadir, but let the Scientific Core/vendor-specific model determine actual transition behavior.
7. Deliberately create a **false detection** with an eligible competing echo or gate choice; then create a **missed detection**. The learner must diagnose which control caused the failure.
8. Advanced: enable **High Density**. Within one steered RX-beam footprint, use validated phase information to estimate additional bottom detections/points. Show ordinary detection count versus high-density point count and spacing. The learner should understand that this increases sounding density **inside the footprint**; it does not create a narrower physical beam or a new TX footprint.

## Operational intuition / trade-offs

| Control / condition | Gain | Cost / risk to retain |
|---|---|---|
| Narrower range gate / detection window | rejects unrelated echoes and can stabilize tracking | can miss the true bottom when range changes unexpectedly |
| Higher threshold / stricter quality | suppresses weak/noisy false candidates | can reject weak true returns, especially at low SNR / outer swath |
| Lower threshold / looser gate | retains weak true returns | admits more false/ambiguous candidates |
| Amplitude detection | robust/simple timing from echo energy where the envelope is well defined | spatial/time averaging and footprint geometry can limit localization; behavior depends on incidence/echo shape |
| Phase detection | can localize the centre/angle of arrival with high precision from split-aperture phase behavior | needs adequate coherent phase support/SNR and appropriate geometry; noise/support length affects stability |
| Multiple detections | preserves more than one plausible return when the scene supports it | more ambiguity/data and downstream discrimination burden |
| High Density phase processing | more bottom points within the receive-beam footprint; denser point cloud | does not shrink the physical footprint; neighboring detections are not automatically independent resolution cells |

Desired operator intuition: **“bottom detection is an estimation decision made from the received echo. A sounding starts only after the system chooses a valid time/direction; gates, thresholds and the amplitude/phase method can change that choice.”**

## Scope boundaries / scientific guardrails

- D8 teaches **bottom detection**, not D3 acoustic-budget physics, D7 footprint formation, D9 sector sequencing, or D14 coordinate transformation. Reuse those results rather than duplicating them.
- Keep **physical echo**, **candidate**, **eligible candidate**, **retained detection**, and **final sounding** as separate states.
- Detection threshold is not the same quantity as D3 SNR margin unless the Scientific Core explicitly maps them.
- Do not teach “amplitude = nadir, phase = outer beams” as a hard universal cutoff. IHO requires analysis of both methods and their relation to depth uncertainty; actual combination/transition is system and condition dependent.
- For amplitude detection, display the actual estimator implemented by the Scientific Core (peak, centre of gravity, matched-filter peak, etc.). Do not label a simple max sample as a universal amplitude detector.
- For phase detection, use the registered split-aperture/phase estimator. Do not draw a decorative zero crossing disconnected from computed phase data.
- A range gate can reduce false detections but can also miss real bottom returns; it is an acquisition/tracking control, not a guarantee of correctness.
- High Density is **not** “more beams.” It uses additional validated phase-supported detections within the footprint of a formed receive beam to increase bottom-point density. Keep physical footprint, sounding density and independent resolution distinct.
- Truth labels are pedagogical/validation aids; operational systems do not know the true seabed echo label a priori.
- Formal uncertainty propagation belongs to D17; D8 may expose detection quality/residual only when defined by the core.

## Dependencies / concepts passed forward

Consumes:
- D2 matched filtering / pulse-compression and range-resolution intuition;
- D3 SNR/detectability context;
- D6 receive beamforming / split-aperture phase context where implemented;
- D7 per-beam footprint, slant range and incidence geometry.

Passes forward:
- valid/invalid detection and TWTT/angle to D14 Sounding Formation;
- detection method/quality contribution to D17 TPU;
- multiple/high-density sounding density to D16 Acquisition Trade-offs;
- sector-specific detection behavior to D9 Multisector MBES.

## Current implementation delta

`BottomDetectionLab.tsx` already has a strong causal scaffold: clear/late/competing echo scenarios, TX delay, steering angle, amplitude-peak vs phase-zero-crossing method selector, detection window, threshold, single/multiple retention, true/false/missed classification, TWTT, candidate separation and a High Density comparison that uses phase information to derive additional across-track bottom points.

Next-version changes:
- keep the current `echo -> candidate -> eligible -> retained -> timing` chain and make it the dominant visual story;
- implement/enable the phase method only after the Scientific Core supports a validated phase estimator; until then do not present the selector as equivalent functionality;
- visualize the **phase trace / split-aperture estimator** when phase detection is selected;
- make the gate and threshold visible on the same trace rather than primarily as controls/readout cards;
- add a weak/noisy echo scenario so threshold trade-offs are not demonstrated only with clean synthetic peaks;
- connect selected TWTT/direction explicitly to D14 rather than implying the detection is already a georeferenced sounding;
- retain true/false/missed labels as pedagogical Truth comparison;
- retain single vs multiple detection as a separate retention decision;
- keep **High Density** advanced and explicitly visualize additional phase-derived detections **inside one receive-beam footprint**, not as extra physical beams;
- where possible, replace hard-coded pedagogical High Density support values with Scientific-Core-generated scenarios so the UI does not carry parallel physics.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H2.2a** — bottom detection principles including matched filtering, thresholding and range resolution; **H2.4a** — amplitude and phase bottom detection, multiple signal returns, and requirement to analyze both methods in relation to depth uncertainty: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Hughes Clarke (2017), “Multibeam Echosounders”** — integrated MBES treatment of bottom-detection method, projected footprint, pulse bandwidth and practical resolution: <https://scholars.unh.edu/ccom/1370/>
- **Kongsberg EM 302 official data sheet / product documentation** — real-system evidence for split-beam/phase-based processing heritage, multiple/high-density soundings and operational MBES detection architecture: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/data-sheet---echosounder-multibeam-em-302/>
- **IHO International Hydrographic Review, “Usability of multibeam echosounder for wreck investigations…”** — operational discussion of amplitude/phase bottom-detection combination in MBES: <https://ihr.iho.int/articles/usability-of-multibeam-echosounder-for-wreck-investigations-using-backscatter-and-water-column-data-in-shallow-waters/>

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