# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product indicators

The active roadmap contains 31 learner-facing submodules: `PED-D1`–`PED-D18`, `P1`–`P6`, `A1`–`A7`.

**Submodule indicator: 14/31 ready submodules (45.2%).**

Ready submodules: `PED-D1`, `PED-D2`, `PED-D3`, `PED-D4`, `PED-D6`, `PED-D7`, `PED-D8`, `PED-D9`, `PED-D10`, `PED-D11`, `PED-D12`, `PED-D14`, `PED-D15`, `PED-D18`.

**Atom indicator: 145/243 ready learner atoms (59.7%).**
Canonical denominator and atom-by-atom evidence: `docs/coordination/product_atom_inventory.md`.

## Completion rule

A submodule enters the numerator only when its complete required Learning, Scientific and Visualization behavior is runnable bilingually on `main`, with focused tests and only the risk-proportionate independent QA actually warranted.

A learner atom is one functional learner input or one functional learner-visible output in the production path. Contracts, documentation, APIs, adapters, tests, PRs, CI, infrastructure, screenshots and coordination tasks are enabling work and are not atoms.

Every visible scientific quantity must trace to a Scientific Contract output.

## Delivery strategy

Build outside-in until the scientific boundary, then complete submodules vertically. Keep the active pipeline small and prefer completing near-ready learner slices over opening speculative horizontal work.

## Current pipeline

- `PED-D9` is complete at 11/11 after PR #341 integrated learner-operable phase-based High Density and its distinct comparison/consequence through the authoritative API.
- `PED-D17` remains the nearest partial submodule at 8/14 and is the next completion-oriented learner slice unless a concrete dependency blocks it.
- `PED-D13` remains dependent on its scientific definition; do not serialize independent PED-D17 work behind it.
- `PED-D5` and `PED-D16` remain unstarted in the canonical atom inventory; do not open them merely to increase WIP.

## Design / implementation boundary

- `concepts/pedagogical-simulator/` is the preserved approved Concept Simulator design baseline.
- `web/pedagogical-explorer/` is the production learner application.
- Routine production work must not alter the Concept baseline. UX implements the approved design language in production while canonical Python Core/API remains scientific authority.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
