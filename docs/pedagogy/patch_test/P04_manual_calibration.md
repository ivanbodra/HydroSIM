# P4 — Manual Patch-Test Calibration

Status: **Mapped**

## Purpose
Teach the learner to estimate and apply residual calibration corrections from paired observations while keeping Truth hidden. The focus is reasoning from residual mismatch to a defensible correction, not pressing an automatic-calibration button.

## Dominant discovery

```text
paired observations disagree
  -> choose one target parameter
  -> adjust candidate correction
  -> reprocess/reconstruct both datasets
  -> residual metric changes
  -> best correction minimizes physically relevant mismatch
```

## Hidden Truth / unknowns
The active residual value remains hidden. In guided cases, only one classic residual is active. The learner sees the current configured value and may edit an **estimated correction**, never the Truth offset.

## Inputs
Primary:
- target parameter: latency, pitch, roll or heading/yaw;
- learner estimate / correction value;
- Apply / Recompute;
- compare before / after.

Secondary:
- comparison window/region within the valid overlap;
- profile/surface registration metric;
- magnification of residual display;
- optional coarse/fine adjustment step.

Advanced:
- automated suggestion shown only after the manual mechanism is understood;
- multiple observers / repeated estimates for variability;
- combined-residual challenge after isolated cases.

## Outputs / visual response
- uncorrected paired profiles/swaths/surfaces;
- corrected pair using the learner estimate;
- same-scale residual/difference visualization;
- scalar mismatch metric such as RMS over the valid comparison region;
- candidate-correction history or objective curve where appropriate;
- explicit configured value + learner correction = candidate calibrated value;
- Truth remains hidden until explicit submit/check.

For pitch, the preserved HydroSIM contract uses reciprocal profiles on a common along-track grid and minimizes RMS mismatch. Equivalent estimators for roll, heading and latency must be defined in their own canonical scientific contracts rather than inferred from vendor UI behavior.

## Observable signature
The correct candidate should reduce the target signature without creating an opposite-sense overcorrection:
- roll: reciprocal flat-bottom across-track disagreement closes;
- pitch: reciprocal slope/feature profiles converge;
- yaw: common outer-swath feature from offset same-direction lines aligns;
- latency: same-direction different-speed feature displacement converges.

## Interaction sequence
1. Load a P3 dataset pair and show its residual with Truth hidden.
2. Ask the learner to predict correction sign before moving the control.
3. Apply a small candidate correction and recompute both datasets.
4. Deliberately overcorrect; show the residual reverse sense.
5. Refine toward the minimum mismatch.
6. Freeze the estimate and submit it without revealing Truth yet.
7. Repeat for each classic parameter under isolated scenarios.
8. Final guided sequence: solve the full calibration campaign in the chosen order, applying each accepted correction before estimating the next.

Recommended didactic sequence for the full classical exercise:

```text
Timing/latency (when required/being tested)
  -> Pitch
  -> Roll
  -> Heading/Yaw
```

Modern NOAA operational guidance may omit a dedicated timing test when system timing is already validated; in that case the exercise begins with pitch.

## Decision / estimation task
For each target parameter, the learner must provide:
- correction sign;
- estimated magnitude;
- evidence that the residual metric improved;
- a short statement on whether the solution is identifiable from the selected data.

## Operational intuition / trade-offs
- a good correction is supported by residual agreement, not by resemblance to a hidden answer;
- too little correction leaves the original signature; too much reverses it;
- a low scalar RMS can still hide localized mismatch, so plots and metrics must be reviewed together;
- automatic routines can assist but should not replace visual/physical validation;
- solving parameters sequentially is useful only when the acquisition geometry successfully isolates them.

## Desired learner message
**Calibration is an estimation problem: adjust the configured model until repeated observations of the same seabed agree, then verify that the improvement is physically consistent rather than merely numerically smaller.**

## Scientific guardrails
- Truth must not enter the learner-facing objective function.
- Report corrections with explicit sign semantics: correction to apply versus residual error are not interchangeable.
- Do not use one generic closed-form equation for all systems/parameters if the registered HydroSIM geometry can perform the reconstruction directly.
- The pitch sign contract already exists and must be preserved.
- Do not estimate multiple unknowns simultaneously in the introductory manual experience.
- Do not treat convergence of one comparison metric as proof that all system biases are correct.
- External software may use different axes/signs; UI labels must stay canonical to HydroSIM and show any mapping explicitly.

## Dependencies / forward reuse
Consumes P3 paired observations and P1 signature intuition. Passes estimated corrections and before/after evidence to P5.

## Current implementation / reuse delta
Issue #343 preserves the future pitch-estimator design: deterministic reciprocal profiles, bounded coarse/fine search, RMS mismatch, hidden Truth and canonical correction sign. Issue #344 preserves roll learner behavior: learner edits only Estimated roll, Truth remains hidden until Check solution, and residuals close when estimate equals Truth. These are design memory, not authorization to restore old code. Equivalent bounded contracts are still needed for heading/yaw and latency.

## Recognized references
- NOAA, **Field Procedures Manual (2020)**, §1.5.6.2 — use of HIPS/SIPS, SIS, HYPACK or other tools; recommends quantifiable/verifiable bias values and independent checking: <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf>
- Brennan, C. W. / R2Sonic, **Multibeam Calibration: The Patch Test (2017)** — interactive graphical versus automatic iterative surface-match approaches and null/minimum concept: <https://www.r2sonic.com/wp-content/uploads/2020/03/The-New-Patch-Test.pdf>
- IHO International Hydrographic Review, **Survey systems verification and calibration in the hydrospatial domain (2025)** — automated routines should still be visually checked after applying suggested values: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- HydroSIM, **Pitch Patch Test v0.1 Scientific Contract** — canonical reciprocal-profile objective and correction sign: `docs/science/pitch_patch_test_v0_1_contract.md`
- Hoy, S. & Kissinger, K. / NOAA Ocean Exploration, **Multibeam Calibration: Conducting a Patch Test (2010)** — four-variable classical calibration sequence: <https://oceanexplorer.noaa.gov/wp-content/uploads/2023/04/patchtest-poster.pdf>