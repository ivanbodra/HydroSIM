# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product indicators

The active roadmap contains 31 learner-facing submodules:

- `PED-D1`–`PED-D18`: Didactic Module
- `P1`–`P6`: Patch Test Module
- `A1`–`A7`: Acquisition Simulator

**Submodule indicator: 3/31 ready submodules.**

Ready submodules:

- `PED-D1` — Wave Fundamentals. Runnable bilingual React experience on `main`, canonical Python wave-kinematics API, focused learner-facing UI/state validation integrated through PR #153, and independent scientific/computational QA PASS in Issue #148 with no material finding.
- `PED-D2` — Signal Types & Pulse Compression. Runnable bilingual React experience on `main` using the canonical Python signal API, focused learner-facing validation and real React + Python API end-to-end runtime evidence through PR #154, and independent narrow scientific/computational QA PASS in Issue #162 with no material finding.
- `PED-D3` — Sonar Equation & Propagation Loss. Runnable bilingual production React experience on `main`, focused learner-facing validation, canonical Python sonar-equation API, and risk-proportionate independent QA closure in Issue #155. QA reused the previously validated D3 physics from #97 and checked only the new React/API boundary, finding no material scientific/computational risk.

**Atom indicator: not yet reportable because the canonical all-roadmap learner input/output inventory has not yet been completed.** The denominator must not be inferred from contracts, APIs, tests, PRs, or broad content labels. Until every planned learner input and learner-visible output across the 31-submodule roadmap has an explicit inventory entry, no atom percentage is authoritative.

This is a baseline deficiency, not zero product functionality. Existing production learner controls and outputs remain real functionality but are not to be counted against an invented denominator.

## Completion rule

A submodule enters the numerator only when its complete required Learning, Scientific and Visualization behavior is runnable bilingually on `main`, with focused tests and only the risk-proportionate independent QA actually warranted.

A learner atom is one functional learner input or one functional learner-visible output in the production path. Contracts, documentation, APIs, adapters, tests, PRs, CI, infrastructure, screenshots and coordination tasks are enabling work and are not atoms.

Every visible scientific quantity must trace to a Scientific Contract output.

## Delivery strategy

Build outside-in until the scientific boundary, then complete submodules vertically.

1. Product shell: Home/System Map → Didactic / Patch Test / Acquisition, with all 31 entries and explicit availability state.
2. Scientific submodules: complete one submodule through science → application/visualization → UX → focused validation → integration before counting it.
3. Keep the active pipeline small (normally 2–3 results in flight). Do not create horizontal implementation inventories merely to generate work.
4. The atom inventory is a measurement baseline: it must describe planned learner-facing inputs/outputs, not create new implementation scope.

## Current pipeline

- `PED-D4` — nearest incomplete production submodule and next readiness target.
- `PED-D7` — QA-found Port/Starboard TX-sector identity defect corrected on `main` through PR #185 / squash `a20f377aef4dbd050d18ab97057c381a9f9bf8b7`; production learner PR #186 must be reconciled and tested against this corrected baseline before integration. Existing QA #107 is limited to narrow post-fix confirmation.
- `PED-D8` — minimal application/API bridge is active in Issue #187 and remains downstream of nearer learner-facing completion work.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

The former eight-submodule `V01-D*` inventory is historical and must not be used as a current product indicator.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
