# Prioritized CAHO support roadmap

Status: initial pedagogical priorities grounded in the materials read on 2026-10-16; not an implementation release order.
Source/locator definitions: curriculum_map.md and reading_log.md.

## Priority basis

This ranking considers relevance to explicit objectives, visual difficulty, operational importance, misconceptions, added value over existing class resources, scientific reuse, feasibility/cost, prerequisites, direct classroom use and later study. Misconceptions below are **pedagogical hypotheses**, not measured CAHO student performance. No invented survey of learners or cost estimate is used.

| Priority / grouping | Course evidence and learning need | Proposed treatment / existing capital | Added value and limits | Next bounded work |
|---|---|---|---|---|
| 1 — Essential classroom support | HYD-05 p.2 objective and p.51 prediction-before-simulation exercise; pp.30–43 profile/reconstruction relationship | Guided full activity using PED-D4; specification in activities/CAHO-HYD05-REFRACTION.md | Compare matched/mismatched endpoints under controlled conditions; existing source/API path minimizes new work. Surface-speed, uncertainty and arbitrary profile exercises are not covered by this pilot | Instructor-guided pilot after a focused runtime check; record whether students distinguish physical path from reconstruction |
| 2 — Essential classroom support | HYD-09 pp.2, 16–33 distinguishes pulse duration, bandwidth, CW/chirp and processing | Short interactive demonstration in PED-D2, building on PED-D1 | Learner predicts before changing pulse controls. Course already has MATLAB/videos; compare their purpose and avoid duplicating a demonstration without gain | Read PDS Aula 3 and existing Matched Filter/Chirp examples, then specify one bounded comparison |
| 3 — Essential classroom support | HYD-09 pp.34, 48–55, 65–68 links settings to resolution/density and sampling distribution | Full activity in PED-D17 with selected PED-D8/PED-D9 references | Make footprint support, sample count, spacing and resolution visibly distinct. More sounds/points must not be presented as more independent resolution or guaranteed detection | Verify the exact current learner controls and prepare a two-configuration decision task; no automatic ping-rate solver |
| 4 — Essential operational preparation | HYD-12 pp.2, 23, 27–30, 68–74 connects prerequisites, line planning, correction and subsequent SIS/CARIS practice | Integrated P1–P5 activity before and after the existing software practical | Geometry makes biases observable; holdout/repeat evidence tests acceptance. High operational value, but current exact runtime path and data transfer require checking | Read the practical instructions, spreadsheet and selected calibration data provenance; then write a lesson wrapper, preserving current science |
| 5 — High-value complement | AC-01 pp.29–38 and 49–52 introduces wave variables and phase-dependent interference | Short PED-D1 demonstration; later reuse PED-D6/PED-D7 | Minimal prerequisite burden; useful as retrieval/review. Existing animation references may already suffice for some concepts | Read acoustic units 1.1/1.2 and transducer lesson before adding a separate interference experience |
| 6 — High-value complement, mapping pending | Visible Hydro lessons 6, 10, 11 and 19 cover motion, installation, offsets and protocols | PED-D11/PED-D12/PED-D13/PED-D14; static annotated frames where sufficient | Likely strong spatial/timing value, but class objectives and existing exercises remain unread | Read lesson 11's offset exercise and lesson 19's communication task; choose the smallest treatment |
| 7 — Advanced/integrative | HYD-12 pp.7–10 distinguishes dynamic residuals from constant biases | Optional P6 visualize_only demonstration; later acquisition synthesis | P6 can illustrate model consequences, not a unique diagnosis. It is not explicitly named in the course material, and #605 blocks current visual readiness | Keep as an optional pedagogical extension; wait for the exact UX correction/QA evidence |
| Deferred scope evaluation | Visible lessons on SSS, sub-bottom, alternative bathymetry, autonomous systems, applied tide and broader positioning | Static visual / guided animation / no treatment until reading; new simulation only if justified | Course breadth is not automatic product scope. Existing class diagrams/video may be better | Read objectives and a representative example; submit a specific extension rationale to the Product Owner if needed |

Priority numbers sequence pedagogical analysis, not the chronological order of CAHO classes. The instructor's actual timetable and student prerequisites determine when to use each activity. Avoid planning a lower-priority new implementation while a higher-value existing demonstration can satisfy the same lesson.

## First activity and release boundary

`CAHO-HYD05-REFRACTION` is a classroom wrapper for existing PED-D4:
- use the currently supported constant/two-layer/mismatch cases;
- ask for prediction, controlled manipulation, comparison, explanation and an operational interpretation;
- keep independent transducer-face sound-speed and formal uncertainty experiments outside this activity;
- rely on the teacher for prompts and the learner's observation table; no new frontend behavior is required by this specification.

Its implementation scope is therefore unblocked at the documentation level. Classroom availability still requires a current local/integrated runtime check; this analysis did not execute the application. Proposed timing and assessment are hypotheses to pilot.

## Concrete gaps and their owners

| Gap | Evidence | Disposition / owner |
|---|---|---|
| Separate surface-speed experiment absent from the inspected PED-D4 interface | HYD-05 pp.45–47, 51 vs RefractionLab.tsx controls | caho-pedagogy maps it as a separate activity; Technical Lead sequences a future exact capability inquiry if selected |
| Complete 2026 course timetable and full curriculum not established | Shared collection, not a formal syllabus | caho-pedagogy locates a syllabus/teaching plan if available; otherwise keeps the limitation explicit |
| Materials of mixed dates and two resolution presentations | File titles and observed folder metadata | caho-pedagogy compares contents before declaring replacement/precedence |
| Simplified density/ping-rate relations in class cannot be lifted directly into UI physics | HYD-09 p.48 and current coverage-density contract | Existing Scientific Core governs; Scientific Lead only if a new achievable-cadence model becomes necessary |
| Alternative Patch Test orders and heading geometries need explicit convention handling | HYD-12 pp.32, 54–58, 68–69 | Existing contract remains valid for its stated case; do not grade other methods as physically wrong or implement them without a bounded scientific decision |
| Full professional-software practical not yet analyzed | HYD-12 p.73; calibration-data and video folders listed | caho-pedagogy reads the assignment before specifying interoperability or assessment claims |
| P6 visual defect already has an owner | #605 at the inspected #602 head | interface-ux then exact-head QA; do not duplicate the request |
| Draft handout incompleteness | Handout pp.4, 282–285 | Use actual class presentations; distinguish missing handout text from absent instruction |

No new scientific, visual or implementation handoff is opened merely because a topic appears here. The current executable cross-role request is integration of the source-backed records; subsequent handoffs must name one approved capability/artifact and its completion condition.

## Next progressive reading cycle

1. Acoustic refraction/velocity/ray-tracing lessons: connect disciplinary foundations to Hydro lesson 5; identify exactly what the classroom simulator already covers.
2. PDS Aula 3 and the resolution matched-filter/chirp materials: inspect current activities before writing a PED-D2 classroom wrapper.
3. Offset exercise and Patch Test practical guidance: connect the verified theory to the actual assignment, without substituting HydroSIM for SIS/CARIS.
4. Survey planning lesson 23 and S-44 lesson: establish the task/quality requirements before proposing integrated scenarios.
5. Motion/protocol lessons and the remaining broader-course topics.

Update the reading log and source rows incrementally. Read only the relevant modular HydroSIM specification and dependent science contracts for each activity. Do not rebuild one monolithic course document.

## Completion of this initial cycle

Completed: supplied folder access; initial subject/source inventory; explicit acoustic-unit structure and hydrography lesson outline; source-backed subset of existing-lab connections; treatment classification; prioritized analysis/reuse roadmap; one bounded classroom specification.

Still open: remaining source reading, complete official syllabus identification, full visual/video review, exact integrated runtime readiness, instructor/learner pilot feedback and any later implementation approval. No course-coverage or readiness percentage follows from this checkpoint.
