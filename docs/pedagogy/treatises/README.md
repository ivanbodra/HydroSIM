# Pedagogical treatises for the next HydroSIM generation

Document revision: 1.0 — 2026-10-16.
Owner: caho-pedagogy. Product Owner: final authority.

## Purpose

The Product Owner has directed that the next HydroSIM version be developed from a sequence of substantial laboratory-level pedagogical treatises. Each treatise connects scientific meaning, intuitive learning, interaction, visualization, assessment and reuse.

The present shell and scientific investment are reusable. Having controls, plots, tests and historical completion credit does not establish the quality of the next learner experience.

This series is the pedagogical foundation of that future generation. It does not assign a product version number, authorize publication, replace scientific contracts or mark planned behavior as implemented.

## Current series

| Experience | Canonical treatise | Portuguese reading edition | Status |
|---|---|---|---|
| PED-D1 — Acoustic wave, observation and acoustic quantities | [D1 treatise](PED-D1_acoustic_foundations.md) | [Tratado do D1](pt-BR/PED-D1_fundamentos_acusticos.md) | Product Owner direction recorded; proposed treatment specified; scientific extension and visual concept required |
| Other Acoustic Lab experiences | Not yet written | Not yet written | Review individually with the Product Owner; no findings or redesigns inferred from D1 |

The English edition is canonical under the repository language policy. The Portuguese edition identifies the same revision and section structure for Product Owner review. Scientific identifiers, units and conventions remain shared.

## Precedence and continuity

- Newer Product Owner decisions govern the pedagogical target.
- Treatises define learning intent and acceptance for the next generation.
- Applicable scientific contracts govern equations, dimensions, conventions and model validity.
- Visual concepts implement the pedagogical meaning without independently redefining physics.
- Existing source, modular specifications and QA evidence describe their historical/current release scopes.
- Differences between a treatise and the implemented release are explicit deltas, not retroactive declarations that the old code implements the new target.

Each existing modular specification should link its next-generation treatise while preserving the current release baseline. Do not replace current scientific contracts with pedagogical prose or silently change readiness denominators.

## Shared candidate interaction grammar

D1 establishes a vocabulary to carry into later treatises:

control -> physical change -> observable measurement -> reference comparison -> explanation / decision.

Preserve the meaning of physical state, measurement, selected location/time, reference/current and derived quantity across labs. Consistency is semantic; it does not require every lab to use the same chart or control.

The Concept Designer owns the visual expression of that grammar. Each later treatise must justify its appropriate scene, inputs and observations rather than copying D1's layout mechanically.

## Required content of a treatise

Record the problem and baseline, Product Owner decisions, curricular sources and evidence limits, target learners and objectives, central phenomenon/question, learning progression, meaningful inputs and visible outputs, comparison states, scaffolding, misconceptions, assessment evidence, scientific guardrails, accessibility/localization, dependencies, acceptance criteria and specific specialist questions.

Separate explicit course content, pedagogical interpretation, proposed HydroSIM extension and unresolved scientific decision. Do not imply that a source-backed lesson link certifies the whole course or the integrated application.

## Workflow

Write and review the pedagogical target; resolve bounded scientific questions; develop the visual concept and align it with the scientific outputs; let Technical Lead sequence implementation; deliver through Core/API and production UX; validate the exact candidate scientifically, pedagogically, visually and in runtime; integrate and then obtain Product Owner acceptance.

Specialist handoffs must identify an executable artifact/decision and completion condition. A treatise is not permission to bypass those ownership boundaries.
