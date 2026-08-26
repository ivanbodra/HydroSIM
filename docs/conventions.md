# HydroSIM Conventions

Version: 0.1.2

> These conventions define the internal geometric and temporal semantics of HydroSIM. External instrument or software conventions must be converted explicitly at system boundaries; they must not silently alter the internal convention.

## 1. Internal units

HydroSIM uses SI units internally unless a scientific model explicitly requires otherwise.

- Length: metre [m]
- Time: second [s]
- Velocity: metre per second [m/s]
- Acceleration: metre per second squared [m/s²]
- Angles: radians internally; user interfaces may display degrees
- Frequency: hertz [Hz]
- Sound speed: metre per second [m/s]
- Acoustic levels: decibels [dB], with the physical reference explicitly identified where required

## 2. Geodetic coordinates and CRS

Geodetic coordinates and local Cartesian coordinates are distinct concepts and must not be conflated.

When geographic/geodetic coordinates are used, HydroSIM represents them explicitly as:

- latitude
- longitude
- ellipsoidal height, where applicable

Ellipsoidal height is positive upward.

A CRS must be identified explicitly by its definition and axis directions. An EPSG code may identify a CRS, but the internal simulation frame is not inferred from an EPSG code alone.

For example, EPSG:4326 defines a two-dimensional geographic CRS and does not itself define the HydroSIM local NED frame or a vertical axis.

## 3. Local navigation frame (N)

The initial prototype uses a local right-handed North-East-Down navigation frame, identified by the symbol `N`:

- `X_N` = North
- `Y_N` = East
- `Z_N` = Down

Therefore:

`X_N × Y_N = Z_N`

Heading is measured clockwise from North:

- 0° = North
- 90° = East
- 180° = South
- 270° = West

Positive `Z_N` is downward.

## 4. Vessel / body frame (B)

The vessel frame is identified by the symbol `B` and is right-handed:

- `X_B` = Forward
- `Y_B` = Starboard
- `Z_B` = Down

Therefore:

`X_B × Y_B = Z_B`

The origin of the body frame is the Vessel Reference Point (`VRP`). The VRP is a defined geometric reference point and is not assumed to coincide with the centre of gravity, GNSS antenna, IMU/MRU, transducer, waterline, or any other sensor unless explicitly configured.

## 5. Sensor frames

Sensors may define their own local frames. Initial frame identifiers are:

- `B` = vessel/body frame
- `N` = local navigation frame
- `T` = transducer frame
- `I` = IMU/MRU frame
- `G` = GNSS antenna/reference frame or reference point, where needed

Additional identifiers such as `T1` and `T2` may be used for dual-head systems.

No sensor frame is assumed to be perfectly aligned with the vessel frame.

## 6. Attitude conventions

HydroSIM uses the following positive attitude conventions in the vessel/body frame:

- Positive roll (`φ`): starboard side down
- Positive pitch (`θ`): bow up
- Positive yaw (`ψ`): turn to starboard; clockwise when viewed from above

With the right-handed Forward-Starboard-Down body frame and the active rotation matrices defined below, these signs are obtained directly from the standard right-hand elementary rotations about `+X_B`, `+Y_B`, and `+Z_B` respectively.

Heading and yaw share the same positive rotational sense in the NED convention, but they remain semantically distinct:

- heading describes vessel orientation relative to North;
- yaw is the rotational degree of freedom about the vertical/body `Z` axis.

## 7. Rotation representation and order

HydroSIM uses column vectors and explicitly defined active rotation matrices.

The conceptual Euler rotation sequence is:

`Roll → Pitch → Yaw`

with:

- `φ` = roll
- `θ` = pitch
- `ψ` = yaw / heading angle as applicable

The elementary active right-hand rotation matrices are:

`R_x(φ) = [[1, 0, 0], [0, cosφ, -sinφ], [0, sinφ, cosφ]]`

`R_y(θ) = [[cosθ, 0, sinθ], [0, 1, 0], [-sinθ, 0, cosθ]]`

`R_z(ψ) = [[cosψ, -sinψ, 0], [sinψ, cosψ, 0], [0, 0, 1]]`

For the Body-to-Navigation transformation, the composite direction-cosine matrix is:

`R_NB = R_z(ψ) R_y(θ) R_x(φ)`

A vector expressed in body coordinates is transformed to navigation coordinates by:

`v_N = R_NB v_B`

Because column vectors are used, the rightmost matrix acts first. Therefore the written product corresponds to the conceptual application order Roll, then Pitch, then Yaw.

The inverse transformation is:

`v_B = R_NB^T v_N`

because a valid rotation matrix is orthogonal:

`R_NB^-1 = R_NB^T`

No implementation may rely on a library's undocumented or default Euler-angle convention.

### Canonical rotation tests

The following cases are mandatory unit-test references.

1. **Zero attitude / heading 0°**
   - input body forward vector: `[1, 0, 0]_B`
   - expected navigation vector: `[1, 0, 0]_N`
   - interpretation: Forward maps to North.

2. **Heading / yaw +90°**
   - input body forward vector: `[1, 0, 0]_B`
   - apply `R_z(+90°)`
   - expected navigation vector: `[0, 1, 0]_N`
   - interpretation: Forward maps to East.

3. **Roll +90°**
   - input body starboard vector: `[0, 1, 0]_B`
   - apply `R_x(+90°)`
   - expected rotated vector: `[0, 0, 1]`
   - interpretation: Starboard rotates toward Down.

4. **Pitch +90°**
   - input body forward vector: `[1, 0, 0]_B`
   - apply `R_y(+90°)`
   - expected rotated vector: `[0, 0, -1]`
   - interpretation: Forward rotates toward Up because positive Z is Down.

In addition to the physical cases above, every implemented rotation matrix must satisfy, within numerical tolerance:

- `R^T R = I`
- `R^-1 = R^T`
- `det(R) = +1`

These tests are normative for the HydroSIM geometry core.

## 8. Heave

Heave uses the hydrographic sign convention:

- Positive heave = upward vessel displacement
- Negative heave = downward vessel displacement

This is intentionally different from the sign of the `Z_N` and `Z_B` coordinates, which are positive downward.

Therefore, for a pure heave displacement:

`ΔZ = -heave`

Heave must never be treated as an alias for a Z coordinate.

## 9. Lever arms

A lever arm is a directed vector from a source reference point to a target reference point.

Naming convention:

`lever_arm_<source>_to_<target>`

Example:

`lever_arm_vrp_to_transducer`

Components are expressed in the source frame unless explicitly stated otherwise.

For a lever arm from the VRP to the transducer expressed in body coordinates:

`p_T^N = p_VRP^N + R_NB l_VRP_to_T^B`

Example interpretation in the body frame:

- `x > 0`: target is forward of the source
- `y > 0`: target is starboard of the source
- `z > 0`: target is below the source

## 10. Sensor alignment

Sensor mounting/alignment angles are fixed installation parameters and are separate from dynamic vessel attitude.

Examples:

- vessel roll = dynamic platform motion
- transducer roll alignment = fixed installation parameter
- IMU-to-vessel misalignment = fixed installation parameter

These values must never be stored as the same variable or silently combined.

Transformations must identify both the source and target frames.

## 11. Time and latency

Internal simulation time is expressed as seconds from the simulation epoch.

UTC timestamps may additionally be stored when needed, but simulation time remains the deterministic internal reference.

HydroSIM defines positive latency as a delayed observation/state:

`state_used(t) = state_true(t - Δt)` for `Δt > 0`

Example:

- ping time = 10.000 s
- latency = +0.100 s
- state used by processing = state at 9.900 s

The sign convention must be applied consistently to all simulated sensor streams and verified with dedicated tests.

Latency must be modelled separately from clock offset, timestamp error, transmission delay, and interpolation error when those effects are introduced.

## 12. Depth, height, and elevation

Within NED and body frames, positive Z is downward.

Therefore:

- depth below the local reference surface is positive;
- upward geometric displacement corresponds to negative ΔZ;
- ellipsoidal height, when used in geodetic coordinates, is positive upward.

Depth, Z coordinate, elevation, ellipsoidal height, draft, water level, and heave are distinct quantities and must not be used interchangeably.

## 13. State categories

Relevant quantities must be semantically associated with one of the following categories:

- `Truth`: physical value used by the simulator
- `Observed`: value delivered by a simulated sensor
- `Configured`: value supplied to the processing/acquisition system
- `Estimated`: value inferred by a student or algorithm
- `Derived`: value calculated from other states

A state category is semantic, not a requirement to duplicate every field into five copies. Data structures should group values by state where appropriate.

## 14. Reproducibility

Every stochastic simulation must receive an explicit random seed.

A reproducible simulation must identify at least:

- scenario ID and version
- HydroSIM software version
- scientific model set and versions
- random seed
- configuration/event history

## 15. External conventions

HydroSIM uses the conventions defined in this document internally. Manufacturer, acquisition-software, processing-software, or survey-organization conventions may differ.

Adapters must explicitly convert external conventions into HydroSIM internal conventions.

Future mappings may include, as needed:

- Kongsberg
- HYPACK/HYSWEEP
- POS MV / Applanix
- CARIS
- NOAA workflows
- other hydrographic systems

No external convention may be assumed to match HydroSIM merely because it uses the terms roll, pitch, yaw, heave, X, Y, or Z.

## 16. Reference and standards context

The initial conventions were selected for internal consistency and interoperability with common hydrographic practice, while keeping external conventions explicitly convertible.

Relevant references for later traceability include:

- NOAA Office of Coast Survey, Hydrographic Survey Specifications and Deliverables, Version 2026.0.02
- NOAA Office of Coast Survey Field Procedures Manual
- IHO S-44 and related hydrographic guidance
- ISO 19111 / OGC WKT coordinate-reference-system concepts
- EPSG Geodetic Parameter Dataset
- manufacturer documentation for supported sonar and positioning systems

The NOAA HSSD is treated primarily as a survey-data specification. Detailed sensor-axis and Euler-angle conventions must be verified against the relevant field-procedure or manufacturer documentation before external adapters are implemented.

## 17. Remaining items before Issue #1 is closed

The rotation matrices and canonical tests are now defined and approved. Before Issue #1 is closed, review and approve:

1. whether `VRP` is the preferred permanent project term for the body-frame origin;
2. whether any additional external convention must be documented before geometry implementation begins.
