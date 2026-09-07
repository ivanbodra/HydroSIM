# HydroSIM Pedagogical Generation — Delivery Baseline

Status: canonical coordination baseline

## Product indicators

The active roadmap contains 30 learner-facing submodules: 17 active Didactic submodules (`PED-D1`–`PED-D18`, excluding retired `PED-D5`), `P1`–`P6`, and `A1`–`A7`.

**Submodule indicator: 16/30 ready submodules (53.3%).**

Ready submodules: `PED-D1`, `PED-D2`, `PED-D3`, `PED-D4`, `PED-D6`, `PED-D7`, `PED-D8`, `PED-D9`, `PED-D10`, `PED-D11`, `PED-D12`, `PED-D13`, `PED-D14`, `PED-D15`, `PED-D17`, `PED-D18`.

**Atom indicator: 161/238 ready learner atoms (67.6%).**
Canonical denominator and atom-by-atom evidence: `docs/coordination/product_atom_inventory.md`.

`PED-D5 — Acoustic Detection Fundamentals` was retired as a standalone submodule by Product Owner decision on 2026-09-06. Its former objectives are explicitly redistributed to PED-D2, PED-D3 and PED-D9; the five retired D5 atoms are not counted again because their learner behavior is already represented by receiving atoms in those submodules.

## Completion rule

A submodule enters the numerator only when its complete required Learning, Scientific and Visualization behavior is runnable bilingually on `main`, with focused tests and only the risk-proportionate independent QA actually warranted.

A learner atom is one functional learner input or one functional learner-visible output in the production path. Contracts, documentation, APIs, adapters, tests, PRs, CI, infrastructure, screenshots and coordination tasks are enabling work and are not atoms.

Every visible scientific quantity must trace to a Scientific Contract output.

## Delivery strategy

Build outside-in until the scientific boundary, then complete submodules vertically. Keep the active pipeline small and prefer completing near-ready learner slices over opening speculative horizontal work.

## Current pipeline

- `PED-D17` is complete at 14/14 after PR #346 integrated High Density, ping-rate/speed, coverage/gaps and along/across density through authoritative API outputs.
- `PED-D16` is the only remaining active Didactic submodule not ready in the canonical inventory and is now the shortest path to Didactic functional completion.
- `PED-D5` is retired, not unstarted: its former learning objectives are redistributed and traceable in the canonical inventory.
- Patch Test implementation remains gated by #359 until Didactic completion, stabilization, Product Owner review and explicit transition authorization.

## Design / implementation boundary

- `concepts/pedagogical-simulator/` is the preserved approved Concept Simulator design baseline.
- `web/pedagogical-explorer/` is the production learner application.
- Routine production work must not alter the Concept baseline. UX implements the approved design language in production while canonical Python Core/API remains scientific authority.

## Historical boundary

`v0.0.1-prototype` preserves the pre-transition Didactic Explorer prototype at commit `d76c4222959afc5be119e8941173c4a67ddddb76`.

## UX / terminology rule

All learner-facing text, plots, axes, legends, annotations and contextual help must be localizable EN/PT-BR from the outset. Established technical terms such as Roll, Pitch, Heave, Yaw and Heading remain in English in the PT-BR UI; the first pedagogical occurrence provides a concise Portuguese explanation through tooltip/context help, with touch/click equivalent.
