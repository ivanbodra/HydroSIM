# HydroSIM Pedagogical Plan

Status: evolving design baseline  
Language: English (canonical repository documentation)

## Purpose

HydroSIM is a hydrographic acquisition simulator with a didactic module. Its pedagogical purpose is to use interactive and visual simulation to improve understanding of concepts that are important to hydrographic acquisition.

This plan defines the intended learning structure. It is not a requirement to reproduce a complete IHO Category A curriculum. HydroSIM remains bounded around acquisition, calibration, observation formation, and synthetic raw-data generation.

All teaching experiences must consume the same Scientific Core used by the simulator. The didactic layer must not create parallel physics.

```text
Scientific Core
    -> Didactic Module
    -> Patch Test Module
    -> Acquisition Simulator
```

The state invariant remains:

```text
Truth != Observed != Configured != Estimated != Derived
```

## 1. Didactic Module

| ID | Submodule | Main content / inputs | Learning outputs / visualizations |
|---|---|---|---|
| D1 | Acoustic Wave & Frequency | Acoustic wave, frequency, period, wavelength, amplitude, phase | Propagating-wave visualization; frequency and wavelength comparisons |
| D2 | Pulse & Signal Processing | CW vs chirp, frequency, bandwidth, pulse length, envelope detection/filtering, matched filtering/pulse compression, phase, zero crossing | Time waveform, envelope, echo, pulse compression, temporal/range resolution |
| D3 | Sonar Equation & Propagation Loss | Source level, spreading, absorption, frequency, range, noise, SNR, sonar-equation parameters | Intensity/SNR versus range, frequency effects, detection margin |
| D4 | Sound Speed & Refraction | Sound speed, SVP, gradients, depth, launch angle | Ray tracing, refraction, acoustic path, effects of an incorrect profile |
| D5 | Acoustic Detection Fundamentals | Signal/noise, threshold, SNR, physical detection principles | Relationship between echo quality and detectability. Review possible merge with D9 to avoid redundancy |
| D6 | Transducer & Array Construction | Elements, frequency, wavelength, spacing, aperture, dimensions, geometry, eccentricity, Mills Cross, shading | Array construction, directivity, beamwidth, side lobes, gains/losses |
| D7 | Beamforming & Electronic Steering | Relative delays/phases, TX/RX beamforming, steering, receive timing, dynamic focusing/steering, apodization | Electronic beam formation and steering, coherent summation, side lobes, steering losses |
| D8 | Echosounders — SBES vs MBES | SBES/MBES architectures, TX/RX arrays, beam geometry, footprint, depth, incidence angle, beam spacing | Synchronized SBES/MBES comparison, footprint, swath, equiangular vs equidistant spacing, sounding spacing |
| D9 | Bottom Detection | Amplitude detection, phase detection, hybrid/transition behavior, detection window, thresholds, multiple detections, High Density | Detection formation, false/missed detections, detection position, signal-to-sounding relationship, High Density |
| D10 | Multisector MBES | Number of sectors, sector angles, frequency per sector, transmission timing/sequence, pulse duration, power | Temporal sector sequence, geometry, footprints, swaths, sector-frequency-time relationship |
| D11 | Vessel & Sensor Configuration | Vessel dimensions, reference point, sensor positions/orientations, lever arms, transducer, antenna, MRU/IMU, waterline/reference heights | Vessel model, sensor layout, frames/offsets, conceptual/realistic vessel file |
| D12 | Vessel Motion | Roll, pitch, yaw/heading, heave, vessel geometry and sensor locations | Vessel/sensor motion, beam displacement, swath and sounding effects, induced effects where pertinent |
| D13 | PU & Sensor Integration | Processing/acquisition unit, representative sensors (e.g. Applanix, Seapath, MRU), serial/Ethernet, ports, baud rate, update/message rates, protocols, time source | PU-to-sensor diagram, streams, connection status, incompatibilities, configuration-error effects |
| D14 | Timing, Synchronization & Latency | Sensor rates, timestamps, clock/time source, latencies, delays, vessel speed | Sensor timeline, synchronization, position/attitude applied to ping, temporal-to-spatial error |
| D15 | Sounding Formation | TWTT/range, beam angle, position, attitude, lever arms, SV/SVP, timing, vessel configuration | Integrated chain: ping -> detection -> range -> transformations -> 3D sounding |
| D16 | Survey Planning | Area/DTM, depth, sonar, swath, overlap, line direction, line spacing, vessel speed | Planned lines, predicted coverage, gaps/overlap, line count and length |
| D17 | Survey Coverage & Acquisition Trade-offs | Frequency, footprint, beam spacing, High Density, swath, depth, ping rate, speed, multisector, detection configuration | Settings -> swath -> footprints -> sounding pattern -> coverage; along/across-track spacing, density, gaps and trade-offs |
| D18 | Uncertainty / TPU | Position, attitude, range, SV, offset, timing and water-level uncertainties when supplied; detection geometry | Uncertainty components and propagation, THU/TVU/TPU, across-track variation, sounding uncertainty visualization |

D17 is intentionally a synthesis experience: previously learned controls are reused so the learner can see how acquisition choices interact rather than treating settings independently.

## 2. Patch Test Module

### Pedagogical objective

The learner must understand not only the final calibration values but why a particular line geometry and bottom feature make each residual bias observable.

The four classic parameters addressed by the conventional patch-test exercise are:

- latency / time delay;
- pitch bias;
- roll bias;
- heading / yaw bias.

Lever arms, heave, SVP, water level, positioning and other errors may contaminate calibration, but they are not presented as the four parameters solved by the conventional patch test.

| ID | Submodule | Learner action / inputs | HydroSIM behavior / outputs |
|---|---|---|---|
| P1 | Patch-Test Fundamentals & Error Signatures | Explore latency, pitch, roll and heading/yaw biases | Show characteristic artifacts and distinguish classic patch-test parameters from other error sources |
| P2 | Patch-Test Area & Line Planning | Inspect a simplified artificial gridded DTM; choose area, line/segment, direction and speed for each parameter | Evaluate whether the selected geometry makes the parameter observable; provide specific feedback without revealing the solution |
| P3 | Synthetic Patch-Test Acquisition | Execute the learner-planned lines | Scientific Core introduces hidden exercise biases and generates synthetic acquired line pairs over the Truth DTM |
| P4 | Manual Patch-Test Calibration | Select line pair and comparison segment; manually vary the candidate component value until datasets match | Reapply correction interactively; show overlaid plan/profile/surface views and residuals; evaluate whether the chosen comparison segment is suitable |
| P5 | Exercise Assessment | Submit final calibration values | Reveal Truth and compare Estimated vs Truth, residual error and performance for each component |
| P6 | RISC Simulator | Work with an equivalent system/dataset | RISC diagnosis/estimate and comparison with the conventional patch-test experience |

### Artificial patch-test DTM

The training DTM should be deliberately simple and mathematically known rather than an unnecessarily realistic seafloor. It should be a small gridded surface containing:

- irregular terrain around the training area;
- a sufficiently large predominantly flat region;
- a slope/transition suitable for pitch and latency observation;
- an isolated, unambiguous feature suitable for heading/yaw and also useful for pitch/latency;
- deliberately less suitable regions so that choosing where to acquire is itself part of the exercise.

The interface must not label areas as "Roll area", "Pitch area", etc. The learner must recognize the useful geometry.

An analytical definition (plane + controlled slopes/features + bounded irregular relief) is preferred where practical because it preserves an exact Truth surface for scientific validation.

### Efficient four-line solution

The following is a valid optimized solution that the learner may discover; it should not be shown as the initial answer:

| Line | Geometry | Reuse |
|---|---|---|
| L1 | Crosses flat region and feature, direction A, speed V1 | Base for roll, pitch and latency |
| L2 | Coincident with L1, reciprocal direction, speed V1 | L1/L2 over flat segment -> roll; L1/L2 over feature/slope -> pitch; base for heading |
| L3 | Coincident with L1, same direction as L1, speed V2 different from V1 (preferably a substantial difference when operationally appropriate) | L1/L3 -> latency |
| L4 | Parallel and laterally displaced from L2, positioned so the same feature is observed with geometry sensitive to heading bias | L2/L4 -> heading/yaw |

The exact heading/yaw line geometry and sign conventions must follow the documented reference procedure selected by the Scientific Core; the pedagogical layer must not invent a universal geometry.

### Planning and segment-selection feedback

HydroSIM should evaluate both the acquisition geometry and the segment selected for analysis.

Internal pedagogical states:

- **Adequate** — good sensitivity to the requested parameter;
- **Suboptimal** — usable, but likely to produce a less robust estimate;
- **Inadequate** — insufficient observability or geometry for a meaningful determination.

Feedback should explain the reason without simply telling the learner where to draw the correct line.

Parameter-specific considerations include:

- **Roll:** reciprocal geometry, swath overlap and sufficiently flat comparison region;
- **Pitch:** reciprocal geometry and a sufficiently identifiable slope/feature in the relevant direction;
- **Latency:** compatible trajectory and direction, sufficiently different speeds, and an observable feature/slope for along-track displacement;
- **Heading/Yaw:** appropriate lateral separation and observation of the same identifiable feature with sufficiently sensitive swath geometry.

A suboptimal choice that still contains useful information should generally remain executable. The difficulty of matching the datasets is itself pedagogically useful. Blocking should be reserved for essentially non-observable configurations.

A good acquisition followed by a poor analysis-segment choice must generate feedback about the segment rather than incorrectly diagnosing the survey lines as inadequate.

### Manual calibration interaction

The core exercise loop is:

```text
plan
  -> acquire
  -> select line pair
  -> select comparison segment
  -> compare
  -> vary candidate bias
  -> reapply correction
  -> observe convergence/divergence
  -> submit estimate
  -> compare with hidden Truth
```

The principal exercise should not simply ask the learner to substitute values into a formula. The learner adjusts a candidate value interactively until the two datasets are judged to match, then submits the estimate.

Example assessment concept:

```text
Hidden Truth pitch: +0.43 deg
Learner trials:      0.00 -> +0.30 -> +0.45 -> +0.41 deg
Submitted estimate: +0.41 deg

Estimated: +0.41 deg
Truth:     +0.43 deg
Error:     -0.02 deg
```

Perfect numerical coincidence is not required for a pedagogically successful solution; assessment should consider residual error and exercise tolerance.

## 3. Acquisition Simulator

| ID | Submodule | Main inputs | Outputs |
|---|---|---|---|
| A1 | Survey Area / True Seafloor | DTM representing the true seafloor | Truth seafloor used by simulation |
| A2 | Vessel & Installation | Vessel file, sensor positions, lever arms, alignments, installation parameters | Integrated physical platform |
| A3 | Sonar Configuration | Frequency, pulse, beams, sectors, swath, ping settings, detection/acquisition configuration | Operational sonar state/configuration |
| A4 | Environment | SV/SVP and other environmental conditions needed by acquisition; water level where applicable as an input | Environment consumed by the Scientific Core |
| A5 | Survey Planning | Area, lines, direction, spacing, speed, sonar configuration | Executable survey plan |
| A6 | Acquisition | Vessel trajectory + installation + sonar + environment + Truth seafloor | Integrated simulation of sensors, pings and observations during the survey |
| A7 | Synthetic Raw Data Generation | Internal synthetic acquisition observations | Synthetic raw data intended for external hydrographic processing software, particularly CARIS HIPS & SIPS |

A7 is essentially the present HydroSIM product boundary. HydroSIM does not need to reproduce bathymetric post-processing already provided by professional software.

## Scope boundaries

The following are not current HydroSIM teaching modules:

- complete GNSS/geodesy;
- tide theory;
- bathymetric post-processing;
- side-scan sonar;
- backscatter;
- LiDAR;
- AUV/ROV;
- subsea positioning;
- nautical cartography / ENC production;
- MSDI / hydrographic database administration;
- legal aspects;
- project management;
- formal survey reporting.

This does not prohibit necessary inputs from those domains. For example, position and water level may be consumed by an acquisition simulation without HydroSIM becoming a GNSS/geodesy or tide-theory course.

Real-time acquisition processing/QC inspired by operational acquisition systems is a possible future capability, not part of the present pedagogical baseline.

## Open structural item

D5 (Acoustic Detection Fundamentals) and D9 (Bottom Detection) should be reviewed before implementation to determine whether D5 retains a distinct learning question or should be merged/reallocated across D3 and D9.

## Development rule

The pedagogical plan defines learning questions and interactions. Scientific equations, sign conventions, coordinate frames, validity domains and calibration algorithms remain responsibilities of the Scientific Core and Scientific Registry and must be independently documented and validated before being treated as authoritative in the training application.
