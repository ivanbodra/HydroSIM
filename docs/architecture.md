# HydroSIM Architecture

Version: 0.1.x experimental core

## Architectural principle

HydroSIM separates scientific models from simulation orchestration, training logic and visualization.

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

Current responsibilities include:

- coordinate frames and transformations;
- vessel/transducer geometry;
- lever arms and alignment;
- terrain intersections;
- dynamic transmit/receive geometry;
- idealized bottom-return reference models;
- transducer-array geometry;
- receive-element timing and coherent summation;
- element factor, array factor and beam-pattern models;
- waveform/filtering/bottom-detection reference components;
- piecewise-constant layered sound-speed propagation;
- explicit processing boundary for sound speed at the transducer;
- sounding reconstruction under Processing hypotheses.

The core is Python-first and independent from Unreal Engine or any UI framework.

Propagation, array physics, signal processing and terrain interaction remain separate enough that their fidelity can evolve independently.

## 2. Scientific Registry

The Scientific Registry stores scientific metadata independently from executable code, including:

- stable model ID;
- model version and scientific status;
- formula or algorithm;
- variables and units;
- sign/equation conventions;
- validity domain;
- assumptions and limitations;
- primary and supporting references;
- source locator and evidence level;
- implementation mapping;
- validation cases and golden values where appropriate;
- alternatives and supersession relationships.

The intended traceability chain is:

```text
Reference
  -> scientific claim/model
  -> equation or algorithm
  -> implementation
  -> validation
```

Explanatory notes under `docs/science/` complement, but do not replace, registry metadata for mature scientific models.

## 3. Simulation Engine

Responsibilities include:

- scenario loading;
- vessel state and motion history;
- sensor state;
- sonar ping/event generation;
- controlled Truth generation;
- deterministic execution using an explicit seed;
- preservation of state semantics across the processing chain.

The fundamental state distinction is:

```text
Truth != Observed != Configured != Estimated != Derived
```

Processing code must not receive hidden Truth merely to make a result close numerically.

## 4. Truth / Processing boundary

A central HydroSIM invariant is that physical simulation and processing hypotheses remain distinct.

Typical flow:

```text
Truth environment + Truth installation + Truth motion
        ↓
physical/observed sonar quantities
        ↓
Configured / Estimated processing state
        ↓
Derived sounding or diagnostic
```

Examples:

- a true sound-speed profile controls Truth propagation;
- a processing profile controls sounding reconstruction;
- sound speed measured/used at the transducer is a distinct boundary state;
- a point measurement at the transducer must not silently overwrite a finite-thickness profile layer;
- an erroneous Processing hypothesis must not trigger a new intersection with hidden Truth terrain.

## 5. Acoustic geometry and beam semantics

`BeamRay`-style geometry is a geometric pencil-ray proxy unless a model explicitly states otherwise. It must not be interpreted as a complete physical MBES transmit beam.

The architecture separates:

```text
propagation geometry
    ↓
array / beam-pattern response
    ↓
signal processing / detection
```

A two-way MBES response is not equivalent to one geometric ray. Finite TX/RX response, scattering and sector geometry must be introduced explicitly rather than inferred from pencil-ray geometry.

## 6. Application / Training Layer

Planned responsibilities include:

- lessons;
- patch-test exercises;
- hidden parameters;
- hints;
- assessment;
- scoring and diagnostics;
- comparison of expected uncertainty, hidden Truth error and observable residuals.

The Scientific Core must not depend on this layer.

## 7. Visualization

Python visualization tools may be used for reference prototypes.

A future Unreal Engine frontend may provide:

- 3D scene;
- vessel operation;
- beam/ray visualization;
- bathymetric plots;
- signal displays;
- training interfaces.

Unreal Engine must remain replaceable as a frontend.

## 8. Validation strategy

Tests should distinguish between:

- implementation-consistency tests;
- inverse/closure tests;
- independent analytical anchors;
- literature/manufacturer golden values where defensible;
- controlled numerical experiments for effects without a simple closed form.

A closure test is useful but does not independently validate the governing physics if both sides use the same implementation assumptions. For Snell/refraction and boundary handling, HydroSIM therefore maintains direct analytical checks based on conserved tangential slowness and closed-form piecewise-constant geometry.

Scientific equations must not be changed merely to satisfy software tests.

## 9. Current evolution path

The original v0.1 geometric slice has already expanded into acoustic and processing reference models. The working progression is now incremental rather than tied rigidly to the original version labels:

```text
geometry foundation
    ↓
dynamic acquisition geometry
    ↓
array / beam-pattern reference physics
    ↓
layered propagation and sound-speed boundary
    ↓
controlled error-isolation experiments
    ↓
TX tilt / roll / sector asymmetry
    ↓
multisector and broader acquisition scenarios
    ↓
uncertainty, calibration and training workflows
```

Each transition should preserve existing reference cases and add tests before increasing physical complexity.

## 10. Dependency rule

Allowed dependency direction:

```text
Visualization -> Application -> Simulation -> Scientific Core
                                      ↓
                              Scientific Registry
```

Dependencies in the opposite direction are prohibited.
