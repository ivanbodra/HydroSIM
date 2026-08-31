# Scientific Coverage Audit 1

Date: 2026-08-31
Status: initial inventory checkpoint
Role: Scientific Lead
Scope: current `main` scientific implementation, documentation, registry, references, and validation coverage

## Purpose

This audit establishes the scientific state of the existing HydroSIM codebase before proposing new physics.

The central rule is:

> Existing scientific work is project heritage. New models should be proposed only after determining whether the phenomenon is already implemented, documented, registered, or validated.

This checkpoint is intentionally diagnostic. It does not change equations, scientific models, conventions, or architecture.

## Overall finding

HydroSIM's implemented Scientific Core is substantially broader than the current Scientific Registry coverage.

The codebase already contains mature or partially mature implementations for geometry, motion/timing, propagation, sound-speed handling, array/beam physics, waveform processing, detection, sounding reconstruction, transmission loss, and initial sonar-equation terms. Many of these implementations have dedicated tests and some have explanatory scientific documents.

However, the canonical Scientific Registry currently covers only a subset of the implemented models. This creates a traceability gap:

```text
implemented model
    -> tests often exist
    -> documentation sometimes exists
    -> Registry entry may be absent
    -> primary-source mapping may therefore be incomplete
```

The immediate Scientific Lead priority is therefore **scientific consolidation and traceability**, not expansion of physics.

## Coverage status vocabulary

This audit uses four states.

- **Consolidated**: implementation, scientific documentation/registry, conventions, and meaningful validation are substantially aligned.
- **Partially traced**: implementation and tests exist, but Registry and/or source mapping is incomplete.
- **Documentation drift**: implementation exists and current dedicated documentation may exist, but another scientific document contains stale statements about implementation status or scope.
- **Real scientific gap**: the phenomenon is intentionally absent and requires a future scientific-model decision rather than only documentation work.

These labels describe the current traceability state, not the intrinsic scientific quality of a model.

## Initial coverage matrix

| Scientific area | Current implementation evidence | Scientific documentation / Registry | Validation evidence | Initial status | Scientific Lead action |
| --- | --- | --- | --- | --- | --- |
| Coordinate frames, rotations, lever arms, attitude signs | `geometry/rotations.py`, `geometry/transforms.py`, geometry models | `docs/conventions.md`; geometry golden values | unit tests + regression golden values | Consolidated baseline | Preserve conventions; audit source provenance only where external-standard claims are made |
| Truth / Observed / Configured / Estimated / Derived semantics | used across geometry/acquisition architecture | `docs/conventions.md`, Registry README | semantic/API tests distributed across modules | Consolidated architectural invariant | Protect during all future reviews |
| Dynamic motion residuals / RISC integration-error family | motion/integration implementations | dedicated `docs/science/*`; multiple Registry integration records; bibliography | controlled studies + RISC golden/regression tests | Consolidated / advanced | Review individual evidence levels separately, but do not redesign |
| Piecewise-constant layered Snell propagation | `acquisition/layered_propagation.py` | Registry `layered_snell_piecewise_constant.yaml`; sound-speed documentation | independent analytical two-layer anchor, closure, rejection tests | Consolidated reference model | Preserve as reference fidelity; later alternatives must be explicit new models |
| Sound speed at transducer / zero-thickness boundary | dedicated acquisition modules | dedicated documentation + Registry entry | targeted unit/reference experiments | Consolidated reference behavior | Audit source locators and product-specific validity boundaries |
| Element factor | `acquisition/element_factor.py` | scientific behavior described through beam-pattern chain; no dedicated Registry entry found in current tree | targeted tests exist | Partially traced | Create canonical Registry record only after source/equation audit |
| Array factor / coherent beamforming | `array_factor.py`, `beamforming.py`, transmit/receive beamforming modules | `docs/science/array_factor.md`; no dedicated Registry record found in current tree | analytical and implementation tests exist | Partially traced | Verify equations, phase convention, weights, far-field assumptions and primary sources; then register |
| One-way physical beam pattern | `beam_pattern.py` | `docs/science/beam_pattern.md`; no dedicated Registry record found | pattern tests include boresight, grating-lobe/element-null interaction, beamwidth, steering behavior | Partially traced | Register after source audit; preserve normalized field/power semantics |
| Two-way TX × RX beam pattern | `two_way_pattern.py` | `docs/science/two_way_beam_pattern.md`; no dedicated Registry record found | extensive `test_two_way_pattern.py` | Partially traced; minor documentation drift elsewhere | Register; reconcile stale statement in older one-way beam-pattern scope text |
| Mills-Cross geometry / visualization | `geometry/mills_cross.py`, visualization module | dedicated visualization documentation; two-way pattern documentation treats Mills Cross as configuration | dedicated tests | Partially traced | Distinguish geometric configuration from acoustic response model; identify primary references before registry promotion |
| Footprint / finite response mapping | `footprint.py`, `footprint_contribution.py`, `pattern_footprint_2d.py`, refracted footprint module | referenced in explorer docs; no canonical Registry record found | several dedicated tests | Partially traced | Separate purely geometric footprint approximations from pattern-weighted insonification before registration |
| CW and LFM waveform primitives | `acquisition/waveform.py` | Signal Explorer documentation; no canonical Registry record found | waveform tests + sampling tests | Partially traced | Audit standard LFM formulation, time origin, bandwidth convention and range-resolution interpretation before registration |
| Matched filtering / autocorrelation | `acquisition/waveform.py` | Signal Explorer documentation; no Registry record found | direct correlation tests | Partially traced | Add primary signal-processing references and independent numerical anchors; explicitly distinguish discrete implementation from continuous theory |
| Sampling / numerical-resolution diagnostics | `numerical_resolution.py`, waveform sampling checks | architecture/science context distributed | dedicated tests | Partially traced | Determine which parts are scientific models versus numerical diagnostics; avoid unnecessary Registry entries for pure implementation checks |
| Transmission loss: spherical spreading + explicit homogeneous absorption | `acquisition/transmission_loss.py` | implementation docstring; no dedicated scientific document or Registry entry found | `test_transmission_loss.py` | Partially traced | Highest-priority traceability item: register spherical-spreading reference model; keep frequency-dependent absorption coefficient model separate |
| Frequency/environment-dependent seawater absorption | deliberately absent; `alpha` is explicit input | absence documented in transmission-loss implementation | none required yet | Real scientific gap | Compare established absorption models (e.g. Francois-Garrison and alternatives) before choosing fidelity levels; do not embed silently in existing model |
| Bottom detection: strongest matched-filter amplitude peak | `bottom_detection.py` | implementation explicitly labels it a reference detector; no Registry entry found | dedicated tests | Partially traced / didactic-reference model | Decide whether this warrants a Registry scientific model or a documented processing algorithm; avoid implying vendor-equivalent bathymetric detection |
| Phase detection / split aperture | `phase_detection.py`, `phase_detection_convergence.py`, `split_aperture.py` | documentation appears distributed; no dedicated Registry entries found | multiple dedicated tests | Partially traced | High-priority source audit because detection-angle physics can materially affect bathymetry |
| Sounding observation / reconstruction | `sounding_observation.py`, `sounding_reconstruction.py` | conventions + architecture docs; no dedicated Registry records found | strong dedicated tests | Partially traced | Map each transformation to geometry/propagation models rather than creating duplicate sounding equations |
| Area backscatter sonar-equation term | `sonar_equation/backscatter.py` | implementation clearly states `BS = S_b + 10 log10(A/1 m²)` and treats `S_b` as explicit input; no Registry entry found | basic dedicated test | Partially traced | Source and register the area-integration term; retain explicit-input policy for `S_b` |
| Bottom scattering law predicting `S_b` from environment/seabed | deliberately absent | absence explicitly documented | none | Real scientific gap | Future comparison of established seabed-scattering models; not needed merely to visualize the existing area term |
| Full sonar equation / calibrated receive level / SNR | only partial terms currently exist | not yet a canonical integrated scientific model | partial component tests | Real scientific gap | Define only when the Didactic Explorer/Survey Simulator requires the physical quantity; integrate existing terms rather than duplicate them |
| Noise/electronics/channel mismatch | deliberately absent from current reference chains | absences documented in several modules | none | Real scientific gap | Defer until a concrete fidelity requirement exists |
| Uncertainty / truth error / a-posteriori residual distinction | architecture proposed in Issue #11 | Issue #11 documents intended separation | not implemented yet | Real scientific gap already scoped | Scientific Lead to define reference uncertainty framework before implementation; Technical Lead decides integration roadmap |

## Confirmed scientific decisions to preserve

### 1. Geometric ray is not a complete physical beam

`BeamRay` is a geometric pencil-ray proxy. Finite TX/RX apertures and two-way directional response are separate physics layers.

The project must preserve:

```text
propagation geometry != beam-pattern physics
```

### 2. TX and RX apertures remain independent

The current two-way reference composition is

\[
B_{2w}(\mathbf u)=B_{Tx}(\mathbf u)B_{Rx}(\mathbf u),
\]

with the same physical direction transformed independently into the TX and RX array frames.

Mills Cross is one array/installational configuration of this model, not a universal MBES assumption.

### 3. Propagation loss remains separate from scattering and electro-acoustics

The present deterministic propagation layer uses spherical spreading plus an explicitly supplied homogeneous absorption coefficient:

\[
TL_{spread}=20\log_{10}(r/r_0),
\]

\[
TL_{abs}=\alpha r_{km}.
\]

No empirical frequency/environment absorption formula is currently hidden inside this model. This separation is scientifically desirable and should be retained.

### 4. Seafloor scattering strength is not inferred from sediment label

The present sonar-equation backscatter term treats `S_b` as explicit input and computes area integration separately:

\[
BS=S_b+10\log_{10}(A/1\,m^2).
\]

A future seabed-scattering model must be separately referenced and versioned.

### 5. Reference bottom detector is intentionally simplified

The current amplitude detector selects the strongest matched-filter magnitude and contains no threshold, noise, sediment response, or proprietary vendor logic. It must not be presented as a high-fidelity commercial MBES detector.

## Documentation drift identified

`docs/science/beam_pattern.md` still contains scope text stating that transmit × receive two-way pattern is not yet implemented and describes it as the next physical composition.

The current repository also contains:

- `src/hydrosim/acquisition/two_way_pattern.py`; and
- `docs/science/two_way_beam_pattern.md` version 0.2.0,

which explicitly document the implemented two-way model.

This is a documentation-consistency issue, not a scientific-model defect. The stale statement should be corrected in a later documentation-only change after this audit.

## Validation observations

The repository contains extensive tests, but test existence alone is not equivalent to independent physical validation.

During the next audit pass each important model should be classified against the Registry validation classes:

- `implementation_consistency`;
- `closure`;
- `independent_analytical`;
- `source_golden_value`;
- `controlled_numerical_experiment`.

Priority should be given to models where sign, phase, angle, or timing errors can produce visually plausible but scientifically wrong results.

## Priority order for Scientific Lead follow-up

1. **Traceability closure for already implemented high-impact physics**
   - element factor;
   - array factor / beamforming;
   - one-way and two-way beam patterns;
   - waveform + matched filtering;
   - transmission loss;
   - phase/split-aperture detection;
   - sounding reconstruction;
   - area backscatter term.

2. **Documentation consistency**
   - remove stale implementation-status statements;
   - ensure dedicated science documents and Registry records agree on scope.

3. **Reference and validation audit**
   - primary source;
   - exact equation/section/page/figure locator when feasible;
   - evidence level;
   - validity domain;
   - independent numerical anchor where scientifically valuable.

4. **Only then evaluate real new-physics gaps**
   - seawater absorption formulations;
   - full sonar equation / noise / SNR;
   - physically based bottom scattering;
   - uncertainty propagation;
   - higher-fidelity propagation and detection where product requirements justify them.

## Architectural handoff boundary

This audit does not prescribe software architecture or roadmap sequencing beyond scientific dependency.

When a model is scientifically ready for implementation or Registry promotion, the Scientific Lead should provide:

- Scientific question
- Reference model
- Equations
- Variables and units
- Assumptions
- Validity domain
- Expected numerical behavior
- Reference values for testing
- Alternative models
- Recommended fidelity level
- Implementation risks

The Technical Lead & Integration Architect remains responsible for deciding how and when that specification enters the product architecture and roadmap.

## Next Scientific Lead action

Perform a model-by-model traceability pass beginning with the **array/beam chain** and **waveform/transmission-loss chain**, because these models are already exposed or becoming exposed through the Didactic Explorer and can therefore create user-visible scientific claims.
