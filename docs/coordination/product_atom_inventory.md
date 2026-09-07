# HydroSIM Product Atom Inventory

Status: canonical product-measurement baseline  
Scope: active 30-submodule roadmap (17 Didactic + `P1`–`P6` + `A1`–`A7`); `PED-D5` is retired and retained only in the traceability note below.

## Product indicator

**238 total atoms = 141 learner inputs + 97 learner-visible outputs.**  
**Current atom indicator: 155/238 ready (65.1%).**

Readiness counts learner-facing production behavior on `main`. Contracts, documentation, APIs, adapters, tests, PRs, CI, screenshots, infrastructure and coordination are not atoms.

| Submodule | Inputs | Outputs | Total | Ready |
|---|---:|---:|---:|---:|
| PED-D1 | 3 | 4 | 7 | 7 |
| PED-D2 | 7 | 6 | 13 | 13 |
| PED-D3 | 6 | 4 | 10 | 10 |
| PED-D4 | 3 | 1 | 4 | 4 |
| PED-D6 | 8 | 4 | 12 | 12 |
| PED-D7 | 6 | 4 | 10 | 10 |
| PED-D8 | 6 | 5 | 11 | 11 |
| PED-D9 | 6 | 5 | 11 | 11 |
| PED-D10 | 6 | 4 | 10 | 10 |
| PED-D11 | 7 | 4 | 11 | 11 |
| PED-D12 | 4 | 4 | 8 | 8 |
| PED-D13 | 6 | 4 | 10 | 10 |
| PED-D14 | 5 | 4 | 9 | 9 |
| PED-D15 | 7 | 3 | 10 | 10 |
| PED-D16 | 7 | 4 | 11 | 0 |
| PED-D17 | 9 | 5 | 14 | 8 |
| PED-D18 | 7 | 4 | 11 | 11 |
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
| **TOTAL** | **141** | **97** | **238** | **155** |

### Retired PED-D5 traceability

`PED-D5 — Acoustic Detection Fundamentals` was retired as a standalone submodule by Product Owner decision on 2026-09-06. Its former atoms are mapped to existing receiving behavior and therefore are removed from the denominator rather than duplicated:

| Retired atom | Former wording | Receiving objective / atom |
|---|---|---|
| PED-D5-I01 | signal level | PED-D3 source/received-level reasoning (`PED-D3-I01` and `PED-D3-O01`) |
| PED-D5-I02 | noise level | PED-D3 noise level (`PED-D3-I05`) and SNR consequence (`PED-D3-O02`) |
| PED-D5-I03 | threshold | PED-D3 required SNR/detection threshold (`PED-D3-I06`) for detection margin and PED-D9 threshold (`PED-D9-I03`) for bottom-detection behavior |
| PED-D5-O01 | signal/noise/SNR detectability | PED-D3 SNR versus range and detection margin (`PED-D3-O02`, `PED-D3-O04`) |
| PED-D5-O02 | detected/not-detected state | PED-D9 detection formation and false/missed consequence (`PED-D9-O01`, `PED-D9-O03`) |

Signal/pulse representation and processing prerequisites that supported the retired D5 learning question remain in PED-D2's existing waveform, received-echo, envelope and processing atoms; no new PED-D2 atom is introduced by the retirement.

### Ready atom evidence for partially/newly reconciled submodules

- **PED-D9 — 11/11:** `I01`–`I06`, `O01`–`O05`. PR #336 added learner-operable threshold (`I03`) and single/multiple detection retention (`I04`) plus false/missed consequence (`O03`). PR #341 completes learner-operable phase-based High Density (`I05`) and the canonical High Density/multiple-detection comparison (`O05`) through authoritative API outputs; High Density remains explicitly distinct from generic multiple detection.
- **PED-D13 — 10/10:** PR #362 makes `I01`–`I06` learner-operable in production (sensor/device, connection/port, baud/data rate, update/message rate, protocol/message and time source) and exposes `O01`–`O04` through the authoritative PU-sensor API: PU↔sensor diagram, stream/status and rate readouts, incompatibility state/reasons and configuration-error consequence. The lesson is bilingual and in the production sequence.
- **PED-D17 — 8/14:** current learner-facing readiness includes the established controls/consequences through PR #254 plus the explicit sounding-pattern consequence integrated by PR #273. No additional unsupported survey-product behavior is inferred.

Complete ready baselines: PED-D1, PED-D2, PED-D3, PED-D4, PED-D6, PED-D7, PED-D8, PED-D9, PED-D10, PED-D11, PED-D12, PED-D13, PED-D14, PED-D15 and PED-D18.

## Atom definitions

Format: `inputs -> outputs`. IDs are sequential per list as `<submodule>-I01...` and `<submodule>-O01...`; list order is canonical.

- **PED-D1:** frequency; amplitude; phase -> propagating wave; period; wavelength; frequency/wavelength comparison.
- **PED-D2:** signal type CW/chirp; frequency; bandwidth; pulse length; envelope/filter mode; matched-filter toggle; phase -> transmitted waveform; received echo; envelope; pulse-compression result; temporal resolution; range resolution.
- **PED-D3:** source level; spreading model/parameter; absorption/frequency; range; noise level; detection threshold/required SNR -> received level vs range; SNR vs range; frequency/absorption comparison; detection margin.
- **PED-D4:** SVP; depth/profile geometry; launch angle -> ray/path visualization including refraction and configured-profile error consequence.
- **PED-D6:** element count; frequency; spacing; aperture/dimension; array geometry; eccentricity; Mills Cross; shading/apodization -> array construction; directivity/beam pattern; beamwidth; side-lobe/gain-loss visualization.
- **PED-D7:** TX/RX role; frequency; element count/array size; spacing/face geometry; steering angle; source/arrival angle -> element phase/coherent contribution; array-factor/physical beam pattern; steered direction/peak; steering-loss/beamwidth/coherent-sum readouts.
- **PED-D8:** echosounder mode/configuration; depth; beam geometry/count; incidence/swath angle; beam-spacing mode; transducer/footprint configuration -> synchronized SBES/MBES geometry; beam-centre/sounding positions; footprint; geometric swath; equiangular/equidistant and adjacent-spacing comparison.
- **PED-D9:** detection method; detection window; threshold; multiple-detection setting; High Density; signal/echo scenario -> detection formation; detected position; false/missed consequence; signal-to-sounding relationship; High Density/multiple-detection comparison.
- **PED-D10:** sector count; sector angles; frequency/sector; transmission timing/sequence; pulse duration; power -> temporal sector sequence; sector geometry; footprints/swaths; sector-frequency-time relationship.
- **PED-D11:** vessel dimensions/model; reference point; transducer pose; antenna pose; MRU/IMU pose; waterline/reference height; installation/lever arms -> vessel model; sensor layout; frames/offsets; configuration readout/file representation.
- **PED-D12:** roll; pitch; yaw/heading; heave -> vessel/sensor motion; beam displacement; swath consequence; sounding consequence.
- **PED-D13:** sensor/device; connection/port; baud/data rate; update/message rate; protocol/message; time source -> PU-sensor diagram; stream/status; incompatibility; configuration-error consequence.
- **PED-D14:** sensor rate; timestamp/time source; latency/delay; vessel speed; sensor/stream -> sensor timeline; synchronization; position/attitude-to-ping association; temporal-to-spatial error.
- **PED-D15:** TWTT/range scenario; beam angle; position; attitude; lever arms; SV/SVP; timing/configuration -> ping-detection-range chain; frame/transformation chain; 3D sounding.
- **PED-D16:** area/DTM; depth; sonar/configuration; swath; overlap; line direction/spacing; speed -> planned lines; predicted coverage; gaps/overlap; line count/length.
- **PED-D17:** frequency; footprint/beamwidth; beam spacing; High Density; swath; depth; ping rate; speed; multisector/detection configuration -> swath/footprint consequence; sounding pattern; coverage/gaps; along/across spacing+density; trade-off comparison.
- **PED-D18:** position; attitude; range; SV; offset; timing; water-level uncertainties -> uncertainty components; THU/TVU/TPU; across-track variation; sounding uncertainty.
- **P1:** latency; pitch; roll; heading/yaw biases -> characteristic signatures; classic-parameter vs contaminating-error distinction.
- **P2:** calibration task; area/segment; line geometry/direction; speed -> planned lines over Truth DTM; observability feedback.
- **P3:** learner line set; acquisition run -> acquisition execution; synthetic biased line pairs.
- **P4:** line pair; comparison segment; candidate calibration value -> corrected overlay; plan/profile/surface comparison; residual/convergence; segment-suitability feedback.
- **P5:** submitted calibration values -> Estimated vs Truth; residual error; performance/tolerance assessment.
- **P6:** RISC dataset/system; diagnosis/estimate controls -> RISC result; conventional-patch-test comparison.
- **A1:** Truth DTM/area -> Truth seafloor visualization/state.
- **A2:** vessel model; sensor positions; lever arms; alignments/installation -> integrated platform; installation-state readout.
- **A3:** frequency; pulse; beams; sectors; swath; ping settings; detection/acquisition configuration -> operational sonar state; configured beam/sector/swath visualization.
- **A4:** SV/SVP; water level; other supported environmental condition -> environment state consumed by simulation.
- **A5:** area; line direction/geometry; line spacing; speed; sonar configuration -> executable survey plan; plan metrics/coverage expectation.
- **A6:** acquisition run control -> vessel trajectory/execution; ping/sensor observation stream; integrated acquired observations.
- **A7:** synthetic-data generation/export action -> synthetic raw dataset; export/result state for external processing.

## Readiness maintenance

When production changes reach `main`, update only atoms with functional learner-facing evidence. A submodule may have ready atoms while incomplete. When all required atoms are ready and the submodule completion rule is satisfied, update this inventory and `pedagogical_generation_status.md` in the same coordination cycle.
