# P6 — RISC / Advanced Integration Diagnostics

Status: **Mapped as advanced/research extension**

## Purpose
Bridge from the classic patch test to the harder reality of residual integration errors that can remain after roll, pitch, heading/yaw and timing calibration. P6 introduces the learner to model-based diagnosis inspired by Brandon Maingot's Rigorous Inter-Sensor Calibrator (RISC) work without redefining the classic patch test itself.

## Dominant discovery

```text
classic patch test passes
  -> structured residuals may still remain
  -> residuals can correlate with motion / space / time / sound-speed model errors
  -> a forward georeferencing model predicts how candidate integration errors deform bathymetry
  -> estimate the parameter set that best explains the residual field
```

P6 is not simply 'a more powerful patch test'. It is a distinct advanced diagnostic/calibration framework.

## Hidden Truth / unknowns
Advanced scenarios may use the six Maingot-style integration-error parameters already represented in HydroSIM's reference implementation:
- GNSS–MBES X lever-arm error `ΔLx`;
- GNSS–MBES Y lever-arm error `ΔLy`;
- INS–MBES latency `Δt`;
- INS scale factor `Δρ`;
- INS–MBES Z-axis misalignment `Δκ`;
- effective surface sound-speed error `ΔSSS`.

These parameters belong to the P6 research/diagnostic exercise only. They do not expand the P1–P5 definition of classic patch-test solved parameters.

## Inputs
Primary:
- calibrated P1–P5 baseline configuration;
- advanced residual scenario;
- candidate diagnostic parameter family or bounded parameter set;
- selected residual region / smoothed-reference scale;
- Run diagnostic / Recompute.

Secondary:
- motion time series visibility;
- bathymetric residual filtering/smoothing scale;
- candidate parameter bounds;
- single-parameter versus coupled estimation mode;
- surface sound-speed and motion observables relevant to the selected model.

Advanced:
- multi-parameter optimization only after single-error signatures are understood;
- noise/outlier robustness controls tied to a validated estimator;
- alternative reference surfaces / regularization only with an explicit scientific contract.

## Outputs / visual response
Required synchronized views:
- observed bathymetric surface and smoothed/reference surface;
- residual field `observed - reference`;
- relevant motion/sensor time series;
- predicted residual pattern for the active candidate error model;
- measured-versus-predicted residual comparison;
- objective/cost value across candidate parameters;
- estimated parameter(s) with confidence/identifiability indicator where the estimator supports it;
- corrected/reconstructed surface after applying the candidate estimate;
- optional final Truth reveal for simulation assessment.

Recommended causal display:

```text
candidate integration error
  -> modified sensor/georeferencing state
  -> reconstructed soundings
  -> predicted residual pattern
  -> compare with measured residuals
```

## Observable signature
Unlike P1–P4, P6 should emphasize that several integration errors can generate periodic or motion-correlated bathymetric residuals and that signatures can be confounded. The learner should inspect whether the residual covariance/geometry is actually consistent with the candidate model rather than relying on one visual archetype.

## Interaction sequence
1. Start from a dataset that has already passed the classic patch-test exercises.
2. Show a remaining structured residual/wobble without exposing its cause.
3. Correlate the residual with motion/trajectory context.
4. Activate one Maingot-style error model and vary its candidate magnitude; show the predicted residual field change.
5. Compare measured and predicted residuals.
6. Estimate one parameter in an isolated deterministic case.
7. Reveal Truth only after submission and compare estimated versus hidden error.
8. Introduce a two-error/confounded case; show that identifiability becomes harder and a low cost may not guarantee a unique physical explanation.
9. Final integrated mode: run a bounded multi-parameter diagnostic using a validated estimator when available.

## Decision / estimation task
The learner must decide:
- whether the residual is adequately explained by the selected model family;
- which parameter(s) are identifiable from the available motion/terrain/data;
- whether to accept the estimate, gather better data, or reject the model explanation.

## Operational intuition / trade-offs
- small residual integration errors may be difficult to recognize visually, especially in deeper water or when several errors interact;
- model-based diagnosis can exploit known relationships between motion, sensor geometry and bathymetric residuals;
- richer parameterization increases explanatory power but also increases confounding/non-uniqueness risk;
- a good forward georeferencing model is essential because the estimator can only be as valid as the model linking errors to soundings;
- external environmental effects and imperfect reference surfaces can bias the diagnostic objective.

## Desired learner message
**Passing a classic patch test does not guarantee a perfectly integrated multibeam system. Persistent structured residuals require a model-based diagnosis that tests whether specific inter-sensor errors can actually explain the observed bathymetric pattern.**

## Scientific guardrails
- P6 must be labelled advanced/research-inspired; do not present RISC as a universal operational standard or manufacturer routine.
- HydroSIM's existing `risc_maingot.py` is explicitly a reference implementation of Maingot's published error parameterization, **not the RISC estimator itself**.
- Preserve Maingot-to-HydroSIM sign crosswalks explicitly; do not silently reinterpret published signs.
- The Maingot 2019 parameterization includes six advanced integration errors that are not the same set as classic roll/pitch/yaw patch-test corrections.
- Do not claim a unique diagnosis when multiple parameter combinations produce comparable residuals.
- The smoothed bathymetric surface is an estimator/reference construct, not unquestionable seafloor Truth.
- External residual sources such as heave, water-column modelling, bubbles/interference or seafloor-model inadequacy can contaminate the objective.
- Multi-parameter optimization must not be implemented until the Scientific Core owns the full estimator contract, bounds, objective and validation behavior.

## Dependencies / forward reuse
Consumes the calibrated P5 baseline plus Acoustic Lab geometry, timing, motion and sounding formation. P6 can later inform Acquisition Simulator diagnostics and QA tooling, but it must not become a prerequisite for the classic P1–P5 learning path.

## Current implementation / reuse delta
`src/hydrosim/integration/risc_maingot.py` already provides transparent functions for the six Maingot 2019 integration-error parameters and explicit sign crosswalks. It intentionally does **not** implement the optimizer/estimator. P6 implementation should therefore proceed in two stages after Product Owner authorization:
1. visualization of forward-model error consequences from the existing reference functions;
2. a separately specified/validated RISC-like estimator built by Scientific Lead/Software Engineering, without treating the reference parameterization as an estimator.

## Recognized references
- Maingot, B. A., **High-Frequency Motion Residuals in Multibeam Echosounder Data: Analysis and Estimation (M.S. thesis, University of New Hampshire, 2019)** — foundation for the six integration-error parameterization and model-based residual analysis: <https://scholars.unh.edu/thesis/1301/>
- Maingot, B.; Hughes Clarke, J. E.; Calder, B. R., **High Frequency Motion Residuals in Multibeam Data: Identification and Estimation (2019)** — traditional patch-test limitations and systematic integration residuals: <https://scholars.unh.edu/ccom/1683/>
- Maingot, B., **An Efficient and Robust Real-Time Calibration Routine for Inter-Sensor Offsets Within Integrated Multibeam Systems (2023)** — RISC continuation, model-based residual minimization and real-time extension: <https://scholars.unh.edu/ccom_seminars/408/>
- UNH/NOAA Joint Hydrographic Center, **2020 Annual Report** — simulator/known-Truth use and refinement of the RISC georeferencing model including non-concentric TX/RX geometry: <https://ccom.unh.edu/sites/default/files/progress_reports/jhc-ccom-2020-annual-report-web.pdf>
- IHO International Hydrographic Review, **Survey systems verification and calibration in the hydrospatial domain (2025)** — broader verification/calibration context and limits of patch-test-only reasoning: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- HydroSIM reference implementation: `src/hydrosim/integration/risc_maingot.py`.