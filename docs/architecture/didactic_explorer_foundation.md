# Didactic Explorer Foundation

Version: 0.1.1

## Purpose

The HydroSIM Didactic Explorer is an interactive teaching application built on the same scientific core as the Survey Simulator. It is not a separate physics implementation and it is not intended to reproduce a commercial hydrographic acquisition package.

The teaching contract is:

```text
control -> physical phenomenon -> observable consequence
```

A learner should be able to change a small number of physically meaningful parameters and immediately see which part of the sounding chain changes and why.

## Architectural boundary

The existing project dependency rule remains authoritative:

```text
Scientific Registry
        -> Scientific Core
        -> Simulation Engine
        -> Application / Training
        -> Visualization
```

The Didactic Explorer belongs to the Application / Training and Visualization layers. It consumes scientific results. It must not redefine scientific equations, silently approximate core results, or pass hidden Truth into Processing.

The state invariant remains:

```text
Truth != Observed != Configured != Estimated != Derived
```

## Learning blocks

The first Didactic Explorer is organized around five connected views of one sounding system rather than five independent simulators.

### 1. Acoustic signal

Learning questions:

- How does a finite CW pulse differ from an LFM chirp?
- What changes when center frequency, bandwidth, or pulse duration changes?
- What does matched filtering do to the received waveform?
- How does frequency-dependent absorption alter propagation loss?

Existing core coverage:

- `ContinuousWavePulse`
- `LinearFMPulse`
- baseband waveform sampling
- waveform autocorrelation
- matched filtering
- deterministic transmission loss with explicit absorption coefficient

Scientific gap before a frequency/attenuation lesson is presented as physically complete:

- the core deliberately accepts `absorption_db_per_km` as an explicit input;
- it does not yet select a literature-based frequency/environment absorption model.

That model should be added to the Scientific Core and Scientific Registry before the UI presents attenuation as a calculated physical function of frequency. HydroSIM should expose established selectable models rather than invent a project-specific absorption law.

### 2. Transducer and beams

Learning questions:

- How do array dimensions and acoustic wavelength affect beam shape?
- What are main lobes and side lobes?
- How do TX and RX patterns combine?
- How does SBES geometry differ from MBES geometry?
- What is the insonified footprint and why does it change across the swath?

Existing core coverage:

- rectangular element factor
- array factor
- one-way and two-way beam patterns
- Mills Cross pattern visualization data
- beamwidth derivation
- footprint and pattern-footprint models
- multibeam fan
- beam spacing and receive beam bank

### 3. Propagation in water

Learning questions:

- What is a sound-speed profile?
- Why does a ray refract?
- How does a Processing SVP error move reconstructed soundings?
- How are ray path and travel time related?

Existing core coverage:

- piecewise-constant layered SVP
- Snell/tangential-slowness ray tracing
- travel-time and depth-driven propagation
- explicit sound-speed-at-transducer boundary
- Truth-versus-Processing reconstruction
- layered-SVP explorer snapshot and reference renderer

The ray is a geometric propagation proxy. It must not be presented as a complete finite acoustic wave field.

### 4. Vessel, sensors, and vertical references

Learning questions:

- Where are GNSS, motion sensor, transducer, and other sensors located relative to the vessel reference frame?
- What do lever arms and angular alignments change?
- How do roll, pitch, yaw, and heave enter the sounding geometry?
- What is the difference between waterline/draft/transducer depth and water level/tide/vertical datum?

Existing core and convention coverage:

- coordinate frames and transformations
- vessel/transducer geometry
- lever arms and alignment
- pose, trajectory, and dynamic acquisition geometry
- controlled motion residuals
- explicit vertical-reference semantics in `docs/conventions.md`, including the distinction among waterline, water level, transducer vertical position, draft, heave, dynamic draft, squat, and datum-referenced quantities

The remaining gap is implementation/integration, not a missing conceptual convention. The didactic application needs to compose the already-defined vertical-reference quantities into a clear visual and processing chain without creating a second vertical-reference model.

### 5. Sounding in motion

Learning questions:

- What does vessel motion do to transmitted sectors, receive beams, footprints, and detections?
- What happens when motion is measured correctly versus with bias, latency, or installation error?
- How does a multisector MBES transmit and receive a swath?

Existing core coverage:

- dynamic TX/RX geometry
- transmit sectors
- sector waveform assignment and signal chain
- receive beam bank
- multibeam fan
- motion residual studies
- bottom detection reference components

The UI should expose Truth and sensor/processing states separately whenever an error is introduced.

## Shared sounding chain

All five learning blocks should reveal different parts of the same causal chain:

```text
vessel + sensors + environment
        -> waveform / TX
        -> array and beam formation
        -> propagation and attenuation
        -> seafloor interaction / footprint
        -> RX and filtering
        -> detection
        -> reconstruction / vertical reduction
        -> sounding
```

A lesson may hide stages for clarity, but it should not implement an alternative chain.

## Interaction rule

Each first-release lesson should expose only the controls needed to answer its learning question. Advanced parameters remain available later.

Examples:

```text
CW <-> LFM chirp
    -> waveform + spectrum/correlation

frequency / array length
    -> wavelength + beam pattern + footprint

Processing SVP layer speed
    -> ray/reconstruction geometry + swath error

Truth roll / measured roll
    -> beam geometry + residual sounding error
```

The initial frontend should prefer immediate deterministic recomputation over a large configuration form.

## Fidelity levels

The Didactic Explorer may use controlled simplifications when they are explicit and scientifically traceable.

A view must communicate whether it is showing:

- conceptual geometry;
- a controlled analytical/reference model;
- a numerical scientific model;
- a synthetic observation;
- or a derived sounding.

Visual animation must not imply physical fidelity that the underlying model does not provide. For example, animated wavefronts may illustrate phase propagation, but they must not be described as a general wave-equation solution unless such a solver actually exists.

## Foundation gates before broad UI development

The scientific core is already sufficient to begin visualization. Two cross-cutting items deserve attention before their respective lessons are presented as complete:

1. **Frequency-dependent absorption selection** — add at least one established, referenced absorption model while retaining the existing explicit-coefficient loss model.
2. **Vertical-reference integration** — implement and visualize the vertical-reference composition already specified by `docs/conventions.md`; do not redefine those conventions in the application layer.

Neither item blocks the existing SVP, waveform, beam-pattern, footprint, or ray-tracing visual prototypes.

## Development discipline

The Didactic Explorer should not drive uncontrolled growth of the scientific core.

Use the following rule:

```text
New physics?        -> new scientific model
New validation?     -> new test or diagnostic
New way to see it?  -> visualization / composition
New summary?        -> reuse existing outputs
```

When multiple established models exist, HydroSIM should make model selection explicit and document each model's validity domain instead of creating a HydroSIM-specific empirical law.

## First visualization sequence

Recommended order for implementation:

1. Signal Explorer: CW versus LFM, duration/bandwidth, matched-filter response.
2. Beam Explorer: frequency/array dimension, main lobe, side lobes, footprint.
3. Propagation Explorer: SVP, ray tracing, Truth versus reconstructed swath.
4. Vessel Explorer: sensor layout, lever arms, waterline and vertical references.
5. Motion/MBES Explorer: roll/pitch/yaw/heave, SBES versus MBES, multisector operation.

The sequence is pedagogical, not a dependency requirement. Every renderer remains downstream of the scientific core and should reuse the same snapshot/composition approach already established by the layered-SVP explorer.
