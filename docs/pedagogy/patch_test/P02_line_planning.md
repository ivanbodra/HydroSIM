# P2 — Patch-Test Planning

Status: **Mapped**

## Purpose
Teach the learner to design line geometry, terrain selection, direction and speed so the desired residual becomes identifiable before any calibration value is estimated.

## Dominant discovery

```text
parameter to estimate
  -> choose seabed geometry + line geometry + direction/speed contrast
  -> make that parameter observable
  -> suppress/confine competing signatures
```

The learner must understand **why** each line pair works, not memorize four recipes without mechanism.

## Hidden Truth / unknowns
The scenario may contain hidden roll, pitch, yaw and/or latency values, but planning is performed without seeing them. The learner knows only which parameter is intended to be isolated and the available terrain.

## Inputs
Primary:
- target parameter: latency, pitch, roll, heading/yaw;
- available seabed map/DTM containing flat region, slope and optional discrete feature;
- line position and heading;
- reciprocal vs same-direction run;
- vessel speed for each pass;
- line offset / overlap for heading test.

Secondary:
- water depth / candidate calibration area;
- swath angle/coverage preview;
- acceptable common overlap;
- environmental-quality preset: calm/moderate motion, current, SVP freshness.

Advanced:
- dual-head system identity, requiring independent head calibration where applicable;
- alternate terrain where ideal geometry is unavailable;
- planning score components based on observability, overlap and confounding risk.

## Outputs / visual response
- plan-view DTM and proposed lines;
- arrows for run directions and labelled speeds;
- expected swath envelopes and overlap region;
- terrain cross-section along the analysis direction;
- observability indicator for the selected target parameter;
- warnings for weak geometry: flat pitch test, insufficient outer overlap for yaw, same speed for latency, slope used for roll when flat area is available, poor common coverage;
- concise explanation of which data slice will later be compared.

## Observable planning logic
### Roll
Use the same line in reciprocal directions at the same speed over a flat seabed. Compare across-track profiles/swaths. The flat bottom avoids mixing an intended roll signature with along-track slope/feature displacement.

### Pitch
Use one coincident line in reciprocal directions at the same speed over a steep, well-defined slope or discrete feature. Compare nadir/near-nadir profiles in a common navigation frame.

### Heading/Yaw
Use two offset parallel lines in the same direction and speed over a steep, well-defined slope or feature, with sufficient outer-swath overlap. Compare the common feature/profile in the overlap zone.

### Timing/Latency
Use the same line in the same direction over a steep, well-defined slope/feature at two different speeds. A fixed timing offset produces a speed-dependent along-track displacement.

## Interaction sequence
1. Present a calibration area with flat, sloping and feature-rich zones.
2. Ask the learner to plan roll lines; show only coverage/geometry feedback first.
3. Plan pitch lines; let the learner try an invalid flat-bottom plan and see weak observability.
4. Plan heading/yaw offset lines; reveal the overlap requirement.
5. Plan timing lines; keep direction fixed and vary speed; show why reciprocal direction would introduce a different comparison logic.
6. Present one non-ideal area and ask for the least-bad plan with an explicit limitation statement.
7. Final task: create a compact four-test campaign that reuses terrain/lines when scientifically legitimate without destroying parameter isolation.

## Decision / estimation task
The learner submits a line plan, not a correction value. The system classifies the plan as **Adequate / Suboptimal / Inadequate** based on explicit geometric reasons, not a hidden aesthetic score.

## Operational intuition / trade-offs
- ideal line geometry improves parameter identifiability more than post-processing sophistication can compensate for poor acquisition;
- a well-defined slope/feature improves pitch/yaw/latency matching;
- deeper water can amplify angular-error signatures but may increase operational cost and environmental sensitivity;
- more speed contrast helps latency observability, but data quality and safe vessel operation remain constraints;
- sufficient overlap is essential for comparing the same seabed, especially heading/yaw;
- calm conditions and current SVP reduce contamination.

## Desired learner message
**The patch test is designed before it is processed: the seabed and line geometry are chosen to turn one hidden residual into a measurable mismatch while keeping other explanations as weak as practical.**

## Scientific guardrails
- Follow HydroSIM frame/sign conventions; line arrows and swath orientation must be geometric, not decorative.
- Do not claim one universal slope angle or depth is mandatory. NOAA gives operational recommendations, not physical constants.
- NOAA 2020 guidance notes timing tests are mainly for gross timing errors and may not be needed for routine standard patch tests; retain the planning exercise as a classical/diagnostic case and label the caveat.
- Do not score a plan as scientifically valid if the two datasets do not observe common seabed.
- Planning should not expose hidden Truth offsets.
- P2 plans acquisition; P3 executes it, P4 estimates offsets.

## Dependencies / forward reuse
Consumes P1 signature intuition and Acoustic Lab survey geometry concepts. Passes line plans and expected comparison regions to P3 synthetic acquisition.

## Current implementation / reuse delta
The preserved pitch contract already defines a deterministic reciprocal-line slope scenario, including common overlap and hidden Truth. Reuse that geometry rather than inventing a second pitch convention. Roll can reuse the flat-terrain scenario. Heading and latency need equivalent canonical scenario contracts before implementation.

## Recognized references
- NOAA, **Field Procedures Manual (2020)**, §1.5.6.2 — exact line-set guidance for heading/yaw, pitch, timing and roll plus test-area recommendations: <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf>
- Hoy, S. & Kissinger, K. / NOAA Ocean Exploration, **Multibeam Calibration: Conducting a Patch Test (2010)** — classical line-plan diagrams, terrain requirements and calibration sequence: <https://oceanexplorer.noaa.gov/wp-content/uploads/2023/04/patchtest-poster.pdf>
- IHO International Hydrographic Review, **Survey systems verification and calibration in the hydrospatial domain (2025)** — calm conditions, depth/slope, steady speed, SVP and overlap recommendations: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- Brennan, C. W. / R2Sonic, **Multibeam Calibration: The Patch Test (2017)** — terrain/line planning and interactive versus automatic surface-matching practice: <https://www.r2sonic.com/wp-content/uploads/2020/03/The-New-Patch-Test.pdf>
- Kongsberg Discovery, **Multibeam survey planning — The key to success (2026 technical note)** — need to plan calibration areas and account for roll/pitch/heading drift and operating conditions: <https://www.kongsberg.com/globalassets/kongsberg-discovery/commerce/seafloor-mapping/em2040-mkii/em-technical-note-multibeam-survey-planning-the-key-to-success.pdf>