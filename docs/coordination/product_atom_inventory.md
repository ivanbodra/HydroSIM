# HydroSIM Product Atom Inventory

Status: canonical product-measurement baseline  
Scope: active 31-submodule roadmap (`PED-D1`–`PED-D18`, `P1`–`P6`, `A1`–`A7`)

## Purpose

This file defines the denominator for HydroSIM's granular product-progress indicator. It is a measurement baseline, not a new implementation specification and not a substitute for Learning, Scientific or Visualization contracts.

## Counting rules

1. One **input atom** is one distinct learner-operable control or selection that can change the functional experience.
2. One **output atom** is one distinct learner-visible functional consequence, visualization or computed readout required by the pedagogical plan.
3. A group of mutually exclusive choices implemented as one selector is one input atom. Independent scalar controls are separate atoms.
4. A plot/view is one output atom even if it contains several traces needed to express the same phenomenon. A separately meaningful computed readout is a separate output atom.
5. Navigation, localization, explanatory text, contracts, documentation, APIs, adapters, tests, PRs, CI, screenshots, infrastructure and coordination are not atoms.
6. An atom is `ready` only when it is functional in the production path on `main`; specification, mock or backend-only availability is not enough.
7. Scope changes must edit this inventory explicitly. The denominator must never change silently.
8. Where the pedagogical plan intentionally leaves structure unresolved (currently `PED-D5`), its atoms remain in the denominator until the roadmap itself is formally changed. If D5 is merged/reallocated, move/remove its atoms in the same change that updates the canonical plan.

## Product indicator

The canonical inventory contains **214 atoms: 118 learner inputs + 96 learner-visible outputs**.

Current atom readiness is intentionally conservative: only atoms belonging to submodules already declared fully ready in `pedagogical_generation_status.md` are marked ready here. This avoids claiming partial readiness without production evidence. On this baseline, **34/214 atoms are ready**.

| Submodule | Input atoms | Output atoms | Total | Ready |
|---|---:|---:|---:|---:|
| PED-D1 | 3 | 4 | 7 | 7 |
| PED-D2 | 7 | 6 | 13 | 13 |
| PED-D3 | 6 | 4 | 10 | 10 |
| PED-D4 | 3 | 1 | 4 | 4 |
| PED-D5 | 3 | 2 | 5 | 0 |
| PED-D6 | 8 | 4 | 12 | 0 |
| PED-D7 | 6 | 4 | 10 | 0 |
| PED-D8 | 6 | 5 | 11 | 0 |
| PED-D9 | 6 | 5 | 11 | 0 |
| PED-D10 | 6 | 4 | 10 | 0 |
| PED-D11 | 7 | 4 | 11 | 0 |
| PED-D12 | 4 | 4 | 8 | 0 |
| PED-D13 | 6 | 4 | 10 | 0 |
| PED-D14 | 5 | 4 | 9 | 0 |
| PED-D15 | 7 | 3 | 10 | 0 |
| PED-D16 | 7 | 4 | 11 | 0 |
| PED-D17 | 9 | 5 | 14 | 0 |
| PED-D18 | 7 | 4 | 11 | 0 |
| P1 | 4 | 2 | 6 | 0 |
| P2 | 4 | 2 | 6 | 0 |
| P3 | 2 | 2 | 4 | 0 |
| P4 | 3 | 4 | 7 | 0 |
| P5 | 1 | 3 | 4 | 0 |
| P6 | 2 | 2 | 4 | 0 |
| A1 | 1 | 1 | 2 | 0 |
| A2 | 4 | 2 | 6 | 0 |
| A3 | 7 | 2 | 9 | 0 |
| A4 | 3 | 1 | 4 | 0 |
| A5 | 5 | 2 | 7 | 0 |
| A6 | 1 | 3 | 4 | 0 |
| A7 | 1 | 2 | 3 | 0 |
| **TOTAL** | **118** | **96** | **214** | **34** |

## Atom definitions

### PED-D1 — Acoustic Wave & Frequency
Inputs: `PED-D1-I01` frequency; `PED-D1-I02` amplitude; `PED-D1-I03` phase.  
Outputs: `PED-D1-O01` propagating-wave visualization; `PED-D1-O02` period readout; `PED-D1-O03` wavelength readout; `PED-D1-O04` frequency/wavelength comparison.

### PED-D2 — Pulse & Signal Processing
Inputs: `PED-D2-I01` signal type (CW/chirp); `PED-D2-I02` frequency; `PED-D2-I03` bandwidth; `PED-D2-I04` pulse length; `PED-D2-I05` envelope/filter mode; `PED-D2-I06` matched-filter/pulse-compression toggle; `PED-D2-I07` phase.  
Outputs: `PED-D2-O01` transmitted time waveform; `PED-D2-O02` received echo; `PED-D2-O03` envelope; `PED-D2-O04` matched-filter/pulse-compression result; `PED-D2-O05` temporal-resolution readout; `PED-D2-O06` range-resolution readout.

### PED-D3 — Sonar Equation & Propagation Loss
Inputs: `PED-D3-I01` source level; `PED-D3-I02` spreading model/parameter; `PED-D3-I03` absorption/frequency; `PED-D3-I04` range; `PED-D3-I05` noise level; `PED-D3-I06` detection threshold/required SNR.  
Outputs: `PED-D3-O01` intensity/received-level versus range; `PED-D3-O02` SNR versus range; `PED-D3-O03` frequency/absorption effect comparison; `PED-D3-O04` detection-margin readout/visualization.

### PED-D4 — Sound Speed & Refraction
Inputs: `PED-D4-I01` sound-speed profile; `PED-D4-I02` depth/profile geometry; `PED-D4-I03` launch angle.  
Outputs: `PED-D4-O01` ray/path visualization including refraction and configured-profile error consequence.

### PED-D5 — Acoustic Detection Fundamentals
Inputs: `PED-D5-I01` signal level; `PED-D5-I02` noise level; `PED-D5-I03` detection threshold.  
Outputs: `PED-D5-O01` signal/noise/SNR detectability visualization; `PED-D5-O02` detected/not-detected state.

### PED-D6 — Transducer & Array Construction
Inputs: `PED-D6-I01` element count; `PED-D6-I02` frequency; `PED-D6-I03` element spacing; `PED-D6-I04` aperture/dimension; `PED-D6-I05` array geometry; `PED-D6-I06` eccentricity; `PED-D6-I07` Mills-Cross configuration; `PED-D6-I08` shading/apodization.  
Outputs: `PED-D6-O01` array-construction visualization; `PED-D6-O02` directivity/beam pattern; `PED-D6-O03` beamwidth readout; `PED-D6-O04` side-lobe/gain-loss visualization.

### PED-D7 — Beamforming & Electronic Steering
Inputs: `PED-D7-I01` TX/RX role; `PED-D7-I02` frequency; `PED-D7-I03` element count/array size; `PED-D7-I04` element spacing/face geometry; `PED-D7-I05` steering angle; `PED-D7-I06` source/arrival angle.  
Outputs: `PED-D7-O01` element phase/coherent-contribution visualization; `PED-D7-O02` array-factor/physical beam pattern; `PED-D7-O03` electronically steered beam direction/peak; `PED-D7-O04` steering-loss/beamwidth/coherent-sum readouts.

### PED-D8 — Echosounders — SBES vs MBES
Inputs: `PED-D8-I01` echosounder mode/configuration; `PED-D8-I02` depth; `PED-D8-I03` beam geometry/count; `PED-D8-I04` incidence/swath angle; `PED-D8-I05` beam-spacing mode; `PED-D8-I06` transducer/footprint configuration supported by contract.  
Outputs: `PED-D8-O01` synchronized SBES/MBES geometry; `PED-D8-O02` beam-centre/sounding positions; `PED-D8-O03` footprint visualization; `PED-D8-O04` geometric swath readout/visualization; `PED-D8-O05` equiangular/equidistant and adjacent-spacing comparison.

### PED-D9 — Bottom Detection
Inputs: `PED-D9-I01` detection method (amplitude/phase/hybrid); `PED-D9-I02` detection window; `PED-D9-I03` threshold; `PED-D9-I04` multiple-detection setting; `PED-D9-I05` High Density setting; `PED-D9-I06` signal/echo scenario.  
Outputs: `PED-D9-O01` detection-formation visualization; `PED-D9-O02` detected position; `PED-D9-O03` false/missed-detection consequence; `PED-D9-O04` signal-to-sounding relationship; `PED-D9-O05` High Density/multiple-detection comparison.

### PED-D10 — Multisector MBES
Inputs: `PED-D10-I01` number of sectors; `PED-D10-I02` sector angles; `PED-D10-I03` frequency per sector; `PED-D10-I04` transmission timing/sequence; `PED-D10-I05` pulse duration; `PED-D10-I06` power.  
Outputs: `PED-D10-O01` temporal sector sequence; `PED-D10-O02` sector geometry; `PED-D10-O03` footprints/swaths; `PED-D10-O04` sector-frequency-time relationship.

### PED-D11 — Vessel & Sensor Configuration
Inputs: `PED-D11-I01` vessel dimensions/model; `PED-D11-I02` reference point; `PED-D11-I03` transducer position/orientation; `PED-D11-I04` antenna position/orientation; `PED-D11-I05` MRU/IMU position/orientation; `PED-D11-I06` waterline/reference height; `PED-D11-I07` installation/lever-arm configuration.  
Outputs: `PED-D11-O01` vessel model; `PED-D11-O02` sensor-layout visualization; `PED-D11-O03` frame/offset visualization; `PED-D11-O04` configuration readout/file representation.

### PED-D12 — Vessel Motion
Inputs: `PED-D12-I01` roll; `PED-D12-I02` pitch; `PED-D12-I03` yaw/heading; `PED-D12-I04` heave.  
Outputs: `PED-D12-O01` vessel/sensor motion; `PED-D12-O02` beam displacement; `PED-D12-O03` swath consequence; `PED-D12-O04` sounding-position consequence.

### PED-D13 — PU & Sensor Integration
Inputs: `PED-D13-I01` sensor/device selection; `PED-D13-I02` connection type/port; `PED-D13-I03` baud/data rate; `PED-D13-I04` update/message rate; `PED-D13-I05` protocol/message configuration; `PED-D13-I06` time-source selection.  
Outputs: `PED-D13-O01` PU-to-sensor diagram; `PED-D13-O02` stream/status visualization; `PED-D13-O03` incompatibility indication; `PED-D13-O04` configuration-error consequence.

### PED-D14 — Timing, Synchronization & Latency
Inputs: `PED-D14-I01` sensor update rate; `PED-D14-I02` timestamp/time source; `PED-D14-I03` latency/delay; `PED-D14-I04` vessel speed; `PED-D14-I05` sensor/stream selection.  
Outputs: `PED-D14-O01` sensor timeline; `PED-D14-O02` synchronization relationship; `PED-D14-O03` position/attitude-to-ping association; `PED-D14-O04` temporal-to-spatial error.

### PED-D15 — Sounding Formation
Inputs: `PED-D15-I01` TWTT/range scenario; `PED-D15-I02` beam angle; `PED-D15-I03` position; `PED-D15-I04` attitude; `PED-D15-I05` lever arms; `PED-D15-I06` SV/SVP; `PED-D15-I07` timing/configuration.  
Outputs: `PED-D15-O01` integrated ping-to-detection-to-range chain; `PED-D15-O02` frame/transformation chain; `PED-D15-O03` resulting 3D sounding.

### PED-D16 — Survey Planning
Inputs: `PED-D16-I01` survey area/DTM; `PED-D16-I02` depth; `PED-D16-I03` sonar/configuration; `PED-D16-I04` swath; `PED-D16-I05` overlap; `PED-D16-I06` line direction/spacing; `PED-D16-I07` vessel speed.  
Outputs: `PED-D16-O01` planned lines; `PED-D16-O02` predicted coverage; `PED-D16-O03` gap/overlap visualization; `PED-D16-O04` line count/length readout.

### PED-D17 — Survey Coverage & Acquisition Trade-offs
Inputs: `PED-D17-I01` frequency; `PED-D17-I02` footprint/beamwidth configuration; `PED-D17-I03` beam spacing; `PED-D17-I04` High Density; `PED-D17-I05` swath; `PED-D17-I06` depth; `PED-D17-I07` ping rate; `PED-D17-I08` vessel speed; `PED-D17-I09` multisector/detection configuration.  
Outputs: `PED-D17-O01` swath/footprint consequence; `PED-D17-O02` sounding pattern; `PED-D17-O03` coverage/gaps visualization; `PED-D17-O04` along/across-track spacing and density; `PED-D17-O05` acquisition trade-off comparison.

### PED-D18 — Uncertainty / TPU
Inputs: `PED-D18-I01` position uncertainty; `PED-D18-I02` attitude uncertainty; `PED-D18-I03` range uncertainty; `PED-D18-I04` SV uncertainty; `PED-D18-I05` offset uncertainty; `PED-D18-I06` timing uncertainty; `PED-D18-I07` water-level uncertainty.  
Outputs: `PED-D18-O01` uncertainty-component visualization; `PED-D18-O02` propagated THU/TVU/TPU; `PED-D18-O03` across-track uncertainty variation; `PED-D18-O04` sounding-uncertainty visualization.

### P1 — Patch-Test Fundamentals & Error Signatures
Inputs: `P1-I01` latency bias; `P1-I02` pitch bias; `P1-I03` roll bias; `P1-I04` heading/yaw bias.  
Outputs: `P1-O01` characteristic error-signature visualization; `P1-O02` classic-patch-test versus contaminating-error distinction.

### P2 — Patch-Test Area & Line Planning
Inputs: `P2-I01` calibration parameter/task; `P2-I02` area/segment selection; `P2-I03` line geometry/direction; `P2-I04` vessel speed.  
Outputs: `P2-O01` planned line/area visualization over Truth DTM; `P2-O02` adequate/suboptimal/inadequate observability feedback.

### P3 — Synthetic Patch-Test Acquisition
Inputs: `P3-I01` learner-planned line set; `P3-I02` acquisition execution control.  
Outputs: `P3-O01` simulated vessel/acquisition execution; `P3-O02` synthetic acquired line pairs with hidden biases.

### P4 — Manual Patch-Test Calibration
Inputs: `P4-I01` line-pair selection; `P4-I02` comparison-segment selection; `P4-I03` candidate calibration value.  
Outputs: `P4-O01` corrected-data overlay; `P4-O02` plan/profile/surface comparison views; `P4-O03` residual/convergence visualization; `P4-O04` segment-suitability feedback.

### P5 — Exercise Assessment
Inputs: `P5-I01` submitted final calibration values.  
Outputs: `P5-O01` Estimated-versus-Truth comparison; `P5-O02` residual-error readout; `P5-O03` performance/tolerance assessment.

### P6 — RISC Simulator
Inputs: `P6-I01` RISC dataset/system scenario; `P6-I02` diagnosis/estimate controls.  
Outputs: `P6-O01` RISC diagnosis/estimate result; `P6-O02` comparison with conventional patch-test result.

### A1 — Survey Area / True Seafloor
Inputs: `A1-I01` Truth DTM/survey-area selection.  
Outputs: `A1-O01` Truth seafloor visualization/state.

### A2 — Vessel & Installation
Inputs: `A2-I01` vessel file/model; `A2-I02` sensor positions; `A2-I03` lever arms; `A2-I04` alignments/installation parameters.  
Outputs: `A2-O01` integrated physical-platform visualization; `A2-O02` installation-state readout.

### A3 — Sonar Configuration
Inputs: `A3-I01` frequency; `A3-I02` pulse; `A3-I03` beam configuration; `A3-I04` sector configuration; `A3-I05` swath; `A3-I06` ping settings; `A3-I07` detection/acquisition configuration.  
Outputs: `A3-O01` operational sonar configuration/state; `A3-O02` configured beam/sector/swath visualization.

### A4 — Environment
Inputs: `A4-I01` SV/SVP; `A4-I02` water level; `A4-I03` other acquisition environmental condition supported by the Scientific Core.  
Outputs: `A4-O01` environment state consumed by simulation.

### A5 — Survey Planning
Inputs: `A5-I01` area; `A5-I02` line direction/geometry; `A5-I03` line spacing; `A5-I04` vessel speed; `A5-I05` sonar configuration.  
Outputs: `A5-O01` executable survey-plan visualization; `A5-O02` plan metrics/coverage expectation.

### A6 — Acquisition
Inputs: `A6-I01` acquisition start/run control for the configured survey.  
Outputs: `A6-O01` vessel trajectory/execution; `A6-O02` ping/sensor observation stream; `A6-O03` integrated acquired sounding/observation visualization.

### A7 — Synthetic Raw Data Generation
Inputs: `A7-I01` synthetic-data generation/export action.  
Outputs: `A7-O01` generated synthetic raw dataset; `A7-O02` export/result state suitable for external hydrographic processing workflow.

## Readiness maintenance

When a production change reaches `main`, update only the atoms for which functional learner-facing evidence exists. A submodule may have ready atoms while remaining incomplete; that is the purpose of this indicator. When all required atoms for a submodule are ready and the submodule completion rule is satisfied, update both this inventory and `pedagogical_generation_status.md` in the same coordination cycle.
