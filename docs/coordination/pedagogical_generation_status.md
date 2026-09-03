# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product denominator

HydroSIM active product completion is measured against 31 pedagogical experiences:

- `PED-D1`–`PED-D18`: Didactic Module
- `P1`–`P6`: Patch Test Module
- `A1`–`A7`: Acquisition Simulator

Current certified completion: **2/31**.

Certified experiences:

- `PED-D1` — Wave Fundamentals. Runnable bilingual React experience on `main`, canonical Python wave-kinematics API, focused learner-facing UI/state validation integrated through PR #153, and independent scientific/computational QA PASS in Issue #148 with no material finding.
- `PED-D2` — Signal Types & Pulse Compression. Runnable bilingual React experience on `main` using the canonical Python signal API, focused learner-facing validation and real React + Python API end-to-end runtime evidence through PR #154, and independent narrow scientific/computational QA PASS in Issue #162 with no material finding.

This does not discard reusable prototype work. Reuse readiness is diagnostic only and does not count as completion.

## Completion rule

An experience is complete only when its Learning, Scientific and Visualization contracts are satisfied in a runnable bilingual implementation on `main`, with focused tests and QA where scientific/computational risk warrants it.

Every visible scientific quantity must trace to a Scientific Contract output.

## Delivery strategy

Build outside-in until the scientific boundary, then complete experiences vertically.

1. Product shell: Home/System Map → Didactic / Patch Test / Acquisition, with all 31 entries and explicit availability state.
2. Scientific experiences: complete one experience through science → application/visualization → UX → focused validation → integration before counting it.
3. Keep the active pipeline small (normally 2–3 results in flight). Do not create horizontal implementation inventories for all 31 experiences.

## Current pipeline

- `PED-D3` — primary certification target. Production React Sonar Equation learner experience and focused learner validation are on `main`; narrow independent scientific/computational certification is pending in Issue #155.
- `PED-D4` — production React Sound Speed & Refraction integration is active in Issue #163 against the canonical bridge already on `main`.
- `PED-D6` — downstream-ready application/API work is active in Issue #159 and must remain secondary to completion of the nearer D3/D4 vertical slices.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

The former eight-submodule `V01-D*` inventory is historical and must not be used as the active product denominator.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
