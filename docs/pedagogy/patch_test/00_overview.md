# HydroSIM Patch Test — Pedagogical Overview

Status: **canonical pedagogical specification — research/mapping complete; implementation remains gated by Product Owner release of the Patch Test phase**

This directory defines the pedagogical structure for the future HydroSIM Patch Test module. It does **not** authorize implementation while the Didactic Explorer release gate remains active.

## Module purpose

The Patch Test module teaches how a hydrographer designs calibration lines that isolate systematic integration biases, observes their bathymetric signatures, estimates corrections, applies them, and verifies that the residual mismatch is reduced.

The classic solved parameters are deliberately limited to:

- navigation / attitude timing delay (latency), when this calibration is required;
- pitch residual alignment;
- roll residual alignment;
- heading / yaw residual alignment.

Lever arms, heave, sound-speed errors, water level, GNSS errors, sensor noise, motion-model errors and other integration defects may contaminate or mimic a patch-test signature, but they are **not silently promoted to additional classic patch-test solved parameters**.

## Pedagogical progression

```text
P1 SEE THE SIGNATURE
P2 DESIGN THE TEST
P3 ACQUIRE THE EVIDENCE
P4 ESTIMATE THE CORRECTION
P5 VALIDATE THE SOLUTION
P6 DIAGNOSE BEYOND THE CLASSIC PATCH TEST
```

The common causal contract is:

```text
KNOWN SURVEY GEOMETRY
  -> HIDDEN SYSTEMATIC ERROR
  -> SYNTHETIC OBSERVATIONS
  -> CHARACTERISTIC RESIDUAL SIGNATURE
  -> LEARNER ESTIMATE
  -> APPLY CORRECTION
  -> REPROCESS / RECOMPUTE
  -> RESIDUAL REDUCES OR PERSISTS
  -> VERIFY AGAINST HOLDOUT / TRUTH
```

## State semantics

Preserve HydroSIM state separation:

- **Truth** — hidden physical/system offset used to generate the synthetic acquisition;
- **Observed** — synthetic sensor/acoustic observations and reconstructed bathymetry available to the learner;
- **Configured** — calibration values currently applied in reconstruction;
- **Estimated** — learner or algorithm estimate of a correction;
- **Derived** — residuals, difference surfaces, statistics and post-application consequences.

Truth must remain hidden during estimation and may be revealed only by an explicit solution-check / instructor action.

## Submodule map

| ID | Submodule | Dominant role | File |
|---|---|---|---|
| P1 | Fundamentals & Error Signatures | recognize what each classic residual does to the data | `P01_fundamentals_error_signatures.md` |
| P2 | Patch-Test Planning | choose terrain, line geometry, direction and speed to isolate each residual | `P02_line_planning.md` |
| P3 | Synthetic Acquisition | execute the planned lines with hidden Truth offsets and collect evidence | `P03_synthetic_acquisition.md` |
| P4 | Manual Calibration | estimate and apply one correction at a time from residual agreement | `P04_manual_calibration.md` |
| P5 | Assessment & Validation | verify correction quality with holdout/reference evidence and diagnose remaining problems | `P05_assessment_validation.md` |
| P6 | RISC / Advanced Integration Diagnostics | show why residuals can remain after a classic patch test and introduce model-based inter-sensor diagnostics | `P06_risc_integrated_diagnostics.md` |

### Historical numbering note
Older HydroSIM issues/contracts were created before this P1–P6 pedagogical taxonomy was fixed. In particular, the preserved `Pitch Patch Test v0.1 Scientific Contract` calls its isolated pitch-calibration experience **P2**, and issues #343/#344 use legacy labels. Those labels are historical references only. Under the canonical taxonomy above, isolated numerical calibration belongs to **P4**, while **P2** is line planning. Do not rename historical artifacts merely to make their old identifiers look current; map their reusable effect into the canonical P-files.

## Classic line-geometry anchors

For the classic MBES patch-test experience, HydroSIM uses the established operational geometries documented by NOAA and other hydrographic sources:

- **Roll:** reciprocal runs over a flat seabed; compare across-track swaths/profiles.
- **Pitch:** reciprocal runs on the same line at the same speed over a well-defined slope/feature; compare nadir or near-nadir along-track profiles.
- **Heading/Yaw:** offset parallel lines in the same direction and speed over a steep, well-defined slope/feature, with overlapping outer swaths; compare the common feature/profile.
- **Timing/Latency:** same-direction runs over a steep, well-defined slope/feature at different speeds; compare the feature displacement. This is retained as a classical teaching case, but modern NOAA guidance notes that a dedicated timing test is primarily useful for gross timing errors and may not be required in routine patch testing when system timing is otherwise validated.

## Rules

- mechanism before memorized line recipe;
- each line geometry must visibly isolate a parameter by making that parameter observable;
- allow invalid/suboptimal planning and explain why it weakens identifiability;
- hide Truth during estimation;
- never infer a unique physical cause from a residual pattern when multiple integration errors can produce similar effects;
- use the common Scientific Core geometry/timing/acquisition models rather than closed-form UI approximations;
- preserve HydroSIM frame/sign conventions and explicitly map external/vendor conventions;
- classic P1–P5 remains distinct from P6 RISC/advanced diagnostics;
- a patch-test correction is a residual calibration correction, not a replacement for the original vessel offset/alignment survey.

## Mapped-submodule completeness contract

Every P-file must contain: Purpose; Dominant discovery; Hidden Truth/unknowns; Inputs; Outputs/visual response; Observable signature; Interaction sequence; Decision/estimation task; Operational intuition/trade-offs; Desired learner message; Scientific guardrails; Dependencies/forward reuse; Current implementation/reuse delta; Recognized references.

References remain local to each submodule during development. Consolidated bibliography can be generated after P1–P6 are implemented/reviewed.

## Source hierarchy

1. IHO S-5A current edition — hydrographic competence and multibeam calibration requirement.
2. NOAA Field Procedures Manual / NOAA Ocean Exploration — operational patch-test geometry and QA practice.
3. IHO International Hydrographic Review — system verification/calibration interpretation and limitations.
4. CCOM/UNH / Multibeam Advisory Committee — calibration reports, error diagnosis and advanced integration research.
5. Manufacturer technical documentation — operational examples and software workflows; not universal law.

## Cross-module boundary

The Acoustic Lab teaches the physics, frames, timing, sounding formation and uncertainty that Patch Test reuses. Patch Test must not reteach those subjects from first principles. The Acquisition Simulator may later provide richer raw-like collection, but P3 must remain a bounded calibration acquisition experience rather than becoming the full survey simulator.