# HydroSIM Conventions

Version: 0.1.0

> No geometry implementation should be considered authoritative before these conventions are reviewed and accepted.

## 1. Internal units

HydroSIM uses SI units internally.

- Length: metre [m]
- Time: second [s]
- Velocity: metre per second [m/s]
- Acceleration: metre per second squared [m/s²]
- Angles: radians internally; user interfaces may display degrees
- Frequency: hertz [Hz]
- Sound speed: metre per second [m/s]
- Acoustic levels: decibels [dB], with reference explicitly identified where required

## 2. Vessel coordinate system

HydroSIM uses a right-handed vessel coordinate system:

- X = forward
- Y = starboard
- Z = down

Therefore:

`X × Y = Z`

## 3. Local navigation frame

The initial prototype uses a local Cartesian navigation frame:

- X_local = East
- Y_local = North
- Z_local = Down

Geodetic coordinates will be introduced later.

## 4. Attitude

- Positive roll: starboard side down
- Positive pitch: bow up
- Heading/yaw: clockwise when viewed from above

The implementation must explicitly document whether matrices represent active or passive rotations.

## 5. Rotation order

The initial implementation uses the documented sequence:

`Yaw → Pitch → Roll`

The exact matrix formulation must be covered by unit tests. No function may rely on an implicit Euler-angle convention.

## 6. Lever arms

Lever arms are vectors from Reference Point A to Reference Point B.

Naming convention:

`lever_arm_<source>_to_<target>`

Example:

`lever_arm_vrp_to_transducer`

Components are expressed in the source reference frame unless explicitly stated otherwise.

## 7. Sensor alignment

Sensor mounting angles are separate from vessel attitude.

Example:

- vessel roll = dynamic platform motion
- transducer roll alignment = fixed installation parameter

These values must never be stored as the same variable.

## 8. Time and latency

Internal simulation time is expressed as seconds from the simulation epoch.

Each sample may additionally contain UTC time in future versions.

Latency is initially defined as:

`observed_time - true_measurement_time`

The convention must be preserved throughout the system and verified with dedicated tests before the latency module is implemented.

## 9. Depth and elevation

Positive Z is downward.

Therefore depth is positive below the local reference surface.

Elevation may be represented separately where required.

## 10. State categories

Relevant quantities must be explicitly associated with one of the following categories:

- Truth: physical value used by the simulator
- Observed: value delivered by a simulated sensor
- Configured: value supplied to the processing/acquisition system
- Estimated: value inferred by a student or algorithm
- Derived: value calculated from other states

## 11. Reproducibility

Every stochastic simulation must receive an explicit random seed.

A reproducible simulation must identify at least:

- scenario ID and version
- HydroSIM software version
- scientific model set and versions
- random seed
- configuration/event history

## 12. Open items for review

Before geometry v0.1 is frozen, the following must be explicitly validated:

1. active versus passive rotation convention;
2. exact yaw-pitch-roll matrix composition;
3. mapping between navigation-frame heading convention and mathematical rotations;
4. latency sign convention in acquisition/processing examples;
5. naming and reference point for vessel and transducer frames.
