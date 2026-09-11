# D17 — Uncertainty / TPU

Status: **Mapped**

**Decision:** `KEEP + REFINE + MAKE STANDARD-vs-EXPANDED UNCERTAINTY EXPLICIT`  
**Current:** `web/pedagogical-explorer/src/UncertaintyLab.tsx`  
**Scientific Core:** `src/hydrosim/integration/uncertainty.py`, `src/hydrosim/app/uncertainty_scalar_api.py`, `src/hydrosim/app/uncertainty_api.py`  
**Historical implementation alias:** `PED-D18`; pedagogical numbering here is authoritative.

## Purpose

Teach that a hydrographic sounding is not known exactly: uncertainty from positioning, attitude, ranging, sound speed, installation, timing, water level and other contributors propagates through the measurement geometry into uncertainty of the final sounding.

D17 must give the learner practical intuition for **where sounding uncertainty comes from, why the dominant contributor changes with geometry, and why uncertainty is not the same thing as realized error**.

The first production slice is deliberately a controlled first-order analytical model. It is not a complete commercial TPU engine and not an automatic IHO survey-order compliance calculator.

## Dominant discovery

```text
uncertainty in measured / configured inputs
  -> measurement geometry gives each source a sensitivity
  -> covariance propagates through that geometry
  -> sounding-position covariance
  -> horizontal / vertical uncertainty summaries
```

The most important causal point is:

```text
same input uncertainty + different beam geometry
  -> different contribution to the sounding uncertainty
```

Examples from the registered first-slice model:

```text
roll uncertainty × slant range / beam angle
  -> mainly across-track / vertical consequence

range + effective sound-speed uncertainty
  -> direction follows the acoustic ray

timing uncertainty × vessel speed
  -> along-track consequence

water-level uncertainty
  -> vertical consequence
```

A second essential distinction is:

```text
UNCERTAINTY
  = quantified dispersion / interval associated with the measurement result

REALIZED ERROR
  = difference from Truth, known only when an accepted Truth/reference exists

RESIDUAL
  = difference between two defined observations / solutions
```

The learner must not leave D17 treating uncertainty as an error vector that simply happened.

## Inputs

### Primary — guided first-slice controls

All are **standard uncertainties (1σ)** and non-negative:

1. horizontal position uncertainty `u_position_horizontal` [m];
2. roll uncertainty `u_roll` [rad or clearly converted mrad];
3. slant-range uncertainty `u_range` [m];
4. effective sound-speed uncertainty `u_sound_speed` [m/s];
5. across-track installation / offset uncertainty `u_offset_across` [m];
6. timing uncertainty `u_timing` [s or ms with explicit conversion];
7. water-level / vertical-reduction uncertainty `u_water_level` [m].

The current scalar model uses one horizontal-position control to populate equal independent along/across standard uncertainties internally.

### Scenario geometry — fixed first, then exposed progressively

- slant range `r`;
- across-track beam angle `β`;
- nominal sound speed `c`;
- vessel speed `v`.

These are scenario quantities, not themselves learner uncertainty controls in the first interaction. Beam angle is the most important geometry parameter to expose after the learner understands isolated contributors.

### Advanced

- coverage factor `k`, only when expanded uncertainty is shown;
- covariance / correlation between inputs using the generic uncertainty API;
- additional uncertainty sources only after an explicit Scientific-Core contract exists for them.

Do not add pitch, heading, full SVP covariance, detection uncertainty, dynamic heave uncertainty or datum-transformation uncertainty as decorative frontend sliders. They are valid real-world contributors but are outside the current controlled scalar contract.

## Outputs / visual response

### A. Sounding uncertainty geometry

Show one sounding in the registered local `along / across / down` frame with an uncertainty representation derived from the propagated covariance.

Required:
- sounding point at the centre;
- horizontal uncertainty summary;
- vertical uncertainty summary;
- clear axis/frame labels;
- beam-angle / geometry context.

A display ellipse/ellipsoid must represent the computed covariance or a clearly labelled pedagogical projection. Do not draw an arbitrary decorative halo whose size is merely normalized to the current panel.

### B. Component standard uncertainties

Show:
- `u_along` [m];
- `u_across` [m];
- `u_down` [m];
- propagated covariance matrix available as advanced evidence.

The current `combined_3d_standard_uncertainty_m` may be shown only as **3-D combined standard uncertainty**. Do not label it as a universal definition of TPU or as an IHO compliance statistic.

### C. THU / TVU semantics

For the current scalar pedagogical model, show the Core-derived horizontal and vertical summaries but distinguish **standard uncertainty** from **expanded / 95%-level uncertainty**.

The current API returns:

```text
THU-like pedagogical standard summary = sqrt(u_along² + u_across²)
TVU-like pedagogical standard summary = u_down
```

These must not be visually presented as IHO S-44 95%-confidence THU/TVU unless the required coverage transformation and statistical assumptions have actually been applied.

Recommended learner-facing labels for the first slice:
- `Horizontal standard uncertainty`;
- `Vertical standard uncertainty`.

Then, in an explicit coverage experiment:

```text
standard uncertainty u
  -> choose / justify coverage factor or probability
  -> expanded uncertainty U
```

Only after that may the interface compare against an external requirement defined at the same confidence/coverage basis.

### D. Contribution view

Rank the per-input **variance contributions** calculated by the Scientific Core. When one input changes, the learner must see the corresponding contribution bar and final sounding uncertainty respond together.

Keep units explicit: variance contributions are `m²`; standard uncertainties are `m`.

### E. Geometry sweep

Show uncertainty across several across-track beam angles using the same model and fixed axes. The learner should see that the contribution pattern changes across the swath even when the input uncertainty magnitudes remain unchanged.

Recommended comparison:
- nadir;
- intermediate beams;
- outer beams on both sides.

Port/starboard reversal may reverse signed sensitivities without changing variance for a single symmetric independent contributor; the visualization must not falsely imply an uncertainty magnitude asymmetry when the model predicts symmetry.

### F. Optional Truth / verification view

The generic Core supports Truth-error and verification residuals. If exposed, show them beside uncertainty rather than replacing it:

```text
uncertainty envelope / covariance
vs
Derived - Truth error vector
vs
A - B verification residual
```

This is the strongest visual mechanism for teaching that uncertainty, error and residual are different quantities.

## Interaction sequence

1. **Start simple — one source at a time.** Use a fixed sounding geometry and set all uncertainty sources to zero. Confirm zero propagated uncertainty.
2. Increase **horizontal position uncertainty only**. Observe the direct horizontal contribution.
3. Reset and increase **water-level uncertainty only**. Observe the vertical one-for-one contribution in the current controlled model.
4. Reset and increase **timing uncertainty only** at non-zero vessel speed. Observe along-track uncertainty; then change vessel speed to reveal the `timing × speed` sensitivity.
5. Reset and increase **range uncertainty only**. At nadir it is primarily vertical; move the beam outward and watch its contribution redistribute across horizontal/vertical components.
6. Repeat with **effective sound-speed uncertainty**. Emphasize that the current `c·TWTT/2` sensitivity is a homogeneous-medium teaching case, not a replacement for D4 ray tracing.
7. Increase **roll uncertainty**. Compare nadir and outer-swath geometry and observe the range/angle-dependent consequence.
8. Turn on two or more sources together. Show that variances are propagated through the registered covariance model rather than adding standard-deviation magnitudes directly.
9. Open the **contribution ranking**. Ask which source dominates this sounding and then change geometry until the dominant contributor changes.
10. Run the **beam-angle sweep** across the swath with the input uncertainty magnitudes fixed.
11. Introduce **standard vs expanded uncertainty**. Apply an explicit coverage factor only after explaining what it changes and what assumptions are required.
12. Advanced: introduce correlated inputs through the generic covariance API and compare with the independent-input result. This must come from the Python Core, never from frontend arithmetic.
13. Optional closure: show a known Truth/reference case so the learner can compare a realized error vector with the uncertainty envelope without claiming that one realized error validates or invalidates the uncertainty model by itself.

## Operational intuition / trade-offs

| Source / condition | Main first-slice consequence | Operational intuition |
|---|---|---|
| horizontal positioning uncertainty ↑ | horizontal sounding uncertainty ↑ | better positioning directly improves horizontal knowledge of soundings |
| roll uncertainty ↑ | geometry-dependent across/vertical uncertainty ↑ | attitude quality matters increasingly with slant range / oblique geometry |
| range uncertainty ↑ | uncertainty along the acoustic path ↑ | ranging quality maps differently into horizontal/vertical components across the swath |
| sound-speed uncertainty ↑ | range/path-related contribution ↑ | water-column knowledge can dominate outer-swath quality; D4 explains the underlying propagation mechanism |
| installation-offset uncertainty ↑ | systematic geometric sensitivity represented here as configured uncertainty | dimensional control and calibration quality feed the sounding budget |
| timing uncertainty ↑ | along-track uncertainty grows with vessel speed | synchronization/latency quality becomes more important as platform dynamics increase |
| water-level uncertainty ↑ | vertical uncertainty ↑ | vertical reduction is part of the sounding uncertainty budget, not a cosmetic post-processing offset |
| wider / more oblique geometry | contributor balance changes | maximum usable swath should be judged by required data quality, not geometric coverage alone |
| more conservative input uncertainties | larger predicted envelope | uncertainty models support risk-aware acquisition and processing decisions but do not improve measurements by themselves |

Desired learner intuition: **“TPU is not one sensor specification and it is not a realized error. It is the propagated consequence of the uncertainties of the whole measurement system through the geometry used to form the sounding. Which source matters most can change across the swath and with operating conditions.”**

## Scientific guardrails

- Preserve `Truth != Observed != Configured != Estimated != Derived`.
- **Uncertainty is not error.** Standard uncertainty is always non-negative; realized error is signed and requires a Truth/reference.
- Do not use `accuracy`, `precision`, `uncertainty`, `repeatability`, `residual` and `error` as synonyms.
- Use the Scientific Core covariance propagation. React must never construct the covariance matrix, Jacobian, variance contributions or THU/TVU values.
- The scalar first slice assumes independent inputs and therefore a diagonal input covariance. That is a teaching assumption, not a general TPU rule. The generic API already supports arbitrary covariance/correlation.
- Propagation is first-order / local linearization. The relation `Σ_y ≈ J Σ_q Jᵀ` is valid within the assumptions documented by the Scientific Core. Strongly nonlinear cases may require higher-order or distribution-propagation methods.
- The current homogeneous sound-speed sensitivity is a controlled simplification. Do not replace D4 refraction/SVP physics with `r = c·t/2` outside this defined case.
- The current model uses one beam in the across/down plane and roll as the representative attitude uncertainty. It is not a complete attitude/MBES TPU model.
- Do not claim that all input errors are Gaussian, independent or unbiased merely because the first slice uses independent standard uncertainties.
- Bias / unresolved systematic error requires separate treatment; increasing the uncertainty bar is not a substitute for correcting a known bias.
- Distinguish a priori predicted uncertainty from a posteriori/empirical quality assessment. IHO S-44 recognizes both in survey uncertainty assessment.
- IHO S-44 THU/TVU requirements are expressed at a stated confidence/coverage basis. Do not compare 1σ standard uncertainty directly with 95%-level limits.
- A coverage factor `k=2` must be labelled `expanded uncertainty, k=2`; it is not automatically synonymous with an exact 95% confidence interval without the relevant distributional assumptions.
- `combined_3d_standard_uncertainty_m` is a HydroSIM pedagogical scalar summary, not a universal IHO definition of TPU.
- Formal compliance with a survey order requires the appropriate requirement, confidence basis, complete uncertainty budget and survey context; D17 should teach the mechanism before any compliance comparison.
- CUBE/grid uncertainty is downstream surface-estimation uncertainty and should not be conflated with the uncertainty of one raw/reduced sounding. It may be referenced as a bridge to later processing, not added to this first-slice sounding model.

## Dependencies / forward reuse

Consumes:
- D3 propagation/SNR context as a source of measurement quality, without deriving uncertainty from SNR unless a Scientific-Core model exists;
- D4 sound-speed/refraction mechanism;
- D8 bottom-detection observables and quality boundaries;
- D10 installation offsets / reference frames;
- D11 motion/attitude geometry;
- D12 sensor integration semantics;
- D13 timing/synchronization;
- D14 sounding formation and frame transformations;
- D15/D16 planning, coverage and acquisition trade-offs.

D17 closes the Acoustic Lab chain by converting those earlier sources and geometries into an explicit **measurement-quality / uncertainty budget** that can inform acquisition limits, processing review and later product-generation choices.

Forward bridge only:
- a priori uncertainty can support survey planning and real-time quality decisions;
- a posteriori checks, crossing/overlap comparisons and gridded-surface uncertainty support downstream validation;
- CUBE and bathymetric-product uncertainty belong to processing/product lessons rather than this sounding-level first slice.

## Current implementation delta

`UncertaintyLab.tsx` already provides a strong first learner-facing slice:
- seven scalar standard-uncertainty controls;
- fixed controlled nominal geometry;
- Scientific-Core API calls only;
- component standard uncertainties;
- horizontal / vertical summaries;
- combined 3-D standard uncertainty;
- ranked variance contributions;
- a five-angle swath sweep;
- an uncertainty-envelope visualization.

`uncertainty_scalar_api.py` correctly delegates covariance propagation to the canonical Core and exposes the first-order geometry defined by the scientific contract. `uncertainty_api.py` already supports the more general covariance contract, coverage factor/probability, Truth-error and verification-residual semantics.

Next-version changes:
- make **uncertainty ≠ error ≠ residual** an explicit first-class teaching distinction;
- rename/qualify the current learner-facing `THU` and `TVU` readouts so the 1σ scalar outputs cannot be mistaken for IHO S-44 95%-level THU/TVU;
- add an explicit **standard uncertainty → expanded uncertainty** experiment using the existing Core coverage-factor path;
- preserve units in the contribution view (`m²`) and explain why variance, not standard-deviation magnitude, is being combined;
- make the geometry sweep a causal experiment rather than a passive final chart: select one contributor, hold it fixed, vary beam angle and predict the result;
- expose nominal beam angle/slant geometry visually so roll/range/sound-speed contributions are interpretable rather than appearing as unexplained bars;
- replace any normalized decorative uncertainty halo with a representation whose axes/aspect are tied to computed horizontal/vertical uncertainty, or label it explicitly as schematic;
- add a zero-uncertainty baseline and isolated-contributor presets;
- optionally expose generic-Core correlation/covariance as an advanced experiment after independent propagation is understood;
- optionally expose Truth-error / verification residual side-by-side through the existing generic API, never by synthesizing error in React;
- keep omitted contributors visibly documented as model scope rather than adding unsupported controls.

## Recognized references

- **International Hydrographic Organization (IHO), S-5A — Standards of Competence for Category “A” Hydrographic Surveyors, Edition 2.0.0, August 2026.** F1.7b explicitly includes uncertainty of observations, covariance, variance propagation, Jacobian matrix, confidence ellipses and the BIPM uncertainty guide; H6.2c/H6.2e include horizontal/vertical TPU and a priori/a posteriori spatial data quality assessment: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **International Hydrographic Organization (IHO), S-44 — Standards for Hydrographic Surveys, Edition 6.2.0, October 2024.** Defines hydrographic TPU context through THU/TVU, whole-system uncertainty sources, confidence/coverage requirements and a priori/a posteriori assessment: <https://iho.int/uploads/user/pubs/standards/s-44/S-44_Edition_6.2.0_adopted.pdf>
- **Joint Committee for Guides in Metrology (JCGM), JCGM 100:2008(E), _Evaluation of measurement data — Guide to the expression of uncertainty in measurement (GUM)_.** General authoritative basis for standard/combined/expanded uncertainty and first-order propagation: <https://doi.org/10.59161/JCGM100-2008E>
- **JCGM 100:2008/Amd.1:2026, _Evaluation of measurement data — Guide to the expression of uncertainty in measurement — Amendment 1: Nonlinearity in measurement models_.** Current metrology guidance relevant to the limits of first-order linear propagation: <https://doi.org/10.59161/PPDI3267>
- **NOAA Office of Coast Survey, _Hydrographic Survey Specifications and Deliverables_, Version 2026.0.00.** Identifies practical sounding-uncertainty contributors including sound speed, beam forming, latency, draft, motion and vertical-datum corrections and specifies THU/TVU requirements for NOAA surveys: <https://nauticalcharts.noaa.gov/publications/documents/HSSD_2026-0-00.pdf>
- **Canadian Hydrographic Service, _Hydrographic Survey Management Guidelines_, Edition 4, February 2021.** Operational guidance for a priori/real-time/post-survey uncertainty assessment and TPU error budgets, including draft, squat, sound speed, instruments, motion, navigation timing and water-level/separation models: <https://www.chs.gc.ca/documents/data-gestion/guidelines-directrices/sg-ld-2021-eng.pdf>
- **Hare, R., Godin, A. & Mayer, L. A. (1995), _Accuracy Estimation of Canadian Swath (Multibeam) and Sweep (Multitransducer) Sounding Systems_. Canadian Hydrographic Service / Ocean Mapping Group, University of New Brunswick.** Foundational hydrographic swath-sounding error-budget / uncertainty treatment: <https://gge.ext.unb.ca/Pubs/TR190.pdf>
- **Center for Coastal and Ocean Mapping / Joint Hydrographic Center (CCOM/JHC), University of New Hampshire, _CUBE — Combined Uncertainty and Bathymetric Estimator_.** Authoritative bridge showing how uncertainty-aware sounding processing can feed bathymetric grid estimation; downstream context only for D17: <https://www.ccom.unh.edu/research/research-areas/data-processing/cube>
