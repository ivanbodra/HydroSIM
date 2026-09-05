# HydroSIM Product Atom Inventory

Status: canonical product-measurement baseline  
Scope: active 31-submodule roadmap (`PED-D1`–`PED-D18`, `P1`–`P6`, `A1`–`A7`)

## Purpose and counting rules

This file defines the denominator for HydroSIM's granular product-progress indicator. It is a measurement baseline, not a new implementation specification.

- One **input atom** = one distinct learner-operable control/selection that changes the functional experience.
- One **output atom** = one distinct learner-visible functional consequence, visualization or computed readout required by the pedagogical plan.
- One selector with mutually exclusive choices is one input; independent scalar controls are separate inputs.
- One plot/view is one output even when it contains several traces expressing the same phenomenon; a separately meaningful computed readout is separate.
- Navigation, localization, explanatory text, contracts, docs, APIs, adapters, tests, PRs, CI, screenshots, infrastructure and coordination are not atoms.
- An atom is `ready` only when functional in the production path on `main`; specification, mock or backend-only availability is not enough.
- Scope changes must edit this inventory explicitly; the denominator must never change silently.
- `PED-D5` atoms remain in the denominator while D5 remains in the canonical roadmap. A future merge/reallocation must update the pedagogical plan and this inventory together.

## Product indicator

**243 total atoms = 144 learner inputs + 99 learner-visible outputs.**  
**Current atom indicator: 122/243 ready (50.2%).**

Readiness counts learner-facing production behavior on `main`. The current conservative reconciliation includes only atom IDs explicitly evidenced by merged production work; unsupported or inferred behavior remains unready.

| Submodule | Inputs | Outputs | Total | Ready |
|---|---:|---:|---:|---:|
| PED-D1 | 3 | 4 | 7 | 7 |
| PED-D2 | 7 | 6 | 13 | 13 |
| PED-D3 | 6 | 4 | 10 | 10 |
| PED-D4 | 3 | 1 | 4 | 4 |
| PED-D5 | 3 | 2 | 5 | 0 |
| PED-D6 | 8 | 4 | 12 | 12 |
| PED-D7 | 6 | 4 | 10 | 10 |
| PED-D8 | 6 | 5 | 11 | 11 |
| PED-D9 | 6 | 5 | 11 | 5 |
| PED-D10 | 6 | 4 | 10 | 10 |
| PED-D11 | 7 | 4 | 11 | 9 |
| PED-D12 | 4 | 4 | 8 | 5 |
| PED-D13 | 6 | 4 | 10 | 0 |
| PED-D14 | 5 | 4 | 9 | 4 |
| PED-D15 | 7 | 3 | 10 | 3 |
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
| **TOTAL** | **144** | **99** | **243** | **122** |

### Ready atom evidence for partially/newly reconciled submodules

- **PED-D6 — 12/12:** `I01`–`I08`, `O01`–`O04`. `I06` eccentricity is learner-operable on `main` through PR #236, with RX X/Y/Z controls and canonical TX→RX vector/magnitude readout.
- **PED-D9 — 5/11:** `I01`, `I06`, `O01`, `O02`, `O04`.
- **PED-D10 — 10/10:** `I01`–`I06`, `O01`–`O04`.
- **PED-D11 — 9/11:** `I03`, `I04`, `I05`, `I06`, `I07`, `O01`, `O02`, `O03`, `O04`. PR #266 integrates the learner-facing configuration readout/file representation.
- **PED-D12 — 5/8:** `I01`–`I04`, `O01`.
- **PED-D14 — 4/9:** `I02`, `I03`, `O01`, `O02`. PR #278 integrates learner-operable sample/timestamp and latency controls with linked ping/sensor timeline and synchronization/alignment consequence. Sensor rate, vessel speed, sensor/stream selection, explicit position/attitude-to-ping association, and temporal-to-spatial error remain unready pending the canonical dependency tracked from #277/#284.
- **PED-D15 — 3/10:** `O01`–`O03`, integrated learner-facing through PR #269.
- **PED-D17 — 8/14:** current learner-facing readiness includes the established controls/consequences through PR #254 plus the explicit sounding-pattern consequence integrated by PR #273. No additional unsupported survey-product behavior is inferred.
- **PED-D18 — 11/11:** `I01`–`I07`, `O01`–`O04`, with the final sounding-uncertainty consequence integrated through PR #262.

Existing complete ready baselines remain PED-D1, PED-D2, PED-D3, PED-D4, PED-D6, PED-D7, PED-D8, PED-D10 and PED-D18.

## Atom definitions

Format: `inputs -> outputs`. IDs are sequential per list as `<submodule>-I01...` and `<submodule>-O01...`; list order is canonical.

- **PED-D1:** frequency; amplitude; phase -> propagating wave; period; wavelength; frequency/wavelength comparison.
- **PED-D2:** signal type CW/chirp; frequency; bandwidth; pulse length; envelope/filter mode; matched-filter toggle; phase -> transmitted waveform; received echo; envelope; pulse-compression result; temporal resolution; range resolution.
- **PED-D3:** source level; spreading model/parameter; absorption/frequency; range; noise level; detection threshold/required SNR -> received level vs range; SNR vs range; frequency/absorption comparison; detection margin.
- **PED-D4:** SVP; depth/profile geometry; launch angle -> ray/path visualization including refraction and configured-profile error consequence.
- **PED-D5:** signal level; noise level; threshold -> signal/noise/SNR detectability; detected/not-detected state.
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
