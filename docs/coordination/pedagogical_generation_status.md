# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product indicators

The active roadmap contains 31 learner-facing submodules:

- `PED-D1`–`PED-D18`: Didactic Module
- `P1`–`P6`: Patch Test Module
- `A1`–`A7`: Acquisition Simulator

**Submodule indicator: 4/31 ready submodules (12.9%).**

Ready submodules:

- `PED-D1` — Wave Fundamentals. Runnable bilingual React experience on `main`, canonical Python wave-kinematics API, focused learner-facing UI/state validation integrated through PR #153, and independent scientific/computational QA PASS in Issue #148 with no material finding.
- `PED-D2` — Signal Types & Pulse Compression. Runnable bilingual React experience on `main` using the canonical Python signal API, focused learner-facing validation and real React + Python API end-to-end runtime evidence through PR #154, and independent narrow scientific/computational QA PASS in Issue #162 with no material finding.
- `PED-D3` — Sonar Equation & Propagation Loss. Runnable bilingual production React experience on `main`, focused learner-facing validation, canonical Python sonar-equation API, and risk-proportionate independent QA closure in Issue #155.
- `PED-D4` — Sound Speed & Refraction. Runnable bilingual production React experience on `main` via PR #165, focused learner-facing tests, canonical Python refraction bridge/Core, and narrow independent QA PASS in Issue #170.

**Atom indicator: 34/243 ready learner atoms (14.0%).**  
Canonical denominator and counting rules: `docs/coordination/product_atom_inventory.md`.

The atom inventory contains 144 learner inputs and 99 learner-visible outputs. Readiness is conservative: partial atoms are counted only with production-path evidence on `main`; enabling work is never counted as product atoms.

## Completion rule

A submodule enters the numerator only when its complete required Learning, Scientific and Visualization behavior is runnable bilingually on `main`, with focused tests and only the risk-proportionate independent QA actually warranted.

A learner atom is one functional learner input or one functional learner-visible output in the production path. Contracts, documentation, APIs, adapters, tests, PRs, CI, infrastructure, screenshots and coordination tasks are enabling work and are not atoms.

Every visible scientific quantity must trace to a Scientific Contract output.

## Delivery strategy

Build outside-in until the scientific boundary, then complete submodules vertically.

1. Product shell: Home/System Map → Didactic / Patch Test / Acquisition, with all 31 entries and explicit availability state.
2. Scientific submodules: complete one submodule through science → application/visualization → UX → focused validation → integration before counting it.
3. Keep the active pipeline small (normally 2–3 results in flight). Do not create horizontal implementation inventories merely to generate work.
4. Maintain `product_atom_inventory.md` as a measurement baseline; it describes planned learner-facing inputs/outputs and must not create implementation scope by itself.

## Current pipeline

- `PED-D7` — nearest completion target. The Port/Starboard TX-sector correction is on `main` through PR #185. The obsolete concept-sandbox production attempt PR #186 is closed without merge. UX rebuilt the learner slice in the correct production location under `web/pedagogical-explorer/` as PR #193, based on the corrected mainline. Integrate #193 after its focused production frontend gates are green. Issue #107 remains only the already-defined narrow post-fix scientific confirmation; do not broaden it.
- `PED-D8` — canonical application/API bridge integrated through PR #190 / squash `8192ac0f0f54cc795868f6a0d2e0201e39708bca`. Production UX delivery is active in Issue #191 under `web/pedagogical-explorer/`, preserving the Concept sandbox.
- `PED-D6` — retain only already-active near-term work; do not expand WIP while D7/D8 are the shortest completion paths.

## Design / implementation boundary

- `concepts/pedagogical-simulator/` is the preserved approved Concept Simulator design baseline.
- `web/pedagogical-explorer/` is the production learner application.
- Routine production work must not alter the Concept baseline. UX implements the approved design language in production while canonical Python Core/API remains scientific authority.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

The former eight-submodule `V01-D*` inventory is historical and must not be used as a current product indicator.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
