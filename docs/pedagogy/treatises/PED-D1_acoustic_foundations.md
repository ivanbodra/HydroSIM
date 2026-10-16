# PED-D1 pedagogical treatise — Acoustic foundations through connected observation

Revision: 1.1 — 2026-10-16.
Documentation language: English. Brazilian Portuguese is an optional user-facing presentation locale.
Owner: caho-pedagogy. Final authority: Product Owner.
Target: next HydroSIM generation; implementation baseline inspected: eed7bedc19f654b9adc13275a249a57576720e5d.
Status: Product Owner direction recorded; detailed pedagogical treatment recommended; physical-quantity scientific contract and visual concept pending.

## 1. Mandate and decision provenance

The Product Owner's 2026-10-16 review establishes these directions:

1. D1 introduces the entire laboratory experience and must establish an intuition that grows across later labs.
2. Preserve the useful existing structure while substantially improving the laboratories' depth, precision and learning experience.
3. Keep frequency as the principal physical control and the other physical controls secondary.
4. Add connected physical/measurement visualizations rather than relying exclusively on sinusoidal plots.
5. Consolidate the meaning of sound wave, pressure, power, logarithmic reference and observation in space/time.
6. Maintain harmony and a recognizable control/visualization language across labs.
7. Use laboratory treatises as the basis of the next HydroSIM version.

Those are Product Owner directions. The sequence, activities, acceptance rubric and specific scene organization below are pedagogical recommendations developed from them. Particle/pressure/energy equations, calibrations and validity limits require Scientific Lead ownership.

This treatise broadens D1's pedagogical target. It is not authorization to relabel today's normalized amplitude as pressure or to change the present production model without a scientific contract.

## 2. D1's role in the cumulative course experience

D1 should leave the learner with an explanatory mental model, not only familiarity with a frequency slider:

- identify what oscillates locally and what propagates;
- connect a physical acoustic field to a measurement at a location and to a spatial snapshot;
- explain frequency, period, wavelength, amplitude and phase in those observations;
- distinguish pressure, energy flow and power before interpreting their logarithmic levels;
- recognize the same control–phenomenon–measurement–comparison grammar in later laboratories.

Depth is achieved through progressive perspectives on one phenomenon. D1 must not become a wall of equally prominent charts, a derivation-heavy textbook or a miniature version of every later lab.

Its opening should be meaningful before the learner operates an acquisition system. Its conclusion should prepare the vocabulary later reused in pulses, acoustic budgets, array geometry and measurement.

## 3. Current baseline and demonstrated limitations

Current sources:
- ../acoustic_lab/D01_wave_frequency.md;
- ../../design/acoustic_lab/D01_wave_frequency_visual.md;
- ../../science/ped_d1_d2_scientific_contract.md;
- ../../../web/pedagogical-explorer/src/WaveLab.tsx.

Keep the useful baseline: frequency prominence, secondary disclosure, reset, authoritative Core/API, explicit period/wavelength, stable amplitude axes and reference comparison.

Inspection establishes these gaps; these are source-level findings, not an observed learner study:

| Current condition | Pedagogical consequence | Required direction |
|---|---|---|
| Two analytic traces dominate; no longitudinal-medium scene | The meaning of the ordinate and the relationship to the water remain abstract | Physical scene linked to the selected measurement |
| Spatial snapshot time is always requested as zero | The learner cannot deliberately observe, pause and inspect propagation | Coherent play/pause/step and a shared observation state |
| A temporal plot and a spatial plot are labelled as the same field without explicit probe/snapshot relationships | Their different independent variables are easy to conflate | Selected location, selected instant and visible correspondence |
| Frequency supports 20–700 kHz while the time window is 14 microseconds and spatial window 22.4 mm | At 20 kHz and 1500 m/s neither view includes one full cycle; span markers disappear | Supported ranges and clearly declared observation scales that preserve complete-cycle reasoning |
| No prediction/explanation task | Slider movement alone does not evidence understanding | Short guided experiments followed by interpretation |
| Amplitude is normalized and dimensionless | It cannot support physical pressure, intensity, power or calibrated levels by changing its label | Explicit physical-quantity extension owned by Scientific Lead |
| Reference data is initialized from the first successful response, while its legend declares 200 kHz / 1500 m/s | Reference identity is not guaranteed by the displayed label | Explicit reference configuration and provenance, independent of request timing |

At the lower frequency, T is 50 microseconds and wavelength is 75 mm. These follow from the existing kinematic relations; they are examples of the observation-window mismatch, not a demand for one new fixed window at all frequencies.

No runtime, accessibility or classroom-effectiveness certification is claimed by this review.

## 4. Curricular connection and evidence boundaries

Primary CAHO context:
- Acústica Submarina, 1 - Aula Inicial_3h.pdf, source CAHO-AC-01.
- PDF p.5 states propagation and instrument-application objectives.
- PDF pp.29–30 introduce pressure waves and compression/rarefaction.
- PDF pp.33–38 introduce oscillation, amplitude, period, frequency and phase.
- PDF pp.49–52 address phase-dependent interference.
- PDF p.13 identifies the acoustic course units.

The source was read in extracted text; visual review sampled pp.5, 13, 29 and 48. Exact path/hash and reading extent are preserved in the [initial CAHO reading log](https://github.com/ivanbodra/HydroSIM/blob/7beeac3de7afe3753b533587475cb524fe99c141/docs/pedagogy/caho/reading_log.md), proposed in PR #606.

This supports a foundations connection. The full pressure–power–decibel sequence proposed here is a Product Owner-directed HydroSIM extension; it is not presented as a verbatim objective or complete mapping of an unread CAHO unit.

Later acoustic-unit and transducer lessons should be read progressively to reconcile class terminology and avoid unnecessary repetition.

## 5. Learners, prerequisite check and objectives

Target: CAHO officers beginning the acoustic laboratory sequence and learners reviewing its physical foundations.
Prerequisites: basic time/distance/units and the idea of a changing quantity. Neither complex exponentials nor sonar-operating experience should be required to understand the opening.

After D1 the learner should be able to:

| Objective | Observable evidence |
|---|---|
| O1 Explain local particle motion versus propagation | Follow a marked particle and a compression feature and describe their different motions |
| O2 Identify the observed quantity and its units | Distinguish displacement, acoustic pressure and a normalized display |
| O3 Distinguish a fixed-location time record from a fixed-time spatial profile | Explain what is held fixed in each view and locate the corresponding scene point |
| O4 Predict frequency/period/wavelength changes | Predict before manipulation, then reconcile with observations at fixed sound speed |
| O5 Distinguish propagation speed from oscillation frequency | Explain a sound-speed change at fixed frequency in the stated reference medium |
| O6 Distinguish amplitude and phase changes from frequency changes | Identify what changes and what remains invariant |
| O7 Distinguish pressure, intensity and power | Name each quantity, unit, observation context and the conditions required to relate them |
| O8 Interpret a logarithmic level with its reference | Explain what is being compared and why changing only a reporting reference leaves the physical field unchanged |
| O9 Use controlled reference/current comparisons | Preserve the declared reference and isolate one variable |
| O10 Transfer the vocabulary | Explain how a CW wave can later become the carrier of a finite pulse and how acoustic levels will be used in a budget |

O7–O8 require the new scientific outputs. Their absence cannot be hidden by marking the older normalized-wave experience complete for this target.

## 6. Central phenomenon and organizing question

One acoustic phenomenon is viewed through connected perspectives:

medium motion and pressure variation -> propagation -> measurement at a fixed location -> spatial snapshot -> derived relationships -> physical quantities -> referenced levels.

Organizing question:

What is changing in the water, what does an observer measure, and how do our choices change the phenomenon and its representation?

Use a homogeneous reference medium for initial exploration. Complexity is earned by observing a new relationship, not by exposing every possible variable.

## 7. Physical, observational and graphical perspectives

The dominant scene should support three distinguishable selections:

1. A marked material particle, tied to an equilibrium position and its local displacement.
2. A fixed spatial probe, tied to a pressure record at a stationary location.
3. A selected instant, tied to a pressure profile across space.

A material particle and a fixed spatial point must never silently become the same object. A displacement trace and a pressure trace require different labels and, where applicable, different units and phase relationships.

Compression/rarefaction should be perceptible without suggesting that the drawn dots are literal resolved water molecules. If particle displacement or density contrast is magnified, disclose the visual exaggeration.

The pressure sinusoid is a graph of a quantity. It is not a transverse trajectory of particles. A passing compression feature can serve as a propagation marker while the marked particle shows local motion.

Concept Designer determines composition and visual hierarchy. Scientific Lead determines the consistent fields and transformations behind the depiction.

## 8. Progressive experience

Preserve the learner's configured case, reference, location and instant as perspectives are revealed.

| Stage | Learner question | Main interaction | Intended discovery |
|---|---|---|---|
| A — Observe the medium | What oscillates and what travels? | Play/pause/step; select particle and propagation marker | Local oscillation and propagation are different |
| B — Observe one location | What does a stationary observer record? | Select the fixed probe; follow the time cursor | Frequency and period belong to a time record |
| C — Freeze an instant | What is distributed across space now? | Pause/select time; measure equivalent spatial states | Wavelength belongs to a spatial profile |
| D — Control frequency and speed | What changes when each is varied independently? | Frequency first; sound speed second | Frequency, period, wavelength and speed are related but distinct |
| E — Separate magnitude and phase | What changes without changing the oscillation rate? | Secondary amplitude and phase controls | Amplitude and phase are not frequency or propagation delay |
| F — Follow the quantities | What does pressure tell us about energy transport? | Inspect physical pressure and validated intensity/power relationships | Different quantities need different meanings, units and assumptions |
| G — Change representation | What does a logarithmic level describe? | Compare linear values and referenced levels for the same state | Reporting scale/reference is separate from physical change |

This is one laboratory with progressive depth, not seven mandatory disconnected applications. Provide guided exploration and free exploration; returning to an earlier perspective should preserve useful context. Avoid compulsory quiz gates before the learner can manipulate the scene.

The teacher may use a short A–D segment during a foundations lesson and return to F–G when appropriate. The full next-generation D1 target includes F–G; they are not abandoned merely because they need additional science.

## 9. Control hierarchy and state semantics

| Control family | Meaning | Hierarchy |
|---|---|---|
| Frequency | Principal physical experiment | Always discoverable and visually dominant |
| Physical amplitude | Magnitude of a declared field with a declared peak/RMS convention | Secondary; physical mode only after scientific contract |
| Normalized amplitude | Dimensionless magnitude in an explicitly normalized mode | Retain honestly if offered; never relabel as Pa or watts |
| Initial phase | Phase origin of the specified analytic field | Secondary |
| Sound speed | Propagation property of the homogeneous reference medium | Secondary; identify what else is held constant |
| Play/pause/step and teaching slow motion | How physical time is inspected | Persistent observation tools; separate from sound speed/frequency |
| Particle/probe/instant selection | Where/when/what is being observed | Direct selection in the scene |
| View, units, linear/log display and reference/current overlay | Representation of the same or explicitly selected state | Clearly separate from physical controls |
| Save/restore reference; reset | Controlled comparison and recovery | Predictable shared behavior across labs |

Period and wavelength remain derived outputs. A log/linear switch must not change the physical case. A pressure/power view switch must not silently reconfigure a source.

The existing wave contract classifies configured analytic fields as Configured/Derived. A simulated probe is not an actual environmental observation; do not invent environmental Truth, measured observations or calibrated hardware provenance for an analytic teaching case.

Selecting a new physical model or changing which quantity is held fixed must be explicit. In particular, changing sound speed in an extended pressure/intensity experiment may change other derived quantities under the approved model; do not promise unchanged energy outputs without specifying the constraints.

## 10. Required outputs and their meaning

| Output | Required interpretation |
|---|---|
| Longitudinal scene | Local displacement, equilibrium position, direction of propagation and compression/rarefaction |
| Fixed-probe time record | Selected physical quantity at a declared stationary position; current time cursor linked to the scene |
| Frozen spatial profile | Same declared quantity at a selected instant; spatial marker linked to the probe |
| T and wavelength markers | A complete repetition measured on the appropriate independent variable |
| Frequency/speed/period/wavelength summary | Concise derived relationships with appropriate scale prefixes |
| Pressure readouts | Instantaneous versus peak/RMS statistic, with acoustic pressure distinguished from static background pressure |
| Intensity/power panel | Clearly different quantities; required medium/surface/direction/averaging context visible |
| Linear/log comparison | Same quantity/case or explicitly linked quantities; reference value, units and level definition shown |
| Reference/current comparison | Identifiable saved configurations; consistent axes, units and observation context |
| Prediction/explanation record | What the learner expected, observed and concluded |

Use readable scaled units: for the present ultrasonic examples microseconds and millimetres are often clearer than long decimal fractions. Show the unit and represented quantity on the relevant axis, not only in a tooltip.

Do not call every numeric readout a measurement. Separate configured values, simulated probe values, derived values and reference quantities.

## 11. Observation scales, reference identity and animation

Supported ranges must permit the activity's complete-cycle reasoning. Give the learner access to at least two full repetitions for cycle comparisons, including the lower frequency end, without losing access to detailed inspection.

Possible design: overview plus an explicitly controlled magnification shared by reference/current. The precise layout is a visual-design decision. Do not silently normalize every trace to a fixed number of cycles or change axes independently as frequency moves.

Reference and current must share comparison scales. If a scale changes, make it visible and explain what comparisons remain valid. A large dynamic range is not solved by hiding the difference that the lab intends to teach.

Establish a baseline from an explicit configuration; show its actual values. It must not depend on which asynchronous response arrives first.

All simultaneous views use one declared physical time and observation context. Teaching slow motion changes playback, not the physical sound speed. A fixed-medium frequency change must not inadvertently accelerate the propagation marker. Reset and reference restore must have defined effects on time and selections.

Respect reduced-motion preferences and offer meaningful paused snapshots. An animation running attractively is not evidence that its causal relationships are correct.

## 12. Physical-quantity and logarithmic treatment

Teach the distinction among pressure, intensity and power, and the meaning of reporting a level relative to a stated reference. Pressure is not simply another label for intensity or total source power.

For a quantitative pressure mode, Scientific Lead must define acoustic perturbation versus static pressure, the input statistic, units, applicable field model and any relationship to particle motion. A pressure-at-probe value alone must not be presented as total radiated source power.

For a power demonstration, use a scientifically declared surface/geometry/averaging context. If a bounded flow-through-surface example is selected, label that power explicitly rather than implying an operational projector output. Geometry/area can initially be fixed and disclosed to avoid competing with frequency.

For logarithmic teaching, specify the quantity, linear reference and level convention. A physically unchanged case reported against a different reference is a particularly useful comparison. Positive/negative levels must not be confused with compression/rarefaction or positive/negative instantaneous acoustic pressure.

Keep physical signed pressure on an appropriate linear trace; a level display needs its approved statistic and domain. Zero-amplitude and undefined logarithmic cases require explicit behavior, not a fabricated finite value or an unexplained clipped axis.

Exact equations, ratio examples, reference values, pressure/particle phase relations and numerical tests belong in the scientific extension. This document requests their pedagogical consequences, not an independently invented calibrated acoustic model.

## 13. Guided experiments and comparison states

Every main experiment follows predict -> manipulate -> observe -> compare -> explain -> apply.

| Experiment | Controlled comparison | Evidence to elicit |
|---|---|---|
| E1 Local motion vs propagation | Track one particle and one compression feature over time | Which one travels through the scene? Where does the particle return? |
| E2 Fixed point vs snapshot | Same field/location/instant linked across scene and graphs | Explain the different independent variables |
| E3 Frequency | Increase/decrease f at fixed c and declared amplitude convention | Predict T and wavelength changes and what does not change |
| E4 Sound speed | Change c while holding f fixed | Distinguish wave advance and spatial period from temporal period |
| E5 Amplitude | Change the declared amplitude with f/c fixed | Separate magnitude from frequency; interpret energy consequences only in the approved mode |
| E6 Phase | Change initial phase with other physical parameters fixed | Explain the shift without claiming a new frequency or a source-to-receiver delay |
| E7 Physical quantities | Inspect the same approved pressure/energy-flow case | Name quantities/units and the conditions linking them |
| E8 Linear and referenced level | Preserve the physical state while changing representation/reference | Explain what changes in the number and what remains physically unchanged |
| E9 Transfer | Interpret a simple hydrographic acoustic statement | Identify which quantity is known and which further assumptions would be required |

Prompts should be short, contextual and available in both supported locales. Example intent: predict which view changes first; identify what is held fixed; explain why two representations describe the same state. Do not replace exploration with paragraphs of instruction.

## 14. Misconceptions and design responses

| Risk | Required response |
|---|---|
| Water particles travel from source to receiver with the wave | Mark equilibrium position, local particle and passing propagation feature |
| The sinusoid is a transverse particle path | Name plotted quantity; connect it to pressure/longitudinal scene |
| A material particle is the fixed probe | Distinct selectable objects and labels |
| Pressure and particle displacement have identical units or phase | Separate fields and scientifically validated relationships |
| Higher frequency means faster propagation in this reference medium | Compare propagation markers at fixed c |
| Frequency change is merely horizontal zoom | Visible scales and consistent reference/current context |
| Amplitude, intensity and power are interchangeable | Distinct quantities, units and assumptions |
| Initial phase is propagation delay or frequency | Controlled E6 with explicit invariants |
| Acoustic pressure is the water's static pressure | Clear perturbation/background distinction |
| A number in dB is an absolute pressure or power without reference | Show quantity, statistic and reference |
| Zero or negative dB means absence of sound or rarefaction | Compare referenced level with the separate signed physical signal |
| More elaborate visualization establishes scientific validity | Canonical outputs, limiting cases and exact-candidate verification |

These are anticipated learning risks, not claims about measured CAHO misconception prevalence.

## 15. Assessment and learning evidence

Use formative evidence without unnecessary scoring infrastructure:

- a prediction before a principal control change;
- one complete-cycle measurement in time and in space;
- an explanation of particle/probe/snapshot distinctions;
- a correct controlled comparison identifying what stayed fixed;
- one pressure/intensity/power classification with units and a condition;
- one explanation of a linear/log or reference change;
- a transfer explanation leading into later labs.

A wrong initial prediction can produce successful learning if the student reconciles it with evidence. Correct slider positions alone do not demonstrate understanding. Do not invent a quality percentage or certify hydrographic operating competence from D1.

A successful learner explanation should answer: what changed, why, how it was observed, what remained fixed, and where the relationship will be useful next.

## 16. Shared visual grammar, accessibility and language

D1 introduces candidate conventions for subsequent treatises:

- primary control remains recognizable;
- physical state, reference/current and selected observation retain semantic roles;
- selections connect scene, measurement and readout;
- local emphasis highlights the changed consequence without flashing the whole page;
- units/scales remain close to the represented quantity;
- the principal physical scene has greater hierarchy than supporting metric cards.

Do not make an arbitrary palette/layout a pedagogical law; Concept Designer owns the coherent visual system.

Require keyboard-operable controls/selections, readable labels and contrast, information beyond color alone, pause/step/reduced-motion support, and concise accessible descriptions of relationships rather than every sample point. EN/PT-BR must communicate the same quantities and assumptions. Preserve scientific identifiers and avoid unlabelled listening analogies or audio that pretends to reproduce ultrasonic frequencies directly.

## 17. Continuity and boundaries with later labs

| Later experience | Foundation supplied by D1 | Work retained there |
|---|---|---|
| PED-D2 — Pulse and signal processing | Carrier frequency, time record, amplitude, phase and units | Finite duration, bandwidth, CW/chirp, envelope, matched filtering and compression |
| PED-D3 — Sonar equation | Distinct physical quantities, logarithmic reference and level interpretation | Source/received budget, propagation loss, noise, SNR and margins |
| PED-D4 — Refraction | Fixed-medium propagation speed and observation geometry | Sound-speed profiles, refraction and reconstruction error |
| PED-D6/PED-D7 — Arrays and beamforming | Wavelength, local phase and coherent observation vocabulary | Aperture geometry, relative channel timing, interference and steering |
| Subsequent acquisition/integration labs | Controlled reference comparison and quantity/measurement discipline | Their own operational phenomena and decisions |

Do not add bathymetric resolution claims, full sonar budgeting, realistic transducer efficiency, complex ocean propagation or bottom detection merely to make D1 look substantial.

## 18. Scientific and implementation dependencies

Existing kinematics can be reused where it satisfies the target. Exact current capability must be checked; the normalized contract does not already authorize physical pressure, particle motion, intensity or power.

Bounded scientific decisions:
- SQ1: define compatible pressure, particle displacement/velocity and compression representation with units, signs, phase, equilibrium and valid amplitude assumptions.
- SQ2: define acoustic pressure statistics and the bridge or explicit separation from normalized amplitude.
- SQ3: define the minimum reference-medium intensity/power demonstration, including required medium properties and surface/geometry context.
- SQ4: define logarithmic quantities, references, peak/RMS/averaging conventions, valid ratios and zero/undefined behavior.
- SQ5: define coupled control constraints, shared observation time, parameter-change semantics and independent numerical/limiting-case anchors.

Required outputs must remain authoritative in the Scientific Core/API; the frontend may project/animate returned state but must not become a separate acoustic model.

Concept Designer develops a connected scene and observation grammar with unresolved physical outputs marked explicitly. Software Engineering assesses model/API/runtime delivery after the scientific decisions. Production UX implements the approved interaction. QA validates the exact implementation against science, pedagogy and visual requirements.

Scientific questions are prerequisites for implementing the affected physical outputs; they do not prevent publishing this pedagogical target or exploring the already-defined kinematic composition.

## 19. Pedagogical acceptance for the next D1

1. One coherent phenomenon connects the physical scene, fixed probe, spatial snapshot and graphs.
2. A particle is visibly distinct from both the probe and propagation marker.
3. Every displayed field has a declared quantity, units and observation context.
4. Frequency remains the primary physical control; secondary controls are progressively discoverable.
5. Frequency and sound speed produce their correct distinct consequences.
6. Play/pause/step and slowed inspection preserve declared physical relationships.
7. Complete cycles can be observed and measured across supported settings.
8. Reference/current comparisons preserve explicit identity and appropriate shared scales.
9. Pressure/amplitude modes do not invent calibration or change dimensionless values into physical units by relabelling.
10. Pressure, intensity and power are distinguished with approved conditions.
11. Logarithmic displays identify quantity, statistic and reference; undefined cases are handled explicitly.
12. Representation-only changes preserve physical state.
13. Guided tasks elicit prediction, controlled comparison, explanation and transfer.
14. Accessibility and EN/PT-BR preserve the same conceptual distinctions.
15. D2/D3 transitions reuse the vocabulary without reteaching an unrelated version.
16. Required scientific, visual and runtime dependencies are resolved and verified on the exact candidate.
17. Instructor/learner review checks whether the intended explanations can actually be produced.
18. Product Owner accepts the resulting experience.

Until these conditions are demonstrated, the redesigned D1 is specified/in development, not complete. Historical readiness of the older normalized-wave slice remains a separate record.

## 20. Delivery and review sequence

1. Persist the English treatise and the link from the modular D1 specification.
2. Scientific Lead resolves SQ1–SQ5 in a bounded contract/extension with authoritative references and validation anchors.
3. Concept Designer proposes the connected experience and shared observation/control grammar, coordinated with available scientific outputs.
4. Technical Lead sequences the changes and identifies independently deliverable portions without dropping required depth.
5. Core/API and production UX implement the approved treatment.
6. QA verifies the exact candidate, including quantity/phase/time/scale consistency, reference closure and pedagogical consequence.
7. Integrate; conduct the focused instructor/learner review; obtain Product Owner acceptance.
8. Revisit D2 and later labs with the same process. D1 does not pre-decide their complete redesign.

No automatic version number, release, deployment, optimizer or new operational scope is created by this treatise.

## 21. Sources and their use

- Product Owner discussion on 2026-10-16: authority for the new pedagogical direction and next-version intent; recorded in section 1.
- CAHO-AC-01, locators and reading extent in section 4: curricular connection, not a complete course map.
- Existing D1 modular pedagogy, visual brief, scientific contract and production source: inspected baseline, reusable structure and implementation gaps.
- [DOSITS / University of Rhode Island — What is sound?](https://dosits.org/science/sound/what-is-sound/): external teaching reference for connecting medium motion, propagation and sound representation.
- [DOSITS — What is intensity?](https://dosits.org/science/advanced-topics/what-is-intensity/): external teaching reference for the energy-flow distinction.
- [DOSITS — Introduction to Decibels](https://dosits.org/science/advanced-topics/introduction-to-decibels/): external teaching reference for linear quantity versus referenced level. Its simplified exposition is not substituted for the new scientific contract.
- [NPL — Good practice guide for underwater noise measurement, GPG133 (2014)](https://eprintspublications.npl.co.uk/6121/): candidate technical reference for Scientific Lead. Metadata was identified; full text retrieval failed in this cycle, so no new model is claimed to have been validated against it.

The references motivate the treatment. Scientific Lead must document the exact equations, applicability and primary validation sources for the implemented extension.

## 22. Revision record

Revision 1.0, 2026-10-16: initial treatise following Product Owner review of D1; expanded physical/measurement/quantity target; explicit preservation of frequency hierarchy; next-generation visual consistency, learning sequence, dependencies and acceptance.

Revision 1.1, 2026-10-16: Product Owner clarified that all GitHub documentation must be in English. Removed the Portuguese documentation edition; retained English as the default application language and Brazilian Portuguese as an optional presentation locale.
