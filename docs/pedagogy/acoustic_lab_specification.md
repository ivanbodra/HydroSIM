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

Target learner progression:

```text
SEE -> UNDERSTAND -> PREDICT -> TUNE / DECIDE -> DIAGNOSE / JUSTIFY
```

Recurring causal contract:

```text
CONTROL
  -> PHYSICAL / SIGNAL / GEOMETRIC CHANGE
  -> OBSERVABLE CONSEQUENCE
  -> BOTTOM-DETECTION / SOUNDING CONSEQUENCE
  -> BENEFIT + COST
  -> ACQUISITION DECISION
```

Early labs may stop before the final stages, but later labs must reuse their concepts rather than teach disconnected rules.

Implementation rules:
- one dominant discovery per lab;
- few primary controls; secondary controls use progressive disclosure;
- deterministic, immediate visual response;
- use fixed/shared plot scales whenever autoscaling would hide the effect being taught;
- show mechanisms before operational rules;
- show both benefit and cost of tunable acquisition parameters;
- allow poor configurations when their consequence is pedagogically useful;
- UI consumes the Scientific Core; equations/signs/frames/validity domains remain scientifically registered and validated;
- never imply that a vendor-specific behavior is universal.

## 2. Source hierarchy for lab review

Use sources for the role they actually support:

1. **IHO S-5A, Edition 2.0.0 (August 2026)** — competence anchor. H2 explicitly includes wave wavelength/amplitude/frequency, CW/chirp, bandwidth, pulse length, pulse repetition rate, range/spatial resolution and the requirement to tune acoustic parameters and assess bottom-detection limitations.
2. **MIT OpenCourseWare 2.682 Acoustical Oceanography (James Lynch)** — first-principles acoustics and pedagogical progression.
3. **CCOM/UNH and UNB/OMG** — hydrographic/ocean-mapping science, system integration and operational interpretation.
4. **DHN** — Brazilian hydrographic operational relevance.
5. **Authoritative manufacturer documentation** — evidence of real controls, operating modes and trade-offs; never the sole authority for general physics.

## 3. Active lab map

The Acoustic Lab has **17 active labs**. The old standalone `Acoustic Detection Fundamentals` lesson is retired; historical numbering in older documents must not be reused here.

| ID | Lab | Review status |
|---|---|---|
| D1 | Acoustic Wave & Frequency | **Mapped** |
| D2 | Pulse & Signal Processing | **Mapped** |
| D3 | Sonar Equation & Propagation Loss | Pending |
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

---

# D1 — Acoustic Wave & Frequency

**Review decision:** `KEEP + REFINE`  
**Current implementation:** `web/pedagogical-explorer/src/WaveLab.tsx`

## Pedagogical purpose

Build the minimum wave intuition reused by all later acoustic labs. The learner should see a continuous sinusoidal acoustic wave and understand the relationships among frequency, period, wavelength, amplitude, phase and sound speed without turning D1 into a general acoustics course.

**Dominant discovery:**

```text
frequency up -> period down
frequency up + fixed sound speed -> wavelength down
```

The learner should be able to predict these changes before moving the control.

## Learner inputs

### Primary
- **Frequency `f`** — main experiment.

### Secondary
- **Normalized amplitude** — changes magnitude only; explicitly **not transmit power/source level**.
- **Initial phase `phi`** — shifts the cycle without changing frequency/wavelength.
- **Sound speed `c`** — advanced/secondary control used only to expose `lambda = c/f`; detailed sound-speed physics belongs to D4.

Do **not** expose period or wavelength as independent inputs. They are derived outputs.

## Expected outputs / visual response

- **Wave in time** `p(t)` with fixed time scale across parameter changes.
- **Wave in space** `p(x)` with fixed/shared distance scale across parameter changes.
- Derived **period `T = 1/f`**.
- Derived **wavelength `lambda = c/f`**.
- Clear cycle/wavelength ruler or markers when useful.
- Optional baseline/current overlay using exactly the same axes.

The learner must visually perceive more cycles in the same time/distance window when frequency increases. **Do not autoscale the spatial plot to preserve a similar number of cycles.**

## Interaction contract

1. Start from one simple CW state.
2. Learner changes **frequency**; both time and space plots update immediately while axes remain fixed.
3. Period and wavelength values update in synchrony with the plots.
4. Learner may then vary amplitude and phase to distinguish magnitude/phase from frequency.
5. Sound speed is revealed as a secondary experiment: changing `c` changes wavelength but not temporal frequency/period.
6. Reset restores a known baseline.

## Operational intuition carried forward

D1 does **not** teach sonar range or beamwidth yet. It creates the prerequisite chain reused later:

```text
frequency -> wavelength
```

Later labs extend the same control to:
- frequency -> absorption/range (D3);
- wavelength + aperture -> beam pattern/beamwidth (D5);
- frequency-dependent acquisition trade-offs (D16).

This prevents the misleading rule `higher frequency = better resolution` from being taught without its physical mechanisms.

## Scope boundaries / scientific guardrails

- No sonar equation, spreading, absorption or SNR in D1.
- No transducer/array response in D1.
- No bottom detection in D1.
- Animated wave graphics are conceptual/analytical wave representations, not a general finite-wavefield solver.
- Normalized amplitude must not be labeled as acoustic source level or power.

## Current implementation delta

Keep the current `WaveLab` structure and API-backed response. Required refinement for the next version:
- **replace the current adaptive spatial x-domain with a fixed/shared domain** suitable for frequency comparison;
- make frequency visually dominant and sound speed/amplitude/phase secondary;
- retain derived period/wavelength and fixed amplitude axis;
- optional baseline/current comparison is useful but must share axes.

## Recognized references

- **IHO S-5A, Ed. 2.0.0 (Aug 2026), H2.1a** — plane/spherical waves in terms of wavelength, amplitude and frequency; CW/chirp and acoustic-system parameters. Official standard index: <https://iho.int/standards-and-specifications>
- **MIT OpenCourseWare, 2.682 Acoustical Oceanography, James Lynch** — foundational wave-equation/acoustics background and frequency-domain framing: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/pages/lecture-notes/>

---

# D2 — Pulse & Signal Processing

**Review decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current implementation:** `web/pedagogical-explorer/src/SignalLab.tsx`

## Pedagogical purpose

Move from an indefinitely repeating CW wave to the signals actually transmitted by an echosounder: finite CW pulses and FM/LFM chirps. Build intuition for **pulse duration, bandwidth, transmitted energy, matched filtering/pulse compression and range resolution**, especially the reason FM allows a long energetic pulse without accepting the range-resolution penalty of an equally long unmodulated CW pulse.

**Dominant discovery:**

```text
finite pulse -> echo-processing problem
CW: longer pulse -> more energy, but poorer raw range resolution
FM/LFM: long pulse + bandwidth + matched filter -> energetic transmission + compressed response
more effective bandwidth -> narrower compressed response -> better range resolution
```

## Learner inputs

### Primary
- **Pulse type:** CW / LFM (chirp).
- **Pulse duration `tau`**.
- **LFM bandwidth `B`** — active only for LFM.
- **Centre frequency `fc`** — keeps continuity with D1; propagation/range penalty from frequency belongs to D3.

### Secondary / advanced
- **Chirp direction:** up / down.
- **Envelope/window model:** e.g. rectangular / Tukey, only if its effect on compressed sidelobes is visibly demonstrated.

Do not expose threshold, receiver gain or bottom-detection method here; those belong to later labs.

## Expected outputs / visual response

Required:
- **TX acoustic waveform** with the finite pulse clearly visible.
- **Instantaneous frequency vs time**: horizontal for CW; sweep for LFM.
- **Matched-filter / pulse-compressed response** on a shared/fixed comparison scale.
- **Pulse duration** and **bandwidth** displayed as measurable extents, not only numbers.
- Model-backed **range-resolution indicator** derived by the Scientific Core.
- **Relative pulse-energy indicator** at fixed normalized amplitude, preferably from signal energy integral, so duration gain is visible without pretending normalized amplitude is source level.

Recommended added experience:
- a simple **ideal delayed return** view or TX/return timeline before matched filtering, with propagation loss/noise disabled or fixed. This should teach `transmit -> delayed return -> matched filter`, not duplicate D3.
- show a **TX occupied interval**. It may be translated to an equivalent two-way range only if the model/assumptions are stated.

## Interaction contract

1. Begin with a short finite **CW pulse**. Learner increases `tau` and sees a longer waveform, more relative energy and a broader raw/matched response.
2. Switch to **LFM** at comparable centre frequency.
3. Increase pulse duration while keeping bandwidth fixed: transmitted energy/occupancy rises; compressed resolution should not be falsely presented as scaling directly with total chirp duration.
4. Increase **bandwidth**: instantaneous-frequency sweep widens and compressed peak narrows.
5. Compare CW and LFM using fixed/shared axes or baseline/current overlay so the UI cannot visually erase the trade-off by rescaling.
6. Explore chirp direction/window only after the main CW-vs-FM relationship is understood.
7. Reset restores a known comparison state.

## Operational intuition carried forward

The learner should leave D2 able to reason about why an operator changes pulse settings:

| Control | Benefit to understand | Cost / limitation to understand |
|---|---|---|
| Pulse duration `tau` up | more transmitted signal energy at fixed level; can support detection/range | longer TX occupancy; CW range resolution worsens; practical near-range/PRR consequences depend on system timing |
| LFM bandwidth `B` up | narrower compressed response; better range resolution | processing/windowing/sidelobe and hardware bandwidth constraints; not a free universal improvement |
| CW -> LFM | permits longer/high-energy transmission with pulse compression | requires matched processing; actual performance depends on effective bandwidth and system implementation |
| Centre frequency up | D1 wave cycles/wavelength change | range/absorption and array consequences are intentionally deferred to D3/D5 |

D2 should prepare, not complete, the later acquisition decision chain. D3 adds propagation/SNR; D8 adds detection; D16 synthesizes pulse/frequency/ping-rate trade-offs.

## Scope boundaries / scientific guardrails

- Do not teach `pulse length = actual minimum range` as a universal equality. Hardware TX/RX switching, blanking and transducer ring-down also matter. D2 may show the transmit-occupied interval and clearly label any simplified equivalent-range metric.
- Do not teach pulse length as the sole determinant of ping rate. Actual PRR/ping interval is also constrained by two-way travel time, depth/slant range, sector scheduling and system architecture.
- Do not teach centre frequency alone as range resolution. **Effective bandwidth and processing are central.**
- Matched filtering belongs here; the threshold/detection decision belongs to D8.
- Do not add propagation loss/noise models merely to make the return look realistic; those are D3 responsibilities and must come from the shared Scientific Core.

## Current implementation delta

Retain the current `SignalLab` fundamentals: CW/LFM selector, centre frequency, duration, bandwidth, chirp direction, envelope, acoustic waveform, instantaneous frequency and matched-filter response.

Refine for the next version:
- add an explicit model-backed resolution output and relative pulse-energy/occupancy consequence;
- provide fixed/shared comparison domains for the key CW/LFM and bandwidth/pulse-length experiments; current x/y domains should not autoscale away the effect being taught;
- consider the ideal delayed-return/timeline bridge before matched filtering;
- demote chirp direction and envelope/window to secondary controls unless their visual consequence is being actively taught.

## Recognized references

- **IHO S-5A, Ed. 2.0.0 (Aug 2026), H2.1a, H2.2a and H2.4b** — differentiate chirp and CW; explain bandwidth vs range resolution; pulse length/PRR/gain/threshold as system parameters; matched filtering and range resolution; tune acoustic parameters and assess detection limitations. Official standard index: <https://iho.int/standards-and-specifications>
- **Schock, S.G.; LeBlanc, L.R.; Mayer, L.A. (2000), “The Development of Chirp Sonar Technology and Its Applications”** — wideband FM pulse, high pulse energy/SNR and high resolution: <https://scholars.unh.edu/ccom/541/>
- **Hughes Clarke, J.E. (2017), “Multibeam Echosounders”** — spatial resolution is jointly controlled by pulse bandwidth, projected beamwidths, beam spacing/stabilization and geometry; use as a guardrail against one-parameter resolution rules: <https://scholars.unh.edu/ccom/1370/>
- **Kongsberg EM 2040 / EM 2040P documentation** — operational evidence that real MBES use short CW pulses and much longer FM chirps, and that FM is used to extend range while maintaining resolution through bandwidth/pulse compression. Treat numerical examples as system-specific: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040-Mk2/>

---

## 4. Review queue

Continue in order D3 -> D17. For every lab, add the same concise contract:

1. pedagogical purpose + dominant discovery;
2. primary and secondary learner inputs;
3. expected outputs/visual response;
4. learner interaction sequence;
5. operational intuition / benefit-cost trade-offs;
6. scope boundaries and scientific guardrails;
7. dependencies on earlier labs / concepts passed forward;
8. current implementation delta (`KEEP`, `REFINE`, `MERGE / MOVE`, `ADD EXPERIENCE`);
9. recognized exact references.

A lab is not considered pedagogically specified because a slider and chart exist. It is specified when an implementation agent can identify **what the learner changes, what must visibly change, why it changes, what intuition must be retained, and where that intuition is reused in acquisition decisions**.