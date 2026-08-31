# HydroSIM

HydroSIM is a scientific and didactic simulator for hydrographic surveying.

The project is organized around two products built on one shared scientific core:

```text
                 SCIENTIFIC CORE
        geometry + acoustics + sensors
                  + references
                       |
          +------------+------------+
          |                         |
          v                         v
   DIDACTIC EXPLORER          SURVEY SIMULATOR
   interactive learning       synthetic acquisition
```

The project aims to combine:

- geometric simulation;
- acoustic propagation and array modelling;
- synthetic sensor and sonar observations;
- hydrographic acquisition scenarios;
- calibration and error-isolation exercises;
- scientific traceability;
- interactive visualization.

## Product intent

### Didactic Explorer

The Didactic Explorer is intended to make hydrographic sounding physics and system integration visually understandable. It should expose a small number of meaningful controls and show their consequences through the teaching contract:

```text
control -> physical phenomenon -> observable consequence
```

It is not a separate physics implementation. It consumes the same scientific models used elsewhere in HydroSIM.

### Survey Simulator

The Survey Simulator is intended to compose vessel, sonar, sensors, environment, terrain and processing configuration into coherent synthetic hydrographic acquisition scenarios.

Both products preserve the same scientific conventions, state semantics and traceability.

## Current status

HydroSIM is still experimental and pre-operational, but the implemented scientific core now extends well beyond the original geometric v0.1 vertical slice.

Current foundations include:

- vessel and transducer reference frames;
- roll, pitch, yaw, heave, lever arms and latency;
- flat and sloping terrain;
- Truth / Observed / Configured / Estimated / Derived state separation;
- dynamic transmit/receive geometry;
- receive-element timing and coherent summation;
- element factor, array factor, one-way and two-way beam-pattern reference models;
- beam spacing and footprint reference models;
- waveform, filtering and bottom-detection reference components;
- piecewise-constant layered sound-speed propagation;
- explicit sound speed at the transducer as a zero-thickness processing boundary;
- controlled Truth-versus-Processing sound-speed error experiments;
- a specified environmental SVP-extension model that derives sound speed from temperature, salinity and pressure below an explicit profile boundary, while preserving strict finite-profile ray tracing;
- first visualization composition adapters and reference renderers;
- first integrated Didactic Explorer desktop shell with the Signal lesson embedded.

The current models intentionally remain modular and limited in fidelity. Finite-bottom scattering, complete operational multisector behaviour, complete uncertainty propagation and several acquisition-system effects remain future work.

The near-term development priority is vertical integration: turn the existing scientific core into usable didactic and survey-simulation workflows before broadening the physics horizontally. The Propagation Explorer is being extended to make the distinction between observed profile support and explicit environmental extrapolation visible, including a didactic comparison between constant sound speed and pressure-dependent `c(T,S,P)` continuation.

## Design principles

1. Scientific models must be explicit and documented.
2. Scientific code must be independent from the visualization layer.
3. Truth, observations, configuration, estimates and derived results must remain separate.
4. Every relevant model must be testable, preferably against independent analytical anchors where available.
5. Simulation results must be reproducible.
6. Scenarios must be versioned.
7. Scientific models must be replaceable without redesigning the system.
8. Visualization must not define the physics.
9. Point/boundary observations must not silently replace finite-thickness environmental models.
10. Reference-model closure must not be generalized beyond its documented validity domain.
11. New models should be added only when they answer a new physical question, not merely to create another summary of existing outputs.
12. Environmental extrapolation beyond observed support must be explicit, traceable, and distinguishable from measured data.

## Architecture

HydroSIM is organized into conceptual layers:

```text
Scientific Registry
        ↓
Scientific Core
        ↓
Simulation Engine
        ↓
Application / Training
        ↓
Visualization
```

The first implementation is Python-first. Future optimized components may be implemented in C++ while preserving a traceable Python reference implementation.

See also:

- `docs/architecture.md`
- `docs/architecture/didactic_explorer_foundation.md`
- `docs/architecture/fidelity_and_performance.md`
- `docs/conventions.md`
- `docs/science/environmental_sound_speed_extension.md`

## Requirements

Python >= 3.12

Main dependencies:

- numpy
- scipy
- pydantic
- pyyaml

Development dependencies include pytest, pytest-cov and ruff. Visualization dependencies are optional.

## Run the Didactic Explorer

Install HydroSIM with the visualization dependencies:

```bash
python -m pip install -e '.[visualization]'
```

Launch the desktop application with either:

```bash
hydrosim-didactic
```

or:

```bash
python -m hydrosim.app
```

The first integrated lesson is **Signal**, which compares finite-duration CW and LFM/chirp waveforms and their normalized pulse-compression responses. The Beam, Propagation, Vessel and Motion entries currently define the application structure and will be filled through subsequent vertical slices.

## Running checks

```bash
pytest -q
ruff check .
```

## Scientific traceability

Scientific metadata is stored under `scientific_registry/`, while explanatory scientific notes are kept under `docs/science/`.

Each mature scientific model should identify, where applicable:

- stable model ID and version;
- equation or algorithm;
- variables and units;
- coordinate/sign conventions;
- validity domain;
- assumptions and limitations;
- primary and supporting references;
- source mapping and evidence level;
- implementation path;
- independent or numerical validation cases.

The intended traceability chain is:

```text
Reference
  -> scientific claim/model
  -> equation or algorithm
  -> implementation
  -> validation
```

## Status

Experimental. Not intended for operational hydrographic use.
