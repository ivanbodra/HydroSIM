# P4 — Manual Calibration — Visual Treatment

Pedagogy: `docs/pedagogy/patch_test/P04_manual_calibration.md`  
Science: `docs/science/patch_test_module_scientific_contract.md` §6

## Visual purpose

Make manual calibration feel like **reconstructing the same Observed evidence with a candidate correction and watching the common-support residual close**.

Learner question: **Which candidate correction best aligns the two datasets over the same physical seabed?**

## Dominant composition

Use one connected calibration instrument:

- compact candidate-correction control at left;
- dominant spatial/profile comparison at center;
- compact residual/objective view adjacent or below.

The correction slider must not become the visual protagonist. The spatial residual is the experiment.

## Parameter-specific scenes

### Roll

Show reciprocal swath/profile disagreement in a common navigation frame over the valid overlapping region. The learner should see outer-beam mismatch collapse as the candidate approaches the solution.

### Pitch

Show reciprocal near-nadir/common along-track profiles over the identifying slope/feature. Feature registration should improve visibly with the candidate correction.

### Yaw / Heading

Show the same identifiable outer-swath feature/surface from two same-direction offset lines, reconstructed on common navigation coordinates.

### Latency

Show the same feature/profile reconstructed from different-speed observations. Candidate latency changes state association/reconstruction, not the physical observation epoch.

## Primary controls

- one candidate-correction slider;
- paired numeric input only when useful;
- view mode: `Current | Residual | Compare`;
- optional `Show common support`;
- reset to Configured state.

Do not expose multiple residual-family corrections simultaneously in the first manual-calibration experience unless pedagogy explicitly calls for it.

## Residual and objective

Show the same spatial residual that underlies the canonical objective. A compact `J(Δq)` trace may show current position and objective value, but should remain subordinate to the physical mismatch.

If the objective is flat, weak, or hits a search boundary, make that visible. Do not style every minimum as a confident solution.

## Immutable-state cue

Observed points/profiles retain the same neutral solid visual identity throughout candidate changes. Only Configured/Derived reconstruction and residual overlays respond. This is a key visual invariant.

## Before/current comparison

Use muted Configured/before geometry and bright Candidate/current geometry on the same scale. Avoid separate autoscaled plots that make improvement impossible to judge visually.

## Acceptance

P4 passes when the learner can move one candidate correction and immediately see the corresponding reconstruction/residual change while Observed data and Truth remain visually immutable.

## Referenced bibliography IDs

`noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `r2sonic_2017_patch_test`.

Exact HydroSIM objective/state/sign semantics remain internal contracts. See `99_references_by_submodule.md`.
