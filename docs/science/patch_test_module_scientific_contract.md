# HydroSIM Patch Test Module Scientific Contract

Status: authoritative scientific contract for the complete P1–P6 Patch Test module. Implementation remains subject to the Product Owner/Technical Lead phase gate.

## 1. Scope and dependencies

This document completes the scientific allocation across the canonical pedagogical sequence:

- P1 Fundamentals & Error Signatures;
- P2 Patch-Test Planning;
- P3 Synthetic Acquisition;
- P4 Manual Calibration;
- P5 Assessment & Validation;
- P6 RISC / Advanced Integration Diagnostics.

All submodules inherit `docs/science/patch_test_common_scientific_contract.md` and `docs/conventions.md`. The common contract owns state categories and the additive correction convention. This module contract adds parameter-specific signatures, planning/observability requirements, acquisition generation, residual objectives, assessment logic, and the P6 boundary.

The classic solved residuals in P1–P5 are only:

- equivalent timing/latency residual;
- pitch alignment residual;
- roll alignment residual;
- heading/yaw alignment residual.

P6 is a distinct model-based diagnostic exercise and does not expand the definition of the classic patch test.

## 2. Shared parameter semantics

For each classic parameter `q`:

`delta_q_true = q_true - q_cfg`

`q_candidate = q_cfg + delta_q_candidate`

`q_est = q_cfg + estimated_correction`.

In an identifiable deterministic closure case:

`estimated_correction -> delta_q_true`.

Units:

- latency: seconds internally, milliseconds permitted for UI;
- pitch/roll/yaw: radians internally, degrees permitted for UI;
- positions/depths/residual distances: metres;
- vessel speed: metres per second internally, knots permitted as UI conversion.

## 3. P1 — Fundamentals & Error Signatures

P1 teaches forward consequences, not numerical calibration.

### 3.1 Roll

A fixed roll-alignment mismatch rotates the reconstructed receive geometry about the vessel forward axis. With the same flat seabed observed on reciprocal headings, the cross-track effect reverses in navigation space and is most visible away from nadir.

Reference acquisition:

- same line;
- reciprocal headings;
- same nominal speed;
- flat or sufficiently uniform seabed;
- overlapping swaths;
- latency, pitch and yaw residuals zero in the isolated case.

Observable: cross-track/depth disagreement between reciprocal swaths that grows in leverage toward outer beams. The lesson must not imply that a flat bottom makes roll the only possible error in unrestricted field data; it is an isolation geometry under the controlled scenario.

### 3.2 Pitch

A pitch-alignment mismatch rotates reconstructed geometry about the body `+Y` axis. Reciprocal passes over the same along-track slope/feature expose opposite-sense along-track placement of that feature.

Reference acquisition:

- same line;
- reciprocal headings;
- same speed;
- distinct along-track slope/feature;
- near-nadir or explicitly selected common profile for the first slice.

The existing `pitch_patch_test_v0_1_contract.md` remains authoritative for the pitch estimator/sign details. A featureless flat plane is non-identifying for the minimum translated near-nadir profile comparison.

### 3.3 Heading/yaw

A fixed heading/yaw alignment mismatch rotates reconstructed sonar geometry horizontally about the down axis relative to the vessel/navigation frame. For two laterally offset, parallel, same-direction lines observing the same distinct slope/feature in their overlapping outer swaths, the same feature is horizontally misplaced differently from the two vessel tracks.

Reference acquisition:

- parallel offset lines;
- same direction;
- same speed;
- distinct slope/feature;
- sufficient common outer-swath coverage of the same physical seabed.

The diagnostic variable is the disagreement of the common feature/surface in navigation coordinates after reconstruction with the candidate yaw alignment. A featureless, translationally invariant surface or absent common coverage is non-identifying.

### 3.4 Timing/latency

HydroSIM positive latency is a delayed state association:

`state_used(t) = state_true(t - Delta_t)`.

For constant straight-line velocity vector `v`, the first-order horizontal position consequence of using a delayed position state is

`delta_p ~= -v * Delta_t`.

For scalar along-track speed `V`, the magnitude scale is

`|delta_x| ~= V |Delta_t|`.

The patch-test comparison uses same-direction observations at materially different speeds over the same distinct slope/feature. A fixed timing residual therefore creates different spatial displacements; their first-order separation scales with

`|Delta x_12| ~= |V_2 - V_1| |Delta_t|`.

This relation is an intuition/validation anchor, not a substitute for reconstruction through the canonical timing and trajectory model.

If `V_1 == V_2` under otherwise identical constant-velocity geometry, this differential timing observable collapses. A featureless translation-invariant bottom is also inadequate for the profile-registration form of the test.

A patch-test latency estimate is an equivalent residual timing correction. It does not uniquely diagnose the physical hardware/software source of the delay.

### 3.5 P1 classification rule

P1 may classify the isolated controlled signature only when the prescribed geometry is present. In combined/contaminated cases it must allow `confounded / insufficient evidence`; it must not force one of the four classic labels.

## 4. P2 — Patch-Test Planning

P2 evaluates whether a proposed line/terrain plan provides the intended comparison geometry. It does not estimate the hidden bias.

### 4.1 Common geometric adequacy

A plan is eligible for `Adequate` only if:

1. both datasets observe a non-empty common physical seabed region relevant to the target parameter;
2. the intended direction/speed/offset contrast is present;
3. the terrain contains the spatial information required by that comparison;
4. the comparison region is not reduced to a numerically negligible sliver by the chosen swath/line geometry.

HydroSIM should compute common coverage geometrically from the planned swath footprints and terrain extent, not from a decorative overlap percentage.

### 4.2 Parameter-specific adequacy

Roll:
- reciprocal directions on the same nominal line;
- common across-track swath coverage;
- flat/uniform comparison region preferred for isolation.

Pitch:
- reciprocal directions on the same nominal line;
- same nominal speed;
- common along-track profile/surface containing a distinct slope/feature.

Heading/yaw:
- two offset parallel lines in the same direction;
- common outer-swath coverage;
- distinct feature/slope represented in that overlap.

Latency:
- same line and direction;
- distinct feature/slope;
- two materially different speeds.

### 4.3 Adequate / Suboptimal / Inadequate

`Inadequate` is required for a structural loss of observability: no common seabed, wrong direction relationship, no speed contrast for the differential latency case, flat/translation-invariant profile for minimum pitch, or no identifiable common feature/structure for heading/yaw.

`Suboptimal` may be used when the required mechanism exists but sensitivity/common support is weak. `Adequate` means the deterministic scenario meets the declared reference geometry; it is not a universal field-survey certification.

Do not invent universal minimum slope, depth, line separation, or speed difference as physical constants. Scenario defaults may be chosen for pedagogy and must be labelled defaults.

## 5. P3 — Synthetic Acquisition

P3 turns an accepted plan into immutable Observed evidence.

### 5.1 Causal generation chain

For every run:

`Truth terrain + Truth trajectory + Truth/equivalent installation/timing state`

`-> acoustic/geometric observation generation`

`-> immutable Observed measurements + acquisition metadata`

`-> reconstruction with Configured calibration`

`-> Derived navigation-frame soundings`.

The hidden calibration residual must act through observation/state association and reconstruction. It must not be represented by shifting finished soundings in display space.

### 5.2 Required provenance

Each synthetic run must retain at least:

- run ID;
- line geometry/trajectory identity;
- direction/heading history;
- speed/time history;
- ping/observation times;
- sonar/transducer identity;
- applicable configuration snapshot/history;
- hidden scenario Truth reference (not learner-visible during estimation);
- deterministic seed if stochastic extensions are enabled.

Paired runs share the same terrain Truth.

### 5.3 Fitness for calibration

P3 may report `usable`, `marginal`, or `reacquire` based on the P2 geometric conditions plus execution evidence. It must not solve a correction value.

## 6. P4 — Manual Calibration

P4 applies a candidate correction to the Configured model and reconstructs the same Observed data.

### 6.1 Common objective form

For target parameter `q`, define a valid comparison operator that returns paired residual components over common physical support:

`r_i(delta_q) = A_i(delta_q) - B_i(delta_q)`.

The first deterministic objective is

`J(delta_q) = sqrt(mean(r_i(delta_q)^2))`.

`estimated_correction = argmin J(delta_q)`

is valid only when the P2/P3 geometry is identifying and the minimum is constrained within the declared search interval.

Manual mode need not run an optimizer: the learner changes `delta_q_candidate` and sees the same `J` and spatial residual used by the reference estimator.

### 6.2 Roll objective

Reconstruct reciprocal swaths using the candidate roll alignment. Transform both datasets into the common navigation frame. In the valid overlapping flat-bottom region, associate/interpolate soundings across a common cross-track or common horizontal grid and compute vertical/surface disagreement.

The estimator minimizes that reciprocal surface/profile mismatch. The comparison must preserve port/starboard and reciprocal-heading geometry; it may not simply compare beam index to beam index when those samples do not represent the same seabed location.

### 6.3 Pitch objective

Use the existing pitch contract: reciprocal near-nadir profiles reconstructed on a common navigation-frame along-track grid; minimize RMS depth/profile mismatch over overlap.

### 6.4 Heading/yaw objective

Reconstruct both same-direction offset-line datasets with candidate yaw alignment. Restrict comparison to the common outer-swath region containing the same identifiable feature/slope. Register/interpolate both onto a common navigation-frame horizontal coordinate/profile or surface grid, then minimize the feature/surface disagreement.

The candidate changes the fixed sensor alignment used in reconstruction. It does not rotate the Truth vessel tracks.

### 6.5 Latency objective

Reconstruct the two same-direction, different-speed datasets using candidate configured latency in the canonical state-association model. Compare the same feature/slope in a common along-track navigation coordinate and minimize profile/feature mismatch.

The candidate latency changes which trajectory/sensor state is associated with each observation. It does not shift observation timestamps, mutate the Truth trajectory, or alter the physical acquisition epoch.

### 6.6 Search behavior

Reference automatic estimators used for validation may use bounded deterministic grid/refinement or a bounded one-dimensional optimizer. The bounds and resolution are scenario/configuration parameters, not scientific constants. The solution must report boundary minima or weak/flat objectives as such rather than silently claiming a well-determined estimate.

## 7. P5 — Assessment & Validation

P5 separates calibration fit from validation.

### 7.1 Required evidence

A candidate is assessed using:

- original calibration-pair spatial residual and summary metric;
- independent/holdout repeated evidence not used to choose the candidate, when the exercise provides it;
- residual structure/sign after correction;
- geometric adequacy/conditioning warnings inherited from P2/P3;
- only after learner submission, optional Truth comparison.

### 7.2 Truth diagnostic

After submission:

`estimation_error = q_est - q_true`.

This is distinct from inter-dataset residual RMS. Neither quantity is TPU.

### 7.3 Assessment categories

`Adequate` requires, for the deterministic reference exercise:

- target residual materially reduced relative to the uncorrected case;
- no systematic opposite-sense overcorrection;
- holdout/repeat evidence, when present, improves consistently;
- the P2/P3 geometry was identifying.

`Suboptimal` covers partial improvement, weak conditioning, boundary/flat objective behavior, or residual structure that warrants refinement/reacquisition.

`Inadequate` covers worsened/persistent target signature, unsupported estimate, or non-identifying acquisition.

No universal arbitrary percentage reduction is scientifically canonical. Each scenario/test may define numerical tolerances from sampling/search resolution and validation needs.

## 8. P6 — RISC / Advanced Integration Diagnostics

P6 is governed by `docs/science/risc.md` and `scientific_registry/models/integration/risc_maingot_2019.yaml`.

The current canonical six-parameter Maingot-style reference vector is:

- GNSS–MBES X lever-arm error `Delta Lx`;
- GNSS–MBES Y lever-arm error `Delta Ly`;
- INS–MBES latency `Delta t`;
- INS scale factor `Delta rho`;
- INS–MBES Z-axis misalignment `Delta kappa`;
- effective surface sound-speed error `Delta SSS`.

P6 begins from a baseline that has passed the classic P1–P5 exercise and asks whether a candidate integration-error model explains remaining structured residuals.

The existing HydroSIM RISC code is a forward/reference parameterization, not by itself the full estimator. A production multi-parameter estimator requires an explicit objective, bounds, identifiability/conditioning treatment, optimization method, and validation anchors before it may claim parameter estimates.

The smoothed/reference bathymetric surface used in RISC is an estimator construct, not hidden Truth. External errors and reference-surface inadequacy can bias the solution. A low objective does not prove a unique physical diagnosis.

## 9. Cross-submodule validation anchors

The module must preserve these deterministic scientific tests:

1. zero bias gives zero systematic isolated signature and zero correction;
2. sign reversal of an isolated hidden correction reverses the estimated correction under HydroSIM's additive convention;
3. identifiable noiseless cases recover the hidden correction within declared numerical tolerance;
4. applying the recovered correction reduces the intended spatial residual;
5. arbitrary dataset-label exchange does not change the physical estimate when acquisition geometry is unchanged;
6. degenerate planning cases are rejected or marked weak, not given falsely precise estimates;
7. P4 reprocessing leaves Truth and Observed acquisition immutable;
8. latency spatial effect scales with vessel speed in the constant-velocity first-order anchor;
9. zero speed contrast collapses the classical differential latency observable;
10. pitch flat-profile degeneracy is exposed;
11. heading/yaw without common identifiable overlap is exposed;
12. roll reference closure is verified in common navigation coordinates, not by beam-index coincidence;
13. P5 `estimation_error` is not labelled residual RMS or TPU;
14. P6 does not silently substitute its six-parameter model for the classic four-parameter patch test.

## 10. References

Stable bibliography IDs and P1–P6 allocation are maintained in:

- `scientific_registry/references/bibliography.yaml`;
- `scientific_registry/references/coverage.yaml`;
- `docs/science/patch_test_references_by_submodule.md`.

External practice claims are source-backed. HydroSIM state/sign semantics and the exact common objective/state architecture are internal contracts derived consistently from those practices and the shared Scientific Core.
