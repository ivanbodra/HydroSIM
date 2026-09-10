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
| D4 | Sound Speed & Refraction | Pending |
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
Build the learner's acoustic-budget intuition: a transmitted signal must survive outward loss, bottom interaction and return loss, then remain sufficiently above noise to support detection. D3 is where the operational meaning of **transmit level/power, range, frequency-dependent absorption, noise and SNR margin** becomes visible.

**Dominant discovery**
```text
more source level -> more received level / SNR margin
more range -> more two-way transmission loss -> less received level / SNR
higher frequency -> usually more absorption -> less long-range margin
more noise -> less SNR margin without changing received signal level
```

The learner should progress from reading a sonar-equation budget to predicting which control can recover a weak return and what trade-off that choice carries.

## Inputs

### Primary
- **Range `R`** — main loss experiment.
- **Source level `SL` / transmit level** — scientific quantity. If the future UI exposes a familiar `% power` control, conversion to SL must come from a documented sonar model; never equate percent power linearly with dB.
- **Frequency `f`** — reused from D1/D2; now changes absorption through the selected Scientific-Core model.
- **Noise level `NL`**.

### Secondary / advanced
- **Bottom scattering/backscatter term** or simple selectable bottom response, only to show that bottom return strength matters; detailed backscatter is outside current scope.
- TX/RX relative beam gain only when coupled to later beam/steering labs; otherwise keep fixed.
- Environmental inputs required by the selected absorption model should normally be hidden under advanced controls or presets.
- **Required SNR / detection margin reference** may be shown as a pedagogical threshold, but it must not masquerade as the actual bottom detector used in D8.

## Expected outputs / visual response

Required:
- **Received level (RL) vs range** on a fixed scale.
- **SNR vs range** on a fixed scale.
- selected-range vertical marker shared by both plots.
- **two-way transmission loss** decomposed into spreading and absorption.
- sonar-equation contribution budget showing at minimum `SL`, outward TL, bottom-return term, inward TL, `RL`, `NL`, and `SNR`.
- **detection/SNR margin** = available SNR minus a clearly labeled required/reference SNR, displayed visually as positive/negative margin rather than as a binary bottom-detection algorithm.
- frequency comparison curve using identical range and vertical scales.

Recommended experience:
- a compact animated or static **energy-budget path**: `TX -> outbound TL -> bottom return -> inbound TL -> receiver/noise`, synchronized with the numeric budget. The goal is causality, not decorative animation.

## Interaction contract

1. Start with a detectable reference case and one selected range.
2. Increase **range**: learner sees both spreading and absorption accumulate on outbound and inbound paths; RL/SNR fall and margin approaches/crosses zero.
3. Increase **source level**: RL and SNR shift upward while propagation loss itself remains unchanged.
4. Increase **noise level**: SNR/margin fall while RL remains unchanged. This distinction is mandatory.
5. Compare **two frequencies** at identical geometry/environment. The higher-frequency curve should diverge only according to the registered absorption model and any explicitly modelled frequency dependence; fixed axes make the range penalty visible.
6. Optionally vary bottom-return strength to show why a stronger/weaker seabed echo changes detection margin without changing transmission loss.
7. Reset to the known reference case.

## Operational intuition / trade-offs

| Control / condition | Expected benefit or effect | Limitation / cost the learner must understand |
|---|---|---|
| Source level / transmit power ↑ | RL and SNR margin increase; potential range extension | Does **not** intrinsically improve resolution; real systems may face saturation, reverberation, unwanted-return and hardware limits |
| Range ↑ | none; it is the geometric demand | two-way spreading + absorption increase; outer/longer paths become harder to detect |
| Frequency ↑ | resolution/array benefits are learned elsewhere | absorption generally rises in hydrographic operating bands, reducing long-range margin; exact relation depends on environment/model |
| Noise ↑ | none | SNR decreases while RL is unchanged |
| Stronger bottom return | echo/SNR improves | seabed response depends on incidence, footprint, material and frequency; D3 uses only a controlled simplified term |

This lab must directly support the later operator diagnosis: **“I am losing the bottom at long range/outer swath — is the problem insufficient signal, excessive loss, high noise, frequency choice, or geometry?”** D3 teaches only the acoustic-budget part of that diagnosis; beam geometry/steering and detector behavior are added later.

## Scope boundaries / scientific guardrails

- **Source level is not resolution.** Increasing power/SL can improve SNR/detectability but must not be rendered as a direct resolution improvement/degradation.
- **Noise is not propagation loss.** Changing NL must not move the RL curve.
- Use a named, registered absorption model with validity domain. Do not invent a HydroSIM empirical frequency-loss law.
- Distinguish one-way and two-way TL. The bottom-return equation must not accidentally apply two-way TL twice.
- Spreading model (spherical/cylindrical/practical transition if available) must be explicit; do not imply a single spreading law is universal.
- A simplified scattering/backscatter term is acceptable for teaching the budget, but D3 is not a backscatter-classification lab.
- The D3 `required SNR` line is a **detectability reference**, not the D8 amplitude/phase/hybrid bottom detector.
- Do not introduce beamwidth/footprint penalties here unless they come from the shared beam model and are intentionally linked; otherwise hold geometry fixed.
- Do not imply higher frequency always gives higher resolution as a single causal rule; D5/D16 complete that trade-off.

## Dependencies / concepts passed forward

Consumes:
- D1: frequency and wavelength vocabulary;
- D2: transmitted pulse concept.

Passes forward:
- `frequency -> absorption -> range margin` to D16;
- `SL / noise / TL -> SNR -> detectability` to D8 Bottom Detection;
- `slant range -> acoustic loss` to D6/D7/D9/D16 when steering/swath geometry is introduced.

## Current implementation delta

The existing lab already provides a strong foundation: frequency, range, source level, noise, comparison frequency; fixed RL/SNR axes; a range marker; model-returned absorption and two-way loss; and a contribution breakdown.

Next-version changes:
- **retain** fixed axes, range marker and frequency comparison;
- separate **spreading loss** and **absorption loss** visually, not only total TL;
- add a clear **required-SNR / detection-margin** visual because the retired detection-fundamentals objective now belongs here;
- make range the first/primary experiment and reduce emphasis on raw numeric cards;
- keep source level scientifically labeled; if a future operator-facing `% power` control is desired, add only through a documented system model;
- keep temperature/salinity/pH/depth used by the absorption model under advanced controls/presets rather than making D3 an oceanography form;
- keep bottom scattering and beam gains fixed by default; expose only if the learner is explicitly studying their contribution;
- consider an energy-budget path synchronized with the existing equation breakdown.

## Recognized references

- **IHO S-5A, Ed. 2.0.0 (Aug 2026)** — current Category A competence standard; use H2 acoustic-system outcomes as the competence anchor: <https://iho.int/standards-and-specifications>
- **MIT OpenCourseWare 2.682 Acoustical Oceanography, James Lynch** — propagation/acoustical-oceanography foundation and transmission-loss context: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- **Hughes Clarke, J.E. (2017), “Multibeam Echosounders”** — hydrographic MBES context tying range, signal quality and imaging geometry to usable bathymetry: <https://scholars.unh.edu/ccom/1370/>
- **Schmidt, V.E.; Weber, T.C.; Lurton, X. (2012), “Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems”** — explicitly relates usable bathymetric resolution/uncertainty to SNR, reinforcing that low-SNR soundings are operationally constrained rather than treating resolution as an isolated setting: <https://scholars.unh.edu/ccom/848/>
- **Kongsberg EM 2040C/EM 2040 MkII official product documentation** — operational evidence that frequency is selected for the application, with lower frequencies used for deeper/longer-range work and higher frequencies for high-resolution inspection; use as system-specific evidence, not universal numerical law: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040C-MkII/> and <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>

---

## 4. Review queue

Continue D4 -> D17. For each lab record:
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