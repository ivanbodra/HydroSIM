# HydroSIM Module Identifier Policy

Status: canonical coordination policy

## Purpose

HydroSIM has a historical prototype decomposition and a new pedagogical-generation curriculum. Their identifiers must remain unambiguous without rewriting historical Issues, PRs, commits, contracts, or validation evidence.

## Canonical namespaces

- `V01-D1` ... `V01-D8` — historical prototype inventory established through Issue #46. Preserve for traceability only.
- `PED-D1` ... `PED-D18` — Didactic Module experiences in `docs/pedagogy/hydrosim_pedagogical_plan.md`.
- `P1` ... `P6` — Patch Test experiences.
- `A1` ... `A7` — Acquisition Simulator experiences.

Do not create new bare `D<number>` references. Use semantic names with identifiers where practical.

## Historical prototype inventory

| Historical ID | Submodule |
|---|---|
| `V01-D1` | Signal |
| `V01-D2` | Beam Pattern |
| `V01-D3` | Sonar Equation / Acoustic Losses |
| `V01-D4` | Sound Velocity & Refraction |
| `V01-D5` | Vessel / Sensors / Vertical References |
| `V01-D6` | Motion |
| `V01-D7` | Sonar Systems & Geometry |
| `V01-D8` | Sounding Formation / Detection Chain |

Issue #28 and the 8-submodule completion indicator are historical coordination evidence. They no longer define the active product roadmap. Existing work remains reusable where it satisfies the new contracts.

## Active pedagogical generation

The active product denominator is 31 experiences:

- Didactic Module: `PED-D1` ... `PED-D18` (18)
- Patch Test: `P1` ... `P6` (6)
- Acquisition Simulator: `A1` ... `A7` (7)

Executive completion is `certified complete experiences / 31`. Existing prototype functionality does not receive automatic completion credit; reuse readiness is tracked separately.

An experience is complete only when its Learning, Scientific, and Visualization contracts are satisfied, required interaction and observable consequence exist, EN/PT-BR behavior is complete, focused tests/QA are satisfied where warranted, and the result is integrated on `main`.

## Historical references

Existing bare identifiers remain historical aliases and must not be mass-renamed. References tied to Issue #46, old release tracking, pre-policy contracts, PR #104, PR #106, and associated QA retain their historical meaning. New references must use the appropriate namespace and semantic name.

## Scientific and implementation references

Scientific contracts should primarily use semantic contract/file names. When an identifier is needed, use the active pedagogical namespace or the historical namespace explicitly. Do not rename stable implementation solely for taxonomy; rename only when active ambiguity would remain.

## Delivery rule

Build the product outside-in until the scientific boundary: complete shell/navigation may expose all 31 experiences, but unavailable experiences must not invent scientific controls or outcomes. Beyond that boundary, complete experiences vertically through science → application state → visualization → UX → focused validation → integration.

Transition coordination is tracked in Issue #111.