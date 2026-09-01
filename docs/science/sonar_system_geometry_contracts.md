# Minimal sonar-system geometry contracts

Status: vendor-neutral scientific contracts for the first Didactic Explorer Sonar Systems & Geometry lesson.

## Shared coordinate and sign conventions

All contracts reuse canonical HydroSIM conventions:

- containing sensor/body-style Cartesian frame: `+X` Forward, `+Y` Starboard, `+Z` Down;
- transducer-array local normal: `+Z`;
- across-track receive steering: zero along the nominal transducer normal, positive toward Port (`-Y`), negative toward Starboard (`+Y`);
- fixed installation orientation is represented by the existing RPY array/sensor transform, separate from dynamic vessel attitude;
- array/beam directions are unit vectors transformed explicitly between local and containing frames;
- TX and RX roles remain distinct where physically relevant.

The lesson must not imply that a displayed geometric beam ray is a complete finite physical beam or that geometric coverage alone determines detectability.

## 1. SBES system geometry

### Minimum representation

For the first didactic experience an SBES can be represented as one co-located `txrx` transducer/array with:

- one origin/pose;
- one nominal acoustic axis equal to the transducer-frame `+Z` normal before installation rotation;
- one finite one-way/two-way beam-pattern or beamwidth representation when available;
- one nominal sounding direction centred on the acoustic axis.

The geometric reference ray can reuse `BeamDefinition`/`BeamRay` semantics with `beam_count=1` and zero steering. The physical aperture and beam-pattern primitives should reuse `TransducerArray`, element/array factor and footprint models where the lesson needs finite-beam consequences.

### Footprint and coverage semantics

SBES coverage is not a multibeam swath. The first lesson should represent a single insonified/detected footprint around the acoustic axis at the selected range/depth. Beam-limited footprint may be derived from the existing footprint model using the effective beamwidth and incidence geometry.

The footprint is a finite region, whereas the zero-angle `BeamRay` is only the centreline/geometric proxy.

### Invariants

- exactly one nominal centre sounding direction for the baseline SBES;
- no across-track fan or multiple simultaneous receive-beam interpretation;
- fixed transducer installation orientation and vessel attitude remain separate;
- footprint size changes with beamwidth and range even though the centreline remains the same.

### Core guidance

No new fundamental scientific model is required for baseline SBES geometry. A thin composition/adapter can reuse existing array, beam-pattern, single-ray and footprint primitives.

## 2. Multisector transmission

### Scientific meaning

A multisector MBES transmit event divides the overall transmit coverage into multiple transmit sectors. Each sector has its own transmit pointing/orientation state and covers a subset of the overall angular domain. Receive beams may later be associated with the sector that illuminated the corresponding direction, but sectorization must not be collapsed into one undifferentiated beam angle.

### Minimum sector state

For the first vendor-neutral lesson, each `TxSector` needs only:

- stable `sector_id` / index;
- transmit array/head identifier;
- nominal sector centre direction or along-track/across-track orientation in the transducer/head frame;
- sector angular support/coverage bounds sufficient to visualize which part of the total transmit field it covers;
- optional sector order for presentation;
- explicit relationship to the containing head/system.

The first lesson does **not** require vendor-specific power, waveform, pulse length, frequency, sector timing offsets or dynamic sector scheduling. If sector timing is shown later, use the existing `sector_tx_time = tx_time + sector_tx_delay` temporal semantics rather than inventing a new timing convention.

### Coverage relationship

The union of sector coverage forms the configured transmit coverage of the head/system. Sectors may meet or overlap; neither perfect tiling nor overlap should be assumed as a universal physical invariant. The lesson may use a clean non-overlapping example for clarity only if labelled as configured example geometry.

A receive beam remains an `RxBeam`; a transmit sector remains a `TxSector`. A sounding may reference both. UX must not replace the pair with a single generic beam angle.

### Invariants

- TX-sector orientation is expressed in an explicit source frame;
- TX and RX semantics remain separate;
- sector identifiers remain stable within a configured system state;
- total coverage derives from the sector set and is not a separate contradictory geometry;
- vendor-specific timing/power/frequency behavior is out of scope unless separately sourced and modelled.

### Core guidance

The geometry can be composed from existing direction/rotation primitives, but a minimal explicit `TxSector` scientific data structure is justified because sector identity and coverage are new state that cannot be represented unambiguously by the current `BeamDefinition` alone. This should remain a small geometry/state model, not a manufacturer simulation.

## 3. Dual-head geometry

### Minimum representation

A dual-head system consists of two independently identifiable transducer heads rigidly installed relative to a common vessel/sensor reference. For each head the minimum state is:

- `head_id`;
- head origin/lever arm relative to a common source reference such as VRP or sonar-frame origin;
- fixed head orientation using canonical HydroSIM RPY conventions;
- the head's own array(s), nominal normal and configured beam fan/coverage.

The position of a point/direction associated with a head is obtained through the same rigid-body transform semantics already used elsewhere:

`p_head^N = p_ref^N + R_NB l_ref_to_head^B`

with head-fixed orientation then composing with vessel attitude as an installation transform, not being merged into dynamic attitude variables.

### Combined coverage semantics

Each head produces its own angular coverage/fan in its own local frame and then transforms it into the common containing/vessel/navigation frame. Combined dual-head coverage is the union of the two head coverages.

Overlap is permitted and must not be treated as duplicate truth or automatically merged into one physical beam. Gaps are also permitted. Whether a real system suppresses, prioritizes or differently configures overlapping beams is vendor/processing behavior outside this baseline geometry contract.

A typical didactic configuration may cant the port and starboard heads outward to extend total coverage, but outward cant is an example configuration, not a definition of dual-head systems.

### Invariants

- each head retains a distinct identity, origin and fixed orientation;
- both heads share the same common frame conventions after explicit transformation;
- dynamic vessel attitude applies consistently to both heads;
- relative head pose is fixed configuration unless a separate mechanical model says otherwise;
- combined coverage is derived from individual head geometry;
- overlap/gap handling must not invent vendor-specific sounding-selection rules.

### Core guidance

No new acoustic-physics model is required. Existing lever-arm, rotation, array and ideal-fan primitives are sufficient scientifically. A small `SonarHead`/dual-head composition adapter is appropriate to preserve head identity and relative pose.

## 4. First-lesson fidelity boundary

The first Sonar Systems & Geometry lesson may compare:

- SBES: one centreline + one finite footprint;
- single-head MBES: one head with a receive fan and associated TX geometry context;
- multisector MBES: multiple explicit TX sectors composing transmit coverage;
- dual-head MBES: two rigidly mounted heads whose transformed coverages combine.

It should not imply or simulate by default:

- proprietary sector sequencing;
- adaptive beam spacing or dynamic swath optimization;
- per-sector source level/pulse/frequency differences;
- vendor-specific dual-head overlap suppression;
- detection probability or seabed response from geometry alone;
- that Mills Cross is universal to every MBES architecture.

## 5. Implementation guidance summary

- **SBES:** composition only; reuse existing core primitives.
- **Multisector:** add a minimal explicit TX-sector state/geometry model or equivalent canonical adapter because sector identity/coverage is scientifically distinct state.
- **Dual-head:** composition only; reuse lever-arm/rotation/array/fan primitives with explicit head identity and pose.

These contracts are intentionally vendor-neutral and sufficient for the D7 first experience without defining operational sonar behavior that the current Scientific Core does not model.
