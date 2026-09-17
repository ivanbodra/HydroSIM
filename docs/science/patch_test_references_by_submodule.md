# HydroSIM Patch Test — Scientific Bibliography by Submodule

Status: canonical human-readable Patch Test bibliography map.

Machine-readable bibliographic metadata remains in `scientific_registry/references/bibliography.yaml`. Scientific coverage is mapped in `scientific_registry/references/coverage.yaml`.

## Reference → submodule map

| Stable ID | Reference | Scientific role in Patch Test | Submodule(s) |
|---|---|---|---|
| `iho_s5a_2_0_0_2026` | IHO, *Standards of Competence for Category A Hydrographic Surveyors*, Ed. 2.0.0 (2026) | Competence/education requirement for MBES operation, calibration procedures and diagnosis; curriculum context, not the source of HydroSIM equations | **P1, P2, P3, P5** |
| `noaa_fpm_2020` | NOAA, *Field Procedures Manual* (2020), §1.5.6.2 | Operational patch-test line sets, terrain/speed/direction conditions, calibration sequence, documentation and verification practice | **P1, P2, P3, P4, P5** |
| `noaa_ocean_exploration_2010_patch_test` | Hoy & Kissinger / NOAA Ocean Exploration (2010), *Multibeam Calibration: Conducting a Patch Test* | Classical four-variable teaching geometry and signatures for timing, pitch, roll and heading | **P1, P2, P3, P4, P5** |
| `noaa_hssd_2022` | NOAA, *Hydrographic Surveys Specifications and Deliverables* (2022) | Preserved HydroSIM calibration-requirement reference, especially for the existing pitch contract | **P1, P2, P3, P4, P5** |
| `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration` | Rathnayake & Lekkerkerk (2025), “Survey systems verification and calibration in the hydrospatial domain” | Current professional synthesis: patch-test conditions, overlap, flat/slope geometry, dual-head considerations, visual verification after automated routines | **P1, P2, P3, P4, P5** |
| `r2sonic_2017_patch_test` | Brennan / R2Sonic (2017), *The Patch Test* | Supporting manufacturer training for line geometry, interactive/automatic nulling and practical surface matching; not universal sign authority | **P1, P2, P4, P5** |
| `hughes_clarke_2003_dynamic_motion_residuals` | Hughes Clarke (2003), “Dynamic Motion Residuals in Swath Sonar Data: Ironing out the Creases” | Dynamic integration-error signatures, confounders and distinction between static classic patch residuals and motion-correlated residuals | **P1, P3, P5, P6** |
| `maingot_2019_high_frequency_motion_residuals_thesis` | Maingot (2019), *High-Frequency Motion Residuals in Multibeam Echosounder Data: Analysis and Estimation* | Primary RISC scientific source: residual modelling, six-parameter integration-error reference and observability | **P1, P5, P6** |
| `maingot_hughes_clarke_calder_2019_identification_estimation` | Maingot, Hughes Clarke & Calder (2019), “High Frequency Motion Residuals in Multibeam Data: Identification and Estimation” | Supporting RISC identification/estimation and limits of simple residual diagnosis | **P5, P6** |
| `maingot_2019_motion_residuals_seminar` | Maingot (2019), “High Frequency Motion Residuals: Analysis and Estimation” | Supporting RISC development/context | **P6** |
| `maingot_2023_realtime_inter_sensor_calibration` | Maingot (2023), “An Efficient and Robust Real-Time Calibration Routine for Inter-Sensor Offsets Within Integrated Multibeam Systems” | RISC continuation: six-error georeferencing model, residual minimization, sensitivity to bathymetry/external systematic errors, robust real-time direction | **P6** |
| `jhc_ccom_2020_annual_report` | UNH/NOAA Joint Hydrographic Center (2020), *Annual Report* | Simulator/known-Truth and RISC georeferencing-model development context | **P6** |
| `jerram_hoy_sowers_baechler_2019_okeanos_shakedown` | Jerram et al. (2019), *NOAA Ship Okeanos Explorer 2019 Acoustic Systems Shakedown Report* | Operational system-calibration campaign example and acquisition/configuration evidence | **P3, P5** |
| `jerram_johnson_ferrini_2019_neil_armstrong_em710` | Jerram, Johnson & Ferrini (2019), *R/V Neil Armstrong 2019 EM710 Calibration Report* | Operational patch-test acquisition/analysis and independent review example | **P3, P5** |
| `jerram_johnson_ferrini_2021_thompson_em302_qat` | Jerram, Johnson & Ferrini (2021), *R/V Thomas G. Thompson EM302 QAT Report* | Post-maintenance calibration/quality-assurance context | **P5** |
| `johnson_beaudoin_et_al_2014_mbac_three_years` | Johnson, Beaudoin et al. (2014), “Three Years of Working Towards the Improvement of Multibeam Echosounder Data Collection” | Multibeam Advisory Committee calibration/planning/analysis support context | **P3, P5** |
| `kongsberg_2026_multibeam_survey_planning` | Kongsberg Discovery (2026), *Multibeam survey planning — The key to success* | Manufacturer planning context for calibration area and operating conditions; supporting, not normative | **P2** |

## Submodule → reference map

| Submodule | Principal scientific references | Role |
|---|---|---|
| **P1 — Fundamentals & Error Signatures** | `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test`; `hughes_clarke_2003_dynamic_motion_residuals`; `maingot_2019_high_frequency_motion_residuals_thesis`; `iho_s5a_2_0_0_2026` | Classic signatures/geometry plus explicit warning that residual signatures can be confounded by broader integration errors |
| **P2 — Patch-Test Planning** | `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test`; `kongsberg_2026_multibeam_survey_planning`; `iho_s5a_2_0_0_2026` | Terrain, direction, speed, overlap and calibration-area planning |
| **P3 — Synthetic Acquisition** | `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `jerram_hoy_sowers_baechler_2019_okeanos_shakedown`; `jerram_johnson_ferrini_2019_neil_armstrong_em710`; `johnson_beaudoin_et_al_2014_mbac_three_years`; `hughes_clarke_2003_dynamic_motion_residuals`; `iho_s5a_2_0_0_2026` | Acquisition execution, reproducible configuration/provenance, and realistic calibration campaign context |
| **P4 — Manual Calibration** | `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test` | Candidate correction, reprocessing, null/minimum concept and visual verification. Exact HydroSIM objective/state/sign semantics are internal derived contracts |
| **P5 — Assessment & Validation** | `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test`; `jerram_johnson_ferrini_2019_neil_armstrong_em710`; `jerram_johnson_ferrini_2021_thompson_em302_qat`; `johnson_beaudoin_et_al_2014_mbac_three_years`; `hughes_clarke_2003_dynamic_motion_residuals`; `maingot_2019_high_frequency_motion_residuals_thesis`; `maingot_hughes_clarke_calder_2019_identification_estimation`; `iho_s5a_2_0_0_2026` | Independent/holdout verification, residual inspection, calibration QA, and bridge from classic calibration to unresolved integration errors |
| **P6 — RISC / Advanced Integration Diagnostics** | `maingot_2019_high_frequency_motion_residuals_thesis`; `maingot_hughes_clarke_calder_2019_identification_estimation`; `maingot_2019_motion_residuals_seminar`; `maingot_2023_realtime_inter_sensor_calibration`; `jhc_ccom_2020_annual_report`; `hughes_clarke_2003_dynamic_motion_residuals` | Model-based residual diagnosis, six-parameter RISC reference model, estimator development context and confounding/observability limits |

## Traceability notes

The bibliography supports external claims and operational practice. It does not replace HydroSIM definitions. The following are internal scientific contracts rather than externally attributed formulas:

- Truth / Observed / Configured / Estimated / Derived separation;
- additive correction convention `q_est = q_cfg + estimated_correction`;
- HydroSIM frame and angle signs;
- exact API/state ownership;
- choice of deterministic RMS objective for the first manual-calibration reference estimator where no external source prescribes that exact implementation.

Pure rigid-body geometry and identities such as the first-order constant-velocity scale `delta_x ~= V Delta_t` are mathematical consequences of the declared HydroSIM timing convention; external sources establish the operational timing-test geometry and interpretation.
