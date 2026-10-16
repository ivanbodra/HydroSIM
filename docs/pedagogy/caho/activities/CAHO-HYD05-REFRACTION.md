# CAHO-HYD05-REFRACTION — From sound-speed profile to sounding position

Status: proposed instructor-guided pilot activity using existing PED-D4.
Treatment: **full laboratory activity around an existing interactive demonstration**.
No new laboratory ID, scientific model, API, frontend feature or release certification is created.

## CAHO connection and sources

- Subject: Hidrografia.
- Lesson: Aula 5 — Velocidade do Som e Refração (5ha).
- Primary material: CAHO-HYD-05, exact path/hash in source_inventory.csv and reading_log.md.
- Explicit objective: p.2 links sound-speed profile to the acoustic path and georeferenced bathymetry.
- Lesson segments: pp.27–28 application; pp.30–43 refraction/ray tracing; p.51 prediction-before-simulation task; pp.53–54 debrief.
- This activity selects the water-column part of p.51. It does not claim to cover that slide's independent surface-speed or uncertainty experiments.

Title for learners in PT-BR: **Do perfil de velocidade do som à posição da sondagem**.

## Target learners and prior knowledge

CAHO officers during/after lesson 5's ray-tracing explanation. Required: distinction between angle and travel time, sound-speed profile as a function of depth, and prior beam/detection vocabulary recalled in the lesson's pp.4–5.

The teacher confirms these prerequisites with one sketch, not a lengthy recap. No assumed ability to operate CARIS or write a ray tracer is required.

## Learning problem

Pedagogical hypothesis: students can recognize a curved ray but may conflate a real change in the water column with processing the same observation through an incorrect profile. A second risk is interpreting visible endpoint mismatch as a measured uncertainty or as a unique diagnostic signature.

This hypothesis has not been confirmed by a CAHO learner study.

## Learning objectives

After the activity the learner can:
1. Predict whether a homogeneous or layered sound-speed description produces a straight or refracted path within the displayed model.
2. Distinguish changing the physical reference profile from changing only the reconstruction profile.
3. Compare reference and reconstructed endpoints for the same reference observation using displayed Δx and Δz.
4. Explain the effect of increasing beam obliquity in the bounded example without inventing a universal error sign.
5. Justify checking the environmental description when reconstructed geometry is inconsistent, while recognizing that a visual artifact alone does not establish a unique cause.

## Central phenomenon and pedagogical question

A reference water column generates the path/travel time; a processing profile reconstructs that observation. A mismatched profile can move its inferred endpoint.

**Question:** If the observation is unchanged, why can using a different sound-speed profile place the sounding at a different location?

## Learner inputs and current interface boundary

Production route: `#refraction-lab`; component: `web/pedagogical-explorer/src/RefractionLab.tsx`.
Inspected implementation: `eed7bedc19f654b9adc13275a249a57576720e5d`.

Meaningful existing controls:
- scenario: constant, layered, profile mismatch;
- launch angle: 5–60 degrees from vertical;
- lower reference-layer speed: 1460–1560 m/s, step 2;
- lower processing-layer speed: same supported range;
- reset.

In the inspected interface the upper layer is 0–50 m at 1500 m/s, the lower layer extends to 150 m, and the reference bottom target is 100 m. These are interface/model choices, not CAHO-prescribed ocean conditions.

There is no independent transducer-face speed control in this path. Do not relabel a lower-layer profile slider as the SV sensor. Do not ask the student to edit arbitrary layer thickness, range-dependent profiles, continuous gradients or target depth through controls that are not exposed.

## Learner-visible outputs

Use the existing connected scene:
- c(z) reference/processing profiles;
- physical reference and reconstructed ray paths;
- fixed reference bottom and endpoint separation;
- Δx/Δz, path length and travel-time readouts;
- error-versus-angle samples as supporting evidence.

The source-level sweep plot rescales its ordinate to the current maximum. Compare **numeric error values and the fixed geometry scene** between configurations, not normalized curve heights. Within one fixed-profile sweep the angle trend remains a usable comparison. Do not describe it as a fixed-scale inter-configuration error chart.

## Reference and comparison states

- **R0:** constant 1500 m/s, angle 30 degrees.
- **R1:** two-layer reference, lower speed 1540 m/s, angle 30 degrees.
- **R2:** same reference as R1; processing lower speed also 1540 m/s.
- **C1:** keep the R1 reference/angle; change only processing lower speed to 1500 m/s.
- **C2:** keep the R1 reference/angle; change only processing lower speed to 1560 m/s.
- **C3:** repeat a selected mismatch at 15, 30 and 60 degrees; record each numerical comparison.
- **Closure:** restore the processing lower speed to 1540 m/s.

R1 is a synthetic physical reference declared for this teaching case. It is not a measured operational profile or an estimated seafloor. C1/C2 compare processing alternatives for the same reference observation at a fixed angle. When C3 changes the angle, a different reference ray/observation is generated; do not say all angle trials share one travel time.

## Learning sequence

Proposed duration: 20–25 minutes, to be adjusted after instructor feedback.

| Stage | Teacher/learner action | Observable evidence |
|---|---|---|
| Observe | Identify the profile, vertical angle, interface, ray and bottom in R0 | Learner locates the reference endpoint and describes what is constant |
| Predict | Before R1, sketch how the path changes across a faster lower layer | A recorded prediction exists before manipulating the slider |
| Manipulate | Select the layered case and set R1; then enter the matched comparison R2 | Student separates reference environment from processing state |
| Compare | Run C1/C2 while keeping the reference fixed | Table records processing speed, Δx and Δz; physical reference ray remains unchanged |
| Explain | Use the profile/ray/endpoint chain to explain why the observed travel-time reconstruction moves | Student explains the mechanism rather than naming a slider |
| Apply | Run C3, then choose a defensible environmental-check response for a wider-swath survey | Written interpretation names obliquity, the modeled effect and what remains uncertain |
| Close | Restore matched profiles and compare to R2 | Visible endpoint/error closure within the application’s numerical tolerance |

No predetermined numerical answers are published here. Values must come from the canonical application response when the experiment is run.

## Guidance and scaffolding

Use these PT-BR prompts in spoken guidance or a classroom observation sheet; adding them to the production UI is a separate implementation decision.

- “Qual perfil representa a água neste exercício? Qual é usado apenas na reconstrução?”
- “Antes de alterar: o que você espera que mude na trajetória e no ponto final?”
- “Ao mudar só o processamento, o perfil físico de referência mudou?”
- “Compare os valores de Δx e Δz, não apenas a aparência do gráfico.”
- “O que este resultado permite afirmar? Que outras causas ele não elimina?”

Show one parameter at a time. Begin with matched profiles and make the mismatch deliberate. The teacher supplies help after the learner's prediction rather than replacing it.

## Misconceptions and correction opportunities

| Likely interpretation | How the activity challenges it |
|---|---|
| A processing slider changes the actual water | The reference ray/profile stays fixed during C1/C2 |
| More speed always creates a particular smiling/crying sign | Every result is tied to declared geometry/profile; the learner reports observed Δx/Δz without universalizing |
| A ray-polyline kink means the physical ocean has a sharp temperature boundary | Explain the finite piecewise-constant sound-speed approximation |
| Large mismatch is the measurement's formal uncertainty | Identify it as simulation-truth reconstruction error in this case |
| Repeated sweep curves with the same height imply the same error | Compare numeric maximum/error values because the sweep ordinate rescales |
| SV at the transducer is interchangeable with the profile | Explicitly state that the separate steering experiment is outside this activity |
| A visually plausible explanation proves the cause of a field artifact | Final task requires a limitation and a further check |

## Assessment evidence

Collect one short observation sheet per learner/pair:
- initial prediction/sketch;
- table for R2, C1/C2 and the selected C3 angle trials;
- explanation linking profile, path and endpoint;
- operational decision plus one limitation;
- matched-profile closure.

Suggested pedagogical rubric: satisfactory when the learner distinguishes reference from reconstruction, explains the controlled comparison, interprets numerical error correctly and avoids a unique-cause/uncertainty claim. Incorrect prediction alone is not failure if the learner reconciles it with the evidence and revises the explanation.

This is formative learning evidence, not certification of field competence or successful operational calibration.

## Scientific sources and model boundaries

Existing project authorities:
- `docs/science/ped_d4_scientific_contract.md`;
- `docs/science/sound_speed_at_transducer.md` for the separate boundary distinction;
- `docs/pedagogy/acoustic_lab/D04_sound_speed_refraction.md`;
- `docs/design/acoustic_lab/D04_sound_speed_refraction_visual.md`;
- registered model `hydrosim.propagation.layered_snell_piecewise_constant`;
- `src/hydrosim/acquisition/layered_propagation.py`.

The primary curricular evidence is CAHO-HYD-05; it does not replace those scientific sources. Their existing external references remain authoritative; this activity adds no new scientific claim.

Boundaries: geometrical acoustics, horizontally stratified finite constant-speed layers, 2-D downward propagation and the solver's stated validity range. No continuous-gradient, turning/critical branch, multipath, environmental forecast, absorption, formal uncertainty or range-dependent ocean model is added.

The interface travel-time readout must be interpreted according to the Core's ray definition. Do not equate it to measured TWTT or silently add a factor of two. The lesson's reciprocal-path/TWTT discussion needs an explicit convention explanation when connecting this bounded ray experiment to two-way acquisition.

## Why interaction is useful here

The course already has static diagrams and an explicit prediction/simulation exercise. Independent manipulation of the processing profile while preserving the reference lets the student test a causal claim that a single diagram cannot establish as clearly. The added value is the controlled comparison and explanation task, not decorative movement or replacing the existing SVP practical.

## Implementation dependencies and readiness

No new Core/API capability is required for the column-profile pilot:
- consume `POST /api/v1/pedagogical/refraction`;
- preserve existing matched/mismatched states, reference geometry and canonical Δx/Δz;
- instructor supplies prompts and the observation sheet outside the application.

Before using the pilot, verify the exact deployed/local application starts, the route/API responds, the three scenarios produce visible comparisons and reset/matched closure works. This cycle inspected source code and existing contracts; it did not run the application or claim independent QA validation.

Any request for independent surface-speed controls, arbitrary profiles, fixed-scale sweep comparison or integrated uncertainty must be separately scoped and sequenced through the responsible specialist. None is an implicit requirement of this classroom wrapper.

## Pedagogical acceptance criteria

1. The learner can identify which profile is physical reference and which is processing.
2. A prediction is recorded before each principal comparison.
3. Changing only the processing profile leaves the reference case/observation fixed at that angle.
4. Reference and reconstruction are visible together with numeric endpoint differences.
5. Matching profiles closes the endpoint mismatch within the canonical numerical tolerance.
6. Angle trials are compared using stated numeric values and geometry, without normalized-height or universal-sign conclusions.
7. The learner explains one operational implication and at least one model/diagnostic limit.
8. Surface steering, formal uncertainty and complete acquisition are explicitly left to their appropriate activities.
9. A teacher can complete the sequence in a normal lesson segment without additional scientific implementation.
10. Classroom pilot findings are recorded before claiming the activity is pedagogically complete.
