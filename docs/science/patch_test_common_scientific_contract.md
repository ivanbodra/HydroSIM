# Patch Test Common Scientific Contract

Status: authoritative common scientific baseline for HydroSIM P1–P6.

## Purpose

This contract fixes the scientific semantics shared by the Patch Test module before P1–P6 receive parameter-specific contracts. It prevents individual lessons, adapters, estimators, or interfaces from defining their own bias signs, state meanings, correction direction, or residual semantics.

The Patch Test module estimates residual calibration quantities from their geometric effect on reconstructed hydrographic observations. It does not, by itself, prove which physical subsystem caused an equivalent residual.

The conventional HydroSIM patch-test scope is:

- equivalent residual latency / time delay;
- transducer pitch alignment;
- transducer roll alignment;
- transducer heading/yaw alignment.

Lever arms, sound-speed errors, heave, water level, positioning, dynamic motion residuals, and other effects may contaminate a calibration exercise, but they are not redefined as conventional patch-test parameters.

## Authoritative dependencies

This contract inherits without modification:

- `docs/conventions.md` for units, NED/body/sensor frames, rotations, attitude signs, lever arms, beam angles, latency, and state categories;
- the canonical sounding-formation / reconstruction chain for transforming observations into navigation-frame soundings;
- `docs/science/timing_clock_sync_v0_1_contract.md` and `docs/science/ped_d14_timing_association_contract.md` for temporal semantics;
- `docs/science/pitch_patch_test_v0_1_contract.md` as reusable pitch-specific capital, subject to this common contract;
- `docs/science/risc.md` and `scientific_registry/models/integration/risc_maingot_2019.yaml` for the distinct P6 RISC method.

No Patch Test implementation may silently override those conventions.

## State model

The invariant is:

`Truth != Observed != Configured != Estimated != Derived`.

For a generic calibration parameter `q`:

- `q_true` — Truth physical/equivalent value used to generate the synthetic exercise;
- `q_cfg` — Configured value used by reconstruction/processing before calibration;
- `delta_q_true = q_true - q_cfg` — Truth correction required for closure;
- `delta_q_candidate` — Configured candidate correction being tried during manual calibration;
- `q_candidate = q_cfg + delta_q_candidate` — candidate processing configuration;
- `estimated_correction` — Estimated correction submitted or returned by an estimator;
- `q_est = q_cfg + estimated_correction` — Estimated calibrated value;
- `estimation_error = q_est - q_true` — Derived Truth-comparison diagnostic;
- dataset/profile/surface residuals — Derived disagreement metrics between reconstructed observations.

A dataset residual is not the same quantity as `estimation_error`. A small inter-line residual may occur in weak or degenerate geometry and must not be reported as proof that `q_est` is close to Truth.

## Canonical correction sign

For every conventional patch-test parameter, HydroSIM reports the **correction to add to the current configured value**:

`q_est = q_cfg + estimated_correction`.

In an identifiable deterministic closure case:

`estimated_correction -> q_true - q_cfg`.

Therefore:

- positive roll correction increases configured roll alignment in HydroSIM's positive roll direction (starboard down);
- positive pitch correction increases configured pitch alignment in HydroSIM's positive pitch direction (bow up);
- positive heading/yaw correction increases configured yaw alignment in HydroSIM's positive yaw direction (starboard/clockwise viewed from above);
- positive latency correction increases the configured HydroSIM latency under the convention `state_used(t) = state_true(t - latency)`.

This additive correction convention is normative. External/vendor patch-test signs must be converted explicitly at the boundary rather than changing HydroSIM semantics.

## Bias insertion and reconstruction

Synthetic exercises must produce calibration signatures through the scientific observation/reconstruction chain, not by applying an arbitrary post-hoc displacement to finished soundings.

The required causal separation is:

1. Truth terrain and vessel trajectory exist independently of calibration error.
2. Truth installation/timing parameters determine the physical or equivalent observations associated with the synthetic acquisition.
3. Observations retain their measurement semantics (for example time/range/beam association) independently of the learner's candidate calibration.
4. Reconstruction uses `q_cfg` or `q_candidate` to transform those observations into navigation-frame soundings.
5. A mismatch between Truth/equivalent generation and Configured reconstruction produces the patch-test signature.
6. Reprocessing the same observations with a candidate correction changes reconstructed soundings; it does not rewrite Truth terrain or the original observations.

Where a parameter is represented as an **equivalent residual** rather than a unique hardware delay/misalignment, that status must be explicit.

## Frames and signs

HydroSIM uses:

- navigation frame `N`: North-East-Down;
- vessel/body frame `B`: Forward-Starboard-Down, origin at VRP;
- sensor/transducer frames as explicitly configured;
- active column-vector rotations with `R_NB = Rz(yaw) Ry(pitch) Rx(roll)`.

Fixed sensor alignment is separate from dynamic vessel attitude. A patch-test alignment parameter is an installation/processing calibration quantity, not a substitute for the vessel's time-varying roll, pitch, or heading.

Heading describes vessel orientation relative to North. Heading/yaw patch-test bias is a fixed alignment/equivalent residual about the vertical axis; it must not be implemented by altering the vessel Truth trajectory heading itself.

## Latency semantics

Positive latency means delayed state association:

`state_used(t) = state_true(t - Delta_t)`, `Delta_t > 0`.

The conventional patch test estimates an equivalent residual timing offset from spatial/geometric disagreement. It does not uniquely identify whether the physical origin was sensor latency, timestamp bias, trigger/Tx delay, processing delay, or another temporal offset.

A candidate latency correction changes the configured temporal association used in reconstruction. It must not change the Truth vessel trajectory or the ping's physical acquisition time.

## Observability principle

A parameter is scientifically estimable only when the selected acquisition geometry and comparison region make its effect observable.

HydroSIM must distinguish:

- **identifiable / adequate** — the chosen data contain sufficient parameter sensitivity and geometric information for a stable determination under the exercise assumptions;
- **weak / suboptimal** — sensitivity exists but the estimate is poorly conditioned or less robust;
- **non-identifiable / inadequate** — the selected geometry is invariant or effectively insensitive to the parameter, so a precise estimate would be scientifically unjustified.

The final quantitative criteria belong in the P1/P2 parameter-specific contracts. They must be based on sensitivity/geometry, not UI heuristics.

Canonical examples that must be preserved:

- pitch requires an along-track slope or identifiable feature; a featureless flat plane is non-identifying for a pure translated near-nadir profile;
- latency requires spatial structure plus a velocity/time lever and is strengthened by materially different speeds under otherwise compatible geometry;
- roll uses reciprocal overlapping swaths and across-track geometry, conventionally over a sufficiently flat region to isolate the characteristic cross-track mismatch;
- heading/yaw requires geometry in which a fixed horizontal angular misalignment moves observations of the same identifiable feature differently between appropriately separated/reciprocal lines.

## Residuals and objective functions

P4 may use profile, point, or surface comparison depending on the parameter and exercise geometry. Every objective must state:

- which reconstructed datasets are compared;
- the common frame;
- the overlap/segment selection rule;
- interpolation/association method;
- residual component(s) used;
- aggregation metric;
- validity/conditioning requirements.

For an objective `J(delta_q)`, the estimated correction may be defined by

`estimated_correction = argmin J(delta_q)`

only when the acquisition/segment is sufficiently identifying and the minimum is meaningfully constrained within the search domain.

A numerical optimizer finding a minimum does not by itself establish observability.

## Manual calibration and automatic estimation

The learner-facing manual loop and any internal numerical estimator must share the same scientific reconstruction and residual definitions.

Manual calibration varies `delta_q_candidate`, reconstructs from the same Observed data, and displays the resulting residual. An automatic estimator, when used for validation or P5 assessment, searches the same candidate parameter space rather than using hidden Truth to generate the answer.

Truth may be used to score/validate an estimate after submission, never as an input to the estimator.

## P1–P6 allocation

- **P1 — Fundamentals & Error Signatures:** parameter-specific forward signatures, symmetries, sign behavior, confounders, and observability intuition.
- **P2 — Area & Line Planning:** quantitative sensitivity/conditioning criteria for acquisition geometry and analysis segments.
- **P3 — Synthetic Acquisition:** deterministic Truth terrain/trajectory, hidden bias injection, observation generation, and replay/provenance contract.
- **P4 — Manual Calibration:** candidate correction application, line/segment association, residual definitions, and parameter-specific objective functions.
- **P5 — Assessment:** Estimated-vs-Truth error, residual-after-correction, tolerances, and safeguards against false confidence from weak geometry.
- **P6 — RISC:** separate Maingot-derived integrated residual-signature model and estimator; conventional patch-test formulas must not be silently substituted for RISC, or vice versa.

## Validation invariants

Every conventional parameter contract must include at least:

1. **Zero closure:** `q_true == q_cfg` gives zero correction and no systematic parameter signature under the isolated deterministic reference case.
2. **Sign closure:** changing the sign of the isolated Truth correction changes the recovered correction consistently with HydroSIM's additive sign convention.
3. **Magnitude closure:** identifiable noiseless reference cases recover `q_true - q_cfg` within declared numerical tolerance.
4. **Correction closure:** applying the recovered correction reduces the relevant inter-dataset residual relative to the uncorrected configuration.
5. **Label/order invariance:** exchanging arbitrary dataset labels must not change the physical estimate when the geometry itself is unchanged; heading/direction-dependent geometry must remain represented explicitly rather than lost through relabeling.
6. **Non-identifiability:** degenerate geometry must not yield a falsely precise calibration result.
7. **Isolation:** single-parameter golden cases hold other conventional residual biases at zero unless the contract explicitly studies confounding.
8. **State separation:** Truth is never overwritten by Configured/Estimated values, and reprocessing never mutates the original Observed acquisition.

## Fidelity boundary

The first Patch Test scientific baseline is deterministic and geometry-first. It may omit stochastic sensor noise, robust statistics, environmental variability, and simultaneous multi-parameter estimation where those are not required for the intended exercise.

Such omissions must be explicit. They must not be compensated by arbitrary display-space distortions or post-hoc sounding offsets.

## References and traceability

Primary reusable HydroSIM references already registered for conventional patch-test practice include NOAA Ocean Exploration patch-test guidance, NOAA HSSD, and R2Sonic patch-test guidance. P6 additionally uses the Maingot/Hughes Clarke RISC material already registered and validated in the Scientific Registry.

This common contract defines HydroSIM state/sign/frame semantics. Parameter-specific external scientific claims must be traced in the P1–P6 contracts to stable bibliography IDs where applicable.
