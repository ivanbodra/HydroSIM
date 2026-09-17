# P3 — Synthetic Patch-Test Acquisition

Status: **Mapped**

## Purpose
Turn the P2 line plan into synthetic multibeam evidence generated from hidden system Truth. The learner should experience that calibration quality depends on how the data were actually collected, not only on the later estimator.

## Dominant discovery

```text
line plan + hidden residual + vessel/sonar state + terrain
  -> synthetic observations
  -> repeated coverage of the same seabed
  -> measurable residual mismatch
```

P3 is an acquisition exercise, not yet a calibration-solving exercise.

## Hidden Truth / unknowns
Hidden scenario values may include:
- one classic residual active in guided mode: latency, pitch, roll or heading/yaw;
- true sensor alignment/timing state;
- deterministic seabed Truth.

Later challenge scenarios may include one controlled contaminant, but not an unrestricted collection of unknown errors.

## Inputs
Primary:
- selected P2 line plan;
- vessel run direction and commanded speed;
- acquisition start/stop;
- sonar operating preset suitable for the selected depth;
- current/accepted sound-speed profile selection where the scenario requires it.

Secondary:
- run repeat count;
- deterministic motion preset;
- beam/swath subset to retain for later comparison;
- display sampling density.

Advanced:
- controlled sensor noise / small motion variation after deterministic behavior is established;
- a known contaminant preset for diagnostic training;
- dual-head identity where each head must be calibrated separately.

The learner does **not** edit the hidden residual during P3.

## Outputs / visual response
- vessel moving along the planned line over the Truth DTM;
- live swath footprint/coverage;
- synthetic soundings in navigation frame;
- per-run identifiers and line direction/speed;
- common-overlap region between repeated runs;
- profile/surface previews used later by P4;
- acquisition completeness checklist: both runs acquired, required overlap achieved, speed/direction condition satisfied;
- recorded configuration snapshot so the calibration remains reproducible.

Recommended post-run views:
- individual swaths/profiles;
- overlay of paired runs without applying a correction;
- residual/difference preview with no numerical solution offered yet.

## Observable signature
P3 must reproduce the P1 signature under the P2 geometry through shared HydroSIM geometry/timing models:
- roll -> reciprocal flat-bottom outer-swath disagreement;
- pitch -> reciprocal slope/feature displacement;
- yaw -> overlapping offset-line feature disagreement;
- latency -> same-direction different-speed displacement.

## Interaction sequence
1. Load an adequate P2 plan and show the hidden-Truth scenario without revealing its numerical offset.
2. Acquire the first run; coverage and observations appear incrementally.
3. Acquire the paired run with the required direction/speed/offset condition.
4. Overlay the runs and expose the residual signature.
5. Re-run with an intentionally poor steering/speed/overlap condition and compare the evidence quality.
6. Reset and repeat with another parameter family.
7. Optional advanced case: add a controlled contaminant and show that the residual becomes less clean without revealing a solution.

## Decision / estimation task
The learner decides whether the acquired pair is fit for calibration:
- **usable** — sufficient common seabed and intended contrast;
- **marginal** — signature present but weak/contaminated;
- **reacquire** — geometry/data cannot support the intended estimate.

No patch value is solved in P3.

## Operational intuition / trade-offs
- good planning can still fail through poor execution;
- line steering, speed consistency, overlap and environmental quality matter because the estimator compares repeated observations of the same seabed;
- adding realistic noise before the deterministic signature is understood obscures the lesson;
- more data are useful only if they preserve the intended comparison geometry;
- acquisition metadata/configuration must remain tied to the observations so the later correction can be interpreted correctly.

## Desired learner message
**A patch-test estimate is only as defensible as the paired observations that support it. The acquisition must preserve the geometry that makes the target residual observable.**

## Scientific guardrails
- Synthetic acquisition must use shared HydroSIM sonar/geometry/timing models; do not generate signature shapes directly in the UI.
- Truth seabed and hidden residual are fixed during a run pair unless the scenario explicitly teaches instability.
- Do not present P3 output as manufacturer-native raw data. It is HydroSIM synthetic acquisition evidence.
- Maintain identical terrain Truth across paired runs.
- When noise is enabled, preserve deterministic random seeds for reproducibility.
- Sound-speed or water-level mismatches may be used only as labelled contaminants, not quietly mixed into the classic calibration target.
- P3 does not estimate calibration values.

## Dependencies / forward reuse
Consumes P2 line plan and Acoustic Lab sounding formation. Passes paired observations, metadata and comparison regions to P4.

## Current implementation / reuse delta
HydroSIM already has shared deterministic geometry, sounding reconstruction and a roll-offset scenario, plus a preserved pitch estimator design. P3 should assemble those capabilities into line-based acquisition rather than building a separate patch-test physics stack. Heading/yaw and latency reference scenarios still require bounded canonical generation contracts before production implementation.

## Recognized references
- IHO, **S-5A Ed. 2.0.0 (2026)**, H4.2d — perform multibeam operations, calibration procedures, online monitoring and diagnosis of data deficiencies: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- NOAA, **Field Procedures Manual (2020)**, §1.5.6.2 — calibration-area conditions, repeated line acquisition and data-comparison practice: <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf>
- Jerram, K.; Hoy, S.; Sowers, D.; Baechler, N., **NOAA Ship Okeanos Explorer 2019 Acoustic Systems Shakedown Report (2019)** — operational geometric calibration and system-configuration review: <https://scholars.unh.edu/ccom/1709/>
- Jerram, K.; Johnson, P.; Ferrini, V., **R/V Neil Armstrong 2019 EM710 Calibration Report (2019)** — real patch-test campaign example and calibration acquisition context: <https://scholars.unh.edu/ccom/1727/>
- Johnson, P.; Beaudoin, J. et al., **Multibeam Advisory Committee – Three Years of Working Towards the Improvement of Multibeam Echosounder Data Collection (2014)** — remote patch-test planning/acquisition/analysis support: <https://scholars.unh.edu/ccom/53/>