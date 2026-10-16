# HydroSIM coverage available for CAHO mapping

Status: implementation-side inventory and pedagogical reuse crosswalk. Source-backed CAHO links are maintained separately in curriculum_map.md.
Baseline: `eed7bedc19f654b9adc13275a249a57576720e5d`; inspected 2026-10-16.

## Evidence limits and identifier crosswalk

The table below checks existing modular specification paths against production imports/routes in `web/pedagogical-explorer/src/main.tsx`. It establishes a reusable implementation surface, not independent scientific, runtime, bilingual or pedagogical validation. Individual Acoustic Lab specifications have not all been re-reviewed in this cycle.

The current plan and production routing preserve the retired `PED-D5` slot: arrays use `PED-D6`, beamforming `PED-D7`, and uncertainty `PED-D18`. The modular Acoustic Lab directory uses a compact D01–D17 file sequence. Use semantic titles and explicit file paths to connect these namespaces; do not mass-rename existing evidence.

The module identifier policy still describes 31 experiences, while the delivery baseline explicitly records 30 after retirement of `PED-D5`. No project completion percentage is recalculated here. The same delivery baseline still describes an old Patch Test release gate, while current #544, integrated code and #601 establish later development. Treat these as documentation reconciliation items, not reasons to restart or block current work.

## Existing acoustic and integration activities

CAHO source access is now available. See curriculum_map.md links C01–C11 and reading_log.md for the subset verified by source pages. Rows here inventory HydroSIM implementation surfaces; they do not claim complete lesson coverage. Classroom treatments remain pedagogical interpretations rather than approvals to redesign existing labs.

Paths in the specification column are relative to `docs/pedagogy/acoustic_lab/`.

| Product ID | Semantic topic | Modular specification | Production route | Candidate classroom treatment / learning evidence |
|---|---|---|---|---|
| PED-D1 | Acoustic Wave & Frequency | D01_wave_frequency.md | #wave-lab | Interactive demonstration; predict wavelength/period changes before manipulating frequency |
| PED-D2 | Pulse & Signal Processing | D02_pulse_signal_processing.md | #signal-lab | Interactive demonstration; compare pulse duration, bandwidth and resolving response |
| PED-D3 | Sonar Equation & Propagation Loss | D03_sonar_equation.md | #sonar-equation-lab | Interactive demonstration; explain a change in detection margin from a controlled setting |
| PED-D4 | Sound Speed & Refraction | D04_sound_speed_refraction.md | #refraction-lab | Full laboratory candidate; compare reference and mismatched profile consequences |
| PED-D6 | Transducer & Array Construction | D05_transducer_array.md | #array-directivity-lab | Interactive demonstration; predict aperture/spacing effects on directivity |
| PED-D7 | Beamforming & Electronic Steering | D06_beamforming_steering.md | #beamforming-lab | Interactive demonstration; explain channel alignment and electronic steering |
| PED-D8 | Echosounders — SBES vs MBES | D07_echosounders_sbes_mbes.md | #echosounder-lab | Interactive demonstration; compare acquisition geometry over the same bottom |
| PED-D9 | Bottom Detection | D08_bottom_detection.md | #bottom-detection-lab | Full laboratory candidate; justify a detection decision using signal evidence |
| PED-D10 | Multisector MBES | D09_multisector_mbes.md | #multisector-lab | Interactive demonstration; relate sector sequence to acoustic and geometric consequences |
| PED-D11 | Vessel & Sensor Configuration | D10_vessel_sensor_configuration.md | #vessel-configuration-lab | Interactive demonstration; trace reference points, offsets and orientations |
| PED-D12 | Vessel Motion | D11_vessel_motion.md | #vessel-motion-lab | Interactive demonstration; predict sensor/beam displacement from platform motion |
| PED-D13 | PU & Sensor Integration | D12_pu_sensor_integration.md | #pu-sensor-lab | Interactive demonstration; explain configuration/stream compatibility consequences |
| PED-D14 | Timing, Synchronization & Latency | D13_timing_sync_latency.md | #timing-lab | Full laboratory candidate; connect temporal association error to spatial consequence |
| PED-D15 | Sounding Formation | D14_sounding_formation.md | #sounding-formation-lab | Integrated scenario candidate; explain the chain from observation to reconstructed sounding |
| PED-D16 | Survey Planning | D15_survey_planning.md | #survey-planning-lab | Full laboratory candidate; justify line geometry and predicted coverage |
| PED-D17 | Survey Coverage & Acquisition Trade-offs | D16_survey_coverage_tradeoffs.md | #tradeoff-lab | Integrated scenario candidate; defend a configuration using competing acquisition consequences |
| PED-D18 | Uncertainty / TPU | D17_uncertainty_tpu.md | #uncertainty-lab | Full laboratory candidate; interpret uncertainty contributions without treating them as actual error |

The retired PED-D5 detection-fundamentals activity must not return as a separate lab. Its objectives are distributed among PED-D2, PED-D3 and PED-D9 in the established plan.

## Patch Test

| ID | Existing pedagogical specification under `docs/pedagogy/patch_test/` | Production evidence | CAHO alignment / candidate treatment |
|---|---|---|---|
| P1 | P01_fundamentals_error_signatures.md | #patch-test-signatures route on inspected main | C08; interactive demonstration of residual signatures |
| P2 | P02_line_planning.md | #patch-test-planning route on inspected main | C09; planning stage of a full laboratory |
| P3 | P03_synthetic_acquisition.md | #patch-test-acquisition route on inspected main | C09; evidence-acquisition stage of that laboratory |
| P4 | P04_manual_calibration.md | #patch-test-calibration route on inspected main | C10; manual estimation and correction stage |
| P5 | P05_assessment_validation.md | #patch-test-assessment route on inspected main; integration commit eed7bed | C10; assessment and independent validation stage |
| P6 | P06_risc_integrated_diagnostics.md | Absent from inspected main routes; open PR #602 at 50188a9a438355f2a0ba889ebd6e253467977d0f | C11, proposed complementary extension; current visualize_only authorization applies |

P1–P5 should be considered as one coherent calibration learning sequence before proposing duplicate isolated experiences. Presence of routes is not certification of that whole sequence.

P6's newer Product Owner authorization, preserved in #601, permits `visualize_only`: six one-at-a-time forward-model parameter influences. It excludes estimation, optimization, automatic diagnosis, real-time correction and unique-cause recovery claims. The broader mapped P6 specification does not supersede this bounded release.

QA handoff #605 remains open to `interface-ux` at inspection time: absolute across-track coordinates were being plotted on a residual scale, hiding most traces. This record reports that existing QA finding; it does not independently rerun or validate it. Do not duplicate its implementation request or claim the candidate is classroom-ready.

## Acquisition Simulator

A1–A7 are defined in `docs/pedagogy/hydrosim_pedagogical_plan.md`: true seafloor, vessel/installation, sonar configuration, environment, planning, acquisition and synthetic raw export. The inspected production router has legacy/integrated views but does not establish seven individually complete A1–A7 experiences. Treat them as planned reuse/dependency areas until their exact implementation is verified.

Synthetic export intended for CARIS HIPS & SIPS is a product intention, not verified compatibility evidence in this cycle.

## Scope and prerequisite interpretation

The existing plan excludes complete GNSS/geodesy, tide theory, bathymetric post-processing, side-scan, backscatter, LiDAR, AUV/ROV, subsea positioning, cartography/ENC, MSDI/database administration, legal aspects, project management and formal survey reporting from current teaching modules. The visible CAHO collection includes several of these areas, documented in curriculum_map.md. Their presence justifies evaluating a small visual aid or an explicit extension proposal after reading the lesson, not automatic product expansion.

Provisional HydroSIM learning dependencies, to be reconciled with actual CAHO lesson order:

- Wave and pulse vocabulary supports propagation, arrays, beamforming and detection.
- Frames, installation, motion and timing support sounding formation.
- Acoustic geometry and sounding formation support planning, coverage and uncertainty interpretation.
- Geometry, timing, motion and residual signatures support P1–P5.
- P6 remains optional advanced support after classic calibration concepts; it is not a prerequisite for P1–P5.

These are pedagogical interpretations of existing HydroSIM architecture. Course-explicit prerequisite anchors are distinguished in curriculum_map.md.

## Inspected reference set

- `docs/language_policy.md`.
- `docs/coordination/agent_handoffs.md`.
- `docs/coordination/module_identifier_policy.md`.
- `docs/coordination/pedagogical_generation_status.md`.
- `docs/pedagogy/hydrosim_pedagogical_plan.md`.
- `docs/pedagogy/didactic_module_pedagogical_framework.md`.
- `docs/pedagogy/pedagogical_reference_index.md`.
- `docs/pedagogy/acoustic_lab/00_overview.md`.
- `docs/pedagogy/patch_test/00_overview.md`.
- `docs/pedagogy/patch_test/P06_risc_integrated_diagnostics.md`.
- `docs/science/patch_test_common_scientific_contract.md`.
- `docs/science/scientific_references_by_submodule.md`.
- `web/pedagogical-explorer/src/main.tsx` and `pedagogical-plan.ts`.
- GitHub #544–#547, #600, #601, #605 and PR #602.

README and coordination snapshots contain historical implementation statements. Current source code and newer directed decisions must be consulted before operational action.
