# P5 — Assessment & Validation — Visual Treatment

Pedagogy: `docs/pedagogy/patch_test/P05_assessment_validation.md`  
Science: `docs/science/patch_test_module_scientific_contract.md` §7

## Visual purpose

Separate calibration fit from validation and make it visually clear that a small residual on the calibration pair is not, by itself, sufficient evidence of a good solution.

Learner question: **Did the candidate correction genuinely improve the result, including independent evidence, or did it merely fit the calibration pair?**

## Dominant composition

Use a three-tier validation layout:

1. **Calibration pair** — before/current residual evidence.
2. **Holdout / repeat evidence** — independent comparison not used to choose the candidate, when available.
3. **Truth reveal after submission** — estimated correction versus Truth and estimation error.

Do not reveal Truth before the learner commits/submits when the pedagogical contract requires it to remain hidden.

## Primary controls

- `Validate` / submit candidate;
- `Show holdout` when available;
- before/current comparison;
- `Reveal solution` only after submission;
- reset/new exercise where supported.

## Visual distinctions

### Residual mismatch

Magenta/red-violet spatial/profile disagreement over common support. Label as residual mismatch/RMS where appropriate.

### Validation evidence

Use the same spatial scale and visual grammar as the calibration pair so improvement is directly comparable.

### Estimation error

After Truth reveal, show `q_est - q_true` as a separate quantity with a separate label and visual container. Never merge it with residual RMS or label it as TPU.

## Assessment state

`Adequate`, `Suboptimal`, or `Inadequate` should be accompanied by the evidence that drove the state:

- residual materially reduced or persistent;
- overcorrection/opposite-sense structure;
- holdout/repeat improvement or failure;
- inherited weak/non-identifying geometry warning.

Do not present a universal percentage threshold as if it were canonical.

## Visual hierarchy

1. spatial before/current evidence;
2. independent validation evidence;
3. assessment category and concise reason;
4. Truth/estimation-error reveal;
5. supporting metrics.

## Acceptance

P5 passes when the learner can distinguish calibration fit, independent validation, residual structure, and post-submit estimation error without explanatory prose and without seeing Truth prematurely.

## Referenced bibliography IDs

`iho_s5a_2_0_0_2026`; `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test`; `jerram_johnson_ferrini_2019_neil_armstrong_em710`; `jerram_johnson_ferrini_2021_thompson_em302_qat`; `johnson_beaudoin_et_al_2014_mbac_three_years`; `hughes_clarke_2003_dynamic_motion_residuals`; `maingot_2019_high_frequency_motion_residuals_thesis`; `maingot_hughes_clarke_calder_2019_identification_estimation`.

See `99_references_by_submodule.md`.
