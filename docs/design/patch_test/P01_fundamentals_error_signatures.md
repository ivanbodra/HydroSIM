# P1 — Fundamentals & Error Signatures — Visual Treatment

Pedagogy: `docs/pedagogy/patch_test/P01_fundamentals_error_signatures.md`  
Science: `docs/science/patch_test_module_scientific_contract.md` §3

## Visual purpose

Teach how each classic residual **looks** under the correct controlled geometry. P1 is forward consequence and recognition, not calibration.

Learner question: **What characteristic spatial signature does this residual create, and under what geometry can I trust that interpretation?**

## Dominant composition

Use one connected two-part instrument:

- **Geometry stage** — vessel tracks, directions/speeds, terrain, swaths and common physical support.
- **Signature stage** — the resulting reconstructed mismatch/profile/surface signature.

Avoid four disconnected cards. The learner changes the residual family and sees both stages update together.

Primary segmented selector: `Roll | Pitch | Yaw / Heading | Latency`.

## Parameter-specific visual scenes

### Roll

- reciprocal headings on the same nominal line;
- flat/uniform comparison terrain;
- overlapping swaths;
- emphasize reciprocal-swath depth/cross-track disagreement growing toward outer beams;
- keep the nadir region visually quieter so leverage is obvious.

### Pitch

- reciprocal headings over a distinct along-track slope/feature;
- near-nadir/common profile highlighted;
- show opposite-sense along-track feature placement after reconstruction.

### Yaw / Heading

- parallel offset lines in the same direction;
- common outer-swath overlap highlighted;
- show the same identifiable feature displaced differently in navigation coordinates.

### Latency

- same line and direction, materially different speeds;
- same distinct feature/profile;
- show speed-dependent along-track displacement difference;
- use timing association markers sparingly to reinforce delayed-state association without turning P1 into a timing lab.

## Confounding / insufficient evidence

The scene must support `confounded / insufficient evidence` when the canonical identifying geometry is absent. Do not force a classic label from arbitrary combined patterns.

## Interaction

Primary controls only:

- residual family;
- small hidden/configured mismatch magnitude control for demonstration;
- canonical geometry preset;
- optional `Show common support`.

Secondary controls belong behind progressive disclosure.

## Visual hierarchy

1. geometry and common support;
2. residual signature;
3. concise state label;
4. numbers.

Do not make the numeric residual value the main discovery.

## Motion

Use restrained animation when switching scenarios or replaying a pass. Motion should make reciprocal/same-direction relationships legible; it must not become decorative vessel animation.

## Acceptance

P1 passes visual conformance when a learner can distinguish the four classic signatures and can see why the selected geometry supports—or fails to support—that diagnosis without reading a paragraph.

## Referenced bibliography IDs

`iho_s5a_2_0_0_2026`; `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test`; `hughes_clarke_2003_dynamic_motion_residuals`; `maingot_2019_high_frequency_motion_residuals_thesis`.

See `99_references_by_submodule.md` for traceability and source roles.
