# P1 — Patch Test Fundamentals & Error Signatures

Status: **Mapped**

## Purpose
Teach what the patch test is actually solving and how the four classic residuals become observable in bathymetric data before the learner is asked to plan or calibrate anything.

## Dominant discovery

```text
residual integration error
  -> systematic geometric displacement
  -> repeat lines disagree in a characteristic way
  -> survey geometry can make one parameter more observable than the others
```

The learner must leave understanding that the patch test is a residual system-calibration procedure. It does not replace dimensional control, lever-arm measurement or the original vessel/sensor alignment survey.

## Hidden Truth / unknowns
A scenario contains hidden residual values for:
- time delay / latency `Δt`;
- pitch alignment `Δpitch`;
- roll alignment `Δroll`;
- heading/yaw alignment `Δyaw`.

Only one residual is active in the first guided cases. Combined residuals are introduced only after the isolated signatures are understood.

## Inputs
Primary:
- active error family: latency, pitch, roll, heading/yaw;
- error magnitude, initially instructor/scenario-controlled rather than visible as Truth;
- water depth / terrain preset;
- show one run / paired runs.

Secondary:
- swath width / selected beam region;
- vessel speed where latency is being explored;
- terrain slope or discrete feature geometry;
- sign-convention overlay.

Advanced:
- combined-error preset;
- contaminant preset: lever-arm, sound-speed or timing/sensor issue that can mimic/confound a classic signature.

## Outputs / visual response
Required synchronized views:
- true/reference seabed, hidden by default or shown only in teaching mode;
- repeated reconstructed profiles/swaths on identical axes;
- difference/residual view;
- vessel direction arrows and line geometry;
- parameter/sign label;
- highlighted region used for comparison: nadir/near-nadir, outer swath, or overlap region depending on the signature.

## Observable signatures
- **Roll residual:** opposite-sense across-track disagreement on reciprocal passes; effect grows toward outer beams and is observable on flat seabed.
- **Pitch residual:** reciprocal passes over a slope/feature show an along-track displacement/mismatch; near-nadir data is especially useful for isolating the signature.
- **Heading/Yaw residual:** displaced parallel lines over a feature/slope disagree where their outer swaths overlap; the same physical feature is placed differently horizontally.
- **Latency residual:** same-direction lines at different speeds place a feature/slope at different along-track positions because a fixed time error maps to a speed-dependent spatial displacement.

## Interaction sequence
1. Show perfectly calibrated repeated lines: profiles/surfaces coincide.
2. Inject hidden roll residual on flat bottom; alternate between single-pass and reciprocal comparison.
3. Reset and inject pitch residual on a slope; show why the slope converts a horizontal displacement into an observable profile mismatch.
4. Reset and inject heading/yaw residual with offset parallel lines; highlight common outer-swath feature mismatch.
5. Reset and inject latency; hold the hidden time error fixed and change vessel speed to reveal speed-dependent displacement.
6. Show a combined-error case and ask the learner to identify why a single visual signature may no longer be uniquely diagnostic.
7. Introduce one contaminant case to establish the limit of visual diagnosis.

## Decision / estimation task
P1 does not ask the learner to solve the numerical correction. The task is to classify:
- which residual is likely being isolated;
- which geometry makes it observable;
- which part of the data should be compared;
- whether the evidence is sufficient or confounded.

## Operational intuition / trade-offs
- deeper water generally magnifies the spatial consequence of small angular residuals;
- distinctive terrain improves identifiability for pitch/yaw/latency;
- flat bottom is useful for roll but poor for pitch observability;
- greater speed separation improves latency observability, but vessel handling and data quality still matter;
- strong motion, poor SVP, bad offsets or timing defects can mask or mimic calibration signatures.

## Desired learner message
**A patch test does not reveal an offset directly. It creates a survey geometry in which a residual offset produces a recognizable disagreement between repeated observations of the same seabed.**

## Scientific guardrails
- Classic patch-test solved parameters here are only latency/time delay, pitch, roll and heading/yaw.
- Heave is not added as a fifth classic solved parameter.
- Lever-arm, sound-speed, GNSS, heave and other integration errors may contaminate the residual but are not silently estimated in P1–P5.
- Do not teach a residual pattern as proof of one unique physical fault.
- Use HydroSIM Truth/Configured separation. Learner-visible geometry must come from shared Scientific Core transforms.
- External sign conventions must be mapped explicitly to HydroSIM conventions.
- Modern NOAA guidance treats a dedicated timing test mainly as a gross-timing diagnostic; HydroSIM retains latency because it is historically/classically part of patch-test instruction and remains pedagogically valuable.

## Dependencies / forward reuse
Consumes Acoustic Lab D10–D14 concepts: frames/lever arms, vessel motion, timing and sounding formation. Passes signature recognition to P2 planning and P4 calibration.

## Current implementation / reuse delta
Reusable HydroSIM assets already include a deterministic roll-offset scenario and a preserved pitch patch-test scientific contract. `src/hydrosim/scenarios/roll_offset.py` can support the roll signature; `docs/science/pitch_patch_test_v0_1_contract.md` provides the pitch sign/reciprocal-slope contract. Do not restore legacy UI code wholesale.

## Recognized references
- IHO, **S-5A Ed. 2.0.0 (2026)**, H4.2d Multi beam and phase-measuring bathymetric system operations — calibration methods/procedures and diagnosis of deficiencies: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- NOAA, **Field Procedures Manual (2020)**, §1.5.6.2 MBES Calibration — roll, pitch, heading and attitude timing error; parameter-isolating line sets: <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf>
- Hoy, S. & Kissinger, K. / NOAA Ocean Exploration, **Multibeam Calibration: Conducting a Patch Test (2010)** — classical four-variable patch-test training and line geometries: <https://oceanexplorer.noaa.gov/wp-content/uploads/2023/04/patchtest-poster.pdf>
- IHO International Hydrographic Review, **Survey systems verification and calibration in the hydrospatial domain (2025)** — patch test as residual angular/latency calibration and general conditions: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- Brennan, C. W. / R2Sonic, **Multibeam Calibration: The Patch Test (2017)** — operational explanation of roll, pitch, heading and latency signatures: <https://www.r2sonic.com/wp-content/uploads/2020/03/The-New-Patch-Test.pdf>
- Maingot, B., Hughes Clarke, J. E. & Calder, B. R., **High Frequency Motion Residuals in Multibeam Data: Identification and Estimation (2019)** — limits of classic patch testing and confounding integration errors: <https://scholars.unh.edu/ccom/1683/>