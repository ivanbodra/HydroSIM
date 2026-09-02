# Pedagogical alignment of the Concept Simulator

Status: concept-design working map  
Source of structure: `docs/pedagogy/hydrosim_pedagogical_plan.md`

This document records how the independent Concept Simulator should evolve to match the current HydroSIM pedagogical plan.

It does **not** validate equations, units, models, sign conventions, frames, algorithms or parameter ranges. Mock interactions remain design probes only.

## New macro navigation

The Concept Simulator should no longer be organized primarily around the original six design buckets (Signal, Beam, Propagation, Vessel, Motion, Integrated). Those remain useful **visual laboratories**, but the learner-facing conceptual map should follow the canonical product structure:

1. **Didactic Module** — D1–D18
2. **Patch Test Module** — P1–P6
3. **Acquisition Simulator** — A1–A7

The existing laboratories become reusable visual languages underneath these experiences.

## Interaction rule

Each experience should expose three layers without turning into a configuration form:

```text
INPUTS
  -> DIRECT MANIPULATION / SCENARIO CHANGE
  -> IMMEDIATE VISUAL CONSEQUENCE
  -> LEARNING OUTPUTS
```

Inputs should be contextual controls located near the phenomenon whenever practical. Outputs should remain visible while the learner changes the input so cause and effect can be compared continuously.

## Design reuse

- Signal Lab becomes the visual foundation for D1–D2.
- Propagation Lab becomes the foundation for D3–D4 and contributes to D15/D17.
- Beam Lab becomes the foundation for D6–D8 and D10.
- Vessel Lab becomes the foundation for D11 and A2.
- Motion Lab becomes the foundation for D12/D14 and contributes to D15.
- Integrated Lab becomes the foundation for D5/D9/D13/D15–D18 and A1–A7.
- A dedicated Patch-Test experience should be created for P1–P6 rather than forcing those exercises into the existing Integrated Lab.

## Important conceptual changes

### D1 and D2 must be separated

The current Signal Lab mixes waveform identity, pulse and processing. Preserve the visual chain, but give D1 a clean wave/frequency/wavelength experiment and D2 the pulse/CW/chirp/filter/compression sequence.

### D3 is larger than attenuation

The current attenuation scene should evolve into a sonar-equation/propagation-loss experience with source, propagation, noise, SNR and detection margin visible in one energy story.

### D6–D10 need an acoustic-system progression

The current Beam Lab already contains useful visual prototypes (singlebeam, multibeam, multisector, dual-head, Mills Cross). Reorganize them pedagogically as:

`array construction -> beamforming -> SBES/MBES -> bottom detection -> multisector`.

### D13 and D14 need new visual languages

Create a PU/sensor connection canvas for D13 and a synchronized multi-sensor timeline for D14. Avoid conventional IT-dashboard styling: streams and timing should be spatial/animated.

### D15 is the integration hinge

Sounding Formation should become the strongest causal sequence in the Didactic Module:

`ping -> echo/detection -> range -> sensor/reference transformations -> 3D sounding`.

The exact science is deliberately not specified here.

### D16–D18 are synthesis experiences

Planning, acquisition trade-offs and uncertainty should reuse controls learned earlier rather than introduce unrelated widgets.

### Patch Test deserves a continuous exercise workspace

P1–P6 should feel like one evolving workspace:

`understand signatures -> choose area/lines -> acquire -> choose pair/segment -> adjust -> submit -> reveal Truth`.

The learner should retain spatial context throughout the exercise.

### Acquisition Simulator should converge on one survey world

A1–A6 should progressively assemble the same world rather than open unrelated pages. A7 is a clear product boundary/export experience.

## Source-of-truth model in code

`src/pedagogical-plan.ts` mirrors the current module/submodule names and the input/output concepts from the canonical pedagogical plan, and adds only a non-authoritative `designCue` for concept development.

When the canonical pedagogical plan changes, this concept model should be reviewed before further interface expansion.