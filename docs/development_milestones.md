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

The first renderer presents Truth and Processing sound-speed profiles, Truth refracted rays and bottom intersections, reconstructed soundings, and beamwise vertical/across-track error.

Enabling Matplotlib execution in CI exposed a real renderer defect: the plotting code originally assumed ray-segment endpoint objects that the scientific path model does not store. The renderer was corrected to reconstruct the polyline from the actual `LayeredRayPath` segment representation. This validated the decision to test visualization code rather than leave it skipped.

## Didactic Explorer learning blocks

The didactic product is organized as connected views of the same sounding system, not as unrelated simulators.

1. **Acoustic signal:** CW versus chirp/LFM, frequency, wavelength, duration, bandwidth, filtering, matched filtering, and frequency-dependent attenuation.
2. **Transducer and beams:** array size, beamwidth, side lobes, footprint, SBES versus MBES, Mills Cross geometry, and multisector transmission.
3. **Propagation:** sound-speed profiles, refraction, ray tracing, and absorption/attenuation.
4. **Vessel, sensors, and vertical references:** GNSS, IMU/MRU, transducer installation, lever arms, waterline, draft, transducer depth, water level, tide, and vertical datum.
5. **Sounding in motion:** roll, pitch, yaw, heave, latency, multibeam geometry, multisector operation, and detection/reconstruction effects.

Each first-release lesson should expose only the controls required to answer its teaching question.

## Vertical-reference architecture decision

A review of the founding conventions confirmed that `waterline`, `water_level`, draft, heave, transducer vertical position, dynamic draft, and squat are already conceptually distinguished.

Therefore the remaining gap is **implementation and integration**, not creation of another conceptual vertical-reference model. This review prevented unnecessary duplication and reinforced the rule that existing project specifications should be checked before adding new abstractions.

## Signal Explorer foundation

The Signal Explorer is the first composition layer for the acoustic-signal learning block. Its snapshot reuses the existing finite-duration CW and LFM/chirp models, complex-baseband sampling, sampling-adequacy diagnostics, and normalized autocorrelation/matched-filter response.

The baseband representation is explicit. In particular, a constant CW baseband signal does **not** imply constant physical acoustic pressure: the carrier oscillation has been removed from the analytic/baseband representation. A future carrier/passband visualization may illustrate that oscillation, but it must remain a presentation layer and must not replace the scientific waveform model.

## First Signal Explorer renderer

The first renderer compares CW and LFM/chirp using three didactic panels:

- **Transmitted waveform: complex baseband** — in-phase waveform component over pulse time;
- **Phase evolution** — constant CW baseband phase versus the LFM chirp phase evolution;
- **Pulse-compression response** — normalized matched-filter/autocorrelation response, making the broad CW response and compressed LFM peak visually comparable.

The renderer consumes `SignalExplorerSnapshot` objects and does not recompute waveform physics.

## First interactive Signal Explorer

The initial interactive prototype demonstrated that the CW-versus-chirp lesson could close a live control loop through the existing Scientific Core and snapshot API. It originally exposed center frequency, pulse duration, and LFM bandwidth.

The subsequent user-experience review identified an important teaching-contract problem: center frequency is part of the waveform definition, but the current complex-baseband plots do not show a meaningful consequence of changing it. Exposing that parameter as an active control therefore invited interaction without an observable physical result.

The integrated Signal lesson now keeps center frequency fixed as explicit context and exposes only:

- pulse duration;
- LFM bandwidth.

Both controls have slider and exact numeric-entry affordances, update immediately, and can be reset to the lesson defaults. The page also states the learning question, tells the learner what to look for, identifies the scientific representation, and declares important phenomena that are not yet shown.

This refines the teaching loop from merely interactive to pedagogically causal:

```text
learning question
    -> meaningful control
    -> scientific model
    -> observable consequence
    -> interpretation boundary
```

## Decision: introduce the application shell now

HydroSIM will not wait for the entire Scientific Core, sensor suite, motion model, and sonar model to be complete before creating the integrated application. The project has reached the point where continuing to expand the backend horizontally would increase the risk of discovering UI/API integration problems too late.

Development therefore proceeds by **vertical slices** inside an early application shell:

```text
learning question
      -> Scientific Core
      -> composition / snapshot
      -> visualization
      -> interaction
      -> tests and user evaluation
```

The application shell is not treated as cosmetic work. For the Didactic Explorer, presentation is part of validating the teaching contract because the project must make physical cause and observable consequence understandable through interaction.

The first shell should remain intentionally small. It should provide a recognizable HydroSIM window, navigation between learning blocks, a content/visualization area, and a place for lesson-specific controls. The existing Signal Explorer becomes the first embedded vertical slice. Later slices are integrated into the same shell rather than developed as independent applications.

This decision preserves the architecture boundary:

```text
Scientific Core -> composition/snapshot -> renderer -> application shell
```

The shell may coordinate controls, navigation, layout, and redraws, but scientific equations and physical behavior remain outside the UI.

## First runnable Didactic Explorer application shell

The first desktop application shell now exists as a PySide6 window with navigation for Signal, Beam, Propagation, Vessel, and Motion. Signal is the first functional page; the other entries intentionally remain placeholders that expose the planned product structure without pretending that the corresponding vertical slices are complete.

A reusable `draw_signal_explorer_comparison(...)` renderer boundary was introduced so both the standalone Matplotlib interaction and the PySide6 application redraw the same existing axes from the same snapshots. The application no longer replaces whole Matplotlib figures on every control change, and the interactive shell no longer duplicates the renderer implementation. This stabilizes the intended boundary:

```text
control state
    -> SignalExplorerSnapshot
    -> shared renderer
    -> existing application canvas
```

The application is directly launchable after installing visualization dependencies through either `hydrosim-didactic` or `python -m hydrosim.app`. This marks the transition from a collection of scientific/visual components to an executable product shell that can receive subsequent vertical slices.

## Didactic Explorer user-experience contract

The product experience is now explicitly documented in `docs/architecture/didactic_explorer_experience.md`. The central design decision is that HydroSIM should feel like an interactive scientific lesson rather than a parameter-dense sonar configuration screen.

A first-release lesson must make four things immediately clear: the learning question, the meaningful control, the observable consequence, and the scientific representation/fidelity boundary. Every active control must change something the learner can actually observe in that lesson.

This decision also introduces progressive disclosure as a product rule: advanced parameters should appear only when they can be interpreted in the active causal chain. Planned learning blocks remain visible in navigation but are clearly marked as planned rather than appearing operational.

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
| `d6ad684` | Add interactive Signal Explorer controls | Added the first live didactic control loop. |
| `c464665` | Document first interactive Signal Explorer | Recorded the first interactive vertical slice. |
| `15cc615` | Add first Didactic Explorer application shell | Created the integrated PySide6 application window. |
| `5bb33ef` | Stabilize Signal Explorer redraw boundary | Introduced the reusable in-place renderer used by interactive shells. |
| `aaa32a3` | Add Didactic Explorer command | Made the desktop application directly launchable after visualization installation. |
| `64b4ddf` | Define Didactic Explorer user experience contract | Formalized guided-learning and progressive-disclosure rules. |
| `2455e39` | Test guided Didactic Explorer experience | Added checks for meaningful controls, guidance, reset, and planned-state labeling. |

## Current development direction

HydroSIM now has a runnable application shell, a stable snapshot-to-renderer boundary, and an explicit user-experience contract. The immediate objective is no longer to add interface surface area, but to integrate the next learning question end to end under the same rules.

Near-term sequence:

1. preserve the guided-learning contract while completing the Signal lesson;
2. connect frequency to a real observable consequence only after a referenced frequency-dependent absorption model is available, or expose frequency first in the Beam lesson where wavelength/array effects are already represented;
3. integrate the existing beam/transducer models as the next vertical slice with a small number of meaningful controls;
4. continue through propagation/SVP -> vessel/sensors -> motion -> integrated acquisition;
5. keep advanced configuration for the Survey Simulator or progressive-disclosure views rather than putting every parameter on the first didactic screen.

## When to update this log

Add a milestone when at least one of the following occurs: a meaningful architectural decision changes project direction; a vertical slice becomes usable end to end; an important physical model is added; a scientific development branch is deliberately closed or rejected; a learning block receives its first renderer or interactive experience; major subsystems become integrated; or the contract between Scientific Core, Didactic Explorer, and Survey Simulator changes.

Routine commits, minor refactors, formatting changes, and ordinary bug fixes do not need individual milestone entries unless they reveal an important architectural or scientific lesson.
