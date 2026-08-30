# HydroSIM Development Milestones

Last updated: 2026-08-30

## Purpose

This document records important decisions and milestones in HydroSIM development. It preserves the project reasoning: what was consolidated, why some scientific branches were deliberately stopped, which integration boundaries were introduced, and how the scientific foundation is being transformed into a didactic system and a survey simulator.

It does not replace detailed scientific documentation, the Scientific Registry, conventions, or tests. It is a high-level technical development log and should be updated for architectural changes, meaningful product milestones, or scientific decisions that materially change project direction.

## Consolidated principles

- **Do not reinvent hydrographic physics.** HydroSIM should implement established models from literature and consolidated practice, documenting assumptions, validity domains, and references.
- **Keep scientific states separate.** `Truth != Observed != Configured != Estimated != Derived`.
- **Keep science separate from presentation.** Renderers and interfaces consume Scientific Core results; they do not redefine physics.
- **Prioritize vertical integration.** Once the scientific base is sufficient, progress should favor complete experiences — control, physical phenomenon, observable consequence — rather than accumulating isolated diagnostics.
- **Create a new scientific model only for a new physical question.** A new visualization or summary of existing outputs belongs in analysis/visualization rather than requiring another scientific model.

## Product architecture

HydroSIM is developed as two products over one shared scientific foundation:

```text
                 Scientific Core
          geometry + acoustics + sensors
                 + references
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Didactic Explorer        Survey Simulator
   Why does it happen?      What would the sonar measure?
```

### Scientific Core

Provides geometry, acoustics, sensors, motion, scientific models, conventions, and traceable references.

### Didactic Explorer

Provides transparent interactive visualization of hydrographic and acoustic phenomena. Its primary teaching contract is:

```text
control -> physical phenomenon -> observable consequence
```

### Survey Simulator

Combines vessel, sonar, sensors, trajectory, environment, seabed, observations, configuration, and processing into coherent synthetic sounding/acquisition experiments.

## Deliberate closure of the SVP diagnostic expansion

The processing-SVP scientific line progressed through:

1. processing-SVP error;
2. swath curvature;
3. interface-depth × contrast response map;
4. local sensitivity;
5. finite-difference convergence;
6. the `C_edge = 0` compensation curve;
7. full-swath error along that compensation curve.

The final full-swath response demonstrated an important identifiability result: closure of a scalar edge-minus-nadir curvature metric does not imply that the Processing SVP equals the Truth SVP, that every beam is correct, or that the reconstructed swath is geometrically correct.

Further hidden-error summary models were deliberately not added because the existing full-swath response already exposes vertical, across-track, and sounding-error metrics. Additional models would have increased structural complexity without answering a new physical question.

This decision marked a shift from horizontal scientific expansion toward vertical product integration.

## First didactic vertical slice: Layered SVP Explorer

The first integrated Didactic Explorer slice packages existing scientific calculations into a stable visualization snapshot without introducing new acoustic physics.

The causal chain is:

```text
Truth SVP
   -> physical propagation
   -> Truth ray + bottom intersection
   -> TWTT / observation
   -> Processing SVP
   -> sounding reconstruction
   -> Truth vs reconstructed sounding
   -> Didactic Explorer snapshot
```

The first renderer presents:

- Truth and Processing sound-speed profiles;
- Truth refracted rays and bottom intersections;
- reconstructed soundings;
- beamwise vertical and across-track error.

Enabling Matplotlib execution in CI exposed a real renderer defect: the plotting code originally assumed ray-segment endpoint objects that the scientific path model does not store. The renderer was corrected to reconstruct the polyline from the actual `LayeredRayPath` segment representation. This validated the decision to test visualization code rather than leave it skipped.

## Didactic Explorer learning blocks

The didactic product is organized as connected views of the same sounding system, not as unrelated simulators.

### 1. Acoustic signal

Topics include CW versus chirp/LFM, frequency, wavelength, duration, bandwidth, transmit/receive filtering, matched filtering, and frequency-dependent attenuation.

### 2. Transducer and beams

Topics include array size, beamwidth, side lobes, footprint, SBES versus MBES, Mills Cross geometry, and multisector transmission.

### 3. Propagation

Topics include sound-speed profiles, refraction, ray tracing, and absorption/attenuation.

### 4. Vessel, sensors, and vertical references

Topics include GNSS, IMU/MRU, transducer installation, lever arms, waterline, draft, transducer depth, water level, tide, and vertical datum.

### 5. Sounding in motion

Topics include roll, pitch, yaw, heave, latency, multibeam geometry, multisector operation, and detection/reconstruction effects.

Each first-release lesson should expose only the controls required to answer its teaching question.

## Vertical-reference architecture decision

A review of the founding conventions confirmed that `waterline`, `water_level`, draft, heave, transducer vertical position, dynamic draft, and squat are already conceptually distinguished.

Therefore the remaining gap is **implementation and integration**, not creation of another conceptual vertical-reference model. This review prevented unnecessary duplication and reinforced the rule that existing project specifications should be checked before adding new abstractions.

## Signal Explorer foundation

The Signal Explorer is the first composition layer for the acoustic-signal learning block.

Its snapshot reuses the existing scientific waveform models:

- finite-duration CW;
- finite-duration linear FM (LFM/chirp);
- complex baseband sampling;
- sampling-adequacy diagnostics;
- normalized autocorrelation / matched-filter response.

The snapshot exposes sample time, real and imaginary baseband components, unwrapped baseband phase, sampling adequacy, and autocorrelation results.

The baseband representation is explicit. In particular, a constant CW baseband signal does **not** imply constant physical acoustic pressure: the carrier oscillation has been removed from the analytic/baseband representation. A future carrier/passband visualization may illustrate that oscillation, but it must remain a presentation layer and must not replace the scientific waveform model.

## First Signal Explorer renderer

The first renderer compares CW and LFM/chirp using three didactic panels:

- **Transmitted waveform: complex baseband** — in-phase waveform component over pulse time;
- **Phase evolution** — constant CW baseband phase versus the LFM chirp phase evolution;
- **Pulse-compression response** — normalized matched-filter/autocorrelation response, making the broad CW response and compressed LFM peak visually comparable.

The renderer consumes `SignalExplorerSnapshot` objects and does not recompute waveform physics.

## Recent repository milestones

| Commit | Milestone | Importance |
| --- | --- | --- |
| `12beaa4` | Define Didactic Explorer foundation | Formalized the didactic foundation. |
| `c7adb0a` | Align project overview with two-product architecture | Aligned README with Didactic Explorer + Survey Simulator over the shared core. |
| `1232881` | Refocus architecture on product integration | Shifted priority from continued scientific expansion to product integration. |
| `191da3f` | Clarify Didactic Explorer foundation gaps | Reclassified vertical references as an integration gap rather than a conceptual gap. |
| `25ddfc9` | Run Matplotlib visualization tests in CI | Made visualization tests execute in CI. |
| `0e6d519` | Fix layered SVP ray rendering from path segments | Corrected a renderer defect revealed by actual plotting tests. |
| `247cf85` | Add Signal Explorer composition snapshot | Added the first signal-block visualization snapshot. |
| `fcf89f8` | Add first Signal Explorer renderer | Added the first CW × LFM renderer. |
| `2e8d74b` | Test Signal Explorer renderer | Added renderer tests. |
| `c693689` | Document first Signal Explorer renderer | Documented the renderer and its scientific boundary. |

## Current development direction

HydroSIM is now transitioning from a predominantly scientific/backend foundation into integrated visual experiences. The immediate objective is to turn stable snapshots and renderers into small interactive experiences while keeping all physical behavior in the Scientific Core.

Near-term sequence:

1. make the Signal Explorer interactive, beginning with CW/LFM selection, pulse duration, and LFM bandwidth;
2. implement frequency-dependent acoustic absorption using published, traceable models rather than a HydroSIM-specific law;
3. integrate the vertical-reference chain already specified in project conventions;
4. continue through vertical slices: signal -> beam/transducer -> propagation/SVP -> vessel/sensors -> motion -> integrated acquisition;
5. maintain independent scientific tests and visualization tests proportional to risk.

## When to update this log

Add a milestone when at least one of the following occurs:

- a meaningful architectural decision changes project direction;
- a vertical slice becomes usable end to end;
- an important physical model is added;
- a scientific development branch is deliberately closed or rejected;
- a learning block receives its first renderer or interactive experience;
- major subsystems become integrated;
- the contract between Scientific Core, Didactic Explorer, and Survey Simulator changes.

Routine commits, minor refactors, formatting changes, and ordinary bug fixes do not need individual milestone entries unless they reveal an important architectural or scientific lesson.
