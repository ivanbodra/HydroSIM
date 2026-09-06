# PED-D9 Detection Extension Contract

Status: authoritative extension for remaining PED-D9 learner atoms  
Experience: `PED-D9`  
Scope: deterministic, vendor-neutral first production slice

## Purpose

This extension defines the smallest scientifically defensible semantics for thresholding, multiple detections, and false/missed classification on top of the existing matched-filter correlation used by the canonical PED-D9 amplitude detector. It does not define a vendor bottom detector and does not add stochastic noise, seabed scattering, phase detection, or proprietary High Density behavior.

## 1. Detection threshold

Let `A[k] = |R[k]|` be the magnitude of the matched-filter correlation within the configured detection window.

Define a normalized correlation magnitude

`a[k] = A[k] / max_j A[j]`

when the window contains at least one strictly positive magnitude. Therefore `0 <= a[k] <= 1` and the strongest sample has `a = 1`.

The learner threshold `tau` is **Configured**, dimensionless, with `0 <= tau <= 1`.

A candidate is threshold-eligible only when

`a[k] >= tau`.

This threshold is relative to the peak of the supplied correlation window. It is not received level, SNR, detection probability, false-alarm probability, or an absolute acoustic threshold.

If the window is identically zero, there are no eligible detections.

## 2. Candidate generation and multiple detections

For the vendor-neutral first slice, detection candidates are local maxima of `a[k]` inside the configured detection window that satisfy `a[k] >= tau` and have non-negative arrival lag under the existing PED-D9 timing convention.

A local maximum is a sample whose magnitude is not smaller than its immediate neighbors. For flat equal-valued plateaus, the implementation must select one deterministic representative index rather than emit duplicate detections from the same plateau.

Candidate ordering is deterministic:

1. descending normalized magnitude;
2. earlier arrival lag as tie-breaker.

`multiple_detection = false` returns only the first candidate under this ordering.

`multiple_detection = true` returns all eligible candidates, preserving the ordered set above. Each returned object is an `Observed BottomDetection`; candidate ranking and count are `Derived`.

This is a didactic peak-retention policy over a supplied matched-filter response. It must not be presented as a universal manufacturer algorithm.

## 3. High Density boundary

`High Density` is **not a universal physical or algorithmic category with a vendor-independent behavior distinct from generic multiple detection**. HydroSIM must therefore not invent a separate acoustic/detection equation or claim a generic sounding-density multiplier for this label.

Authoritative scientific disposition for the current PED-D9 slice:

- generic multiple detections per receive beam are scientifically defined by section 2;
- a separate `High Density` control remains unavailable unless Technical Lead either:
  1. redefines/renames the learner atom to a vendor-neutral quantity with distinct semantics; or
  2. selects a specific sourced manufacturer/algorithm behavior for a higher-fidelity model.

Until then, `High Density` must not be implemented as an alias that silently duplicates `multiple_detection`.

## 4. False and missed detection classification

False/missed labels require an explicit didactic Truth reference. For the first slice, the configured signal scenario may provide a finite set of **Truth echo arrival lags** `K_truth` in samples. These are scenario truth, not observations.

A returned detection at lag `k_d` matches a Truth echo at lag `k_t` when

`|k_d - k_t| <= delta_k`

where `delta_k >= 0` is a Configured matching tolerance in samples. Matching is one-to-one, choosing the smallest absolute lag difference first; ties use earlier detection lag.

Classification:

- matched detection -> `true_detection`;
- unmatched returned detection -> `false_detection`;
- unmatched Truth echo -> `missed_detection`.

These labels are `Derived` by comparison of Observed detections against configured scenario Truth. They are not estimates of real-world probability of false alarm or probability of detection.

If no Truth echo reference is supplied, HydroSIM may show detections but must not label them true/false/missed.

## 5. Learner-visible comparison quantities

Renderable scientific outputs may include:

- normalized matched-filter magnitude and configured threshold;
- eligible candidate peak locations;
- retained detection locations/count for single- versus multiple-detection mode;
- true/false/missed classification markers when Truth echo arrivals are explicitly present;
- detection count per beam and detection separation in samples or seconds.

No separate `High Density` comparison is scientifically authorized until the product atom is redefined or a sourced algorithm is selected.

## 6. State semantics

Configured:
- detection window;
- threshold `tau`;
- single/multiple-detection selector;
- optional Truth echo arrival lags for the didactic scenario;
- matching tolerance `delta_k`.

Observed:
- returned `BottomDetection` objects.

Derived:
- normalized correlation magnitude;
- local-maximum candidates/ranking;
- retained detection count;
- true/false/missed labels relative to explicit Truth.

No new `Estimated` quantity is introduced.

## 7. Acceptance anchors

- one unique positive peak with `tau <= 1` yields one candidate;
- raising `tau` above a secondary peak removes that secondary candidate but not the normalized main peak at `a=1`;
- `multiple_detection=false` returns the strongest eligible candidate only;
- `multiple_detection=true` returns all eligible local maxima in deterministic order;
- an all-zero window yields no detections;
- with one Truth lag and one detection at the same lag, classification is one true detection with no false or missed events;
- one extra unmatched detection adds one false detection;
- one unmatched Truth echo adds one missed detection;
- no false/missed labels are emitted without explicit Truth reference;
- `High Density` has no separate executable behavior in this contract.

## 8. Fidelity boundary and traceability

This contract extends the existing PED-D9 reference detector only with deterministic thresholding, local-peak retention, and Truth-relative didactic classification. It deliberately avoids stochastic signal detection theory, CFAR, vendor bottom-detection logic, phase-ramp processing, seabed-response models, and proprietary high-density modes.

Primary HydroSIM dependencies:
- `docs/science/ped_d9_scientific_contract.md`;
- `src/hydrosim/acquisition/bottom_detection.py`;
- `docs/science/signal_waveform_contract.md`;
- `docs/science/d8_observation_state_contract.md`.
