# HydroSIM Acoustic Lab — Pedagogical Overview

Status: **canonical modular specification — iterative**

This directory is the canonical editable pedagogical specification for the Acoustic Lab. Each lab is maintained in its own file so UX, Scientific Core, QA and implementation agents can load only the active block plus this overview.

The former monolithic specification is retained only as an archive snapshot and must not be treated as the active source of truth.

## Teaching contract

HydroSIM is a hydrographic acquisition simulator. The Acoustic Lab develops the physical, signal-processing, geometric and operational intuition required to understand, tune and diagnose hydrographic acquisition.

```text
SEE -> UNDERSTAND -> PREDICT -> TUNE / DECIDE -> DIAGNOSE / JUSTIFY
```

```text
CONTROL
  -> PHYSICAL / SIGNAL / GEOMETRIC CHANGE
  -> OBSERVABLE CONSEQUENCE
  -> BOTTOM-DETECTION / SOUNDING CONSEQUENCE
  -> BENEFIT + COST
  -> ACQUISITION DECISION
```

Recurring spatial chain across D5-D8:

```text
PHYSICAL ARRAY GEOMETRY
  -> 2-D / 3-D DIRECTIVITY
  -> BEAMFORMING
  -> STEERING / MULTIPLE RX LOOK DIRECTIONS
  -> TX × RX TWO-WAY RESPONSE
  -> SEAFLOOR FOOTPRINT / SAMPLING CELL
  -> RECEIVED AMPLITUDE + PHASE
  -> BOTTOM DETECTION(S)
```

## Rules

- one dominant discovery per lab;
- few primary controls; secondary controls use progressive disclosure;
- deterministic immediate response;
- fixed/shared plot scales when autoscaling would hide the concept;
- mechanism before operational rule;
- show benefit and cost of tunable parameters;
- permit poor configurations when their consequence is useful;
- prefer connected 3-D geometry when a 2-D section would hide an essential mechanism;
- UI consumes the Scientific Core; no parallel physics;
- preserve `Truth != Observed != Configured != Estimated != Derived`;
- vendor behavior is evidence, not universal law.

## Mapped-lab completeness contract

A lab may be marked **Mapped** only when its own modular file contains enough information for an implementation agent to know what the learner changes, what must visibly change, why it changes, what message should remain, and where that knowledge is reused. Every mapped lab must therefore contain:

1. **Purpose**;
2. **Dominant discovery** / central causal chain;
3. **Inputs**, distinguishing primary from secondary/advanced where useful;
4. **Outputs / visual response**;
5. **Interaction sequence**;
6. **Operational intuition / trade-offs**;
7. an explicit **desired learner message / intuition**;
8. **Scientific guardrails** and scope boundaries;
9. **Dependencies / forward reuse**;
10. **Current implementation delta**;
11. **Recognized references** with author/institution, title, year/edition where available, and stable URL.

Each active lab must receive fresh source research before final mapping. References are recorded locally in that lab file. A consolidated bibliography is intentionally deferred until D1–D17 are mapped so routine editing does not repeatedly load/update a global reference list.

## Source hierarchy

1. IHO S-5A Ed. 2.0.0 (Aug 2026) — competence anchor.
2. MIT OCW 2.682 Acoustical Oceanography — first-principles acoustics.
3. CCOM/UNH and UNB/OMG — hydrographic/ocean-mapping science.
4. DHN — Brazilian operational relevance.
5. Authoritative manufacturer documentation — real controls/modes/trade-offs.

## Lab map

| ID | Lab | Status | File |
|---|---|---|---|
| D1 | Acoustic Wave & Frequency | Mapped | `D01_wave_frequency.md` |
| D2 | Pulse & Signal Processing | Mapped | `D02_pulse_signal_processing.md` |
| D3 | Sonar Equation & Propagation Loss | Mapped | `D03_sonar_equation.md` |
| D4 | Sound Speed & Refraction | Mapped | `D04_sound_speed_refraction.md` |
| D5 | Transducer & Array Construction | Mapped | `D05_transducer_array.md` |
| D6 | Beamforming & Electronic Steering | Mapped | `D06_beamforming_steering.md` |
| D7 | Echosounders — SBES vs MBES | Mapped | `D07_echosounders_sbes_mbes.md` |
| D8 | Bottom Detection | Mapped | `D08_bottom_detection.md` |
| D9 | Multisector MBES | Mapped | `D09_multisector_mbes.md` |
| D10 | Vessel & Sensor Configuration | Mapped | `D10_vessel_sensor_configuration.md` |
| D11 | Vessel Motion | Mapped | `D11_vessel_motion.md` |
| D12 | PU & Sensor Integration | Mapped | `D12_pu_sensor_integration.md` |
| D13 | Timing, Synchronization & Latency | Mapped | `D13_timing_sync_latency.md` |
| D14 | Sounding Formation | Pending | `D14_sounding_formation.md` |
| D15 | Survey Planning | Pending | `D15_survey_planning.md` |
| D16 | Survey Coverage & Acquisition Trade-offs | Pending | `D16_survey_coverage_tradeoffs.md` |
| D17 | Uncertainty / TPU | Pending | `D17_uncertainty_tpu.md` |

The retired standalone `Acoustic Detection Fundamentals` lesson must not be reintroduced. Its SNR/detectability objective belongs to D3; threshold-driven bottom detection belongs to D8.

## Editing rule

For work on a specific lab, read this overview plus that lab file. Read neighboring labs only when a dependency requires it. Do not reconstruct a monolithic working document during active development.
