# HydroSIM Scientific References by Submodule

Status: canonical human-readable reference index  
Language: English  
Machine-readable bibliography: `scientific_registry/references/bibliography.yaml`  
Traceability map: `scientific_registry/references/coverage.yaml`

## Purpose

This index presents the HydroSIM scientific bibliography in a form that answers two questions directly:

1. Which scientific or standards reference supports a HydroSIM model or claim?
2. In which pedagogical, patch-test, or acquisition submodule is that reference used?

The bibliography YAML remains the canonical source for bibliographic metadata and stable reference IDs. This document is the human-readable project view. A reference may support several submodules because the Scientific Core is shared; this does not mean that every result shown by those submodules is taken directly from that source. HydroSIM mathematical identities and internal state/sign/frame conventions remain identified separately from external scientific claims.

## Submodule key

### Didactic Explorer

- `D1` Acoustic Wave & Frequency
- `D2` Pulse & Signal Processing
- `D3` Sonar Equation & Propagation Loss
- `D4` Sound Speed & Refraction
- `D6` Transducer & Array Construction
- `D7` Beamforming & Electronic Steering
- `D8` Echosounders — SBES vs MBES
- `D9` Bottom Detection
- `D10` Multisector MBES
- `D11` Vessel & Sensor Configuration
- `D12` Vessel Motion
- `D13` PU & Sensor Integration
- `D14` Timing, Synchronization & Latency
- `D15` Sounding Formation
- `D16` Survey Planning
- `D17` Survey Coverage & Acquisition Trade-offs
- `D18` Uncertainty / TPU

`D5` is retired; its learning objectives are absorbed by D2, D3 and D9.

### Patch Test

- `P1` Patch-Test Fundamentals & Error Signatures
- `P2` Patch-Test Area & Line Planning
- `P3` Synthetic Patch-Test Acquisition
- `P4` Manual Patch-Test Calibration
- `P5` Exercise Assessment
- `P6` RISC Simulator

### Acquisition Simulator

- `A1` Survey Area / True Seafloor
- `A2` Vessel & Installation
- `A3` Sonar Configuration
- `A4` Environment
- `A5` Survey Planning
- `A6` Acquisition
- `A7` Synthetic Raw Data Generation

## General scientific reference list

| Stable ID | Reference | Principal HydroSIM use | Submodules using / inheriting it |
|---|---|---|---|
| `lurton_2010_underwater_acoustics` | Lurton (2010), *An Introduction to Underwater Acoustics*, 2nd ed. | General underwater-acoustics foundation: waves, propagation, arrays, transducers and signal processing | **D1, D2, D6, D7, D8, D15; A3, A6** |
| `waite_2002_sonar_for_practising_engineers` | Waite (2002), *Sonar for Practising Engineers*, 3rd ed. | Sonar equation, acoustic levels, active-sonar relationships and general array/propagation context | **D1, D2, D3; A3, A6** |
| `ainslie_mccolm_1998_seawater_absorption` | Ainslie & McColm (1998), “A simplified formula for viscous and chemical absorption in sea water” | Canonical empirical absorption approximation selected for the first HydroSIM sonar-equation lesson | **D3; A3, A4, A6** |
| `francois_garrison_1982_absorption_part1` | Francois & Garrison (1982), Part I | Higher-detail scientific reference for pure-water and magnesium-sulfate absorption contributions | **D3; A4, A6** |
| `francois_garrison_1982_absorption_part2` | Francois & Garrison (1982), Part II | Higher-detail scientific reference for boric-acid contribution and total seawater absorption | **D3; A4, A6** |
| `chen_millero_1977_sound_speed_seawater` | Chen & Millero (1977), “Speed of sound in seawater at high pressures” | Empirical seawater sound-speed formulation underlying the optional environmental extension | **D4; A4, A6** |
| `wong_zhu_1995_sound_speed_seawater` | Wong & Zhu (1995), “Speed of sound in seawater as a function of salinity, temperature, and pressure” | ITS-90 correction/recast of Chen–Millero used by the environmental sound-speed extension | **D4; A4, A6** |
| `ioc_scor_iapso_2010_teos10_manual` | IOC, SCOR & IAPSO (2010), TEOS-10 | Modern seawater thermodynamics and pressure/depth context | **D4; A4, A6** |
| `nistad_improved_water_column_sound_speed_ray_tracing` | Nistad et al., “Improved Techniques to Resolve the Water Column Sound Speed Structure for Multibeam Ray Tracing” | Hydrographic support for explicit water-column sound-speed structure and ray tracing | **D4, D15; A4, A6** |
| `beaudoin_hughes_clarke_bartlett_2004_surface_sound_speed` | Beaudoin, Hughes Clarke & Bartlett (2004), “Application of Surface Sound Speed Measurements in Post-processing for Multi-Sector Multibeam Echosounders” | Surface sound speed, beam steering, refraction and multisector processing | **D4, D10, D15; A3, A4, A6** |
| `kongsberg_em120_operator_manual_850_164112` | Kongsberg Maritime, *EM 120 Operator Manual* | Product-specific evidence for transducer sound speed, beam pointing and ray bending | **D4, D10; A3, A4, A6** |
| `kongsberg_em1002_operator_manual_850_160977` | Kongsberg, *EM 1002 Operator Manual* | Product-specific evidence for transducer sound speed as steering/profile-start information | **D4; A3, A4, A6** |
| `van_trees_2002_optimum_array_processing` | Van Trees (2002), *Optimum Array Processing* | Array factor, electronic steering, coherent summation, spatial aliasing and grating lobes | **D6, D7; A3, A6** |
| `demer_et_al_2015_calibration_acoustic_instruments` | Demer et al. (2015), *Calibration of acoustic instruments*, ICES CRR 326 | Transducer arrays, split-beam/multibeam bearing estimation and Mills-Cross geometry | **D6, D7, D8, D10; A3, A6** |
| `lurton_2003_acoustical_measurement_accuracy` | Lurton (2003), “Theoretical Modelling of Acoustical Measurement Accuracy for Swath Bathymetric Sonars” | Time/angle bathymetry, amplitude/phase bottom detection and intrinsic acoustic measurement accuracy | **D8, D9, D15, D18; A3, A6** |
| `bourguignon_et_al_2009_me70_bottom_detection` | Bourguignon et al. (2009), “Methodological developments for improved bottom detection with the ME70 multibeam echosounder” | Split-aperture phase difference, phase zero crossing and phase bottom detection | **D9; A3, A6** |
| `kongsberg_em2040_instruction_manual_346210` | Kongsberg Maritime (2012), *EM 2040 Multibeam Echo Sounder Instruction Manual* | Direct product evidence for phase bottom detection, High Density, footprint/sounding spacing and multisector behavior | **D9, D10, D17; A3, A6** |
| `iec_61162_1_2024` | IEC 61162-1:2024 | Generic maritime digital-interface semantics and serial sensor integration | **D13, D14; A2, A6** |
| `nmea_0183_interface_standard` | NMEA 0183 Interface Standard | Marine serial-message/transport semantics and standard signalling rates | **D13, D14; A2, A6** |
| `hughes_clarke_2003_dynamic_motion_residuals` | Hughes Clarke (2003), “Dynamic Motion Residuals in Swath Sonar Data: Ironing out the Creases” | Dynamic integration-error taxonomy; motion scale, latency, axis cross-talk, lever-arm/heave and observable bathymetric signatures | **D12, D14, D15, D18; P1, P3, P4; A2, A6** |
| `maingot_2019_high_frequency_motion_residuals_thesis` | Maingot (2019), *High-Frequency Motion Residuals in Multibeam Echosounder Data: Analysis and Estimation* | Primary source for HydroSIM's six-parameter RISC reference model and observability | **P1, P6; D18; A6** |
| `maingot_hughes_clarke_calder_2019_identification_estimation` | Maingot, Hughes Clarke & Calder (2019), “High Frequency Motion Residuals in Multibeam Data: Identification and Estimation” | Supporting RISC identification/estimation publication | **P6; D18; A6** |
| `maingot_2019_motion_residuals_seminar` | Maingot (2019), “High Frequency Motion Residuals: Analysis and Estimation” | Supporting RISC development and model context | **P6** |
| `noaa_ocean_exploration_2010_patch_test` | Hoy & Kissinger (2010), *Multibeam Calibration: Conducting a Patch Test* | Practical geometry and observability for latency, pitch, roll and heading patch-test components | **P1, P2, P3, P4, P5** |
| `noaa_hssd_2022` | NOAA (2022), *Hydrographic Surveys Specifications and Deliverables* | Hydrographic calibration requirements and patch-test practice | **P1, P2, P3, P4, P5; A2, A6** |
| `r2sonic_2017_patch_test` | Brennan / R2Sonic (2017), *The Patch Test* | Supporting practical procedure for reciprocal-line pitch calibration and iterative null/minimum | **P2, P4, P5** |
| `jcgm_100_2008_gum` | JCGM 100:2008, GUM | Measurement uncertainty, covariance and first-order law of propagation of uncertainty | **D18; A6** |
| `jcgm_100_2008_amd1_2026` | JCGM 100:2008/Amd.1:2026 | Nonlinearity in measurement models and limits of simple first-order propagation | **D18; A6** |
| `jcgm_101_2008_monte_carlo` | JCGM 101:2008 | Monte-Carlo propagation of distributions as higher-fidelity uncertainty path | **D18; A6** |
| `iho_s44_6_2_0_2024` | IHO S-44 Edition 6.2.0 (2024), *IHO Standards for Hydrographic Surveys* | Hydrographic uncertainty and survey-quality context; THU/TVU, coverage and feature-detection terminology | **D16, D17, D18; A5, A6** |

## Reference view by Didactic Explorer submodule

| Submodule | Principal external references |
|---|---|
| **D1 — Acoustic Wave & Frequency** | Lurton (2010); Waite (2002) |
| **D2 — Pulse & Signal Processing** | Lurton (2010); Waite (2002) |
| **D3 — Sonar Equation & Propagation Loss** | Waite (2002); Ainslie & McColm (1998); Francois & Garrison (1982 I/II) |
| **D4 — Sound Speed & Refraction** | Chen & Millero (1977); Wong & Zhu (1995); TEOS-10 (2010); Nistad et al.; Beaudoin et al. (2004); Kongsberg EM120/EM1002 manuals |
| **D6 — Transducer & Array Construction** | Van Trees (2002); Lurton (2010); Demer et al. (2015) |
| **D7 — Beamforming & Electronic Steering** | Van Trees (2002); Lurton (2010); Demer et al. (2015) |
| **D8 — Echosounders — SBES vs MBES** | Demer et al. (2015); Lurton (2003, 2010) |
| **D9 — Bottom Detection** | Lurton (2003); Bourguignon et al. (2009); Kongsberg EM2040 manual |
| **D10 — Multisector MBES** | Beaudoin et al. (2004); Demer et al. (2015); Kongsberg EM2040/EM120 manuals |
| **D11 — Vessel & Sensor Configuration** | No dedicated external model required for the current rigid-body geometry slice; HydroSIM frame/reference-point conventions and mathematical geometry are authoritative |
| **D12 — Vessel Motion** | Hughes Clarke (2003) for error/signature context; rigid-body motion geometry itself is mathematical/internal |
| **D13 — PU & Sensor Integration** | IEC 61162-1:2024; NMEA 0183 |
| **D14 — Timing, Synchronization & Latency** | IEC 61162-1:2024; NMEA 0183; Hughes Clarke (2003) |
| **D15 — Sounding Formation** | Lurton (2003, 2010); Nistad et al.; Beaudoin et al. (2004); Hughes Clarke (2003), plus inherited D4/D8/D11/D14 contracts |
| **D16 — Survey Planning** | IHO S-44 6.2.0 as standards context; first-slice line/swath equations are deterministic geometry |
| **D17 — Survey Coverage & Acquisition Trade-offs** | IHO S-44 6.2.0 as standards context; Kongsberg EM2040 only where High Density/multisector behavior is inherited; core spacing/coverage equations are mathematical geometry |
| **D18 — Uncertainty / TPU** | JCGM 100:2008; JCGM 100:2008/Amd.1:2026; JCGM 101:2008; IHO S-44 6.2.0; Hughes Clarke (2003); Lurton (2003) |

## Reference view by Patch Test submodule

| Submodule | Principal external references |
|---|---|
| **P1 — Fundamentals & Error Signatures** | NOAA patch-test guidance; NOAA HSSD; Hughes Clarke (2003); Maingot (2019) where dynamic residuals/RISC are contrasted |
| **P2 — Area & Line Planning** | NOAA patch-test guidance; NOAA HSSD; R2Sonic patch-test training |
| **P3 — Synthetic Acquisition** | NOAA patch-test guidance/HSSD for exercise geometry; Hughes Clarke (2003) for dynamic integration-error separation |
| **P4 — Manual Calibration** | NOAA patch-test guidance; NOAA HSSD; R2Sonic patch-test training; HydroSIM estimator is explicitly `derived_from_source` |
| **P5 — Exercise Assessment** | Same patch-test sources as P4; Truth-vs-Estimated assessment semantics are HydroSIM internal state semantics |
| **P6 — RISC Simulator** | Maingot (2019 thesis); Maingot, Hughes Clarke & Calder (2019); Maingot (2019 seminar) |

## Reference view by Acquisition Simulator submodule

The Acquisition Simulator consumes the same Scientific Core rather than creating a second bibliography.

| Submodule | Inherited scientific reference families |
|---|---|
| **A1 — Survey Area / True Seafloor** | No dedicated external scientific model currently required; the DTM is explicit simulation Truth |
| **A2 — Vessel & Installation** | D11 geometry/conventions; IEC/NMEA where sensor integration is represented; NOAA HSSD where calibration context is relevant |
| **A3 — Sonar Configuration** | D2/D3/D6/D7/D8/D9/D10 acoustic, array, detection and multisector references |
| **A4 — Environment** | D3/D4 absorption, sound-speed, TEOS-10 and refraction references |
| **A5 — Survey Planning** | D16/D17 geometry; IHO S-44 as standards context only |
| **A6 — Acquisition** | Integrated inheritance of D4, D8–D15, D17 and D18 references according to enabled simulation effects |
| **A7 — Synthetic Raw Data Generation** | No separate physical model: serialization/export must preserve A6 observations and their provenance. Format/vendor references are implementation/interface references, not substitutes for the scientific sources above |

## Traceability rule

For each authoritative scientific behavior, HydroSIM should preserve the chain:

```text
stable bibliography ID
    -> supported claim/model
    -> equation or algorithm / explicit internal derivation
    -> Scientific Core implementation
    -> validation anchor/test
    -> learner-facing submodule(s)
```

A submodule entry in this index means that the reference supports at least one scientific behavior consumed by that submodule. It must not be interpreted as claiming that the entire submodule is specified by that source.
