# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product denominator

HydroSIM active product completion is measured against 31 pedagogical experiences:

- `PED-D1`–`PED-D18`: Didactic Module
- `P1`–`P6`: Patch Test Module
- `A1`–`A7`: Acquisition Simulator

Current certified completion: **0/31**.

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

- Product shell / bilingual navigation — `interface-ux`, Issue #112.
- Localization engineering support only if concretely needed — `software-engineering`, Issue #113.
- First scientific experience contracts — activated by Technical Lead as the shell advances.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

The former eight-submodule `V01-D*` inventory is historical and must not be used as the active product denominator.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
