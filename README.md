# HydroSIM

HydroSIM is a scientific and didactic simulator for hydrographic surveying.

The project aims to combine:

- geometric simulation;
- acoustic modelling;
- synthetic sensor data;
- hydrographic acquisition scenarios;
- calibration exercises;
- scientific traceability;
- interactive visualization.

## Current version

HydroSIM v0.1 focuses on the geometric foundation of hydrographic surveying.

The first prototype includes:

- vessel reference frame;
- transducer reference frame;
- roll, pitch, yaw and heave;
- lever arms;
- multibeam fan geometry;
- flat and sloping terrain;
- true versus calculated beam intersections;
- roll, pitch and latency errors;
- Truth / Observed / Configured / Estimated state separation.

Acoustic propagation and signal processing will be added in later versions.

## Design principles

1. Scientific models must be explicit and documented.
2. Scientific code must be independent from the visualization layer.
3. Truth, observations, configuration and estimates must remain separate.
4. Every relevant model must be testable.
5. Simulation results must be reproducible.
6. Scenarios must be versioned.
7. Scientific models must be replaceable without redesigning the system.
8. Visualization must not define the physics.

## Architecture

HydroSIM is organized into four conceptual layers:

```text
Scientific Core
      ↓
Simulation Engine
      ↓
Application / Training
      ↓
Visualization
```

The first implementation is Python-first. Future optimized components may be implemented in C++ while preserving the Python reference implementation.

## Requirements

Python >= 3.12

Main dependencies:

- numpy
- scipy
- pydantic
- pyyaml
- pytest
- matplotlib

Optional:

- plotly
- PySide6

## Running tests

```bash
pytest
```

## Scientific traceability

Scientific models and their metadata are stored in `scientific_registry/`.

Each model should contain:

- stable identifier;
- version;
- equation;
- variables;
- units;
- validity domain;
- assumptions;
- references;
- implementation;
- test cases;
- known limitations.

## Status

Experimental. Not intended for operational hydrographic use.
