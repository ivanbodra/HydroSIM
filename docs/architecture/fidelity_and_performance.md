# HydroSIM Fidelity and Performance Architecture

Version: 0.1.0

> HydroSIM shall preserve one scientific model while allowing different numerical realizations and computational costs. Performance choices may change how a model is evaluated, but must not silently change the scientific meaning of the model.

## 1. Purpose

HydroSIM includes demonstrations ranging from elementary geometry to realistic multibeam survey simulation. These use cases have very different computational requirements.

A simple slant-range demonstration must remain computationally trivial. It must not incur the cost of ray tracing, vessel dynamics, waveform simulation, dynamic terrain, high-rate sensor interpolation, or other unrelated capabilities merely because those capabilities exist elsewhere in HydroSIM.

Conversely, a scientific experiment may explicitly enable high-fidelity models where their additional computational cost is justified.

The architecture therefore separates:

1. the scientific capability being studied;
2. the numerical fidelity used to represent that capability;
3. the execution/performance target;
4. the visualization used to present the result.

## 2. Fundamental architecture

The high-level simulation chain is:

```text
Synthetic World / Truth Generator
            ↓
Acquisition System Model
            ↓
Observed / Measured Data
            ↓
Configuration / Integration / Calibration Models
            ↓
Derived Results and Visualization
```

The synthetic world is computationally different from a real survey environment. In reality, the seabed, vessel motion, water column, and environmental state physically exist. In HydroSIM, these may need to be generated numerically.

The acquisition system itself should not require exceptional computing resources at normal technical fidelity. Additional cost should arise only when a scenario explicitly requests more sophisticated synthetic-world or sensor models.

## 3. Scientific model, numerical realization, and visualization

HydroSIM shall keep the following layers conceptually separate:

```text
Scientific Model
      ↓
Numerical Realization
      ↓
Visualization
```

The scientific model defines the physical or mathematical meaning of the process.

The numerical realization defines how that process is computed, for example analytical evaluation, interpolation, numerical integration, iterative ray tracing, vectorized execution, or an optimized backend.

Visualization consumes results from the scientific layer. Visualization requirements shall not determine the scientific calculation.

For example, a ray tracer may internally evaluate hundreds of integration steps while the visualization receives only a reduced set of ray points suitable for display.

## 4. Minimal-dependency execution

HydroSIM experiments shall instantiate and execute only the capabilities required by that experiment.

Disabled or unused capabilities shall impose no meaningful computational cost.

This is a normative architectural requirement.

A simple slant-range demonstration may require only:

```text
SlantRangeDemo
    geometry.vector
    geometry.distance
```

with:

```math
R = \sqrt{\Delta x^2 + \Delta y^2 + \Delta z^2}
```

Such an experiment shall not initialize or evaluate unrelated modules such as:

- vessel dynamics;
- motion time series;
- sound-speed profiles;
- ray tracing;
- physical-array beamforming;
- waveform simulation;
- bottom detection;
- terrain evolution;
- uncertainty propagation.

A refraction demonstration may instead request:

```text
RefractionDemo
    geometry
    acoustics.sound_speed_profile
    acoustics.ray_tracing
```

A more complete survey simulation may request:

```text
SurveySimulation
    terrain
    vessel_motion
    sensor_geometry
    beam_generation
    timing
    sound_speed
    propagation
    bottom_intersection
    georeferencing
```

The architecture shall be additive: simulations begin with the minimum required scientific components and explicitly add capabilities as needed.

## 5. Capability, fidelity, and execution profile

These are independent concepts.

### 5.1 Capability

A capability answers:

> What phenomenon is being modeled?

Examples include geometry, attitude, vessel motion, beam steering, sound-speed propagation, terrain intersection, waveform generation, bottom detection, timing, uncertainty, or calibration.

### 5.2 Fidelity

Fidelity answers:

> With what scientific or numerical sophistication is the enabled phenomenon represented?

Fidelity is configured locally by subsystem. Increasing fidelity in one subsystem shall not implicitly activate unrelated high-cost models.

Examples:

```text
motion.interpolation
    prescribed
    linear
    spline
    high_rate

acoustics.propagation
    straight_ray
    layered_raytrace
    full_raytrace

beamforming.model
    ideal_direction
    sector_geometry
    physical_array

bottom_detection.model
    exact_intersection
    threshold
    waveform_detection

terrain.model
    plane
    analytical_surface
    raster
    mesh
    dynamic

time.model
    ping_epoch
    tx_rx_epochs
    continuous

sound_speed.model
    constant
    surface_only
    layered_profile
    dynamic_field
```

A latency experiment may therefore use high-rate motion and separate Tx/Rx epochs while retaining a flat seabed, ideal beams, no waveform, and simple propagation.

Likewise, a beamforming experiment may use a physical array while the vessel is static and the terrain is planar.

### 5.3 Execution profile

An execution profile answers:

> What performance behaviour is expected from this run?

Initial execution classes are:

- `realtime` — intended to keep pace with simulated acquisition time;
- `interactive` — intended to respond smoothly to user interaction and visualization;
- `batch` — intended for reproducible scientific runs where wall-clock speed is secondary to requested fidelity.

Simulation time and wall-clock time are distinct concepts.

## 6. Fidelity presets

HydroSIM may provide convenience presets, but presets shall not replace explicit subsystem configuration.

Initial presets are:

| Profile | Primary purpose | Typical characteristics |
| --- | --- | --- |
| `conceptual` | immediate explanation of a single concept | analytical geometry, few objects/beams, no unnecessary temporal or propagation models |
| `didactic` | cause-and-effect teaching | selected motion, offsets, latency, SSS, simplified realistic beam geometry |
| `technical` | quantitative hydrographic simulation | realistic timing, Tx/Rx states where needed, SSP/ray tracing where relevant, sensor geometry, reproducible outputs |
| `evaluation` | scientific experiment and validation | explicitly selected maximum relevant fidelity, fine temporal/spatial resolution, uncertainty and traceability as required |

These profiles are presets only. A user or experiment shall be able to override each subsystem independently.

## 7. Acquisition pipeline performance target

The core acquisition pipeline should be real-time capable by design at reasonable technical fidelity on contemporary, commonly available computing hardware.

HydroSIM shall not assume that realistic hydrographic acquisition requires exceptional workstations or high-end GPUs.

GPU acceleration, native-code backends, or parallel computing may be introduced where they provide a clear advantage, but they shall be optional accelerators rather than scientific requirements for ordinary acquisition simulation.

The architecture shall therefore distinguish between:

```text
Acquisition pipeline
    → real-time capable by design

Synthetic environment
    → fidelity-scalable

Advanced environmental or acoustic dynamics
    → optional and explicitly enabled
```

## 8. Synthetic-world computational cost

Compared with real acquisition, HydroSIM must numerically create phenomena that physically exist in the real world.

Potential computational costs include:

- generating vessel trajectory and attitude;
- generating high-rate sensor observations;
- evaluating terrain intersections;
- generating environmental fields;
- propagating acoustic rays;
- synthesizing waveforms;
- evolving terrain or other environmental states with time.

These costs shall remain isolated from experiments that do not require them.

## 9. Time-dependent terrain

HydroSIM should preserve the architectural possibility of terrain that changes with time, even though realistic morphodynamic modeling is a low-priority capability.

The conceptual terrain interface should therefore support:

```text
Terrain(x, y, t)
```

rather than being fundamentally restricted to:

```text
Terrain(x, y)
```

Static terrain implementations may simply ignore `t`.

Potential implementations include:

```text
StaticTerrain
AnalyticalTerrain
RasterTerrain
MeshTerrain
DynamicTerrain
```

A simple future analytical bedform model could be expressed as:

```math
z(x,y,t) = z_0(x,y) + A\sin(\mathbf{k}\cdot\mathbf{x} - \omega t + \phi)
```

or as a superposition of several components.

A more realistic sandwave model may eventually depend on currents, sediment properties, bed shear stress, and morphodynamic processes. Such physics constitutes a separate scientific domain and is explicitly not an initial HydroSIM development priority.

Time-dependent terrain is therefore a planned architectural capability, not an implementation requirement for the initial simulator.

## 10. Reference and optimized implementations

Scientific reference implementations should be preserved when practical, even after optimized implementations are added.

A subsystem may later provide interchangeable backends such as:

```text
RayTracerReferencePython
RayTracerVectorized
RayTracerNative
RayTracerGPU
```

All optimized implementations shall be validated against the corresponding reference model or suitable golden values within documented tolerances.

Performance optimization may change the numerical implementation, but must not silently change the scientific model.

## 11. Reproducibility and fidelity manifest

Every scientific run should be able to record the relevant fidelity and execution configuration.

An illustrative manifest is:

```yaml
simulation_fidelity:
  profile: technical
  execution_target: realtime
  motion_interpolation: cubic
  time_model: tx_rx_epochs
  propagation_model: layered_raytrace
  beam_model: sector_geometry
  bottom_detection: exact_intersection
  waveform_model: disabled
  terrain_model: raster
  terrain_time_dependence: static
  uncertainty_model: enabled
```

The manifest should record the effective configuration rather than only the name of a preset, so that results remain reproducible if preset defaults evolve in later HydroSIM versions.

## 12. Performance design principles

HydroSIM adopts the following principles:

1. **Minimal dependency execution** — an experiment computes only what it needs.
2. **Zero meaningful cost for disabled capabilities** — unavailable or inactive scientific modules shall not remain in hidden computational loops.
3. **Local fidelity control** — higher fidelity in one subsystem shall not automatically activate unrelated expensive models.
4. **Acquisition realism without exceptional hardware** — normal technical acquisition simulation should remain feasible on ordinary contemporary computers.
5. **Synthetic-world scalability** — computationally expensive environmental realism is added explicitly and only where required.
6. **Reference-first scientific correctness** — optimized backends are checked against documented reference implementations or golden values.
7. **Visualization independence** — display detail may be reduced without altering the underlying scientific calculation.
8. **Explicit reproducibility** — effective capability, fidelity, and execution settings are recorded with scientific results.

## 13. Development priority

The near-term priority is not premature optimization. It is to preserve clean module boundaries so that inexpensive demonstrations remain inexpensive and future high-fidelity models can be introduced without forcing their computational cost on simpler experiments.

Implementation priority should therefore be:

```text
correct scientific separation
        ↓
minimal modular implementation
        ↓
reference validation
        ↓
profiling with realistic workloads
        ↓
targeted optimization only where demonstrated necessary
```

This document defines the architectural constraints under which later performance engineering should occur.
