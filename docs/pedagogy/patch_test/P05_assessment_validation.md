# P5 — Patch-Test Assessment & Validation

Status: **Mapped**

## Purpose
Teach the learner to verify that an estimated patch-test correction actually improves the integrated bathymetric result and to distinguish an acceptable calibration from a numerically plausible but poorly supported solution.

## Dominant discovery

```text
estimated correction
  -> apply to reconstruction
  -> compare independent/repeated evidence
  -> residual signature should reduce without new artifacts
  -> accept, refine, or reacquire
```

Validation is based first on observable performance. Hidden Truth is used only as a final pedagogical check.

## Hidden Truth / unknowns
Truth offsets remain hidden until the learner submits a final assessment. Holdout lines/reference evidence may be generated from the same fixed Truth but are not used directly to tune the learner estimate.

## Inputs
Primary:
- candidate calibrated configuration from P4;
- validation dataset / holdout line set;
- Apply candidate;
- Submit assessment: Adequate / Suboptimal / Inadequate.

Secondary:
- difference-surface/profile threshold display;
- comparison-region selection;
- reference-surface or cross-line view;
- before/after toggle.

Advanced:
- repeatability statistics across several independent line pairs;
- multiple observers/solutions;
- controlled contaminant case that prevents a perfect classic patch-test closure.

## Outputs / visual response
- before/after paired-profile or difference-surface views on identical scales;
- holdout residual metrics not used during P4 fitting;
- remaining systematic pattern detector/annotation;
- calibration-value summary with explicit signs and units;
- acceptance evidence panel: residual magnitude, repeatability, common coverage and warnings;
- final optional Truth reveal showing estimation error `Estimated - Truth` only after submission.

A final assessment should not collapse to one number. At minimum, show both a spatial residual view and a summary metric.

## Observable validation logic
A robust candidate should:
- reduce the intended error signature in the calibration pair;
- also reduce it in independent/holdout evidence;
- not introduce an opposite-sense residual indicating overcorrection;
- preserve agreement across the common swath/feature rather than only at one selected point;
- remain consistent under the same frame/sign convention.

## Interaction sequence
1. Load the P4 candidate without revealing Truth.
2. Apply it to the original pair and inspect the residual.
3. Apply it to a holdout/repeat line pair not used for fitting.
4. Compare before/after difference surfaces/profiles.
5. Ask the learner to classify the result and justify the decision.
6. If Suboptimal/Inadequate, route back to P4 refinement or P3 reacquisition depending on whether the evidence problem is estimation or acquisition geometry.
7. On final submission, reveal Truth and show estimation error as a teaching diagnostic.
8. Present one case where the classic four corrections cannot remove all residuals; use this as the bridge to P6.

## Decision / estimation task
The learner chooses one of:
- **Adequate** — residual signature materially reduced and independent evidence is consistent;
- **Suboptimal** — improvement exists but residual structure/repeatability indicates refinement or better data are needed;
- **Inadequate** — estimate is unsupported, residual worsened/persisted, or acquisition geometry cannot validate the solution.

The UI must state the specific reasons behind the classification rather than provide an opaque score.

## Operational intuition / trade-offs
- fitting the calibration lines is necessary but not sufficient; holdout/reference evidence reduces overfitting to one pair;
- a low average residual can hide structured swath artifacts;
- repeated independent estimates provide evidence of calibration stability;
- a reference surface can expose combined effects beyond the individual patch parameters;
- if a systematic pattern remains after credible classic calibration, the correct next action may be diagnosis, not increasingly aggressive patch adjustment.

## Desired learner message
**A patch-test result is accepted because it improves independent bathymetric agreement and removes the expected systematic signature, not because the estimated number is close to an unseen Truth value.**

## Scientific guardrails
- Truth reveal is assessment-only and must not influence the estimate.
- Do not equate residual RMS with formal TPU; uncertainty analysis is a separate construct.
- Do not hide local/systematic artifacts behind a favorable global statistic.
- Reference-surface agreement tests the integrated result; it does not uniquely identify which subsystem caused any remaining error.
- Self-comparison cannot establish every possible absolute bias, especially an overall vertical bias.
- Acceptance thresholds must be tied to the chosen pedagogical/operational criterion rather than invented arbitrary percentages.
- P5 may identify the need for P6 diagnosis but must not silently fit non-classic parameters.

## Dependencies / forward reuse
Consumes P4 candidate corrections and P3 observations. Passes unresolved structured residuals and calibrated baseline to P6.

## Current implementation / reuse delta
No dedicated P5 production path is currently identified. Reuse difference-surface/profile infrastructure and Truth/Configured comparisons already present in HydroSIM rather than creating validation-only physics. The preserved roll and pitch invariants provide useful first acceptance anchors: zero-error closure, sign closure, mismatch reduction and repeatability.

## Recognized references
- NOAA, **Field Procedures Manual (2020)**, §1.5.6.2–1.5.6.3 — patch-test documentation, independent checking, and reference-surface comparison as a capstone system assessment: <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf>
- IHO International Hydrographic Review, **Survey systems verification and calibration in the hydrospatial domain (2025)** — visual verification after automated patch-test solutions and broader system-calibration context: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- Jerram, K.; Johnson, P.; Ferrini, V., **R/V Neil Armstrong 2019 EM710 Calibration Report (2019)** — operational calibration/review example: <https://scholars.unh.edu/ccom/1727/>
- Jerram, K.; Johnson, P.; Ferrini, V., **2021 R/V Thomas G. Thompson EM302 QAT Report (2021)** — calibration and post-maintenance quality-assurance context: <https://scholars.unh.edu/ccom/1577/>
- Johnson, P.; Beaudoin, J. et al., **Multibeam Advisory Committee – Three Years of Working Towards the Improvement of Multibeam Echosounder Data Collection (2014)** — accuracy/swath-performance tools and patch-test support: <https://scholars.unh.edu/ccom/53/>