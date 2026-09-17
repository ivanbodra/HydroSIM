# HydroSIM Patch Test — Visual Design Treatment

Status: canonical visual-design treatment for the Patch Test module.

This document does not redefine science or pedagogy. It must be read with:

- `docs/pedagogy/patch_test/00_overview.md` and P01–P06 pedagogical treatments;
- `docs/science/patch_test_common_scientific_contract.md`;
- `docs/science/patch_test_module_scientific_contract.md`;
- `docs/conventions.md`;
- `docs/science/patch_test_references_by_submodule.md`.

## 1. Canonical submodules

- **P1 — Fundamentals & Error Signatures**
- **P2 — Patch-Test Planning**
- **P3 — Synthetic Acquisition**
- **P4 — Manual Calibration**
- **P5 — Assessment & Validation**
- **P6 — RISC / Advanced Integration Diagnostics**

P1–P5 share the classic residual families: latency, pitch, roll, and heading/yaw. P6 is an advanced model-based diagnostic stage and must not look like a fifth classic patch-test residual.

## 2. Module-level visual narrative

The Patch Test should feel like one coherent hydrographic calibration laboratory, not six independent pages.

Primary visual narrative:

`GEOMETRY → ACQUISITION → RESIDUAL → CANDIDATE CORRECTION → VALIDATION → ADVANCED DIAGNOSIS`

The learner should understand the process mainly from the changing geometry and data, with text limited to labels, units, concise state annotations, and necessary warnings.

## 3. Shared visual grammar

### Truth
Hidden whenever the pedagogical contract requires it. When revealed, use a restrained gold outline/trace. Truth must never become the active calibration surface.

### Observed
Neutral light/cool-gray solid geometry or points. Observed data must look acquired, fixed, and immutable after P3.

### Configured / before
Muted blue-gray. This is the reconstruction using the current configured calibration.

### Candidate / estimated correction
Bright cyan/aqua. This is the learner-manipulated state and should dominate during P4.

### Derived / reconstructed result
Use the active candidate color when it is the output of the current reconstruction. In before/current comparison, keep before muted and current bright.

### Residual / mismatch
Use magenta or red-violet, supported by geometry/line-style differences. Residuals should read as disagreement between datasets over common physical support, not as arbitrary screen-space displacement.

### Adequacy / validation
Use green / amber / red for Adequate / Suboptimal / Inadequate, but never color alone. Add icon/label/state-shape differences.

## 4. Recurring spatial primitives

Use a small stable vocabulary across P1–P6:

- HydroSIM vessel icon;
- survey track with heading arrow;
- reciprocal tracks;
- same-direction offset tracks;
- speed badges;
- swath/footprint region;
- common-support overlay;
- terrain profile/surface;
- sounding profile/cloud;
- residual vectors/bands;
- timing/association markers;
- compact objective trace where scientifically appropriate.

Terrain should be simplified and parameter-specific: flat/uniform for roll isolation, along-track slope/feature for pitch, identifiable common outer-swath structure for yaw, and a distinct feature with speed contrast for latency.

## 5. Controls

Controls should look like scientific-laboratory controls, not a web form.

Prefer:

- segmented selectors for residual family and view mode;
- one dominant candidate-correction slider in P4;
- compact numeric entry paired with sliders only when useful;
- toggles for overlap, residual vectors, holdout, and Truth reveal when permitted;
- preset buttons for canonical geometries;
- `Acquire`, `Reconstruct`, `Validate` only where the pedagogy benefits from staged action;
- progressive disclosure for secondary configuration.

## 6. Motion

Animation must communicate process:

- vessel traversing a planned line;
- swath painting/acquisition progress;
- common-support reveal;
- smooth residual closure as a candidate correction changes;
- staged Truth reveal after submission;
- structured residual response in P6.

Avoid continuous decorative motion.

## 7. Module shell and continuity

All Patch Test submodules should share:

- one persistent module header/navigation;
- the same P1–P6 step identity;
- the same state colors and line grammar;
- the same vessel/track/swath language;
- consistent EN/PT-BR terminology;
- a dominant scientific stage with compact controls rather than stacked explanatory cards.

Recommended view-mode vocabulary when useful: `Geometry`, `Data`, `Residual`, `Compare`.

## 8. Text discipline

Keep learner-facing text primarily for:

- parameter names and values;
- units;
- plot/axis labels;
- concise status labels;
- short technical annotations required to interpret the experiment.

Avoid explanatory paragraphs, slogans, coach-like copy, and narration that the visualization can carry.

## 9. State and science boundaries

The visual layer must preserve the canonical state model:

- Truth remains separate from Observed;
- Observed acquisition remains immutable during P4 reprocessing;
- candidate corrections modify Configured reconstruction, not Truth vessel tracks or physical acquisition epochs;
- P5 estimation error is distinct from residual RMS and from TPU;
- P6 does not silently replace the classic four-parameter Patch Test.

React/SVG may map authoritative values to screen coordinates; it must not recreate Patch Test physics, objectives, sign conventions, or state association models.

## 10. Responsive behavior

For smaller viewports:

- preserve the main scientific scene first;
- collapse secondary controls/details into drawers;
- keep core state selectors visible;
- permit horizontal scroll for wide profile/map instruments rather than shrinking labels to illegibility;
- never replace spatial evidence with text-only summaries.

## 11. Completion standard

A Patch Test submodule is visually complete when:

1. its dominant scene communicates the required physical/comparison mechanism without relying on prose;
2. the learner immediately understands what can be manipulated;
3. Truth / Observed / Configured / Candidate / Derived semantics remain visually distinct;
4. common support and residual structure are explicit when scientifically required;
5. the visual treatment is coherent with the rest of the Patch Test module;
6. no visual decision changes the scientific or pedagogical contract.

## 12. Submodule treatments

See:

- `P01_fundamentals_error_signatures.md`
- `P02_line_planning.md`
- `P03_synthetic_acquisition.md`
- `P04_manual_calibration.md`
- `P05_assessment_validation.md`
- `P06_risc_integrated_diagnostics.md`
- `99_references_by_submodule.md`
