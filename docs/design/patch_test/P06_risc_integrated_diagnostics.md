# P6 — RISC / Advanced Integration Diagnostics — Visual Treatment

Pedagogy: `docs/pedagogy/patch_test/P06_risc_integrated_diagnostics.md`  
Science: `docs/science/patch_test_module_scientific_contract.md` §8 and `docs/science/risc.md`

## Visual purpose

Present P6 as an advanced structured-residual diagnostic stage after the classic P1–P5 workflow, not as another classic Patch Test parameter screen.

Learner question: **Can a defined integration-error model explain structured residuals that remain after the classic Patch Test, and how well constrained is that explanation?**

## Visual identity

P6 should deliberately look more analytical than P1–P5 while preserving the same state colors and spatial grammar.

Use:

- residual field/surface as the dominant scene;
- parameter-influence panel;
- compact model/objective summary;
- clear warnings for weak identifiability, confounding, or reference-surface inadequacy.

Do not make the first view a bank of six sliders.

## Dominant composition

### Main residual scene

Show the structured residual pattern in navigation coordinates or an equivalent canonical view. Preserve a clear baseline/reference surface and avoid autoscaling that hides pattern magnitude changes.

### Parameter-influence view

Allow the learner to inspect how the current six-parameter reference model changes the predicted residual structure:

- GNSS–MBES X lever-arm error `ΔLx`;
- GNSS–MBES Y lever-arm error `ΔLy`;
- INS–MBES latency `Δt`;
- INS scale factor `Δρ`;
- INS–MBES Z-axis misalignment `Δκ`;
- effective surface sound-speed error `ΔSSS`.

The visual treatment must not imply these are simply the four classic Patch Test residuals plus two extras.

## Interaction

Prefer:

- scenario/residual-field selector;
- one-at-a-time influence inspection for first experience;
- compare/reference mode;
- progressive disclosure for full model parameter editing;
- reset to baseline.

If a future estimator is exposed, its objective, bounds, conditioning, and confidence/identifiability treatment must come from the scientific contract; the visual layer must not invent them.

## Confounding and identifiability

Use visible warnings and pattern ambiguity cues when multiple parameter combinations can explain similar residual structure. A low objective must not be styled as proof of a unique physical diagnosis.

## Reference-surface semantics

The smoothed/reference bathymetric surface is an estimator construct, not hidden Truth. Use a distinct neutral/reference visual style rather than the Truth gold treatment.

## Visual hierarchy

1. structured residual field;
2. parameter influence / model response;
3. conditioning/confounding warning;
4. objective/fit metric if supported;
5. numeric parameter readouts.

## Acceptance

P6 passes when the learner can see that advanced residual diagnosis is model-based, potentially confounded, and scientifically distinct from the classic P1–P5 calibration sequence.

## Referenced bibliography IDs

`hughes_clarke_2003_dynamic_motion_residuals`; `maingot_2019_high_frequency_motion_residuals_thesis`; `maingot_hughes_clarke_calder_2019_identification_estimation`; `maingot_2019_motion_residuals_seminar`; `maingot_2023_realtime_inter_sensor_calibration`; `jhc_ccom_2020_annual_report`.

See `99_references_by_submodule.md`.
