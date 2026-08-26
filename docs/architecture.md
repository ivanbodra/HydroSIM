# HydroSIM Architecture

Version: 0.1.0

## Architectural principle

HydroSIM separates scientific models from simulation orchestration and visualization.

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

The frontend must consume simulation results; it must not define scientific behaviour.

## 1. Scientific Core

Responsibilities:

- coordinate frames and transformations;
- vessel/transducer geometry;
- lever arms and alignment;
- terrain intersections;
- later: acoustics, propagation, signal processing and uncertainty.

The first implementation is Python-first and independent from Unreal Engine or any UI framework.

## 2. Scientific Registry

Stores scientific metadata independently from code, including:

- stable model ID;
- version;
- formula;
- variables and units;
- sign/equation conventions;
- validity domain;
- assumptions;
- primary references;
- secondary references;
- implementation mapping;
- validation cases;
- alternatives and limitations.

## 3. Simulation Engine

Responsibilities:

- scenario loading;
- vessel state;
- sensor state;
- sonar ping generation;
- event history;
- Truth / Observed / Configured / Estimated separation;
- deterministic execution using an explicit seed.

## 4. Application / Training Layer

Later responsibilities:

- lessons;
- patch-test exercises;
- hidden parameters;
- hints;
- assessment;
- scoring and diagnostics.

The scientific core must not depend on this layer.

## 5. Visualization

The first prototype may use Python visualization tools.

A future Unreal Engine frontend may provide:

- 3D scene;
- vessel operation;
- beam/ray visualization;
- bathymetric plots;
- signal displays;
- training interfaces.

Unreal Engine must remain replaceable as a frontend.

## 6. State model

HydroSIM distinguishes:

```text
Truth
Observed
Configured
Estimated
Derived
```

Example for transducer roll alignment:

- Truth: actual installed alignment used by the simulator;
- Configured: value entered in acquisition/processing settings;
- Estimated: value inferred during patch test;
- Derived: residual error or calculated sounding.

## 7. Initial v0.1 scope

The first vertical slice is geometric only:

1. local terrain;
2. vessel pose;
3. transducer pose;
4. ideal beam fan;
5. true ray/terrain intersection;
6. configured ray/terrain intersection;
7. error vector;
8. roll-offset demonstration.

Acoustic intensity, SSP ray tracing, waveform generation and signal processing are deliberately outside the first geometric slice.

## 8. Evolution path

```text
v0.1 Geometry
      ↓
v0.2 Water column / ray tracing
      ↓
v0.3 Acoustic and signal laboratory
      ↓
v0.4 Patch test
      ↓
v0.5 Acquisition simulator
      ↓
Future Unreal frontend and selective C++ optimization
```

## 9. Dependency rule

Allowed dependency direction:

```text
Visualization → Application → Simulation → Scientific Core
                                      ↓
                              Scientific Registry
```

Dependencies in the opposite direction are prohibited.
