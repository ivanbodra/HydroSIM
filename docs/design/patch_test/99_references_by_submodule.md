# HydroSIM Patch Test — Visual References by Submodule

Status: canonical visual-design traceability map for the Patch Test module.

Bibliographic metadata remains authoritative in `scientific_registry/references/bibliography.yaml`. Scientific allocation remains authoritative in `scientific_registry/references/coverage.yaml` and `docs/science/patch_test_references_by_submodule.md`.

This file does **not** create a second scientific bibliography. It records which existing references inform the visual treatment of each Patch Test submodule and what aspect of the visual treatment they support.

## Reference → visual-treatment map

| Stable ID | P1 | P2 | P3 | P4 | P5 | P6 | Visual-design use |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `iho_s5a_2_0_0_2026` | ✓ | ✓ | ✓ |  | ✓ |  | Competence/education context for calibration, planning, acquisition and validation; supports workflow emphasis rather than equations |
| `noaa_fpm_2020` | ✓ | ✓ | ✓ | ✓ | ✓ |  | Operational line sets, terrain/speed/direction conditions, calibration sequence and verification workflow |
| `noaa_ocean_exploration_2010_patch_test` | ✓ | ✓ | ✓ | ✓ | ✓ |  | Classic four-variable teaching geometry and recognizable error signatures |
| `noaa_hssd_2022` | ✓ | ✓ | ✓ | ✓ | ✓ |  | Calibration-requirement context and continuity with the established HydroSIM pitch contract |
| `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration` | ✓ | ✓ | ✓ | ✓ | ✓ |  | Current professional synthesis of patch-test geometry, overlap, visual verification and calibration workflow |
| `r2sonic_2017_patch_test` | ✓ | ✓ |  | ✓ | ✓ |  | Supporting training imagery/interaction concepts for line geometry, nulling and surface/profile matching; not sign authority |
| `hughes_clarke_2003_dynamic_motion_residuals` | ✓ |  | ✓ |  | ✓ | ✓ | Visual distinction between classic static residuals, motion-correlated structure and confounding patterns |
| `maingot_2019_high_frequency_motion_residuals_thesis` | ✓ |  |  |  | ✓ | ✓ | Residual-pattern grammar, RISC model context, observability and confounding |
| `maingot_hughes_clarke_calder_2019_identification_estimation` |  |  |  |  | ✓ | ✓ | Advanced residual identification/estimation and ambiguity/conditioning treatment |
| `maingot_2019_motion_residuals_seminar` |  |  |  |  |  | ✓ | Supporting RISC visual-development context |
| `maingot_2023_realtime_inter_sensor_calibration` |  |  |  |  |  | ✓ | Six-error integration model and robust residual-minimization context |
| `jhc_ccom_2020_annual_report` |  |  |  |  |  | ✓ | Simulator/known-state and RISC development context |
| `jerram_hoy_sowers_baechler_2019_okeanos_shakedown` |  |  | ✓ |  | ✓ | Operational acquisition/configuration and calibration-campaign evidence |
| `jerram_johnson_ferrini_2019_neil_armstrong_em710` |  |  | ✓ |  | ✓ | Operational acquisition/analysis and independent-review workflow |
| `jerram_johnson_ferrini_2021_thompson_em302_qat` |  |  |  |  | ✓ |  | Post-maintenance calibration and QA/validation context |
| `johnson_beaudoin_et_al_2014_mbac_three_years` |  |  | ✓ |  | ✓ |  | Calibration planning, acquisition and analysis context |
| `kongsberg_2026_multibeam_survey_planning` |  | ✓ |  |  |  |  | Calibration-area and operating-condition planning context; supporting, not normative |

## Submodule → visual reference map

### P1 — Fundamentals & Error Signatures

References: `iho_s5a_2_0_0_2026`, `noaa_fpm_2020`, `noaa_ocean_exploration_2010_patch_test`, `noaa_hssd_2022`, `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`, `r2sonic_2017_patch_test`, `hughes_clarke_2003_dynamic_motion_residuals`, `maingot_2019_high_frequency_motion_residuals_thesis`.

Visual role: classic controlled geometry and signature recognition, plus explicit visual warning that residual patterns can be confounded outside the isolation scenario.

### P2 — Patch-Test Planning

References: `iho_s5a_2_0_0_2026`, `noaa_fpm_2020`, `noaa_ocean_exploration_2010_patch_test`, `noaa_hssd_2022`, `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`, `r2sonic_2017_patch_test`, `kongsberg_2026_multibeam_survey_planning`.

Visual role: terrain, direction, speed, overlap, line relation and calibration-area planning; supports the map-first adequacy treatment.

### P3 — Synthetic Acquisition

References: `iho_s5a_2_0_0_2026`, `noaa_fpm_2020`, `noaa_ocean_exploration_2010_patch_test`, `noaa_hssd_2022`, `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`, `jerram_hoy_sowers_baechler_2019_okeanos_shakedown`, `jerram_johnson_ferrini_2019_neil_armstrong_em710`, `johnson_beaudoin_et_al_2014_mbac_three_years`, `hughes_clarke_2003_dynamic_motion_residuals`.

Visual role: acquisition execution, paired-run identity, provenance/configuration, fixed Observed evidence and calibration-campaign context.

### P4 — Manual Calibration

References: `noaa_fpm_2020`, `noaa_ocean_exploration_2010_patch_test`, `noaa_hssd_2022`, `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`, `r2sonic_2017_patch_test`.

Visual role: candidate correction, profile/surface matching, null/minimum intuition and visual verification. Exact HydroSIM objective/state/sign semantics remain internal contracts.

### P5 — Assessment & Validation

References: `iho_s5a_2_0_0_2026`, `noaa_fpm_2020`, `noaa_ocean_exploration_2010_patch_test`, `noaa_hssd_2022`, `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`, `r2sonic_2017_patch_test`, `jerram_johnson_ferrini_2019_neil_armstrong_em710`, `jerram_johnson_ferrini_2021_thompson_em302_qat`, `johnson_beaudoin_et_al_2014_mbac_three_years`, `hughes_clarke_2003_dynamic_motion_residuals`, `maingot_2019_high_frequency_motion_residuals_thesis`, `maingot_hughes_clarke_calder_2019_identification_estimation`.

Visual role: independent/holdout verification, residual inspection, calibration QA and the bridge from classic calibration to unresolved integration residuals.

### P6 — RISC / Advanced Integration Diagnostics

References: `hughes_clarke_2003_dynamic_motion_residuals`, `maingot_2019_high_frequency_motion_residuals_thesis`, `maingot_hughes_clarke_calder_2019_identification_estimation`, `maingot_2019_motion_residuals_seminar`, `maingot_2023_realtime_inter_sensor_calibration`, `jhc_ccom_2020_annual_report`.

Visual role: structured residual fields, six-parameter RISC reference model, parameter influence, confounding/conditioning and the distinction between fit and unique physical diagnosis.

## Traceability rule

Each P01–P06 visual-treatment document must end with the stable bibliography IDs it uses. If a reference is later added or removed from a visual treatment, update this map and the relevant per-submodule footer in the same change.

The scientific bibliography remains the source of truth for citation metadata and scientific role; this design map records only visual-design consumption.
