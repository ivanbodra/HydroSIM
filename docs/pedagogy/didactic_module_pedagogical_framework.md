# HydroSIM Didactic Module — Pedagogical Framework

Status: **next-version development baseline**  
Scope: **Didactic Module pedagogy and interaction design**  
Scientific authority: **none — scientific equations, signs, frames, limits and model validity remain in the Scientific Core / Scientific Registry**

Related documents:

- [`hydrosim_pedagogical_plan.md`](hydrosim_pedagogical_plan.md) — submodule scope and curriculum structure;
- [`pedagogical_reference_index.md`](pedagogical_reference_index.md) — historical and candidate teaching references;
- [`../architecture/didactic_explorer_foundation.md`](../architecture/didactic_explorer_foundation.md) — application/scientific-core boundary.

## 1. Pedagogical mission

HydroSIM is not intended to be an animated textbook or a training clone of one manufacturer's acquisition software.

Its didactic purpose is to develop **physical, operational and system-level intuition about hydrographic acquisition** through controlled interactive simulation.

The learner should understand how physical phenomena, sonar and sensor configuration, environmental conditions and operational choices combine to produce hydrographic observations, and should progressively become able to **predict and justify the consequences of acquisition decisions before changing a control**.

### General objective

> Enable the learner, through visual and interactive experimentation, to understand how a hydrographic sounding is formed and to develop the intuition needed to predict, tune and diagnose acquisition behavior, including the benefits, costs and limitations associated with operational choices.

The equations support this intuition; memorizing equations is not the terminal learning objective.

## 2. Core learning progression

Every major learning experience should move the learner as far as appropriate through this progression:

```text
SEE
  -> UNDERSTAND
      -> PREDICT
          -> TUNE / DECIDE
              -> DIAGNOSE / JUSTIFY
```

### See

The learner changes one meaningful parameter and can clearly perceive a consequence.

### Understand

The learner can explain the physical or geometric mechanism responsible for that consequence.

### Predict

Before moving the control, the learner can anticipate the direction and approximate character of the change.

### Tune / Decide

Given an acquisition objective or constraint, the learner can choose among controls and recognize that an improvement in one dimension may impose a cost in another.

### Diagnose / Justify

Given degraded or unexpected acquisition behavior, the learner can identify plausible causes, choose a corrective action and explain why it should help.

Not every introductory lesson must reach the final stage by itself. Early lessons create concepts that later synthesis experiences reuse operationally.

## 3. The HydroSIM teaching contract

The existing teaching contract is extended from:

```text
CONTROL -> PHYSICAL PHENOMENON -> OBSERVABLE CONSEQUENCE
```

to the next-version target:

```text
CONTROL
  -> PHYSICAL / SIGNAL / GEOMETRIC CHANGE
  -> OBSERVABLE CONSEQUENCE
  -> SOUNDING / BOTTOM-DETECTION CONSEQUENCE
  -> BENEFIT + COST
  -> ACQUISITION DECISION
```

Where a lesson is still foundational, the later stages may be previewed and completed in a later lesson. The causal chain must nevertheless remain consistent across the module.

### No rule without a mechanism

HydroSIM should avoid teaching operational folklore as universal one-line rules.

For example, a control may appear to improve or degrade resolution in a particular operating regime without intrinsically controlling resolution. The UI should show the mechanism and applicable conditions rather than encode an oversimplified arrow as scientific truth.

This is especially important for coupled controls such as power, gain, frequency, pulse length, bandwidth, steering, swath, beam spacing, detection threshold, ping rate and vessel speed.

## 4. Primary pedagogical outcome: acquisition intuition

A learner completing the Didactic Module should not merely recognize sonar terminology. The desired outcome is that the learner can reason through situations such as:

- bottom detections are being lost at the outer swath;
- sufficient SNR exists but two nearby features are not being resolved;
- the survey is productive but along-track density is inadequate;
- increasing swath improves coverage but degrades the quality or robustness of outer-beam observations;
- an environmental or timing error creates a recognizable spatial signature;
- two apparently useful control changes solve the same problem by different mechanisms and carry different penalties.

HydroSIM should therefore teach **trade-offs rather than recipes**.

The learner should routinely ask:

1. What am I trying to improve?
2. Which physical limitation is currently dominant?
3. Which control acts on that limitation?
4. What else will that control change?
5. Is that trade-off acceptable for this acquisition?

## 5. Operational control intuition

The following table defines **pedagogical relationships to expose and scientifically validate**, not implementation equations. Exact behavior depends on the selected scientific model, sonar architecture and operating regime.

| Control / choice | Mechanism the learner should understand | Typical benefit to investigate | Typical cost / limitation to investigate |
|---|---|---|---|
| Transmit power / source level | Changes transmitted acoustic level and therefore echo/SNR margin | Greater detection margin and potential range | Saturation/clipping, stronger unwanted returns/reverberation or detector consequences in some regimes; **power is not intrinsically a resolution control** |
| CW pulse length | Changes transmitted duration/energy and temporal extent of an uncompressed pulse | More transmitted energy and potential range/SNR | Poorer CW range resolution, longer transmit blanking/minimum-range implications, and more of the acoustic cycle occupied |
| FM/chirp duration and bandwidth | Long coded pulse carries energy; bandwidth and matched filtering determine compressed response | Energy/range benefit while preserving substantially better range resolution than an equivalent long CW pulse | Processing/system bandwidth constraints; ambiguity and implementation limits must follow the actual model/system |
| Frequency | Changes wavelength and frequency-dependent propagation/scattering behavior | For a fixed physical aperture, can support narrower beams; often associated with finer-scale observations and available bandwidth | Absorption generally increases with frequency in seawater, reducing practical range; scattering/environment response changes |
| Array aperture / beamwidth | Controls angular directivity and projected footprint | Smaller footprint / better angular-spatial discrimination | Physical array constraints; frequency/wavelength dependence; sidelobe and steering behavior |
| Steering angle | Applies direction-dependent delays/phases and changes propagation/footprint geometry | Places virtual beam away from broadside and increases accessible across-track coverage | Greater slant range, more oblique incidence/projected footprint, element/array steering losses and potentially degraded outer-swath performance |
| Swath / angular sector | Chooses how far from nadir the system attempts to observe | Greater coverage per ping | Outer-beam range/incidence/footprint/SNR/refraction consequences; not all depths/conditions support the same useful sector |
| Beam / sounding spacing and density | Changes sampling pattern, not necessarily the underlying physical resolving power | Denser representation and greater probability of sampling small features | More samples do not automatically create new physical resolution; interpretation must remain tied to footprint, beamforming, bandwidth and detection |
| Ping rate / ping mode | Changes along-track temporal sampling | Greater sounding density for a given speed | Constrained by two-way travel time, pulse/sector sequence and avoidance of acoustic ambiguity/interference |
| Vessel speed | Changes distance traveled between usable observations | Higher area-production rate | Lower along-track density at fixed ping rate and potentially stronger consequences from timing/latency errors |
| Gain / receiver scaling | Changes receiver amplification / dynamic use of returned signal | Makes weak returns more usable within system limits | Also amplifies unwanted components and can contribute to clipping/saturation; does not improve the physical echo SNR by itself |
| Detection threshold / detector settings | Changes the criterion by which a received response becomes a detection | Can recover weak detections or suppress unwanted responses depending on tuning | False/missed detections and bias/robustness trade-offs |
| Sound-speed sampling / profile choice | Controls propagation correction and ray reconstruction | More representative acoustic geometry and lower refraction error | Operational time/sampling burden; benefit depends on actual water-column variability |

The final UI language for each relationship must be approved against the Scientific Core. This table is a pedagogical target, not permission to implement unsupported causal shortcuts.

## 6. Lesson design rules for the next version

### 6.1 One dominant discovery per lesson

Each lesson should have a clear answer to:

> What should the learner discover here that was not already learned elsewhere?

A lesson should not become a collection of every parameter available in the underlying model.

### 6.2 Few controls first, progressive disclosure later

The primary experience should expose only the controls required for the dominant learning question. Secondary controls may appear after the learner understands the first-order behavior.

A configuration panel is not, by itself, a pedagogical experience.

### 6.3 Immediate causal feedback

A meaningful control change should recompute the affected view immediately where computationally practical. The learner should not have to submit a large form before seeing the consequence.

### 6.4 Preserve visual comparability

When the learning objective is to compare magnitude, frequency, duration, angle, range, footprint, error or response, plots should retain **fixed or explicitly shared scales** whenever autoscaling would hide the physical change.

Baseline/current comparisons must share the same scale unless the interface explicitly explains a normalization.

### 6.5 Show both gain and penalty

Operational controls should not be presented as one-directional improvements. Where a meaningful trade-off exists, HydroSIM should make both sides observable.

### 6.6 Carry concepts forward

A concept introduced in an early lesson should reappear later in the acquisition chain rather than being re-taught from scratch.

Example:

```text
frequency
  D1: frequency <-> period <-> wavelength
  later propagation: frequency <-> absorption/range
  array/beam lesson: wavelength + aperture <-> beam behavior
  acquisition synthesis: choose frequency for the operating objective
```

### 6.7 End at the sounding when useful

A physics lesson may stop at the phenomenon when that is the appropriate first step. As the curriculum progresses, the learner should increasingly be able to follow the effect into:

```text
signal -> beam -> propagation -> echo -> detection -> sounding -> swath / coverage
```

### 6.8 Let the learner create bad acquisition states

Scientifically valid poor choices are pedagogically valuable. The learner should be allowed to create low-SNR, low-density, poorly steered, badly synchronized or otherwise suboptimal conditions and observe the result.

The simulator should explain consequences, not protect the learner from every mistake.

### 6.9 Distinguish physical limitation from processing/configuration limitation

HydroSIM should make clear whether a consequence comes from:

- acoustic physics;
- physical array geometry;
- electronic processing;
- sensor/configuration error;
- acquisition geometry;
- environmental mismatch;
- detection logic;
- or visualization/normalization.

### 6.10 Same science, different didactic views

All lessons remain consumers of the shared Scientific Core. Pedagogical simplification may hide stages, but it must not invent parallel physics.

## 7. Reference-institution comparison and adopted lessons

The framework was matured against teaching and professional-competence patterns from MIT, IHO/IBSC, CCOM/UNH, UNB Ocean Mapping Group and DHN. HydroSIM does not copy any curriculum; it adopts compatible pedagogical principles while preserving its narrower acquisition-simulator scope.

### MIT OpenCourseWare — Acoustical Oceanography

MIT 2.682 begins its ocean-acoustics treatment by motivating **why the topic matters** through real applications before moving into the mathematical wave model. The course then uses formal theory, problem sets and projects.

HydroSIM adopts:

- motivate a physical concept by the acquisition problem it eventually helps solve;
- preserve rigorous causal physics beneath the visualization;
- do not introduce mathematics without showing why the quantity matters.

HydroSIM deliberately does **not** adopt the full graduate ocean-acoustics breadth or derivation depth.

Reference: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>

### IHO / IBSC — S-5A competence model

The IHO/IBSC competence framework is especially aligned with the intended HydroSIM outcome because it expresses education in **learning outcomes** and deliberately connects theory to application and practical skill rather than treating topic coverage as sufficient.

The current S-5A content explicitly groups CW/chirp, bandwidth, pulse length, pulse repetition rate, gain, detection threshold, range/spatial resolution, clipping/saturation, sound speed and ray tracing under underwater acoustics. It also requires learners to relate acoustic parameters to returns and to tune acoustic parameters on-line for depth/backscatter and assess footprint, sounding spacing and detection limitations under varying survey conditions.

HydroSIM adopts:

- progress from knowledge to application;
- define lesson outcomes in terms of what the learner can explain, predict, select, tune or assess;
- integrate several previously learned concepts into practical acquisition tasks;
- treat hands-on parameter tuning as a genuine competence, not an optional illustration.

HydroSIM is not intended to reproduce the complete S-5A curriculum.

References:

- <https://iho.int/standards-and-specifications>
- <https://ihr.iho.int/articles/maintaining-the-standards-of-competence-for-hydrographic-surveyors-and-nautical-cartographers-a-modern-approach/>

### CCOM / UNH

CCOM/UNH combines Category-A hydrographic education with field work, at-sea experience and practical use of common hydrographic systems. Its stated educational mission emphasizes the transition from sparse traditional sounding to modern high-volume ocean mapping.

Research and teaching material from John Hughes Clarke, Jonathan Beaudoin, Thomas Weber, Brian Calder and colleagues repeatedly connects system configuration to **observable survey consequences** rather than treating parameters independently. Examples include:

- practical seafloor resolution depending jointly on pulse bandwidth, beam widths, spacing, stabilization and platform altitude;
- visualizing refraction uncertainty across potential sounding space to tune sound-speed sampling;
- resolution/uncertainty trade-offs as SNR changes;
- operational reasons for FM pulses, multisector behavior, sounding-density strategies and transmit focusing.

HydroSIM adopts:

- treat the MBES as an integrated measurement system;
- make configuration consequences visible in the resulting sounding/swath;
- emphasize interacting trade-offs rather than isolated parameter definitions;
- use realistic acquisition problems to reconnect physics, sensors, environment and operational choices.

References:

- CCOM education: <https://www.ccom.unh.edu/education>
- Hughes Clarke, *Multibeam Echosounders*: <https://scholars.unh.edu/ccom/1370/>
- Beaudoin, *Real-time Monitoring of Uncertainty due to Refraction in Multibeam Echo Sounding*: <https://scholars.unh.edu/ccom/1050/>
- Beaudoin, Weber et al., *Multibeam Echosounder System Optimization for Water Column Mapping of Undersea Gas Seeps*: <https://scholars.unh.edu/ccom/693/>
- Schmidt, Weber, Lurton, *Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems*: <https://scholars.unh.edu/ccom/848/>
- Calder, *Use (and Potential Abuse) of Uncertainty in Hydrography*: <https://scholars.unh.edu/ccom/666/>

### UNB Ocean Mapping Group

The UNB Ocean Mapping Group has a long teaching/research lineage in hydrography and multibeam sonar and preserves class reports from *Multibeam Sonar Theory*. More recent work under Ian Church includes Category-A ocean-mapping education and a student-led capstone field camp with external stakeholders.

HydroSIM adopts:

- connect individual scientific concepts into realistic integrated survey problems;
- let the learner make and defend engineering/acquisition choices;
- progressively move from sonar theory toward field-system behavior and survey consequences.

Reference: <https://www.omg.unb.ca/publications/>

### DHN — Brazilian operational grounding

DHN normative hydrographic material is not used as a general pedagogical theory source, but it provides an essential **operational reality check** for a simulator intended to build hydrographic acquisition intuition in the Brazilian context.

HydroSIM should ensure that concepts such as sensor uncertainty, sound speed, coverage, swath behavior, acquisition quality and survey checks lead naturally toward the practices and terminology the learner encounters in professional hydrography.

HydroSIM adopts:

- use Brazilian hydrographic operational requirements as a relevance check;
- do not confuse operational/normative requirements with universal physical laws;
- keep scientific equations and model validity in the Scientific Registry.

Reference entry point: <https://www.marinha.mil.br/dhn/>

## 8. Consequence for the curriculum structure

The Didactic Module should progress from **fundamental quantities** to **signal and beam behavior**, then to **integrated sounding formation**, and finally to **acquisition decisions and trade-offs**.

The pedagogical arc is therefore:

```text
WHAT IS THE SIGNAL?
  -> HOW IS IT TRANSMITTED / FORMED / PROPAGATED?
      -> HOW DOES THE SYSTEM DECIDE WHERE THE BOTTOM IS?
          -> HOW DO VESSEL, SENSORS, ENVIRONMENT AND TIMING MOVE THE SOUNDING?
              -> HOW SHOULD I CONFIGURE AND OPERATE THE SYSTEM FOR THIS SURVEY?
```

Early lessons must remain simple. Later lessons earn complexity by reusing concepts already made intuitive.

### Example: D1 and D2 role in that arc

**D1 — introductory CW wave** should establish the visual vocabulary of frequency, period, wavelength, amplitude and phase. Its main operational bridge is that frequency is a physical choice whose consequences will later reappear in propagation and beam behavior. It should not prematurely teach the complete frequency/range/resolution trade-off.

**D2 — finite pulse / FM-chirp** should establish pulse duration, bandwidth, CW versus coded FM behavior, echo delay and matched-filter/pulse-compression intuition. It should begin the learner's first explicit acquisition trade-off: transmitted duration/energy versus temporal/range resolving behavior and acoustic-cycle implications.

The later synthesis lessons should reuse those exact controls rather than introduce unrelated versions of them.

## 9. Review rubric for every lesson

Before a lesson is accepted for the next version, answer:

1. **Learning question** — what single dominant discovery does the lesson enable?
2. **Future decision** — which real acquisition decision will this concept eventually support?
3. **Controls** — are the primary controls minimal and physically meaningful?
4. **Causal visibility** — can the learner see the mechanism, not only the final number?
5. **Prediction** — can the learner anticipate the direction of change before moving the control?
6. **Trade-off** — where relevant, are both benefit and penalty shown?
7. **Sounding consequence** — does the lesson connect to echo/detection/sounding when pedagogically mature enough to do so?
8. **Comparability** — do fixed/shared scales prevent visualization from hiding the consequence?
9. **Reuse** — does it build on earlier concepts instead of re-teaching them?
10. **Scientific fidelity** — are equations, conventions, units, validity domains and simplifications traceable to the Scientific Core/Registry?
11. **Scope discipline** — is the experience teaching hydrographic acquisition intuition rather than expanding into an adjacent course?

Review decisions should use the established vocabulary:

- **KEEP**
- **REFINE**
- **MERGE / MOVE**
- **ADD EXPERIENCE**

## 10. Development acceptance principle

A lesson is not pedagogically complete merely because its controls work and its plots render.

For the next HydroSIM version, a lesson should be considered successful when a learner can use it to form a reliable causal expectation that remains useful in a later acquisition decision.

The target is not:

> “I know what this slider is called.”

The target is:

> “I know why I would change it, what I expect to happen, what I may lose by doing so, and where that consequence will appear in the acquired data.”
