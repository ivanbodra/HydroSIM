# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product indicators

The active roadmap contains 31 learner-facing submodules:

- `PED-D1`–`PED-D18`: Didactic Module
- `P1`–`P6`: Patch Test Module
- `A1`–`A7`: Acquisition Simulator

**Submodule indicator: 7/31 ready submodules (22.6%).**

Ready submodules:

- `PED-D1` — Wave Fundamentals. Runnable bilingual React experience on `main`, canonical Python wave-kinematics API, focused learner-facing UI/state validation integrated through PR #153, and independent scientific/computational QA PASS in Issue #148 with no material finding.
- `PED-D2` — Signal Types & Pulse Compression. Runnable bilingual React experience on `main` using the canonical Python signal API, focused learner-facing validation and real React + Python API end-to-end runtime evidence through PR #154, and independent narrow scientific/computational QA PASS in Issue #162 with no material finding.
- `PED-D3` — Sonar Equation & Propagation Loss. Runnable bilingual production React experience on `main`, focused learner-facing validation, canonical Python sonar-equation API, and risk-proportionate independent QA closure in Issue #155.
- `PED-D4` — Sound Speed & Refraction. Runnable bilingual production React experience on `main` via PR #165, focused learner-facing tests, canonical Python refraction bridge/Core, and narrow independent QA PASS in Issue #170.
- `PED-D7` — Beamforming & Electronic Steering. Production learner experience integrated under `web/pedagogical-explorer/` through PR #193 / merge `5e5788cef23599247d158d687997ff1599df3607`, consuming the canonical Python beamforming API and preserving the Concept baseline. The previously identified Port/Starboard identity defect was corrected on `main`, and narrow independent confirmation #107 is complete.
- `PED-D8` — Echosounders — SBES vs MBES. Production bilingual learner experience integrated under `web/pedagogical-explorer/` through PR #192 / merge `176d4331ff5e560cbdf498a6540b9269d88de397`, consuming the canonical echosounders API and preserving the Concept baseline.
- `PED-D10` — Multisector MBES. Complete inventoried learner-facing slice is integrated bilingually on `main` through PR #221, consuming the canonical Python multisector capability with focused production validation; all 10 inventoried learner atoms are ready.

**Atom indicator: 100/243 ready learner atoms (41.2%).**  
Canonical denominator and atom-by-atom evidence: `docs/coordination/product_atom_inventory.md`.

The atom inventory contains 144 learner inputs and 99 learner-visible outputs. Enabling work is never counted as product atoms.

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

- `PED-D1`, `PED-D2`, `PED-D3`, `PED-D4`, `PED-D7`, `PED-D8` and `PED-D10` are complete and no longer pipeline work.
- `PED-D6` is one atom short of its inventory; `I06 eccentricity` remains unresolved and is routed to the Scientific Lead in Issue #232.
- `PED-D9`, `PED-D11`, `PED-D12` and `PED-D17` have partial learner-facing production readiness recorded atom-by-atom in `product_atom_inventory.md`; their remaining behavior must not be inferred from backend or documentation alone.
- Keep the next independent specialist slice in parallel when a concrete unblocked dependency exists; do not create speculative horizontal inventory.

## Design / implementation boundary

- `concepts/pedagogical-simulator/` is the preserved approved Concept Simulator design baseline.
- `web/pedagogical-explorer/` is the production learner application.
- Routine production work must not alter the Concept baseline. UX implements the approved design language in production while canonical Python Core/API remains scientific authority.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

The former eight-submodule `V01-D*` inventory is historical and must not be used as a current product indicator.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
